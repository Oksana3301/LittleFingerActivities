'use client';
import {useEffect,useRef,useState,type Dispatch,type SetStateAction} from 'react';
import {defaults,type Saved,type AudioLang} from '../app/data/types';
import {emptyLog,mergeLogs,reportStorage,type LearningLog} from '../app/data/daily-report';
import type {WorksheetState} from '../app/data/workbook';
import {accountFetch,jsonAction,type AccountOverview,type ChildProfile} from './customer-client';
type Book={progress:Record<string,WorksheetState>;favorites:string[];last:string};
type State<T>=Dispatch<SetStateAction<T>>;
export function useFamilyStorage(args:{account:AccountOverview;child:ChildProfile|null;saved:Saved;setSaved:State<Saved>;book:Book;setBook:State<Book>;learning:LearningLog;setLearning:State<LearningLog>;ready:boolean;setReady:State<boolean>;setStorageError:State<string>}){
 const {account,child,saved,setSaved,book,setBook,learning,setLearning,ready,setReady,setStorageError}=args;
 const revision=useRef(0),lastSaved=useRef(''),blocked=useRef(false),writing=useRef(false);const [tick,setTick]=useState(0);
 const baseFamily=():Saved=>({...structuredClone(defaults),settings:{...defaults.settings,lang:child?.preferred_language==='en'?'en':'id',audioLang:(child?.preferred_language||'id') as AudioLang,age:child?.age_band.split('-')[0]||'2',nickname:child?.display_name||'',stickers:true}});
 const prefix=account.user?'lf-local-'+account.user.id+'-':'';
 const keys={family:prefix+'little-world-v1',book:prefix+'astra-workbook-v2',learning:prefix+reportStorage};
 useEffect(()=>{
  let cancelled=false;
  async function read(){
   try{
    let family:any,workbook:any,history:any;
    if(account.user&&child){
     const response=await accountFetch('/api/account/workbook?child='+child.id);const data:any=await response.json();if(!response.ok)throw new Error(data.error||'Riwayat belum dapat dimuat.');
     revision.current=data.revision;family=data.payload?.family;workbook=data.payload?.book;history=data.payload?.learning;
    }else{family=JSON.parse(localStorage.getItem(keys.family)||'null');workbook=JSON.parse(localStorage.getItem(keys.book)||'null');history=JSON.parse(localStorage.getItem(keys.learning)||'null');}
    if(cancelled)return;
    const nextFamily=family&&Array.isArray(family.observations)&&family.settings?{...baseFamily(),...family,settings:{...baseFamily().settings,...family.settings,...(child?{nickname:child.display_name}:{})}}:baseFamily();
    const nextBook=workbook&&workbook.progress&&Array.isArray(workbook.favorites)?workbook:{progress:{},favorites:[],last:'activity/telur-dan-hewan'};
    const nextLearning=history?.version===1&&Array.isArray(history.events)&&Array.isArray(history.previous)?history:{...emptyLog,previous:Object.entries(nextBook.progress).filter(([,v])=>(v as WorksheetState).complete).map(([k])=>k)};
    lastSaved.current=JSON.stringify({family:nextFamily,book:nextBook,learning:nextLearning});
    setSaved(nextFamily);setBook(nextBook);setLearning(nextLearning);setReady(true);
   }catch(error){if(!cancelled){blocked.current=true;setStorageError(error instanceof Error?error.message:'Riwayat belum dapat dimuat. Muat ulang sebelum bermain.');}}
  }
  void read();return()=>{cancelled=true;};
 },[]);
 useEffect(()=>{
  if(!ready||blocked.current)return;
  const payload={family:saved,book,learning};const encoded=JSON.stringify(payload);
  if(account.user&&child){
   if(!account.access||encoded===lastSaved.current||writing.current)return;
   const timer=setTimeout(async()=>{
    writing.current=true;
    try{const data=await jsonAction('/api/account/workbook',{child:child.id,revision:revision.current,payload});revision.current=data.revision;lastSaved.current=encoded;setStorageError('');}
    catch(error){blocked.current=true;setStorageError((error instanceof Error?error.message:'Aktivitas belum tersimpan.')+' Ekspor riwayat melalui pengaturan orang tua sebelum memuat ulang.');}
    finally{writing.current=false;setTick(v=>v+1);}
   },700);return()=>clearTimeout(timer);
  }
  try{localStorage.setItem(keys.family,JSON.stringify(saved));localStorage.setItem(keys.book,JSON.stringify(book));localStorage.setItem(keys.learning,JSON.stringify(learning));setStorageError('');}catch{setStorageError('Perubahan belum tersimpan. Penyimpanan perangkat mungkin penuh.');}
 },[ready,saved,book,learning,account.access,tick]);
 useEffect(()=>{
  if(!account.user||!child||!ready)return;
  const warn=(event:BeforeUnloadEvent)=>{if(JSON.stringify({family:saved,book,learning})!==lastSaved.current){event.preventDefault();event.returnValue='';}};
  window.addEventListener('beforeunload',warn);return()=>window.removeEventListener('beforeunload',warn);
 },[ready,saved,book,learning,account.user,child]);
 useEffect(()=>{
  if(account.user)return;
  const sync=(event:StorageEvent)=>{try{if(!event.newValue)return;const v=JSON.parse(event.newValue);if(event.key===keys.learning&&v?.version===1&&Array.isArray(v.events))setLearning(old=>mergeLogs(old,v));if(event.key===keys.book&&v.progress&&Array.isArray(v.favorites))setBook(v);if(event.key===keys.family&&v.settings&&Array.isArray(v.observations))setSaved(v);}catch{}};
  window.addEventListener('storage',sync);return()=>window.removeEventListener('storage',sync);
 },[]);
}
