-- These tests roll back all users, sessions, subscriptions and audit entries.
begin;
select set_config('lf.admin',gen_random_uuid()::text,true),set_config('lf.parent',gen_random_uuid()::text,true),set_config('lf.other',gen_random_uuid()::text,true),set_config('lf.admin_session',gen_random_uuid()::text,true),set_config('lf.parent_session',gen_random_uuid()::text,true),set_config('lf.other_session',gen_random_uuid()::text,true),set_config('lf.child',gen_random_uuid()::text,true),set_config('lf.activation',gen_random_uuid()::text,true);
insert into auth.users(id,email,email_confirmed_at) values(current_setting('lf.admin')::uuid,'qa-admin-'||current_setting('lf.admin')||'@example.invalid',now()),(current_setting('lf.parent')::uuid,'qa-parent-'||current_setting('lf.parent')||'@example.invalid',now()),(current_setting('lf.other')::uuid,'qa-other-'||current_setting('lf.other')||'@example.invalid',now());
insert into auth.sessions(id,user_id) values(current_setting('lf.admin_session')::uuid,current_setting('lf.admin')::uuid),(current_setting('lf.parent_session')::uuid,current_setting('lf.parent')::uuid),(current_setting('lf.other_session')::uuid,current_setting('lf.other')::uuid);
insert into public.profiles(id,full_name) values(current_setting('lf.admin')::uuid,'QA admin'),(current_setting('lf.parent')::uuid,'QA parent'),(current_setting('lf.other')::uuid,'QA other');
insert into public.account_access(user_id,admin_role) values(current_setting('lf.admin')::uuid,true),(current_setting('lf.parent')::uuid,false),(current_setting('lf.other')::uuid,false);
insert into public.subscriptions(user_id) values(current_setting('lf.parent')::uuid);
insert into public.children(id,parent_user_id,display_name,age_band) values(current_setting('lf.child')::uuid,current_setting('lf.parent')::uuid,'QA child','2-3');
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.parent'),'role','authenticated','session_id',current_setting('lf.parent_session'),'user_metadata',json_build_object('admin',true))::text,true);
set local role authenticated;
do $$ declare denied boolean:=false;begin
 if public.littlefinger_has_access() then raise exception 'Registration incorrectly activates access';end if;
 begin perform public.littlefinger_admin_customers('');exception when insufficient_privilege then denied=true;end;
 if not denied then raise exception 'Editable metadata grants admin';end if;
end $$;
reset role;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.admin'),'role','authenticated','session_id',current_setting('lf.admin_session'))::text,true);
set local role authenticated;
do $$ declare a jsonb;b jsonb;denied boolean:=false;begin
 a=public.littlefinger_admin_subscription(current_setting('lf.parent')::uuid,'activate','QA-PAYMENT',39000,current_setting('lf.activation')::uuid);
 if (a->>'access_expires_at')::timestamptz-(a->>'access_starts_at')::timestamptz<>interval '365 days' then raise exception 'Activation duration failure';end if;
 if (a->>'access_starts_at')::timestamptz<>now() then raise exception 'Activation started on registration date';end if;
 b=public.littlefinger_admin_subscription(current_setting('lf.parent')::uuid,'activate','QA-PAYMENT',39000,current_setting('lf.activation')::uuid);
 if a<>b then raise exception 'Idempotent activation failure';end if;
 begin perform public.littlefinger_admin_subscription(current_setting('lf.parent')::uuid,'activate','OTHER-PAYMENT',39000,current_setting('lf.activation')::uuid);exception when raise_exception then denied=true;end;
 if not denied then raise exception 'Conflicting idempotency accepted';end if;
 b=public.littlefinger_admin_subscription(current_setting('lf.parent')::uuid,'renew','QA-RENEWAL',55000,gen_random_uuid());
 if (b->>'access_expires_at')::timestamptz-(a->>'access_expires_at')::timestamptz<>interval '365 days' or b->>'access_starts_at'<>a->>'access_starts_at' then raise exception 'Early renewal loses remaining time';end if;
end $$;
reset role;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.parent'),'role','authenticated','session_id',current_setting('lf.parent_session'))::text,true);
set local role authenticated;
do $$ declare v integer;denied boolean:=false;begin
 v=public.littlefinger_save_workbook(current_setting('lf.child')::uuid,0,'{"family":{},"book":{},"learning":{}}');if v<>1 then raise exception 'Initial cloud save failed';end if;
 v=public.littlefinger_save_workbook(current_setting('lf.child')::uuid,1,'{"family":{"test":"kept"}}');if v<>2 then raise exception 'Revision update failed';end if;
 begin perform public.littlefinger_save_workbook(current_setting('lf.child')::uuid,1,'{"overwritten":true}');exception when raise_exception then denied=true;end;
 if not denied then raise exception 'Stale device overwrote newer data';end if;
end $$;
reset role;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.other'),'role','authenticated','session_id',current_setting('lf.other_session'))::text,true);
set local role authenticated;
do $$ begin if (select count(*) from public.family_workbooks)>0 then raise exception 'Other family can read workbook';end if;end $$;
reset role;
update public.subscriptions set access_starts_at=now()-interval '400 days',access_expires_at=now()-interval '35 days' where user_id=current_setting('lf.parent')::uuid;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.parent'),'role','authenticated','session_id',current_setting('lf.parent_session'))::text,true);
set local role authenticated;
do $$ declare denied boolean:=false;begin
 if (select count(*) from public.family_workbooks)<>1 then raise exception 'History missing after expiry';end if;
 begin perform public.littlefinger_save_workbook(current_setting('lf.child')::uuid,2,'{}');exception when insufficient_privilege then denied=true;end;
 if not denied then raise exception 'Expired write allowed';end if;
end $$;
reset role;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.admin'),'role','authenticated','session_id',current_setting('lf.admin_session'))::text,true);
set local role authenticated;
do $$ declare a jsonb;begin
 a=public.littlefinger_admin_subscription(current_setting('lf.parent')::uuid,'renew','QA-LATE-RENEWAL',39000,gen_random_uuid());
 if (a->>'access_starts_at')::timestamptz<>now() or (a->>'access_expires_at')::timestamptz<>now()+interval '365 days' then raise exception 'Late renewal duration failure';end if;
 perform public.littlefinger_admin_account_status(current_setting('lf.parent')::uuid,'suspended',gen_random_uuid());
end $$;
reset role;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.parent'),'role','authenticated','session_id',current_setting('lf.parent_session'))::text,true);
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Suspended account retains access';end if;end $$;
reset role;
do $$begin if (select count(*) from public.admin_audit_logs where admin_user_id=current_setting('lf.admin')::uuid)<>4 then raise exception 'Audit missing or duplicate';end if;end $$;
select 'PASS: registration stays pending, privilege denial, exact 365-day activation, replay protection, early/late renewal, ownership, revision conflict, retained expired history, suspension and audit' result;
rollback;
