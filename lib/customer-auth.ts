import 'server-only';
import {cookies} from 'next/headers';
import {env} from 'cloudflare:workers';
import {supabaseConfiguration} from './supabase/connection';

export const privateHeaders = {'Cache-Control':'private, no-store', 'Vary':'Cookie', 'X-Content-Type-Options':'nosniff', 'Referrer-Policy':'no-referrer'};
export class AccountError extends Error {
  constructor(public status:number, message:string, public code='account_error') {super(message);}
}
export type CustomerUser={id:string;email?:string;email_confirmed_at?:string;is_anonymous?:boolean;user_metadata?:Record<string,unknown>};
export type Customer={token:string;user:CustomerUser};
export type AuthTokens={access_token:string;refresh_token:string;expires_in:number;user?:CustomerUser};
export const customerEmailReady=()=> (env as unknown as Record<string,string>).CUSTOMER_EMAIL_READY==='true';
export const authCookie=async(name:string)=>(await cookies()).get(import.meta.env.DEV?name:'__Host-'+name)?.value;

export async function supabaseRequest(path:string, options:{method?:string;body?:unknown;token?:string;headers?:Record<string,string>}={}) {
  const config=supabaseConfiguration();
  if(!config)throw new AccountError(503,'Layanan akun belum tersedia. Silakan coba lagi nanti.','not_configured');
  let response:Response;
  try {response=await fetch(config.url+path,{method:options.method||'GET',headers:{apikey:config.publishableKey,'Content-Type':'application/json',...(options.token?{Authorization:'Bearer '+options.token}:{}),...options.headers},body:options.body===undefined?undefined:JSON.stringify(options.body),cache:'no-store',signal:AbortSignal.timeout(15000)});}
  catch {throw new AccountError(503,'Koneksi akun belum tersedia. Perubahan belum disimpan.','unavailable');}
  const text=await response.text();
  let data:any=null;try{data=text?JSON.parse(text):null;}catch{}
  if(!response.ok){
    const code=String(data?.error_code||data?.code||'upstream_error');
    if(response.status===429)throw new AccountError(429,'Terlalu banyak percobaan. Tunggu beberapa menit lalu coba lagi.','rate_limited');
    if(code==='email_not_confirmed')throw new AccountError(403,'Verifikasi email terlebih dahulu melalui tautan yang dikirim.','email_not_confirmed');
    if(code==='email_address_not_authorized'||code==='unexpected_failure')throw new AccountError(503,'Email verifikasi belum dapat dikirim. Pendaftaran belum selesai. Silakan coba lagi nanti.','email_delivery_unavailable');
    if(response.status===401||code==='bad_jwt'||code==='refresh_token_not_found')throw new AccountError(401,'Silakan masuk kembali.','session_expired');
    if(response.status===403||code==='42501')throw new AccountError(403,'Akun ini tidak memiliki akses untuk tindakan tersebut.','forbidden');
    if(code==='P0001'||code==='23505')throw new AccountError(409,'Data telah berubah atau tindakan ini sudah diproses. Muat ulang sebelum mencoba lagi.','conflict');
    throw new AccountError(response.status>=500?503:400,'Permintaan belum dapat diproses. Periksa isian atau coba lagi nanti.',code);
  }
  return data;
}

export async function rpc(name:string, body:unknown, token:string) {
  return supabaseRequest('/rest/v1/rpc/'+name,{method:'POST',body,token});
}

export async function customerSession():Promise<Customer|null> {
  const token=await authCookie('lf-access');
  if(!token)return null;
  try {
    const user=await supabaseRequest('/auth/v1/user',{token}) as CustomerUser;
    if(!user.id||!user.email_confirmed_at||user.is_anonymous)return null;
    if(!await rpc('littlefinger_session_ok',{},token))return null;
    return {token,user};
  } catch(error) {if(error instanceof AccountError&&[401,403].includes(error.status))return null;throw error;}
}

export async function requireCustomer() {
  const session=await customerSession();
  if(!session)throw new AccountError(401,'Masuk dengan akun yang sudah terverifikasi.','login_required');
  return session;
}

export async function hasCustomerAccess(session:Customer) {return await rpc('littlefinger_has_access',{},session.token)===true;}

export async function requirePremium() {
  const session=await requireCustomer();
  if(!await hasCustomerAccess(session))throw new AccountError(403,'Aktivitas ini tersedia setelah akses tahunan diaktifkan.','subscription_required');
  return session;
}

export function result(data:unknown,status=200) {return Response.json(data,{status,headers:privateHeaders});}
export function accountFailure(error:unknown) {
  return error instanceof AccountError?result({error:error.message,code:error.code},error.status):result({error:'Permintaan belum berhasil. Silakan coba lagi.',code:'unavailable'},503);
}

export async function boundedJson(request:Request,maxBytes=10000):Promise<any> {
  if(request.headers.get('origin')!==new URL(request.url).origin)throw new AccountError(403,'Buka formulir dari website Littlefinger.','origin_required');
  if(!request.headers.get('content-type')?.startsWith('application/json'))throw new AccountError(415,'Format permintaan tidak sesuai.');
  if(Number(request.headers.get('content-length')||0)>maxBytes)throw new AccountError(413,'Data terlalu panjang.');
  const reader=request.body?.getReader();if(!reader)throw new AccountError(400,'Isian belum lengkap.');
  const chunks:Uint8Array[]=[];let length=0;
  for(;;){const item=await reader.read();if(item.done)break;length+=item.value.byteLength;if(length>maxBytes){await reader.cancel();throw new AccountError(413,'Data terlalu panjang.');}chunks.push(item.value);}
  const all=new Uint8Array(length);let offset=0;for(const chunk of chunks){all.set(chunk,offset);offset+=chunk.length;}
  try{return JSON.parse(new TextDecoder().decode(all));}catch{throw new AccountError(400,'Periksa isian formulir.');}
}

export async function rateLimit(request:Request,action:string,limit:number,subject='') {
  const db=(env as unknown as {DB:D1Database}).DB;
  const now=Date.now(),window=Math.floor(now/900000);
  const identifiers=[request.headers.get('cf-connecting-ip')||'preview',...(subject?[subject.toLowerCase()]:[])];
  for(const identifier of identifiers){
    const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(action+':'+window+':'+identifier));
    const key='auth:'+Array.from(new Uint8Array(bytes),v=>v.toString(16).padStart(2,'0')).join('');
    const row=await db.prepare('INSERT INTO submission_limits (key,count,expires) VALUES (?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1 RETURNING count').bind(key,now+900000).first<{count:number}>();
    if(!row||row.count>limit)throw new AccountError(429,'Terlalu banyak percobaan. Coba lagi dalam 15 menit.','rate_limited');
  }
  await db.prepare('DELETE FROM submission_limits WHERE expires < ?').bind(now).run();
}

function cookie(response:Response,request:Request,name:string,value:string,maxAge:number){
  const production=!import.meta.env.DEV;
  response.headers.append('Set-Cookie',`${production?'__Host-':''}${name}=${encodeURIComponent(value)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${production||new URL(request.url).protocol==='https:'?'; Secure':''}`);
}
export function setSession(response:Response,request:Request,tokens:AuthTokens){
  cookie(response,request,'lf-access',tokens.access_token,Math.max(1,Math.min(tokens.expires_in||3600,3600)));
  cookie(response,request,'lf-refresh',tokens.refresh_token,60*60*24*30);
}
export function clearSession(response:Response,request:Request){for(const name of ['lf-access','lf-refresh','lf-verifier'])cookie(response,request,name,'',0);}
export function verifierCookie(response:Response,request:Request,value:string){cookie(response,request,'lf-verifier',value,value?3600:0);}
export async function createProof(){
  const bytes=crypto.getRandomValues(new Uint8Array(48));
  const verifier=Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
  const digest=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(verifier)));
  const challenge=btoa(String.fromCharCode(...digest)).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');
  return {verifier,challenge};
}

export async function initializeCustomer(session:Customer){
  const meta=session.user.user_metadata||{};
  await rpc('littlefinger_initialize_account',{p_name:typeof meta.full_name==='string'?meta.full_name.slice(0,100):'Orang tua',p_whatsapp:typeof meta.whatsapp==='string'?meta.whatsapp:null,p_language:['id','en','zh','ar'].includes(String(meta.language))?meta.language:'id',p_marketing:meta.marketing_consent===true,p_age:['2-3','3-4','4-5','5-6'].includes(String(meta.child_age))?meta.child_age:'2-3'},session.token);
}

export async function customerOverview(session:Customer){
  const [profile,account,subscriptions,children,access]=await Promise.all([
    supabaseRequest('/rest/v1/profiles?select=*&id=eq.'+session.user.id,{token:session.token}),
    supabaseRequest('/rest/v1/account_access?select=account_status,admin_role&user_id=eq.'+session.user.id,{token:session.token}),
    supabaseRequest('/rest/v1/subscriptions?select=id,status,access_starts_at,access_expires_at,price_paid&user_id=eq.'+session.user.id+'&order=created_at.desc&limit=1',{token:session.token}),
    supabaseRequest('/rest/v1/children?select=id,display_name,age_band,preferred_language&parent_user_id=eq.'+session.user.id+'&order=created_at',{token:session.token}),
    hasCustomerAccess(session)
  ]);
  return {user:{id:session.user.id,email:session.user.email},profile:profile?.[0]||null,account:account?.[0]||null,subscription:subscriptions?.[0]||null,children:children||[],access};
}
