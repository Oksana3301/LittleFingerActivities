import {authCookie,initializeCustomer,privateHeaders,rpc,setSession,supabaseRequest,verifierCookie,type AuthTokens} from '../../../lib/customer-auth';
export const dynamic='force-dynamic';
export async function GET(request:Request){
  const target=new URL('/verify-email?error=expired',request.url);
  try{
    const code=new URL(request.url).searchParams.get('code');
    const proof=await authCookie('lf-verifier');
    if(!code||code.length>2048||!proof||!/^\w+:[a-f0-9]{96}$/.test(proof))throw new Error('missing_proof');
    const [flow,verifier]=proof.split(':');
    const tokens=await supabaseRequest('/auth/v1/token?grant_type=pkce',{method:'POST',body:{auth_code:code,code_verifier:verifier}}) as AuthTokens;
    const user=await supabaseRequest('/auth/v1/user',{token:tokens.access_token});
    if(!user.email_confirmed_at||user.is_anonymous||!await rpc('littlefinger_session_ok',{},tokens.access_token))throw new Error('unverified');
    await initializeCustomer({token:tokens.access_token,user});
    const response=new Response(null,{status:303,headers:{...privateHeaders,Location:new URL(flow==='recovery'?'/reset-password':'/account?verified=1',request.url).toString()}});
    setSession(response,request,tokens);verifierCookie(response,request,'');return response;
  }catch{
    return new Response(null,{status:303,headers:{...privateHeaders,Location:target.toString()}});
  }
}
