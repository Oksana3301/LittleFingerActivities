-- Disposable fixtures only. All changes roll back; no credentials or emails.
begin;
select set_config('lf.admin',gen_random_uuid()::text,true),
       set_config('lf.other',gen_random_uuid()::text,true),
       set_config('lf.admin_session',gen_random_uuid()::text,true),
       set_config('lf.admin_child',gen_random_uuid()::text,true),
       set_config('lf.other_child',gen_random_uuid()::text,true);
insert into auth.users(id,email,email_confirmed_at) values
 (current_setting('lf.admin')::uuid,'qa-access-'||current_setting('lf.admin')||'@example.invalid',now()),
 (current_setting('lf.other')::uuid,'qa-other-'||current_setting('lf.other')||'@example.invalid',now());
insert into auth.sessions(id,user_id) values(current_setting('lf.admin_session')::uuid,current_setting('lf.admin')::uuid);
insert into public.profiles(id,full_name) values(current_setting('lf.admin')::uuid,'QA admin'),(current_setting('lf.other')::uuid,'QA other');
insert into public.account_access(user_id,admin_role) values(current_setting('lf.admin')::uuid,true),(current_setting('lf.other')::uuid,false);
insert into public.children(id,parent_user_id,display_name,age_band) values
 (current_setting('lf.admin_child')::uuid,current_setting('lf.admin')::uuid,'Admin child','2-3'),
 (current_setting('lf.other_child')::uuid,current_setting('lf.other')::uuid,'Other child','2-3');
insert into public.family_workbooks(child_id,user_id,payload) values(current_setting('lf.other_child')::uuid,current_setting('lf.other')::uuid,'{"private":true}');
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.admin'),'role','authenticated','session_id',current_setting('lf.admin_session'),'user_metadata',json_build_object('admin_role',true))::text,true);
set local role authenticated;
do $$ declare denied boolean:=false; n integer; begin
 if not public.littlefinger_has_access() then raise exception 'Admin without subscription denied'; end if;
 if (select count(*) from public.children)<>1 or (select count(*) from public.family_workbooks)<>0 then raise exception 'Admin can read another family'; end if;
 n=public.littlefinger_save_workbook(current_setting('lf.admin_child')::uuid,0,'{"admin_progress":true}');
 if n<>1 then raise exception 'Admin own-family save denied'; end if;
 update public.family_workbooks set payload='{}' where child_id=current_setting('lf.other_child')::uuid;
 get diagnostics n=row_count;
 if n<>0 then raise exception 'Admin can overwrite another family'; end if;
 begin
   insert into public.activity_progress(user_id,child_id,activity_id,category_id) values(auth.uid(),current_setting('lf.other_child')::uuid,'qa','qa');
 exception when insufficient_privilege or foreign_key_violation then denied=true; end;
 if not denied then raise exception 'Admin cross-family progress allowed'; end if;
 denied=false;
 begin update public.account_access set admin_role=true; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Admin role self-edit allowed'; end if;
end $$;
reset role;
insert into public.subscriptions(user_id) values(current_setting('lf.admin')::uuid);
set local role authenticated;
do $$ begin if not public.littlefinger_has_access() then raise exception 'Pending subscription blocks admin'; end if; end $$;
reset role;
update public.subscriptions set status='expired',access_starts_at=now()-interval '366 days',access_expires_at=now()-interval '1 day' where user_id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if not public.littlefinger_has_access() then raise exception 'Expired subscription blocks admin'; end if; end $$;
reset role;
-- Changes to the database role apply without refreshing stale JWT metadata.
update public.account_access set admin_role=false where user_id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Revoked admin / editable metadata grants access'; end if; end $$;
reset role;
update public.subscriptions set status='pending' where user_id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Pending ordinary customer granted access'; end if; end $$;
reset role;
update public.subscriptions set status='active',access_starts_at=now()-interval '1 day',access_expires_at=now()+interval '364 days' where user_id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if not public.littlefinger_has_access() then raise exception 'Paid ordinary customer denied'; end if; end $$;
reset role;
update public.account_access set admin_role=true,account_status='suspended' where user_id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Suspended paid admin granted access'; end if; end $$;
reset role;
update public.account_access set account_status='blocked' where user_id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Blocked paid admin granted access'; end if; end $$;
reset role;
update public.account_access set account_status='active' where user_id=current_setting('lf.admin')::uuid;
update auth.users set email_confirmed_at=null where id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Unverified admin granted access'; end if; end $$;
reset role;
update auth.users set email_confirmed_at=now(),is_anonymous=true where id=current_setting('lf.admin')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Anonymous admin granted access'; end if; end $$;
reset role;
update auth.users set is_anonymous=false where id=current_setting('lf.admin')::uuid;
update auth.sessions set not_after=now()-interval '1 second' where id=current_setting('lf.admin_session')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Expired admin session granted access'; end if; end $$;
reset role;
delete from auth.sessions where id=current_setting('lf.admin_session')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Revoked admin session granted access'; end if; end $$;
reset role;
select set_config('request.jwt.claims','{}',true);
set local role anon;
do $$ declare denied boolean:=false; begin
 begin perform public.littlefinger_has_access(); exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Unauthenticated visitor can invoke entitlement'; end if;
end $$;
reset role;
select 'PASS: admin product access, customer subscriptions, role revocation, account/session restrictions and family isolation' result;
rollback;
