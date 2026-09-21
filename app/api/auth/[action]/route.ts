import {z} from 'zod';
import {AccountError,accountFailure,authCookie,boundedJson,clearSession,createProof,customerEmailReady,customerOverview,customerSession,initializeCustomer,rateLimit,result,rpc,setSession,supabaseRequest,verifierCookie,type AuthTokens,type Customer} from '../../../../lib/customer-auth';
import {normalizeWhatsApp} from '../../../../lib/preorder';

export const dynamic='force-dynamic';
const email=z.string().trim().toLowerCase().email().max(254);
const password=z.string().min(12,'Gunakan password minimal 12 karakter.').max(128);
const registration=z.object({email,password,confirmPassword:z.string(),name:z.string().trim().min(2).max(100),whatsapp:z.string().max(25).transform(normalizeWhatsApp).refine(v=>/^[1-9]\d{7,14}$/.test(v)).transform(v=>'+'+v),language:z.enum(['id','en','zh','ar']),childAge:z.enum(['2-3','3-4','4-5','5-6']),terms:z.literal(true),marketing:z.boolean(),website:z.string().max(0).optional()}).refine(v=>v.password===v.confirmPassword,{message:'Konfirmasi password belum sama.'});
const redirect='https://little-world-playroom.atikadewi.chatgpt.site/auth/finish';

async function validatedTokens(tokens:AuthTokens):Promise<Customer>{
  const user=await supabaseRequest('/auth/v1/user',{token:tokens.access_token});
  if(!user?.email_confirmed_at||user.is_anonymous||!await rpc('littlefinger_session_ok',{},tokens.access_token))throw new AccountError(403,'Verifikasi email sebelum masuk.','email_not_confirmed');
  return {token:tokens.access_token,user};
}

export async function GET(_request:Request,context:{params:Promise<{action:string}>}){
  try{
    const {action}=await context.params;
    if(action==='config')return result({emailReady:customerEmailReady()});
    if(action!=='session')return result({error:'Tidak ditemukan.'},404);
    const session=await customerSession();
    if(!session)return result({user:null,profile:null,account:null,subscription:null,children:[],access:false,refreshable:!!await authCookie('lf-refresh')});
    return result(await customerOverview(session));
  }catch(error){return accountFailure(error);}
}

export async function POST(request:Request,context:{params:Promise<{action:string}>}){
  try{
    const {action}=await context.params;
    const body=await boundedJson(request);
    if(['register','recover','resend'].includes(action)&&!customerEmailReady())throw new AccountError(503,'Pendaftaran dan email akun sedang disiapkan. Daftar minat preorder untuk menerima kabar pembukaan.','email_setup_pending');
    if(action==='login'){
      const parsed=z.object({email,password:z.string().min(1).max(128)}).safeParse(body);
      if(!parsed.success)throw new AccountError(400,'Isi email dan password yang valid.');
      await rateLimit(request,'login',12,parsed.data.email);
      let tokens:AuthTokens;
      try{tokens=await supabaseRequest('/auth/v1/token?grant_type=password',{method:'POST',body:parsed.data});}
      catch(error){if(error instanceof AccountError&&error.code==='invalid_credentials')throw new AccountError(400,'Email atau password belum sesuai. Gunakan Lupa Password bila diperlukan.','invalid_credentials');throw error;}
      const session=await validatedTokens(tokens);await initializeCustomer(session);
      const response=result({ok:true});setSession(response,request,tokens);return response;
    }
    if(action==='register'){
      const parsed=registration.safeParse(body);
      if(!parsed.success)throw new AccountError(400,parsed.error.issues[0]?.message||'Periksa data pendaftaran.');
      const values=parsed.data;await rateLimit(request,'signup',5,values.email);
      const proof=await createProof();
      await supabaseRequest('/auth/v1/signup?redirect_to='+encodeURIComponent(redirect),{method:'POST',body:{email:values.email,password:values.password,code_challenge:proof.challenge,code_challenge_method:'s256',data:{full_name:values.name,whatsapp:values.whatsapp,language:values.language,child_age:values.childAge,marketing_consent:values.marketing,privacy_consent_at:new Date().toISOString(),consent_version:'littlefinger-2026-09'}}});
      const response=result({ok:true,message:'Jika pendaftaran dapat diproses, email verifikasi akan dikirim. Periksa juga folder spam.'},202);
      verifierCookie(response,request,'signup:'+proof.verifier);return response;
    }
    if(action==='recover'||action==='resend'){
      const parsed=email.safeParse(body.email);if(!parsed.success)throw new AccountError(400,'Isi alamat email yang valid.');
      await rateLimit(request,action,4,parsed.data);
      const proof=await createProof();
      const payload=action==='recover'?{email:parsed.data,code_challenge:proof.challenge,code_challenge_method:'s256'}:{email:parsed.data,type:'signup'};
      await supabaseRequest('/auth/v1/'+(action==='recover'?'recover':'resend')+'?redirect_to='+encodeURIComponent(redirect),{method:'POST',body:payload});
      const response=result({ok:true,message:'Jika permintaan dapat diproses, petunjuk akan dikirim ke email Anda.'},202);
      if(action==='recover')verifierCookie(response,request,'recovery:'+proof.verifier);
      return response;
    }
    if(action==='refresh'){
      const refresh=await authCookie('lf-refresh');if(!refresh)throw new AccountError(401,'Silakan masuk kembali.');
      await rateLimit(request,'refresh',80);
      const tokens=await supabaseRequest('/auth/v1/token?grant_type=refresh_token',{method:'POST',body:{refresh_token:refresh}}) as AuthTokens;
      await validatedTokens(tokens);const response=result({ok:true});setSession(response,request,tokens);return response;
    }
    if(action==='logout'){
      const token=await authCookie('lf-access');
      let revoked=true;
      if(token)try{await supabaseRequest('/auth/v1/logout?scope=global',{method:'POST',token});}catch(error){revoked=error instanceof AccountError&&error.status===401;}
      const response=result({ok:true,revoked});clearSession(response,request);return response;
    }
    if(action==='password'){
      const session=await customerSession();if(!session)throw new AccountError(401,'Buka tautan reset terbaru dari email Anda.');
      const parsed=z.object({password,confirmPassword:z.string()}).refine(v=>v.password===v.confirmPassword).safeParse(body);
      if(!parsed.success)throw new AccountError(400,'Gunakan minimal 12 karakter dan konfirmasi password yang sama.');
      await rateLimit(request,'password',5,session.user.id);
      await supabaseRequest('/auth/v1/user',{method:'PUT',token:session.token,body:{password:parsed.data.password}});
      await supabaseRequest('/auth/v1/logout?scope=global',{method:'POST',token:session.token});
      const response=result({ok:true});clearSession(response,request);return response;
    }
    return result({error:'Tidak ditemukan.'},404);
  }catch(error){
    const response=accountFailure(error);
    if((await context.params).action==='refresh'&&error instanceof AccountError&&[400,401,403].includes(error.status))clearSession(response,request);
    return response;
  }
}
