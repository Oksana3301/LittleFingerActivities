-- Customer operations use verified live Supabase sessions, never editable JWT metadata.
create table private.owner_allowlist (
  email text primary key check (email=lower(btrim(email)))
);
alter table private.owner_allowlist enable row level security;
revoke all on private.owner_allowlist from public,anon,authenticated;

create function public.littlefinger_session_ok() returns boolean language sql stable security invoker set search_path='' as $$
 select auth.uid() is not null and private.verified_parent_session();
$$;
revoke all on function public.littlefinger_session_ok() from public,anon;
grant execute on function public.littlefinger_session_ok() to authenticated;

create function private.initialize_account(p_name text,p_whatsapp text,p_language text,p_marketing boolean,p_age text) returns void
language plpgsql security definer set search_path='' as $$
declare v_user uuid:=auth.uid(); v_email text;
begin
 if v_user is null or not private.verified_parent_session() then raise insufficient_privilege; end if;
 select lower(email) into v_email from auth.users where id=v_user;
 insert into public.profiles(id,full_name,whatsapp_e164,preferred_language)
 values(v_user,p_name,p_whatsapp,p_language) on conflict(id) do nothing;
 insert into public.account_access(user_id,admin_role)
 values(v_user,exists(select 1 from private.owner_allowlist where email=v_email)) on conflict(user_id) do nothing;
 if not exists(select 1 from public.subscriptions where user_id=v_user) then
  insert into public.subscriptions(user_id) values(v_user);
 end if;
 if p_whatsapp is not null then
  insert into public.marketing_leads(email_normalized,parent_name,whatsapp_e164,child_age_band,preferred_language,status,email_verified_at,marketing_consent_at,privacy_consent_at,consent_version)
  values(v_email,p_name,p_whatsapp,p_age,p_language,'preorder_pending',now(),case when p_marketing then now() else null end,now(),'littlefinger-2026-09')
  on conflict(email_normalized) do nothing;
 end if;
end;
$$;
revoke all on function private.initialize_account(text,text,text,boolean,text) from public,anon;
grant execute on function private.initialize_account(text,text,text,boolean,text) to authenticated;
create function public.littlefinger_initialize_account(p_name text,p_whatsapp text,p_language text,p_marketing boolean,p_age text) returns void
language sql security invoker set search_path='' as $$ select private.initialize_account(p_name,p_whatsapp,p_language,p_marketing,p_age); $$;
revoke all on function public.littlefinger_initialize_account(text,text,text,boolean,text) from public,anon;
grant execute on function public.littlefinger_initialize_account(text,text,text,boolean,text) to authenticated;

create table public.family_workbooks (
 child_id uuid primary key,
 user_id uuid not null references public.profiles(id) on delete cascade,
 payload jsonb not null default '{}'::jsonb check(jsonb_typeof(payload)='object' and pg_column_size(payload)<=1500000),
 revision integer not null default 1 check(revision>0),
 updated_at timestamptz not null default now(),
 foreign key(child_id,user_id) references public.children(id,parent_user_id) on delete cascade
);
create index family_workbooks_user_idx on public.family_workbooks(user_id);
alter table public.family_workbooks enable row level security;
revoke all on public.family_workbooks from public,anon,authenticated;
grant select,insert,update on public.family_workbooks to authenticated;
create policy workbook_read on public.family_workbooks for select to authenticated
using(user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy workbook_create on public.family_workbooks for insert to authenticated
with check(user_id=(select auth.uid()) and (select public.littlefinger_has_access()));
create policy workbook_write on public.family_workbooks for update to authenticated
using(user_id=(select auth.uid()) and (select public.littlefinger_has_access()))
with check(user_id=(select auth.uid()) and (select public.littlefinger_has_access()));
create function public.littlefinger_save_workbook(p_child uuid,p_revision integer,p_payload jsonb) returns integer
language plpgsql security invoker set search_path='' as $$
declare next_revision integer;
begin
 if auth.uid() is null or not public.littlefinger_has_access() then raise insufficient_privilege; end if;
 if p_revision=0 then
  insert into public.family_workbooks(child_id,user_id,payload) values(p_child,auth.uid(),p_payload)
  on conflict(child_id) do nothing returning revision into next_revision;
 else
  update public.family_workbooks set payload=p_payload,revision=revision+1,updated_at=now()
  where child_id=p_child and user_id=auth.uid() and revision=p_revision returning revision into next_revision;
 end if;
 if next_revision is null then raise exception 'workbook_conflict'; end if;
 return next_revision;
end;
$$;
revoke all on function public.littlefinger_save_workbook(uuid,integer,jsonb) from public,anon;
grant execute on function public.littlefinger_save_workbook(uuid,integer,jsonb) to authenticated;

create table public.subscription_requests (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references public.profiles(id) on delete cascade,
 request_type text not null check(request_type in ('activate','renew')),
 status text not null default 'pending' check(status in ('pending','completed','cancelled')),
 created_at timestamptz not null default now()
);
create index subscription_requests_user_idx on public.subscription_requests(user_id);
create unique index subscription_requests_pending_idx on public.subscription_requests(user_id) where status='pending';
alter table public.subscription_requests enable row level security;
revoke all on public.subscription_requests from public,anon,authenticated;
grant select,insert(user_id,request_type) on public.subscription_requests to authenticated;
create policy request_read on public.subscription_requests for select to authenticated
using(user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy request_create on public.subscription_requests for insert to authenticated
with check(user_id=(select auth.uid()) and (select private.verified_parent_session()));

create function private.customer_is_admin() returns boolean
language sql stable security definer set search_path='' as $$
 select auth.uid() is not null and private.verified_parent_session() and exists(select 1 from public.account_access where user_id=auth.uid() and admin_role and account_status='active');
$$;
revoke all on function private.customer_is_admin() from public,anon;
grant execute on function private.customer_is_admin() to authenticated;

create function private.admin_customers(p_query text) returns jsonb
language plpgsql stable security definer set search_path='' as $$
begin
 if auth.uid() is null or not private.customer_is_admin() then raise insufficient_privilege; end if;
 return coalesce((select jsonb_agg(to_jsonb(t)) from (
 select p.id,p.full_name,p.whatsapp_e164,u.email,a.account_status,a.admin_role,
 (select to_jsonb(s) from public.subscriptions s where s.user_id=p.id order by s.created_at desc limit 1) subscription,
 (select to_jsonb(r) from public.subscription_requests r where r.user_id=p.id and r.status='pending' limit 1) request
 from public.profiles p join auth.users u on u.id=p.id join public.account_access a on a.user_id=p.id
 where p_query='' or p.full_name ilike '%'||left(p_query,100)||'%' or u.email ilike '%'||left(p_query,100)||'%' or p.whatsapp_e164 ilike '%'||left(p_query,100)||'%'
 order by p.created_at desc limit 100
 ) t),'[]'::jsonb);
end;
$$;
revoke all on function private.admin_customers(text) from public,anon;
grant execute on function private.admin_customers(text) to authenticated;
create function public.littlefinger_admin_customers(p_query text default '') returns jsonb
language sql stable security invoker set search_path='' as $$ select private.admin_customers(p_query); $$;
revoke all on function public.littlefinger_admin_customers(text) from public,anon;
grant execute on function public.littlefinger_admin_customers(text) to authenticated;

create function private.admin_subscription(p_user uuid,p_action text,p_reference text,p_amount integer,p_key uuid) returns jsonb
language plpgsql security definer set search_path='' as $$
declare v_actor uuid:=auth.uid(); v_before jsonb; v_after jsonb; v_existing public.admin_audit_logs%rowtype; v_sub public.subscriptions%rowtype; v_start timestamptz; v_end timestamptz;
begin
 if v_actor is null or not private.customer_is_admin() then raise insufficient_privilege; end if;
 if p_action not in ('activate','renew') or p_amount not in (39000,55000) or char_length(btrim(p_reference)) not between 3 and 200 or p_key is null then raise exception 'invalid_activation'; end if;
 perform pg_advisory_xact_lock(hashtextextended(p_user::text,0));
 select * into v_existing from public.admin_audit_logs where idempotency_key=p_key;
 if found then
  if v_existing.admin_user_id<>v_actor or v_existing.action<>p_action or v_existing.after_data->>'user_id'<>p_user::text or v_existing.after_data->>'payment_reference'<>p_reference or (v_existing.after_data->>'price_paid')::integer<>p_amount then raise exception 'idempotency_conflict'; end if;
  return v_existing.after_data;
 end if;
 if not exists(select 1 from auth.users where id=p_user and email_confirmed_at is not null and not is_anonymous) then raise exception 'unverified_customer'; end if;
 if not exists(select 1 from public.account_access where user_id=p_user and account_status='active') then raise exception 'inactive_customer'; end if;
 select * into v_sub from public.subscriptions where user_id=p_user order by created_at desc limit 1 for update;
 if not found then raise exception 'missing_subscription'; end if;
 v_before=to_jsonb(v_sub);
 if p_action='activate' and v_sub.status='active' and v_sub.access_expires_at>now() then raise exception 'already_active'; end if;
 if p_action='renew' and v_sub.access_starts_at is null then raise exception 'activate_first'; end if;
 if p_action='renew' and v_sub.status='active' and v_sub.access_expires_at>now() then
  v_start=v_sub.access_starts_at; v_end=v_sub.access_expires_at+interval '365 days';
 else v_start=now();v_end=v_start+interval '365 days';end if;
 update public.subscriptions set status='expired' where user_id=p_user and status='active' and id<>v_sub.id;
 update public.subscriptions set status='active',access_starts_at=v_start,access_expires_at=v_end,price_paid=p_amount,payment_reference=p_reference,activated_by=v_actor where id=v_sub.id returning to_jsonb(subscriptions.*) into v_after;
 insert into public.admin_audit_logs(admin_user_id,action,target_type,target_id,before_data,after_data,idempotency_key)
 values(v_actor,p_action,'subscription',v_sub.id,v_before,v_after,p_key);
 update public.subscription_requests set status='completed' where user_id=p_user and status='pending';
 return v_after;
end;
$$;
revoke all on function private.admin_subscription(uuid,text,text,integer,uuid) from public,anon;
grant execute on function private.admin_subscription(uuid,text,text,integer,uuid) to authenticated;
create function public.littlefinger_admin_subscription(p_user uuid,p_action text,p_reference text,p_amount integer,p_key uuid) returns jsonb
language sql security invoker set search_path='' as $$ select private.admin_subscription(p_user,p_action,p_reference,p_amount,p_key); $$;
revoke all on function public.littlefinger_admin_subscription(uuid,text,text,integer,uuid) from public,anon;
grant execute on function public.littlefinger_admin_subscription(uuid,text,text,integer,uuid) to authenticated;

create function private.admin_account_status(p_user uuid,p_status text,p_key uuid) returns void
language plpgsql security definer set search_path='' as $$
declare v_before jsonb;v_after jsonb;v_actor uuid:=auth.uid();v_existing public.admin_audit_logs%rowtype;
begin
 if v_actor is null or not private.customer_is_admin() then raise insufficient_privilege; end if;
 if p_status not in ('active','suspended','blocked') or p_user=v_actor then raise exception 'invalid_status_change'; end if;
 perform pg_advisory_xact_lock(hashtextextended(p_user::text,0));
 select * into v_existing from public.admin_audit_logs where idempotency_key=p_key;
 if found then
  if v_existing.admin_user_id<>v_actor or v_existing.action<>'account_status' or v_existing.target_id<>p_user or v_existing.after_data->>'account_status'<>p_status then raise exception 'idempotency_conflict';end if;
  return;
 end if;
 select to_jsonb(a) into v_before from public.account_access a where user_id=p_user for update;
 if v_before is null then raise exception 'missing_account';end if;
 update public.account_access set account_status=p_status where user_id=p_user returning to_jsonb(account_access.*) into v_after;
 insert into public.admin_audit_logs(admin_user_id,action,target_type,target_id,before_data,after_data,idempotency_key) values(v_actor,'account_status','account',p_user,v_before,v_after,p_key);
end;
$$;
revoke all on function private.admin_account_status(uuid,text,uuid) from public,anon;
grant execute on function private.admin_account_status(uuid,text,uuid) to authenticated;
create function public.littlefinger_admin_account_status(p_user uuid,p_status text,p_key uuid) returns void
language sql security invoker set search_path='' as $$ select private.admin_account_status(p_user,p_status,p_key); $$;
revoke all on function public.littlefinger_admin_account_status(uuid,text,uuid) from public,anon;
grant execute on function public.littlefinger_admin_account_status(uuid,text,uuid) to authenticated;

create function private.customer_marketing(p_consent boolean) returns void
language plpgsql security definer set search_path='' as $$
begin
 if auth.uid() is null or not private.verified_parent_session() then raise insufficient_privilege;end if;
 update public.marketing_leads set marketing_consent_at=case when p_consent then now() else null end
 where email_normalized=(select lower(email) from auth.users where id=auth.uid());
end;
$$;
revoke all on function private.customer_marketing(boolean) from public,anon;
grant execute on function private.customer_marketing(boolean) to authenticated;
create function public.littlefinger_marketing_consent(p_consent boolean) returns void
language sql security invoker set search_path='' as $$ select private.customer_marketing(p_consent); $$;
revoke all on function public.littlefinger_marketing_consent(boolean) from public,anon;
grant execute on function public.littlefinger_marketing_consent(boolean) to authenticated;
