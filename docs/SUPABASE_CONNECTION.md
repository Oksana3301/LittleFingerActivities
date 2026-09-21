# Littlefinger account integration

Updated 21 September 2026. Project: `eamewoihspijkbsmegod` (Little Finger Activities, Singapore).

Site: https://little-world-playroom.atikadewi.chatgpt.site
Source mirror: https://github.com/Oksana3301/LittleFingerActivities

## Implemented

The existing Site now contains an email/password account BFF, child profiles, cloud workbooks, annual access enforcement, manual owner activation/renewal, and explicit parent-recording linking. Existing artwork, activity IDs, optional faith content, four narration languages, local preview history, preorder leads and private R2 audio remain.

`SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` are hosting environment values. No service-role or secret key is required or committed. Runtime configuration is server-only. Sessions are kept in HttpOnly, Secure, SameSite=Lax, host-only cookies in production. The browser receives account summaries, never Auth tokens. Mutations require same-origin JSON with bounded bodies; Auth operations use shared D1 rate limits.

Registration and recovery use PKCE. A verified email alone is insufficient: session checks also require a live Supabase session. Logout globally revokes the session and clears cookies. Role and subscription checks use database-controlled values, never editable user metadata. Signup creates pending access, not a paid subscription. Owner provisioning requires an address in the private owner allowlist.

The default `CUSTOMER_EMAIL_READY=false` closes registration, resend and recovery with a visible explanation and links to the existing preorder interest form. Login remains available for confirmed accounts. SMTP and real email callback delivery are not yet verified; this release is not a completed public customer onboarding launch.

## Data and content boundaries

- All public account tables have RLS and explicit grants. Each family's children, subscriptions and workbooks are isolated.
- `family_workbooks` stores the existing settings, progress and daily-report data per child. Writes use optimistic revisions; a stale device cannot silently overwrite another device. Failed saves show an export/reload instruction. Browser navigation warns while changes remain unsaved.
- After access expires, parents can read their retained history. Premium payloads and cloud writes are denied. Renewal before expiry adds 365 days to the old expiry; renewal after expiry starts a fresh 365 days.
- Premium category and legacy activity payloads live in `content/` and are served by guarded API routes. The public index contains cover metadata and empty answer keys. Six specified previews plus the introduction remain free. Generator paths preserve this boundary.
- Existing browser history is imported only after an explicit parent confirmation into an empty child profile. It is never silently assigned to a new account.
- Parent voice remains in D1/R2. A new D1 mapping associates the verified customer with the old ChatGPT owner only when both identities authenticate and the parent confirms. Email equality does not link recordings. Competing or nonempty destination collections are rejected.

The full GitHub repository is public at the owner's requested destination. Its contents include the worksheet bank, so repository access is a separate commercial launch decision from website access control.

## Migrations and operational access

Applied Supabase migrations are checked in under `supabase/migrations/`. Do not reapply them to this project. The customer portal migration was generated with Supabase CLI 2.117.0, applied through the connector and renamed to its actual server migration version.

Activation requires a verified administrator, an active target account, a payment reference, an allowed amount and an idempotency key. Atomic writes preserve audit entries and complete pending requests. Repeated keys cannot double-extend access. Audit rows cannot be edited or deleted. The UI does not collect payment automatically.

The original `/admin` lead management still uses trusted Sites identity and server-only `LITTLEFINGER_OWNER_EMAIL`. New `/account/admin` uses the verified customer administrator. Do not merge their identities by email or publish lead exports.

## Verification and limits

Transactional SQL checks in `supabase/tests/account_isolation.sql` and `yearly_access.sql` cover family isolation, verified/live sessions, pending/expired/suspended denial, role and subscription mutation denial, exact activation/renewal windows, idempotency, audit immutability and revision conflicts. Fixtures roll back.

`scripts/verify-customer-live.cjs` exercises actual BFF handlers with real disposable Supabase Auth/REST accounts. Its host adapters supply Next cookies and SQLite-backed D1; it is not a real emailed-link or deployed-browser acceptance test. It never sends email. Run only with the documented disposable fixture naming and clean up afterward.

The existing catalogue/narration checks cover 3,365 worksheets, 159 categories, 12,942 playable parts including the introduction and 79,269 four-language text checks. Daily-report and parent-voice regression suites remain available. Browser QA checks free completion/reporting, premium gating, account layouts and Arabic direction. No physical-device microphone or pronunciation certification is claimed.

The Security Advisor reports intentional deny-all RLS on the unexposed `private.owner_allowlist`, and warns that leaked-password protection is disabled. Configure this with the Auth settings before launch if supported by the project plan: https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

See `docs/launch/OPERATIONS.md` for the remaining email/provider setup and go-live sequence.
