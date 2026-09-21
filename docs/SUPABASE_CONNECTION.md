# Littlefinger Supabase connection

Project: `eamewoihspijkbsmegod` (Little Finger Activities, Singapore).
Site: https://little-world-playroom.atikadewi.chatgpt.site
Requested GitHub repository: https://github.com/Oksana3301/LittleFingerActivities

## Current scope

This revision connects the existing Site to Supabase and applies the account database foundation. It does **not** release the new email/password customer portal or replace the existing identity/storage flows. The existing activity collection, illustrations, narration, local learning report, D1 preorder records and private R2 parent recordings remain intact.

Production configuration contains `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`. The publishable key was retrieved from the selected project; the project reference itself is not an API key. No service-role or secret key is committed. `.env.example` documents variable names only. Runtime values are supplied by the hosting environment, and local `.env.local` is ignored.

`lib/supabase/connection.ts` is server-only. `/api/admin/integrations` validates the existing trusted owner identity before checking Auth reachability and the schema marker. It returns sanitized status with private/no-store caching; it never returns keys or family records. A healthy marker proves connection and schema version, not that the launch funnel is complete.

## Database

The controlled migration creates:

- `profiles`, `children`, `activity_progress`: owner-only access with column restrictions and a child/parent composite foreign key.
- `account_access`: server-controlled account status/admin role, readable only by the account owner.
- `subscriptions`: owner-readable, no normal-user mutation of price, status or access dates.
- `marketing_leads`: no anonymous or ordinary-user table access.
- `admin_audit_logs`: service insert/read only, update/delete/truncate blocked.
- `private.legacy_voice_links`: reserved for explicit, dual-authenticated identity linking. Empty; no recording has been reassigned.

RLS is enabled on every new table. The non-exposed private session helper checks verified email, a matching live Auth session, and session expiration. The public entitlement RPC runs with caller privileges and checks current active account/subscription status and start/expiry boundaries. Missing records fail closed. Expired subscriptions retain access to their owner's history, while progress writes require active entitlement.

No signup trigger auto-grants a subscription or administrator role. Future server operations must provision account status deliberately. The migration preserves Supabase's existing RLS event trigger while revoking unnecessary direct API execution of its privileged function.

Migration was created with CLI 2.117.0, applied through the Supabase connector, and the local filename reconciled to the exact server-returned migration version. Do not apply it again to this project.

## Verification performed

- Auth settings reachable; email enabled; email auto-confirm disabled; anonymous and phone login disabled.
- Transaction-only SQL regression passed: own profile/child/subscription reads, allowed own-profile update, foreign-family denial, child ownership reassignment denial, role escalation denial, subscription mutation denial, private leads/audit denial.
- Active entitlement allowed; pending, expired, suspended, unverified, mismatched-session and revoked-session entitlement denied.
- Progress survives expiry and cannot be modified after expiry.
- Incomplete subscription dates rejected and audit mutation rejected.
- All test users/sessions/records rolled back. No emails sent.
- Live REST checks: schema marker returned 200; anonymous profile and lead reads returned 401.
- Owner-only integration route passed live read-only checks with real Supabase responses, including denial before fetch, outage/wrong-project failure, no key disclosure, anonymous table denial, and an unexposed private schema.
- TypeScript and production build passed; existing large client-bundle warnings remain part of the premium-content migration work. No Supabase configuration or key was found in the emitted client JavaScript.
- Security Advisor: no findings after migration.
- Performance Advisor: informational unused-index notices only on this new, empty project; retained indexes support ownership joins, expiry queries, and future admin lookup. [Advisor explanation](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index).

These are database integration tests, not end-to-end customer Auth tests. See `supabase/tests/account_isolation.sql`.

## Launch work still required

The attached launch brief remains the next implementation milestone; the current production Site must not be described as a protected paid-access portal yet.

1. Configure and verify transactional SMTP delivery, approved Site/redirect URLs, CAPTCHA/Turnstile and privileged server operations. The current connector does not provide SMTP credentials or CAPTCHA keys. Email-confirmation settings alone do not prove deliverability.
2. Implement a server-only Auth BFF with HttpOnly/Secure/SameSite cookies, CSRF/body limits, shared rate limits, recovery and revocation. Browser clients must not receive tokens. Preserve a clear failure state when a dependency is unavailable.
3. Move premium worksheet/index/legacy payloads out of public assets and client bundles; expose only a bounded free preview. Enforce entitlement before every premium payload. The current public workbook is not yet gated.
4. Build the marketing/account/admin routes and four-language copy. Reviewed draft strings are retained in `docs/launch/launch-i18n.ts`, not claimed as deployed UI.
5. Add verified lead double opt-in, separate optional marketing consent, atomic/idempotent activation and renewal with audit, launch instructions, reminders, monitoring, and tested backup recovery.
6. Explicitly link the old ChatGPT voice owner only after both identities authenticate. Import device-local progress only with parent confirmation into a chosen child/account; never silently associate shared-browser history by email.
7. Run the full brief's real customer and admin end-to-end acceptance tests before replacing the production journey.

## GitHub handoff

The configured GitHub installation is limited to selected repositories and currently includes only the unrelated laundry repository. The requested new repository is readable because it is public, but a write attempt returned HTTP 403 `Resource not accessible by integration`. No GitHub file or commit was created.

Owner action: open https://github.com/settings/installations/160833715, add `LittleFingerActivities` under repository access, and save. The `github` remote points to the requested repo; the existing Site `origin` remains unchanged. Push the complete reviewed source/assets after the installation can write; do not force-push or substitute a different repository.

The repository is currently public. Publishing its full source also publishes the worksheet bank; website entitlement checks do not make a public source repository private. Choose repository visibility deliberately before a commercial launch.
