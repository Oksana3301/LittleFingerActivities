-- Transaction-only regression checks. No emails sent; fixtures are rolled back.
begin;
select set_config('lf.test_a',gen_random_uuid()::text,true), set_config('lf.test_b',gen_random_uuid()::text,true), set_config('lf.session_a',gen_random_uuid()::text,true), set_config('lf.session_b',gen_random_uuid()::text,true), set_config('lf.child_a',gen_random_uuid()::text,true), set_config('lf.child_b',gen_random_uuid()::text,true);
insert into auth.users(id,email,email_confirmed_at) values
(current_setting('lf.test_a')::uuid,'lf-rls-a-'||current_setting('lf.test_a')||'@example.invalid',now()),
(current_setting('lf.test_b')::uuid,'lf-rls-b-'||current_setting('lf.test_b')||'@example.invalid',now());
insert into auth.sessions(id,user_id) values
(current_setting('lf.session_a')::uuid,current_setting('lf.test_a')::uuid),
(current_setting('lf.session_b')::uuid,current_setting('lf.test_b')::uuid);
insert into public.profiles(id,full_name) values(current_setting('lf.test_a')::uuid,'Test A'),(current_setting('lf.test_b')::uuid,'Test B');
insert into public.account_access(user_id) values(current_setting('lf.test_a')::uuid),(current_setting('lf.test_b')::uuid);
insert into public.children(id,parent_user_id,display_name,age_band) values
(current_setting('lf.child_a')::uuid,current_setting('lf.test_a')::uuid,'Child A','2-3'),
(current_setting('lf.child_b')::uuid,current_setting('lf.test_b')::uuid,'Child B','3-4');
insert into public.subscriptions(user_id,status,access_starts_at,access_expires_at) values
(current_setting('lf.test_a')::uuid,'active',now()-interval '1 day',now()+interval '364 days'),
(current_setting('lf.test_b')::uuid,'active',now()-interval '366 days',now()-interval '1 day');
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.test_a'),'role','authenticated','session_id',current_setting('lf.session_a'),'user_metadata',json_build_object('admin',true))::text,true);
set local role authenticated;
do $$ declare n integer; denied boolean; begin
 if (select count(*) from public.profiles)<>1 then raise exception 'Profile ownership failure'; end if;
 if (select count(*) from public.children)<>1 then raise exception 'Child ownership failure'; end if;
 if (select count(*) from public.subscriptions)<>1 then raise exception 'Subscription ownership failure'; end if;
 if not public.littlefinger_has_access() then raise exception 'Active entitlement failure'; end if;
 update public.profiles set full_name='Allowed' where id=auth.uid(); get diagnostics n=row_count;
 if n<>1 then raise exception 'Owner profile update failed'; end if;
 update public.children set display_name='Not allowed' where id=current_setting('lf.child_b')::uuid; get diagnostics n=row_count;
 if n<>0 then raise exception 'Cross-family update allowed'; end if;
 denied=false;
 begin insert into public.children(parent_user_id,display_name,age_band) values(current_setting('lf.test_b')::uuid,'Forbidden','2-3'); exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Cross-family child insert allowed'; end if;
 denied=false;
 begin insert into public.activity_progress(user_id,child_id,activity_id,category_id) values(auth.uid(),current_setting('lf.child_b')::uuid,'test','test'); exception when insufficient_privilege or foreign_key_violation then denied=true; end;
 if not denied then raise exception 'Cross-family progress insert allowed'; end if;
 insert into public.activity_progress(user_id,child_id,activity_id,category_id,is_correct) values(auth.uid(),current_setting('lf.child_a')::uuid,'test','test',true);
 denied=false; begin update public.subscriptions set access_expires_at=now()+interval '10 years'; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Subscription self-edit allowed'; end if;
 denied=false; begin update public.account_access set admin_role=true; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Role self-escalation allowed'; end if;
 denied=false; begin perform * from public.marketing_leads; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Lead disclosure allowed'; end if;
 denied=false; begin perform * from public.admin_audit_logs; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Audit disclosure allowed'; end if;
 denied=false; begin update public.children set parent_user_id=current_setting('lf.test_b')::uuid; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Child reassignment allowed'; end if;
end $$;
reset role;
update public.subscriptions set access_expires_at=now()-interval '1 hour' where user_id=current_setting('lf.test_a')::uuid;
set local role authenticated;
do $$ declare n integer; begin
 if public.littlefinger_has_access() then raise exception 'Expired entitlement allowed'; end if;
 if (select count(*) from public.activity_progress)<>1 then raise exception 'Expired progress history lost'; end if;
 update public.activity_progress set attempt_count=100; get diagnostics n=row_count;
 if n<>0 then raise exception 'Expired progress writes allowed'; end if;
end $$;
reset role;
update public.subscriptions set access_expires_at=now()+interval '365 days' where user_id=current_setting('lf.test_a')::uuid;
update public.account_access set account_status='suspended' where user_id=current_setting('lf.test_a')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Suspended entitlement allowed'; end if; end $$;
reset role;
update public.account_access set account_status='active' where user_id=current_setting('lf.test_a')::uuid;
update public.subscriptions set status='pending' where user_id=current_setting('lf.test_a')::uuid;
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Pending entitlement allowed'; end if; end $$;
reset role;
update public.subscriptions set status='active' where user_id=current_setting('lf.test_a')::uuid;
update auth.users set email_confirmed_at=null where id=current_setting('lf.test_a')::uuid;
set local role authenticated;
do $$ begin
 if public.littlefinger_has_access() then raise exception 'Unverified entitlement allowed'; end if;
 if (select count(*) from public.children)<>0 then raise exception 'Unverified session read allowed'; end if;
end $$;
reset role;
update auth.users set email_confirmed_at=now() where id=current_setting('lf.test_a')::uuid;
-- A signed JWT carrying another person's session id must not authenticate the caller.
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.test_a'),'role','authenticated','session_id',current_setting('lf.session_b'))::text,true);
set local role authenticated;
do $$ begin if public.littlefinger_has_access() then raise exception 'Session/user mismatch allowed'; end if; end $$;
reset role;
select set_config('request.jwt.claims',json_build_object('sub',current_setting('lf.test_a'),'role','authenticated','session_id',current_setting('lf.session_a'))::text,true);
delete from auth.sessions where id=current_setting('lf.session_a')::uuid;
set local role authenticated;
do $$ begin
 if public.littlefinger_has_access() then raise exception 'Revoked session entitlement allowed'; end if;
 if (select count(*) from public.profiles)<>0 then raise exception 'Revoked session read allowed'; end if;
end $$;
reset role;
-- Date constraints and append-only enforcement are independent of frontend checks.
do $$ declare denied boolean; begin
 denied=false; begin insert into public.subscriptions(user_id,access_starts_at) values(current_setting('lf.test_b')::uuid,now()); exception when check_violation then denied=true; end;
 if not denied then raise exception 'Incomplete subscription dates allowed'; end if;
 insert into public.admin_audit_logs(admin_user_id,action,target_type,target_id,idempotency_key) values(current_setting('lf.test_a')::uuid,'test','account',current_setting('lf.test_b')::uuid,gen_random_uuid());
 denied=false; begin update public.admin_audit_logs set action='tampered'; exception when raise_exception then denied=true; end;
 if not denied then raise exception 'Audit change allowed'; end if;
end $$;
select set_config('request.jwt.claims','{}',true);
set local role anon;
do $$ declare denied boolean; begin
 if public.littlefinger_schema_version()<>1 then raise exception 'Database probe failure'; end if;
 denied=false; begin perform * from public.profiles; exception when insufficient_privilege then denied=true; end;
 if not denied then raise exception 'Anonymous profile read allowed'; end if;
end $$;
reset role;
select 'PASS: ownership, grants, active/pending/expired/suspended/unverified/revoked sessions, date constraints, immutable audit, anonymous denial' as result;
rollback;
