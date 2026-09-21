import 'server-only';
import {env} from 'cloudflare:workers';

export type SupabaseConfiguration = {url: string; publishableKey: string};

/** Server-only configuration. Never import into a client component. */
export function supabaseConfiguration(): SupabaseConfiguration | null {
  const values = env as unknown as Record<string, string | undefined>;
  const url = values.SUPABASE_URL?.replace(/\/$/, '');
  const publishableKey = values.SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey?.startsWith('sb_publishable_')) return null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' || parsed.hostname !== 'eamewoihspijkbsmegod.supabase.co' || parsed.pathname !== '/' || parsed.search || parsed.hash || parsed.username || parsed.password) return null;
    return {url, publishableKey};
  } catch { return null; }
}

/** Verify Auth and the exact database migration without reading family records. */
export async function checkSupabaseConnection() {
  const config = supabaseConfiguration();
  if (!config) return {configured: false, connected: false, authReachable: false, schemaVersion: null};
  try {
    const headers = {apikey: config.publishableKey, 'Content-Type': 'application/json'};
    const results = await Promise.all([
      fetch(config.url + '/auth/v1/settings', {headers, cache: 'no-store', signal: AbortSignal.timeout(20000)}),
      fetch(config.url + '/rest/v1/rpc/littlefinger_schema_version', {method: 'POST', headers, body: '{}', cache: 'no-store', signal: AbortSignal.timeout(20000)}),
    ]);
    const authReachable = results[0].ok;
    const version: unknown = results[1].ok ? await results[1].json() : null;
    return {configured: true, connected: authReachable && version === 1, authReachable, schemaVersion: version === 1 ? 1 : null};
  } catch { return {configured: true, connected: false, authReachable: false, schemaVersion: null}; }
}
