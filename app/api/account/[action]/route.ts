import {z} from 'zod';
import {AccountError,accountFailure,boundedJson,hasCustomerAccess,rateLimit,requireCustomer,requirePremium,result,rpc,supabaseRequest} from '../../../../lib/customer-auth';
export const dynamic='force-dynamic';
const childSchema=z.object({name:z.string().trim().min(1).max(60),age:z.enum(['2-3','3-4','4-5','5-6']),language:z.enum(['id','en','zh','ar'])});
const uuid=z.string().uuid();

export async function GET(request:Request,context:{params:Promise<{action:string}>}){
  try{
    const session=await requireCustomer();const {action}=await context.params;
    if(action==='workbook'){
      const child=uuid.safeParse(new URL(request.url).searchParams.get('child'));if(!child.success)throw new AccountError(400,'Pilih profil anak.');
      const profiles=await supabaseRequest('/rest/v1/children?select=id&id=eq.'+child.data,{token:session.token});if(!profiles?.length)throw new AccountError(404,'Profil anak tidak ditemukan.');
      const rows=await supabaseRequest('/rest/v1/family_workbooks?select=payload,revision&child_id=eq.'+child.data,{token:session.token});
      return result(rows?.[0]||{payload:null,revision:0});
    }
    if(action==='request')return result(await supabaseRequest('/rest/v1/subscription_requests?select=id,request_type,status,created_at&status=eq.pending',{token:session.token}));
    return result({error:'Tidak ditemukan.'},404);
  }catch(error){return accountFailure(error);}
}
export async function POST(request:Request,context:{params:Promise<{action:string}>}){
  try{
    const {action}=await context.params;const body=await boundedJson(request,action==='workbook'?1200000:10000);
    const session=await requireCustomer();
    if(action==='child'){
      const parsed=childSchema.safeParse(body);if(!parsed.success)throw new AccountError(400,'Periksa nama, usia, dan bahasa anak.');
      await rateLimit(request,'child',20,session.user.id);
      const children=await supabaseRequest('/rest/v1/children?select=id',{token:session.token});if(children.length>=6)throw new AccountError(400,'Maksimal enam profil anak per akun.');
      const rows=await supabaseRequest('/rest/v1/children',{method:'POST',token:session.token,headers:{Prefer:'return=representation'},body:{id:crypto.randomUUID(),parent_user_id:session.user.id,display_name:parsed.data.name,age_band:parsed.data.age,preferred_language:parsed.data.language}});return result(rows[0],201);
    }
    if(action==='workbook'){
      if(!await hasCustomerAccess(session))throw new AccountError(403,'Perpanjang atau aktifkan akses untuk menyimpan aktivitas.');
      const schema=z.object({child:uuid,revision:z.number().int().min(0),payload:z.object({family:z.record(z.unknown()),book:z.object({progress:z.record(z.unknown()),favorites:z.array(z.string().max(140)).max(4000),last:z.string().max(240)}),learning:z.object({version:z.literal(1),events:z.array(z.record(z.unknown())).max(12000),previous:z.array(z.string()).max(20000)}).passthrough()})});
      const parsed=schema.safeParse(body);if(!parsed.success)throw new AccountError(400,'Data aktivitas tidak sesuai.');
      const revision=await rpc('littlefinger_save_workbook',{p_child:parsed.data.child,p_revision:parsed.data.revision,p_payload:parsed.data.payload},session.token);
      return result({ok:true,revision});
    }
    if(action==='request'){
      await rateLimit(request,'subscription-request',6,session.user.id);
      const pending=await supabaseRequest('/rest/v1/subscription_requests?select=id&status=eq.pending',{token:session.token});
      if(pending.length)return result({ok:true,existing:true});
      const subscriptions=await supabaseRequest('/rest/v1/subscriptions?select=access_starts_at&order=created_at.desc&limit=1',{token:session.token});
      await supabaseRequest('/rest/v1/subscription_requests',{method:'POST',token:session.token,body:{user_id:session.user.id,request_type:subscriptions?.[0]?.access_starts_at?'renew':'activate'}});
      return result({ok:true},201);
    }
    if(action==='marketing'){
      if(typeof body.consent!=='boolean')throw new AccountError(400,'Pilihan belum valid.');
      await rpc('littlefinger_marketing_consent',{p_consent:body.consent},session.token);return result({ok:true});
    }
    return result({error:'Tidak ditemukan.'},404);
  }catch(error){return accountFailure(error);}
}
