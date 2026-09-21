import {z} from 'zod';
import {AccountError,accountFailure,boundedJson,rateLimit,requireCustomer,result,rpc} from '../../../../lib/customer-auth';
export const dynamic='force-dynamic';
export async function GET(request:Request,context:{params:Promise<{action:string}>}){
  try{const session=await requireCustomer();if((await context.params).action!=='customers')return result({error:'Tidak ditemukan.'},404);return result(await rpc('littlefinger_admin_customers',{p_query:(new URL(request.url).searchParams.get('q')||'').slice(0,100)},session.token));}catch(error){return accountFailure(error);}
}
export async function POST(request:Request,context:{params:Promise<{action:string}>}){
  try{
    const body=await boundedJson(request);const session=await requireCustomer();await rateLimit(request,'admin',50,session.user.id);const {action}=await context.params;
    if(action==='subscription'){
      const parsed=z.object({user:z.string().uuid(),action:z.enum(['activate','renew']),reference:z.string().trim().min(3).max(200),amount:z.union([z.literal(39000),z.literal(55000)]),key:z.string().uuid(),confirmed:z.literal(true)}).safeParse(body);
      if(!parsed.success)throw new AccountError(400,'Isi referensi pembayaran dan konfirmasi sebelum mengaktifkan akses.');
      const p=parsed.data;return result(await rpc('littlefinger_admin_subscription',{p_user:p.user,p_action:p.action,p_reference:p.reference,p_amount:p.amount,p_key:p.key},session.token));
    }
    if(action==='status'){
      const parsed=z.object({user:z.string().uuid(),status:z.enum(['active','suspended','blocked']),key:z.string().uuid(),confirmed:z.literal(true)}).safeParse(body);if(!parsed.success)throw new AccountError(400,'Konfirmasi perubahan status akun.');
      await rpc('littlefinger_admin_account_status',{p_user:parsed.data.user,p_status:parsed.data.status,p_key:parsed.data.key},session.token);return result({ok:true});
    }
    return result({error:'Tidak ditemukan.'},404);
  }catch(error){return accountFailure(error);}
}
