-- Product access follows the server-managed role, never editable user metadata.
-- Admins still need an active account and a verified, non-revoked Auth session.
create or replace function public.littlefinger_has_access() returns boolean
language sql stable security invoker set search_path = '' as $$
  select auth.uid() is not null
    and (select private.verified_parent_session())
    and exists (
      select 1 from public.account_access a
      where a.user_id=auth.uid() and a.account_status='active'
        and (
          a.admin_role
          or exists (
            select 1 from public.subscriptions s
            where s.user_id=a.user_id and s.status='active'
              and s.access_starts_at<=now() and s.access_expires_at>now()
          )
        )
    );
$$;
revoke all on function public.littlefinger_has_access() from public, anon, authenticated;
grant execute on function public.littlefinger_has_access() to authenticated;
