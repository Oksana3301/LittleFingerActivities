'use client';
import {useEffect,useState} from 'react';
import {Art} from './artwork';
import {languages,launchMessages,type LanguageCode} from '../../docs/launch/launch-i18n';
export function useAccountLanguage(){
  const [lang,setLang]=useState<LanguageCode>('id');
  useEffect(()=>{try{const stored=localStorage.getItem('lf-account-language');if(languages.some(l=>l.code===stored))setLang(stored as LanguageCode);}catch{}},[]);
  const change=(value:LanguageCode)=>{setLang(value);try{localStorage.setItem('lf-account-language',value);}catch{}};
  return {lang,setLang:change,m:launchMessages[lang]};
}
export function PortalShell({children,lang,setLang}:{children:React.ReactNode;lang:LanguageCode;setLang:(l:LanguageCode)=>void}){
  const m=launchMessages[lang];
  return <div className="lf-portal" lang={lang} dir={lang==='ar'?'rtl':'ltr'}><header className="lf-portal-nav"><a className="brand-lockup" href="/preorder"><Art name="sun"/><span>littlefinger<small>ACTIVITIES</small></span></a><nav aria-label={m.account}><a href="/#collection">{m.activitiesPreview}</a><a href="/account">{m.account}</a><select aria-label={m.preferredLanguage} value={lang} onChange={e=>setLang(e.target.value as LanguageCode)}>{languages.map(l=><option key={l.code} value={l.code}>{l.label}</option>)}</select></nav></header>{children}<footer className="lf-portal-footer"><a href="/privacy">{m.privacy}</a><a href="/terms">{m.terms}</a><a href="/preorder">{m.preorder}</a></footer></div>;
}
