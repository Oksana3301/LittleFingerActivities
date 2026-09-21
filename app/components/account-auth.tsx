'use client';
import {useCallback,useEffect,useState} from 'react';
import {ArrowRight,Mail,ShieldCheck,Eye,EyeOff} from 'lucide-react';
import {Input} from '@/components/ui/input';
import {Button} from '@/components/ui/button';
import {Checkbox} from '@/components/ui/checkbox';
import {PortalShell,useAccountLanguage} from './account-shell';
import {AccountActionError,jsonAction} from '../../lib/customer-client';
import {authCopy} from '../../docs/launch/auth-i18n';

type Mode='login'|'register'|'verify'|'recover'|'reset';
export default function AccountAuth({mode}:{mode:Mode}){
  const {lang,setLang,m}=useAccountLanguage();
  const copy=authCopy[lang];
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[message,setMessage]=useState(''),[show,setShow]=useState(false),[terms,setTerms]=useState(false),[marketing,setMarketing]=useState(false);
  const [email,setEmail]=useState(''),[errorCode,setErrorCode]=useState(''),[notice,setNotice]=useState(''),[cooldown,setCooldown]=useState(0);
  const [emailStatus,setEmailStatus]=useState<'checking'|'ready'|'pending'|'unavailable'>('checking');
  useEffect(()=>{
    const query=new URLSearchParams(location.search);
    if((mode==='verify'||mode==='recover')&&query.has('error'))setNotice('expired');
    else if(mode==='verify'&&query.get('sent')==='1')setNotice('sent');
    else if(mode==='verify'&&query.get('required')==='1')setNotice('required');
    else if(mode==='login'&&query.get('logout')==='partial')setNotice('partial');
    else if(mode==='login'&&query.get('reset')==='1')setNotice('reset');
    try{setEmail(sessionStorage.getItem('lf-auth-email')||'');}catch{}
  },[mode]);
  const emailNeeded=['register','verify','recover'].includes(mode);
  const checkEmail=useCallback(async()=>{
    setEmailStatus('checking');
    try{
      const response=await fetch('/api/auth/config',{cache:'no-store',signal:AbortSignal.timeout(10000)});
      if(!response.ok)throw new Error('config_unavailable');
      const data:unknown=await response.json();
      if(!data||typeof data!=='object'||!('emailReady' in data)||typeof data.emailReady!=='boolean')throw new Error('invalid_config');
      setEmailStatus(data.emailReady?'ready':'pending');
    }catch{setEmailStatus('unavailable');}
  },[]);
  useEffect(()=>{if(emailNeeded)void checkEmail();},[checkEmail,emailNeeded]);
  useEffect(()=>{if(cooldown<=0)return;const timer=setTimeout(()=>setCooldown(value=>value-1),1000);return()=>clearTimeout(timer);},[cooldown]);
  const emailReady=emailStatus==='ready';
  const pendingCopy=mode==='recover'?copy.recoverPending:mode==='verify'?copy.verifyPending:copy.registerPending;
  function rememberEmail(){try{sessionStorage.setItem('lf-auth-email',email.trim().toLowerCase());}catch{}}
  const title={login:m.loginCta,register:m.registerCta,verify:m.verifyEmail,recover:m.resetPassword,reset:m.resetPassword}[mode];
  async function submit(event:React.FormEvent<HTMLFormElement>){
    event.preventDefault();if(busy||cooldown>0||(emailNeeded&&!emailReady))return;setError('');setErrorCode('');setMessage('');setNotice('');const data=Object.fromEntries(new FormData(event.currentTarget));
    if(mode==='register'&&!terms){setError(m.termsRequired);return;}
    if((mode==='register'||mode==='reset')&&data.password!==data.confirmPassword){setError(copy.passwordMismatch);return;}
    setBusy(true);
    try{
      const action={login:'login',register:'register',verify:'resend',recover:'recover',reset:'password'}[mode];
      await jsonAction('/api/auth/'+action,{...data,terms,marketing,language:lang});
      if(mode==='login'){try{sessionStorage.removeItem('lf-auth-email');}catch{}location.assign('/account');return;}
      if(mode!=='reset')rememberEmail();
      if(mode==='register'){location.assign('/verify-email?sent=1');return;}
      if(mode==='reset'){location.assign('/login?reset=1');return;}
      setMessage(mode==='recover'?m.resetSent:m.verificationSent);
      setCooldown(60);
    }catch(err){
      if(err instanceof AccountActionError){
        setErrorCode(err.code);
        if(err.code==='email_not_confirmed'){rememberEmail();setError(copy.verificationRequired);}
        else if(err.code==='invalid_credentials')setError(m.loginError);
        else if(err.code==='email_setup_pending'){setEmailStatus('pending');setError(pendingCopy);}
        else setError(err.code==='unavailable'?m.serviceError:err.message);
      }else setError(m.serviceError);
    }finally{setBusy(false);}
  }
  return <PortalShell lang={lang} setLang={setLang}><main className="lf-auth-grid"><aside><span className="lf-kicker">LITTLEFINGER ACTIVITIES</span><h1>{mode==='register'?m.heroTitle:m.account}</h1><p>{m.heroBody}</p><img src="/assets/workbook/together.webp" alt=""/><div className="lf-access-promise"><ShieldCheck/><div><strong>{m.accessDuration}</strong><p>{m.activationNote}</p></div></div></aside><section className="lf-account-card"><span className="lf-card-icon"><Mail size={25}/></span><h2>{title}</h2>{mode==='verify'&&<><p>{m.verifyEmailHint}</p><p className="lf-small-note">{copy.sameBrowser}</p></>}
      {notice&&<p className={['expired','partial','required'].includes(notice)?'lf-error':'lf-account-success'} role={['expired','partial','required'].includes(notice)?'alert':'status'}>{notice==='expired'?(mode==='recover'?copy.resetExpired:copy.verifyExpired):notice==='partial'?copy.partialLogout:notice==='required'?copy.verificationRequired:notice==='sent'?copy.signupSent:m.passwordUpdated}</p>}
      {emailNeeded&&!emailReady&&<div className="lf-email-pending" role="status"><p>{emailStatus==='checking'?copy.checking:emailStatus==='unavailable'?copy.unavailable:pendingCopy}</p>{emailStatus!=='checking'&&<div className="lf-auth-actions"><Button type="button" variant="outline" onClick={()=>void checkEmail()}>{copy.retry}</Button>{mode==='register'&&emailStatus==='pending'&&<a className="lf-secondary" href="/preorder#daftar">{m.preorder}</a>}</div>}</div>}
      <form onSubmit={submit} className="lf-account-form">
        {mode==='register'&&<><label htmlFor="account-name">{m.parentName}</label><Input id="account-name" name="name" autoComplete="name" required minLength={2} maxLength={100}/></>}
        {mode!=='reset'&&<><label htmlFor="account-email">{m.email}</label><Input id="account-email" name="email" type="email" autoComplete="email" autoCapitalize="none" spellCheck={false} value={email} onChange={event=>setEmail(event.target.value)} required maxLength={254}/></>}
        {['login','register','reset'].includes(mode)&&<><label htmlFor="account-password">{m.password}</label><div className="lf-password-field"><Input id="account-password" name="password" type={show?'text':'password'} autoComplete={mode==='login'?'current-password':'new-password'} required minLength={mode==='login'?1:12} maxLength={128}/><button type="button" onClick={()=>setShow(!show)} aria-label={show?m.hidePassword:m.showPassword}>{show?<EyeOff size={18}/>:<Eye size={18}/>}</button></div>{mode!=='login'&&<><small>{m.passwordHint}</small><label htmlFor="confirm-password">{m.confirmPassword}</label><Input id="confirm-password" name="confirmPassword" type={show?'text':'password'} autoComplete="new-password" required minLength={12} maxLength={128}/></>}</>}
        {mode==='register'&&<><label htmlFor="account-wa">{m.whatsapp}</label><Input id="account-wa" name="whatsapp" type="tel" autoComplete="tel" required maxLength={25} placeholder="0812 3456 7890"/><label htmlFor="child-age">{m.childAge}</label><select id="child-age" name="childAge" defaultValue="2-3"><option value="2-3">2–3</option><option value="3-4">3–4</option><option value="4-5">4–5</option><option value="5-6">5–6</option></select><div className="po-trap" aria-hidden="true"><Input name="website" tabIndex={-1} autoComplete="off"/></div><label className="lf-consent"><Checkbox checked={terms} onCheckedChange={v=>setTerms(v===true)}/><span>{m.termsConsent} <a href="/terms" target="_blank" rel="noopener">{m.terms}</a> · <a href="/privacy" target="_blank" rel="noopener">{m.privacy}</a></span></label><label className="lf-consent"><Checkbox checked={marketing} onCheckedChange={v=>setMarketing(v===true)}/><span>{m.marketingConsent}</span></label></>}
        {error&&<p className="lf-error" role="alert">{error}</p>}{message&&<p className="lf-account-success" role="status">{message}</p>}
        {errorCode==='email_not_confirmed'&&<a className="lf-secondary" href="/verify-email?required=1">{copy.verificationHelp}</a>}
        {cooldown>0&&<p className="lf-small-note" role="status">{copy.cooldown.replace('{{seconds}}',String(cooldown))}</p>}
        <Button className="lf-primary" type="submit" disabled={busy||cooldown>0||(emailNeeded&&!emailReady)}>{busy?m.loading:mode==='login'?m.login:mode==='register'?m.register:mode==='verify'?m.resendVerification:mode==='recover'?m.sendResetLink:m.savePassword}<ArrowRight size={18}/></Button>
      </form><div className="lf-account-links">{mode!=='login'&&<a href="/login">{m.login}</a>}{mode==='login'&&<><a href="/forgot-password">{m.forgotPassword}</a><a href="/register">{m.register}</a></>}<a href="/#activity/telur-dan-hewan">{m.previewCta}</a></div></section></main></PortalShell>;
}
