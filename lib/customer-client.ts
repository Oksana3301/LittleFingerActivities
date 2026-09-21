'use client';
export type ChildProfile={id:string;display_name:string;age_band:string;preferred_language:string};
export type AccountOverview={user:{id:string;email:string}|null;profile:{full_name:string;preferred_language:string}|null;account:{account_status:string;admin_role:boolean}|null;subscription:{id:string;status:string;access_starts_at:string|null;access_expires_at:string|null;price_paid:number}|null;children:ChildProfile[];access:boolean};
export const signedOut:AccountOverview={user:null,profile:null,account:null,subscription:null,children:[],access:false};
export class AccountActionError extends Error {
  constructor(message:string,public code='account_error',public status=0){super(message);this.name='AccountActionError';}
}
export async function loadAccount():Promise<AccountOverview>{
  let response=await fetch('/api/auth/session',{cache:'no-store'});
  if(!response.ok)throw new Error('Akun belum dapat dimuat. Coba lagi.');
  let data:any=await response.json();
  if(data.refreshable){
    const refreshed=await fetch('/api/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    if(refreshed.ok){response=await fetch('/api/auth/session',{cache:'no-store'});if(!response.ok)throw new Error('Akun belum dapat dimuat.');data=await response.json();}
  }
  return data;
}
let refreshing:Promise<Response>|null=null;
export async function accountFetch(path:string,options:RequestInit={}){
  const send=()=>fetch(path,{...options,credentials:'same-origin',cache:'no-store'});
  let response=await send();
  if(response.status===401&&!path.startsWith('/api/auth/')){
    if(!refreshing)refreshing=fetch('/api/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}',credentials:'same-origin'}).finally(()=>{refreshing=null;});
    if((await refreshing).ok)response=await send();
  }
  return response;
}
export async function jsonAction(path:string,body:unknown,method='POST'){
  let response:Response;
  try{response=await accountFetch(path,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(25000)});}
  catch{throw new AccountActionError('Koneksi terputus. Periksa internet, lalu coba lagi.','unavailable');}
  let data:any;
  try{data=await response.json();}catch{throw new AccountActionError('Layanan akun belum merespons. Silakan coba lagi.','unavailable',response.status);}
  if(!response.ok)throw new AccountActionError(data.error||'Permintaan belum berhasil.',data.code||'account_error',response.status);
  return data;
}
