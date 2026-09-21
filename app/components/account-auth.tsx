'use client';
import {useEffect,useState} from 'react';
import {ArrowRight,Mail,ShieldCheck,Eye,EyeOff} from 'lucide-react';
import {Input} from '@/components/ui/input';
import {Button} from '@/components/ui/button';
import {Checkbox} from '@/components/ui/checkbox';
import {PortalShell,useAccountLanguage} from './account-shell';
import {jsonAction} from '../../lib/customer-client';

type Mode='login'|'register'|'verify'|'recover'|'reset';
export default function AccountAuth({mode}:{mode:Mode}){
  const {lang,setLang,m}=useAccountLanguage();
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[message,setMessage]=useState(''),[show,setShow]=useState(false),[terms,setTerms]=useState(false),[marketing,setMarketing]=useState(false);
  const [emailReady,setEmailReady]=useState(false);
  useEffect(()=>{const query=new URLSearchParams(location.search);if(mode==='verify'&&query.has('error'))setError('Tautan verifikasi tidak dapat digunakan di browser ini. Jika email sudah terverifikasi, pilih Masuk; jika belum, minta email baru.');if(mode==='login'&&query.get('logout')==='partial')setError('Anda sudah keluar dari browser ini, tetapi pencabutan sesi di server belum terkonfirmasi. Masuk lalu keluar lagi saat koneksi tersedia.');if(mode==='login'&&query.get('reset')==='1')setMessage('Password berhasil diperbarui. Silakan masuk kembali.');},[mode]);
  useEffect(()=>{fetch('/api/auth/config',{cache:'no-store'}).then(r=>r.json()).then((data:any)=>setEmailReady(data.emailReady===true)).catch(()=>setEmailReady(false));},[]);
  const emailNeeded=['register','verify','recover'].includes(mode);
  const title={login:m.loginCta,register:m.registerCta,verify:m.verifyEmail,recover:m.resetPassword,reset:m.resetPassword}[mode];
  async function submit(event:React.FormEvent<HTMLFormElement>){
    event.preventDefault();if(busy)return;setError('');setMessage('');const data=Object.fromEntries(new FormData(event.currentTarget));
    if(mode==='register'&&!terms){setError(m.termsRequired);return;}
    if((mode==='register'||mode==='reset')&&data.password!==data.confirmPassword){setError(lang==='id'?'Konfirmasi password belum sama.':'Passwords must match.');return;}
    setBusy(true);
    try{
      const action={login:'login',register:'register',verify:'resend',recover:'recover',reset:'password'}[mode];
      await jsonAction('/api/auth/'+action,{...data,terms,marketing,language:lang});
      if(mode==='login'){location.assign('/account');return;}
      if(mode==='register'){location.assign('/verify-email');return;}
      if(mode==='reset'){location.assign('/login?reset=1');return;}
      setMessage(mode==='recover'?m.resetSent:m.verificationSent);
    }catch(err){setError(err instanceof Error?err.message:m.serviceError);}finally{setBusy(false);}
  }
  return <PortalShell lang={lang} setLang={setLang}><main className="lf-auth-grid"><aside><span className="lf-kicker">LITTLEFINGER ACTIVITIES</span><h1>{mode==='register'?m.heroTitle:m.account}</h1><p>{m.heroBody}</p><img src="/assets/workbook/together.webp" alt=""/><div className="lf-access-promise"><ShieldCheck/><div><strong>{m.accessDuration}</strong><p>{m.activationNote}</p></div></div></aside><section className="lf-account-card"><span className="lf-card-icon"><Mail size={25}/></span><h2>{title}</h2>{mode==='verify'&&<><p>{m.verifyEmailHint}</p><p className="lf-small-note">{lang==='id'?'Buka tautan di browser dan perangkat yang dipakai saat mendaftar. Bila tautan lama tidak bekerja, masuk setelah email terverifikasi atau minta tautan baru.':'Open the link in the same browser and device used to sign up. If an old link fails, log in after verifying your email or request a new link.'}</p></>}
      {emailNeeded&&!emailReady&&<div className="lf-email-pending" role="status"><p>{lang==='id'?'Pendaftaran akun sedang disiapkan. Daftar minat preorder untuk menerima kabar pembukaan.':lang==='zh'?'账号注册正在准备中。您可以先登记预订意向，获取开放通知。':lang==='ar'?'يجري تجهيز تسجيل الحسابات. يمكنك تسجيل اهتمامك بالحجز المسبق لتلقي خبر الإتاحة.':'Account registration is being prepared. Join the preorder list for opening updates.'}</p><a className="lf-secondary" href="/preorder#daftar">{m.preorder}</a></div>}
      <form onSubmit={submit} className="lf-account-form">
        {mode==='register'&&<><label htmlFor="account-name">{m.parentName}</label><Input id="account-name" name="name" autoComplete="name" required minLength={2} maxLength={100}/></>}
        {mode!=='reset'&&<><label htmlFor="account-email">{m.email}</label><Input id="account-email" name="email" type="email" autoComplete="email" required maxLength={254}/></>}
        {['login','register','reset'].includes(mode)&&<><label htmlFor="account-password">{m.password}</label><div className="lf-password-field"><Input id="account-password" name="password" type={show?'text':'password'} autoComplete={mode==='login'?'current-password':'new-password'} required minLength={mode==='login'?1:12} maxLength={128}/><button type="button" onClick={()=>setShow(!show)} aria-label={show?m.hidePassword:m.showPassword}>{show?<EyeOff size={18}/>:<Eye size={18}/>}</button></div>{mode!=='login'&&<><small>{m.passwordHint}</small><label htmlFor="confirm-password">{m.confirmPassword}</label><Input id="confirm-password" name="confirmPassword" type={show?'text':'password'} autoComplete="new-password" required minLength={12} maxLength={128}/></>}</>}
        {mode==='register'&&<><label htmlFor="account-wa">{m.whatsapp}</label><Input id="account-wa" name="whatsapp" type="tel" autoComplete="tel" required maxLength={25} placeholder="0812 3456 7890"/><label htmlFor="child-age">{m.childAge}</label><select id="child-age" name="childAge" defaultValue="2-3"><option value="2-3">2–3</option><option value="3-4">3–4</option><option value="4-5">4–5</option><option value="5-6">5–6</option></select><div className="po-trap" aria-hidden="true"><Input name="website" tabIndex={-1} autoComplete="off"/></div><label className="lf-consent"><Checkbox checked={terms} onCheckedChange={v=>setTerms(v===true)}/><span>{m.termsConsent} <a href="/terms" target="_blank" rel="noopener">{m.terms}</a> · <a href="/privacy" target="_blank" rel="noopener">{m.privacy}</a></span></label><label className="lf-consent"><Checkbox checked={marketing} onCheckedChange={v=>setMarketing(v===true)}/><span>{m.marketingConsent}</span></label></>}
        {error&&<p className="lf-error" role="alert">{error}</p>}{message&&<p className="lf-account-success" role="status">{message}</p>}
        <Button className="lf-primary" type="submit" disabled={busy||(emailNeeded&&!emailReady)}>{busy?m.loading:mode==='login'?m.login:mode==='register'?m.register:mode==='verify'?m.resendVerification:mode==='recover'?m.sendResetLink:m.savePassword}<ArrowRight size={18}/></Button>
      </form><div className="lf-account-links">{mode!=='login'&&<a href="/login">{m.login}</a>}{mode==='login'&&<><a href="/forgot-password">{m.forgotPassword}</a><a href="/register">{m.register}</a></>}<a href="/#activity/telur-dan-hewan">{m.previewCta}</a></div></section></main></PortalShell>;
}
