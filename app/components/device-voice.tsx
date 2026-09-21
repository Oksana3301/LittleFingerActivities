'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {Square,Volume2} from 'lucide-react';
import {Switch} from '@/components/ui/switch';
import type {AudioLang,Settings} from '../data/types';

// SpeechSynthesisVoice has no gender field. Prefer recognized voice names only;
// the actual installed voice remains visible and can always be changed.
const preferredNames=/\b(?:gadis|zira|hazel|susan|catherine|linda|heera|jenny|aria|sonia|huihui|yaoyao|xiaoxiao|xiaoyi|yating|hanhan|hoda|salma|zariyah|fatima|laila|amina|rana|sana|noura|layla|iman|mouna|aysha|amal|amany|reem|maryam)(?:MultilingualNeural|Neural)?\b/i;
const matchesLanguage=(voice:SpeechSynthesisVoice,lang:AudioLang)=>{const locale=voice.lang.toLowerCase().replaceAll('_','-');if(lang==='zh')return (/^(?:cmn(?:-|$)|zh-cmn(?:-|$)|zh-(?:(?:hans|hant)-)?(?:cn|tw|sg)(?:-|$))/.test(locale)||(/^zh(?:-hans|-hant)?$/.test(locale)&&/mandarin|普通话|普通話|国语|國語/i.test(voice.name)))&&!/(?:^|-)(?:hk|mo|yue)(?:-|$)/.test(locale)&&!/cantonese|粤|粵|廣東|广东/i.test(voice.name);return locale.split('-')[0]===lang};
const voiceKey=(voice:SpeechSynthesisVoice)=>voice.voiceURI||voice.name;
export function useDeviceVoice(settings:Settings){
 const [voices,setVoices]=useState<SpeechSynthesisVoice[]>([]);
 const [supported,setSupported]=useState(true);
 const [activeKey,setActiveKey]=useState('');
 const [message,setMessage]=useState('');
 const current=useRef<SpeechSynthesisUtterance|null>(null);
 const generation=useRef(0),timer=useRef<ReturnType<typeof setTimeout>|null>(null);
 const lang=settings.audioLang||settings.lang;const id=settings.lang==='id';
 const clearTimer=()=>{if(timer.current)clearTimeout(timer.current);timer.current=null};
 const stop=useCallback(()=>{
  generation.current++;clearTimer();current.current=null;
  if(typeof window!=='undefined'&&'speechSynthesis'in window)window.speechSynthesis.cancel();
  setActiveKey('');setMessage('');
 },[]);
 useEffect(()=>{
  if(!('speechSynthesis'in window)){setSupported(false);return}
  const read=()=>setVoices(window.speechSynthesis.getVoices());read();
  window.speechSynthesis.addEventListener('voiceschanged',read);
  const hide=()=>{if(document.hidden)stop()};document.addEventListener('visibilitychange',hide);
  return()=>{generation.current++;clearTimer();window.speechSynthesis.removeEventListener('voiceschanged',read);document.removeEventListener('visibilitychange',hide);if(current.current)window.speechSynthesis.cancel();current.current=null};
 },[stop]);
 useEffect(()=>{if(settings.mute)stop()},[settings.mute,stop]);
 useEffect(()=>{stop()},[lang,settings.voiceId,settings.voiceRate,stop]);
 const available=voices.filter(v=>matchesLanguage(v,lang));
 const choose=(list:SpeechSynthesisVoice[])=>list.find(v=>voiceKey(v)===settings.voiceId)||list.find(v=>preferredNames.test(v.name))||list.find(v=>v.default)||list[0];
 const selectedVoice=choose(available);
 const say=(text:string,key:string,spokenLang:AudioLang=lang)=>{
  if(!text.trim())return;
  if(activeKey===key){stop();return}
  stop();
  const unavailable=id?'Suara belum tersedia. Bacakan teks bersama, ya.':'Voice is unavailable. Please read the text together.';
  if(!('speechSynthesis'in window)||!('SpeechSynthesisUtterance'in window)){setMessage(unavailable);return}
  const synth=window.speechSynthesis,installed=synth.getVoices(),matching=installed.filter(v=>matchesLanguage(v,spokenLang));
  if(installed.length&&!matching.length){setMessage(id?'Suara '+({id:'Indonesia',en:'Inggris',zh:'Mandarin',ar:'Arab'}[spokenLang])+' belum tersedia di perangkat ini. Pilih atau pasang suara bahasa tersebut di pengaturan perangkat.':'A '+({id:'Indonesian',en:'English',zh:'Mandarin',ar:'Arabic'}[spokenLang])+' voice is not available on this device. Choose or install that language in device voice settings.');return}
  const utterance=new SpeechSynthesisUtterance(text);
  const voice=choose(matching);if(voice)utterance.voice=voice;
  utterance.lang=voice?.lang||({zh:'zh-CN',id:'id-ID',en:'en-US',ar:'ar-SA'}[spokenLang]);
  utterance.rate=Math.max(.7,Math.min(1,settings.voiceRate??.86));
  utterance.pitch=1;utterance.volume=1;
  current.current=utterance;const token=generation.current;
  const finish=()=>{if(token!==generation.current)return;clearTimer();current.current=null;setActiveKey('');setMessage('')};
  utterance.onstart=()=>{if(token!==generation.current)return;clearTimer();setMessage(id?'Sedang membacakan…':'Reading aloud…')};
  utterance.onend=finish;
  utterance.onerror=e=>{if(token!==generation.current)return;finish();if(e.error!=='canceled'&&e.error!=='interrupted')setMessage(unavailable)};
  setActiveKey(key);setMessage(id?'Menyiapkan suara…':'Preparing voice…');
  timer.current=setTimeout(()=>{if(token!==generation.current)return;stop();setMessage(unavailable)},8000);
  try{synth.speak(utterance)}catch{stop();setMessage(unavailable)}
 };
 return {available,selectedVoice,supported,activeKey,message,say,stop,voiceKey};
}

export function VoiceSettings({settings,onChange}:{settings:Settings;onChange:(p:Partial<Settings>)=>void}){
 const voice=useDeviceVoice(settings),id=settings.lang==='id',audioLang=settings.audioLang||settings.lang;
 const value=voice.available.some(v=>voice.voiceKey(v)===settings.voiceId)?settings.voiceId:'auto';
 return <section className="voice-settings"><h3>{id?'Suara pendamping':'Reading voice'}</h3>
  <div className="setting-row"><label htmlFor="parent-voice-mode">{id?'Gunakan rekaman orang tua':'Use parent recordings'}</label><Switch id="parent-voice-mode" checked={!!settings.parentVoice} onCheckedChange={parentVoice=>onChange({parentVoice})}/></div><div className="setting-row"><label htmlFor="parent-record-mode">{id?'Tampilkan tombol rekam di aktivitas':'Show recording buttons in activities'}</label><Switch id="parent-record-mode" checked={!!settings.recordMode} onCheckedChange={recordMode=>onChange({recordMode})}/></div><p>{id?'Rekam pertanyaan, nama gambar, dan respons di tiap bahasa. Rekaman yang cocok dipakai otomatis; kalimat yang belum direkam memakai suara perangkat.':'Record questions, picture names, and responses in each language. Matching recordings play automatically; unrecorded sentences use the device voice.'}</p><a className="soft-button" href="/parent-voice">{id?'Kelola rekaman pribadi':'Manage private recordings'}</a><p>{id?'Suara perempuan diprioritaskan bila tersedia. Dengarkan contohnya, lalu pilih yang paling nyaman.':'A female voice is preferred when available. Listen to a sample and choose a comfortable voice.'}</p>
  <label className="field-label">{id?'Bahasa suara':'Audio language'}<select aria-label={id?'Bahasa suara':'Audio language'} value={audioLang} onChange={e=>onChange({audioLang:e.target.value as AudioLang,voiceId:'auto'})}><option value="id">Indonesia</option><option value="en">English</option><option value="zh">Mandarin · 中文</option><option value="ar">Arab · العربية</option></select></label>
  <label className="field-label">{id?'Pilihan suara':'Choose a voice'}<select aria-label={id?'Pilihan suara':'Choose a voice'} value={value} onChange={e=>onChange({voiceId:e.target.value})}><option value="auto">{id?'Otomatis':'Automatic'}{voice.selectedVoice?' · '+voice.selectedVoice.name:''}</option>{voice.available.map(v=><option key={voice.voiceKey(v)} value={voice.voiceKey(v)}>{v.name} · {v.lang}</option>)}</select></label>
  <label className="field-label">{id?'Tempo membaca':'Reading pace'}<select aria-label={id?'Tempo membaca':'Reading pace'} value={settings.voiceRate??.86} onChange={e=>onChange({voiceRate:Number(e.target.value)})}><option value={.75}>{id?'Pelan':'Slow'}</option><option value={.86}>{id?'Lembut':'Gentle'}</option><option value={1}>{id?'Biasa':'Normal'}</option></select></label>
  <button className="soft-button" onClick={()=>{onChange({mute:false});voice.say(audioLang==='ar'?'مرحبًا يا صغيري. هيا نلعب معًا. اختر صورة تعجبك.':audioLang==='zh'?'宝贝，你好。我们一起来玩吧。选一张你喜欢的图片。':audioLang==='id'?'Halo, sayang. Yuk, kita bermain bersama. Pilih gambar yang kamu suka.':'Hello, little one. Let’s play together. Choose a picture you like.','sample')}}>{voice.activeKey==='sample'?<Square size={17}/>:<Volume2 size={18}/>} {id?'Coba suara':'Try voice'}</button>
  <p className="voice-settings-note">{id?'Suara berbeda di tiap perangkat. Audio dibuat saat diketuk; beberapa suara memerlukan internet.':'Voices vary by device. Audio is created on tap; some voices need an internet connection.'}</p>
  {!voice.supported&&<p role="status">{id?'Peramban ini belum mendukung suara.':'This browser does not support speech.'}</p>}
  <p role="status" aria-live="polite">{voice.message}</p>
 </section>;
}
