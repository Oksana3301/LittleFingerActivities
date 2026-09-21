'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {Square,Volume2} from 'lucide-react';
import type {AudioLang,Settings,Text} from '../data/types';
import {useDeviceVoice} from './device-voice';
import {address,voiceTextKey} from '../data/personalization';
import {RecordVoiceButton} from './parent-voice';

type Dictionary=Record<string,string>;
type TranslationLang='zh'|'ar';
const dictionaries:Partial<Record<TranslationLang,Dictionary>>={};
const requests:Partial<Record<TranslationLang,Promise<Dictionary>>>={};
function loadDictionary(lang:TranslationLang){
 if(dictionaries[lang])return Promise.resolve(dictionaries[lang]!);
 if(!requests[lang])requests[lang]=fetch('/audio/'+(lang==='ar'?'arabic':'mandarin')+'.json').then(r=>{if(!r.ok)throw new Error('translation');return r.json() as Promise<Dictionary>}).then(data=>{dictionaries[lang]=data;return data}).finally(()=>{delete requests[lang]});
 return requests[lang]!;
}
export function AudioLanguagePicker({settings,onChange}:{settings:Settings;onChange:(p:Partial<Settings>)=>void}){
 const id=settings.lang==='id';
 return <label className="audio-language" data-voice-control><Volume2 size={17}/><span>{id?'Bahasa suara':'Audio language'}</span><select aria-label={id?'Bahasa suara':'Audio language'} value={settings.audioLang||settings.lang} onChange={e=>onChange({audioLang:e.target.value as AudioLang,voiceId:'auto'})}><option value="id">Indonesia</option><option value="en">English</option><option value="zh">Mandarin · 中文</option><option value="ar">Arab · العربية</option></select></label>;
}
export function useNarration(settings:Settings,onMute:(mute:boolean)=>void){
 const voice=useDeviceVoice(settings),lang=settings.audioLang||settings.lang,translated=lang==='zh'||lang==='ar';
 const [loaded,setLoaded]=useState<Partial<Record<TranslationLang,Dictionary>>>({...dictionaries});
 const [errorLang,setErrorLang]=useState<TranslationLang|null>(null),[retry,setRetry]=useState(0),[missing,setMissing]=useState(false);
 useEffect(()=>{setMissing(false);setErrorLang(null);if(lang!=='zh'&&lang!=='ar')return;let cancelled=false;loadDictionary(lang).then(data=>{if(!cancelled)setLoaded(previous=>({...previous,[lang]:data}))}).catch(()=>{if(!cancelled)setErrorLang(lang)});return()=>{cancelled=true}},[lang,retry]);
 const dictionary=translated?loaded[lang]:undefined;
 const text=(value:Text|undefined)=>!value?'':translated?(value[lang]||dictionary?.[value.en]||''):value[lang];
 const [parentKey,setParentKey]=useState(''),[parentMessage,setParentMessage]=useState('');
 const audioRef=useRef<HTMLAudioElement|null>(null),urlRef=useRef(''),requestRef=useRef(0),clips=useRef(new Map<string,Blob|null>());
 const stop=useCallback(()=>{requestRef.current++;audioRef.current?.pause();audioRef.current=null;if(urlRef.current)URL.revokeObjectURL(urlRef.current);urlRef.current='';setParentKey('');setParentMessage('');voice.stop()},[voice.stop]);
 useEffect(()=>{const reset=()=>{clips.current.clear();stop()},hide=()=>{if(document.hidden)stop()};window.addEventListener('littlefinger-stop-audio',stop);window.addEventListener('littlefinger-voice-updated',reset);document.addEventListener('visibilitychange',hide);return()=>{window.removeEventListener('littlefinger-stop-audio',stop);window.removeEventListener('littlefinger-voice-updated',reset);document.removeEventListener('visibilitychange',hide);stop()}},[stop]);
 useEffect(()=>{stop()},[lang,settings.parentVoice,settings.nickname,stop]);
 useEffect(()=>{if(settings.mute)stop()},[settings.mute,stop]);
 const question=(value:Text,language:AudioLang=lang)=>address(language===lang?text(value):value[language]||'',settings.nickname,language);
 const activeKey=parentKey||voice.activeKey;
 const play=async(value:Text,key:string)=>{
  const content=key==='instruction'?question(value):text(value);if(!content){setMissing(true);return}setMissing(false);
  if(activeKey===key){stop();return}window.dispatchEvent(new Event('littlefinger-stop-audio'));if(settings.mute)onMute(false);
  const token=++requestRef.current;
  if(settings.parentVoice){
   try{const hash=await voiceTextKey(content),cacheKey=lang+':'+hash;let blob=clips.current.get(cacheKey);
    if(blob===undefined){const r=await fetch('/api/parent-voice?lang='+lang+'&key='+hash);if(r.ok){blob=await r.blob();if(token!==requestRef.current)return;clips.current.set(cacheKey,blob)}else if(r.status===404){blob=null;if(token!==requestRef.current)return;clips.current.set(cacheKey,null)}else throw new Error('unavailable')}
    if(token!==requestRef.current)return;
    if(blob){urlRef.current=URL.createObjectURL(blob);const audio=new Audio(urlRef.current);audioRef.current=audio;setParentKey(key);setParentMessage(settings.lang==='id'?'Suara orang tua':'Parent voice');audio.onended=()=>{if(token===requestRef.current)stop()};audio.onerror=()=>{if(token===requestRef.current){stop();setParentMessage(settings.lang==='id'?'Rekaman belum bisa diputar. Ketuk lagi atau pilih suara perangkat.':'Recording could not play. Tap again or choose the device voice.')}};await audio.play();return}
    setParentMessage(settings.lang==='id'?'Belum direkam dalam bahasa ini; memakai suara perangkat.':'No recording in this language; using the device voice.');
   }catch{if(token!==requestRef.current)return;audioRef.current?.pause();audioRef.current=null;if(urlRef.current)URL.revokeObjectURL(urlRef.current);urlRef.current='';setParentKey('');setParentMessage(settings.lang==='id'?'Rekaman belum tersedia. Memakai suara perangkat. Masuk untuk mengakses suara pribadi.':'Recording unavailable. Using the device voice. Sign in for private recordings.')}
  }
  if(token===requestRef.current)voice.say(content,key,lang);
 };
 const record=(value:Text,key='')=>settings.recordMode?<RecordVoiceButton text={key==='instruction'?question(value):text(value)} lang={lang}/>:null;
 const audio=(value:Text,key:string,className='choice-audio')=><span className="spoken-control"><button type="button" data-voice-control className={className+(activeKey===key?' is-speaking':'')} disabled={translated&&!text(value)} aria-label={(settings.lang==='id'?'Dengarkan: ':'Listen: ')+(text(value)||value[settings.lang])} aria-pressed={activeKey===key} onClick={e=>{e.stopPropagation();void play(value,key)}}>{activeKey===key?<Square size={14}/>:<Volume2 size={17}/>}</button>{record(value,key)}</span>;
 const languageName=lang==='ar'?(settings.lang==='id'?'Arab':'Arabic'):'Mandarin';
 const status=<div className="voice-feedback" role="status" aria-live="polite">{translated&&!dictionary?(errorLang===lang?<><span>{settings.lang==='id'?`Teks ${languageName} belum termuat. Periksa koneksi.`:`${languageName} text could not load. Check your connection.`}</span><button data-voice-control onClick={()=>setRetry(v=>v+1)}>{settings.lang==='id'?'Coba lagi':'Retry'}</button></>:settings.lang==='id'?`Menyiapkan teks ${languageName}…`:`Preparing ${languageName} text…`):missing?(settings.lang==='id'?'Teks suara belum tersedia untuk bagian ini.':'Audio text is unavailable for this part.'):[parentMessage,voice.message].filter(Boolean).join(' ')}{activeKey&&<button data-voice-control onClick={stop}>{settings.lang==='id'?'Hentikan suara':'Stop audio'}</button>}</div>;
 return {...voice,stop,activeKey,question,record,lang,translated,textLang:lang==='ar'?'ar':lang==='zh'?'zh-CN':lang,textDirection:(lang==='ar'?'rtl':'ltr') as 'rtl'|'ltr',text,play,audio,status};
}
