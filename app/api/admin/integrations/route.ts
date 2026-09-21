import {isOwner} from '../../../../lib/owner';
import {checkSupabaseConnection} from '../../../../lib/supabase/connection';
export const dynamic = 'force-dynamic';
export async function GET() {
  const headers = {'Cache-Control': 'private, no-store', 'Vary': 'Cookie', 'X-Content-Type-Options': 'nosniff'};
  if (!await isOwner()) return Response.json({error: 'Akses khusus pemilik.'}, {status: 403, headers});
  const status = await checkSupabaseConnection();
  return Response.json(status, {status: status.connected ? 200 : 503, headers});
}
