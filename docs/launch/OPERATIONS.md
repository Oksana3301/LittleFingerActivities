# Littlefinger launch operations

## Pending owner setup

The Supabase dashboard currently requires owner login. Use its secure login flow; never put dashboard passwords, SMTP passwords or recovery codes in chat or source files.

1. In Auth URL configuration, set the Site URL to `https://little-world-playroom.atikadewi.chatgpt.site` and allow the exact callback `https://little-world-playroom.atikadewi.chatgpt.site/auth/finish`. Keep email confirmation required.
2. Configure a transactional SMTP sender whose address/domain the owner controls. Verify sender DNS and provider delivery. The provider's credentials must remain in Supabase configuration.
3. Review Auth password/rate-limit settings, including leaked-password protection where the project plan supports it. The BFF enforces 12-character new passwords and shared rate limits. A CAPTCHA integration is still a separate unfinished launch task; do not enable a provider requirement until the client passes its token.
4. Test signup and reset through a controlled staging path with two real test inboxes before opening public registration. Confirm receipt, spam behavior, confirmation, expiry, resend, password reset, session revocation and error messages. The default flag keeps these paths closed until email setup is ready. If temporarily enabling the flag for final production acceptance, close it immediately if delivery fails.
5. Only after successful delivery and callback checks, configure the Site secret `CUSTOMER_EMAIL_READY=true` and republish. Missing/false keeps the preorder interest list open while account email actions remain disabled.

## Owner access and payment review

The existing verified owner address is provisioned in `private.owner_allowlist` outside committed source. Register and verify that address through the same customer journey; its first account initialization grants the owner role. User-supplied metadata cannot grant that role. If the address changes, update the private allowlist through a privileged database operation after verifying authorization.

Open `/account/admin`, find the customer, check their payment independently, then confirm the payment reference and amount. Activation grants exactly 365 days from activation. An early renewal preserves remaining time; a late renewal begins immediately. Retrying the same confirmed action reuses its key. Do not manually edit access dates to work around an error.

Subscription requests are stored in Supabase and visible in the owner list. They do not charge a card or send an email/WhatsApp message. Automatic payment collection, renewal reminders, marketing email campaigns, scheduled monitoring and a tested backup/restore drill remain future work.

Account suspension/blocking and immutable auditing exist in the protected database operations; the current customer list focuses on activation and renewal. A complete audit viewer and customer-support status UI remain future work.

## Test and recovery commands

Use the configured Sites runtime and supervised preview. Typical checks:

```sh
npx tsc --noEmit
node scripts/validate-workbook.mjs
node scripts/validate-narration.cjs
node scripts/verify-daily-report.cjs
node scripts/verify-parent-voice.cjs
node scripts/verify-auth-flows.cjs
```

Run the two `supabase/tests/*.sql` scripts against the intended project as privileged transaction-only tests; they end with rollback. The live BFF script needs two explicitly disposable confirmed Auth users named `lf-qa-<hex>@example.invalid` and an external JSON fixture file, never committed. It runs phases `pending`, `active`, then `expired`; privileged fixture changes between phases must target only those exact IDs. Its optional `LF_TEST_HTTP=python` transport uses real HTTPS through the managed runtime proxy. Delete the test Auth users and temporary credential/state files afterward.

`verify-auth-flows.cjs` checks signup, verified/unverified login, callback routing and client failures with controlled Auth responses. It sends no email and does not establish SMTP readiness. The account UI distinguishes configuration loading/failure from a closed registration service, lets visitors retry the status check, preserves only the entered email in tab session storage for verification, and directs unverified logins to verification. A failed recovery callback returns to password recovery. Credentials are never stored in browser storage.

If cloud saving fails or another device has advanced the revision, export the current family workbook from parent settings before reloading. Do not blindly retry a stale revision or replace a nonempty child's history. Device imports require the parent to confirm the child and begin only at revision zero.

For a rollback, redeploy a known saved Site version. Database migrations are append-only; do not delete live family data. Older versions expose their former content model, so review that consequence before reverting a commercial launch.

## Public source decision

The requested GitHub repository is currently public and includes full worksheets and artwork. Server entitlement checks protect the running website, not the public GitHub copy. Repository visibility must be chosen by the owner before relying on source confidentiality.
