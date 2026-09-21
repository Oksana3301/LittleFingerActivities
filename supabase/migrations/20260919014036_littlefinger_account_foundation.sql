-- Account foundation only. No customer or legacy recording is migrated here.
-- Private schema is deliberately NOT an exposed Data API schema.
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
grant usage on schema private to authenticated, service_role;

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null check (char_length(full_name) between 1 and 100),
  whatsapp_e164 text check (whatsapp_e164 ~ '^\+[1-9][0-9]{7,14}$'),
  preferred_language text not null default 'id' check (preferred_language in ('id','en','zh','ar')),
  timezone text not null default 'Asia/Jakarta' check (char_length(timezone) between 1 and 80),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Separate from editable profile data: no user can grant themselves a role/access.
create table public.account_access (
  user_id uuid primary key references auth.users(id) on delete cascade,
  account_status text not null default 'active' check (account_status in ('active','suspended','blocked')),
  admin_role boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.children (
  id uuid primary key default gen_random_uuid(),
  parent_user_id uuid not null references public.profiles(id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 60),
  age_band text not null check (age_band in ('2-3','3-4','4-5','5-6')),
  preferred_language text not null default 'id' check (preferred_language in ('id','en','zh','ar')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, parent_user_id)
);
create index children_parent_idx on public.children(parent_user_id);

create table public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  plan_code text not null default 'yearly' check (char_length(plan_code) between 1 and 40),
  status text not null default 'pending' check (status in ('pending','payment_review','active','expired','cancelled')),
  access_starts_at timestamptz,
  access_expires_at timestamptz,
  price_paid integer not null default 39000 check (price_paid >= 0),
  currency text not null default 'IDR' check (currency ~ '^[A-Z]{3}$'),
  payment_reference text check (char_length(payment_reference) <= 200),
  activated_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check ((access_starts_at is null and access_expires_at is null) or (access_starts_at is not null and access_expires_at is not null and access_expires_at > access_starts_at)),
  check (status <> 'active' or (access_starts_at is not null and access_expires_at is not null))
);
create index subscriptions_user_idx on public.subscriptions(user_id, access_expires_at desc);
create index subscriptions_actor_idx on public.subscriptions(activated_by);
create index subscriptions_expiry_idx on public.subscriptions(access_expires_at) where status='active';
create unique index subscriptions_one_active_idx on public.subscriptions(user_id) where status='active';

create table public.activity_progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  child_id uuid not null,
  activity_id text not null check (char_length(activity_id) between 1 and 140),
  category_id text not null check (char_length(category_id) between 1 and 100),
  is_correct boolean,
  attempt_count integer not null default 1 check (attempt_count between 0 and 10000),
  duration_seconds integer not null default 0 check (duration_seconds between 0 and 86400),
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key(child_id, user_id) references public.children(id, parent_user_id) on delete cascade
);
create index progress_parent_date_idx on public.activity_progress(user_id, created_at desc);
create index progress_child_parent_idx on public.activity_progress(child_id, user_id);

create table public.marketing_leads (
  id uuid primary key default gen_random_uuid(),
  email_normalized text not null unique check (char_length(email_normalized) <= 254 and email_normalized=lower(btrim(email_normalized)) and email_normalized ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'),
  parent_name text not null check (char_length(parent_name) between 1 and 100),
  whatsapp_e164 text not null check (whatsapp_e164 ~ '^\+[1-9][0-9]{7,14}$'),
  child_age_band text not null check (child_age_band in ('2-3','3-4','4-5','5-6')),
  preferred_language text not null default 'id' check (preferred_language in ('id','en','zh','ar')),
  status text not null default 'new' check (status in ('new','email_pending','verified','preorder_pending','payment_review','active','expiring','expired','unsubscribed','rejected','suspended','blocked')),
  email_verified_at timestamptz,
  marketing_consent_at timestamptz,
  privacy_consent_at timestamptz not null,
  consent_version text not null check (char_length(consent_version) between 1 and 80),
  utm_source text check (char_length(utm_source)<=200),
  utm_medium text check (char_length(utm_medium)<=200),
  utm_campaign text check (char_length(utm_campaign)<=200),
  utm_content text check (char_length(utm_content)<=200),
  utm_term text check (char_length(utm_term)<=200),
  referral_code text check (char_length(referral_code)<=100),
  landing_page text check (char_length(landing_page)<=500),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (status not in ('verified','preorder_pending','payment_review','active','expiring','expired') or email_verified_at is not null)
);
create index leads_status_date_idx on public.marketing_leads(status, created_at desc);
create index leads_whatsapp_idx on public.marketing_leads(whatsapp_e164);

create table public.admin_audit_logs (
  id uuid primary key default gen_random_uuid(),
  admin_user_id uuid not null references auth.users(id) on delete restrict,
  action text not null check (char_length(action) between 1 and 100),
  target_type text not null check (target_type in ('profile','subscription','lead','account','session','role')),
  target_id uuid not null,
  before_data jsonb not null default '{}'::jsonb check (jsonb_typeof(before_data)='object' and pg_column_size(before_data)<=8192),
  after_data jsonb not null default '{}'::jsonb check (jsonb_typeof(after_data)='object' and pg_column_size(after_data)<=8192),
  idempotency_key uuid not null unique,
  created_at timestamptz not null default now()
);
create index audit_actor_date_idx on public.admin_audit_logs(admin_user_id, created_at desc);
create index audit_target_idx on public.admin_audit_logs(target_type, target_id, created_at desc);

-- Reserved for explicit, dual-authenticated linking; never match owners by email.
create table private.legacy_voice_links (
  user_id uuid primary key references auth.users(id) on delete cascade,
  legacy_owner_hash text not null unique check (legacy_owner_hash ~ '^[a-f0-9]{64}$'),
  linked_at timestamptz not null default now()
);
alter table private.legacy_voice_links enable row level security;
revoke all on private.legacy_voice_links from public, anon, authenticated;
grant select, insert, delete on private.legacy_voice_links to service_role;

-- Needed to validate Auth session revocation and email status without exposing Auth tables.
create function private.verified_parent_session() returns boolean
language sql stable security definer set search_path = '' as $$
  select auth.uid() is not null and exists (
    select 1 from auth.users u join auth.sessions s on s.user_id=u.id
    where u.id=auth.uid() and u.email_confirmed_at is not null and not u.is_anonymous
      and s.id::text=auth.jwt()->>'session_id' and (s.not_after is null or s.not_after>now())
  );
$$;
revoke all on function private.verified_parent_session() from public, anon, authenticated;
grant execute on function private.verified_parent_session() to authenticated;

create function private.touch_updated_at() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin new.updated_at=now(); return new; end;
$$;
revoke all on function private.touch_updated_at() from public, anon, authenticated;

-- Audit records cannot be updated, deleted or truncated through application roles.
create function private.reject_audit_change() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin raise exception 'Audit log is append-only'; end;
$$;
revoke all on function private.reject_audit_change() from public, anon, authenticated;
create trigger audit_no_change before update or delete or truncate on public.admin_audit_logs
for each statement execute function private.reject_audit_change();

do $$ declare t text; begin
  foreach t in array array['profiles','account_access','children','subscriptions','activity_progress','marketing_leads','admin_audit_logs'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on table public.%I from public, anon, authenticated', t);
    execute format('grant select, insert, update, delete on table public.%I to service_role', t);
    if t <> 'admin_audit_logs' then
      execute format('create trigger touch_updated_at before update on public.%I for each row execute function private.touch_updated_at()', t);
    end if;
  end loop;
end $$;
revoke update, delete on public.admin_audit_logs from service_role;

-- Fixed profile ownership plus column grants protect server-owned timestamps/IDs.
grant select on public.profiles, public.account_access, public.children, public.subscriptions, public.activity_progress to authenticated;
grant insert(id, full_name, whatsapp_e164, preferred_language, timezone) on public.profiles to authenticated;
grant update(full_name, whatsapp_e164, preferred_language, timezone) on public.profiles to authenticated;
grant insert(id, parent_user_id, display_name, age_band, preferred_language) on public.children to authenticated;
grant update(display_name, age_band, preferred_language) on public.children to authenticated;
grant delete on public.children to authenticated;
grant insert(id, user_id, child_id, activity_id, category_id, is_correct, attempt_count, duration_seconds, completed_at) on public.activity_progress to authenticated;
grant update(is_correct, attempt_count, duration_seconds, completed_at) on public.activity_progress to authenticated;

create policy profiles_read on public.profiles for select to authenticated
using (id=(select auth.uid()) and (select private.verified_parent_session()));
create policy profiles_create on public.profiles for insert to authenticated
with check (id=(select auth.uid()) and (select private.verified_parent_session()));
create policy profiles_edit on public.profiles for update to authenticated
using (id=(select auth.uid()) and (select private.verified_parent_session()))
with check (id=(select auth.uid()) and (select private.verified_parent_session()));
create policy account_read on public.account_access for select to authenticated
using (user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy subscription_read on public.subscriptions for select to authenticated
using (user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy children_read on public.children for select to authenticated
using (parent_user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy children_create on public.children for insert to authenticated
with check (parent_user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy children_edit on public.children for update to authenticated
using (parent_user_id=(select auth.uid()) and (select private.verified_parent_session()))
with check (parent_user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy children_delete on public.children for delete to authenticated
using (parent_user_id=(select auth.uid()) and (select private.verified_parent_session()));
create policy progress_read on public.activity_progress for select to authenticated
using (user_id=(select auth.uid()) and (select private.verified_parent_session()));

-- These read only the caller's rows under RLS; neither is a privileged RPC.
create function public.littlefinger_has_access() returns boolean
language sql stable security invoker set search_path = '' as $$
 select auth.uid() is not null and (select private.verified_parent_session())
   and exists(select 1 from public.account_access where user_id=auth.uid() and account_status='active')
   and exists(select 1 from public.subscriptions where user_id=auth.uid() and status='active' and access_starts_at<=now() and access_expires_at>now());
$$;
revoke all on function public.littlefinger_has_access() from public, anon, authenticated;
grant execute on function public.littlefinger_has_access() to authenticated;

create policy progress_create on public.activity_progress for insert to authenticated
with check (user_id=(select auth.uid()) and (select public.littlefinger_has_access()) and child_id in (select id from public.children where parent_user_id=(select auth.uid())));
create policy progress_edit on public.activity_progress for update to authenticated
using (user_id=(select auth.uid()) and (select public.littlefinger_has_access()))
with check (user_id=(select auth.uid()) and (select public.littlefinger_has_access()) and child_id in (select id from public.children where parent_user_id=(select auth.uid())));

-- No public/authenticated table grants for leads or audit. Explicit service-only policies
-- document intended access; normal users cannot obtain privileged roles via metadata.
create policy leads_service_only on public.marketing_leads for all to service_role using(true) with check(true);
create policy audit_service_read on public.admin_audit_logs for select to service_role using(true);
create policy audit_service_insert on public.admin_audit_logs for insert to service_role with check(true);
create policy voice_link_service_only on private.legacy_voice_links for all to service_role using(true) with check(true);

-- Harmless connectivity probe: no records, IDs, credentials, or infrastructure details.
create function public.littlefinger_schema_version() returns integer
language sql immutable security invoker set search_path = '' as $$ select 1; $$;
revoke all on function public.littlefinger_schema_version() from public;
grant execute on function public.littlefinger_schema_version() to anon, authenticated, service_role;

-- Preserve Supabase's existing event trigger; remove unnecessary direct API execution.
do $$ begin
 if to_regprocedure('public.rls_auto_enable()') is not null then
   revoke execute on function public.rls_auto_enable() from public, anon, authenticated;
 end if;
end $$;
