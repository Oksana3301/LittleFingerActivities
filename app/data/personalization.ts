import type {AudioLang,Text} from './types';
export function childName(value:string){const name=value.trim().replace(/\s+/g,' ').slice(0,40);return name==='Little explorer'?'':name}
export function address(text:string,name:string,lang:AudioLang){const n=childName(name);return !n?text:lang==='ar'?`يا ${n}، ${text}`:lang==='zh'?`${n}，${text}`:`${n}, ${text}`}
export function feedbackText(name:string,kind:'retry'|'success'|'creative'):Text{
 const n=childName(name),id=n?`, ${n}`:'',en=n?`, ${n}`:'',zh=n?`，${n}`:'',ar=n?` يا ${n}`:'';
 if(kind==='retry')return {id:`Yuk, coba lagi${id}!`,en:`Let’s try again${en}!`,zh:`${n?n+'，':''}我们再试一次吧！`,ar:`${n?'يا '+n+'، ':''}لنجرب مرة أخرى!`};
 if(kind==='creative')return {id:`Terima kasih sudah berbagi ide${id}! Yuk, lanjut berkreasi!`,en:`Thanks for sharing your idea${en}! Let’s keep creating!`,zh:`谢谢你分享想法${zh}！我们继续创作吧！`,ar:`شكرًا على هذه الفكرة${ar}! لنواصل الإبداع!`};
 return {id:`Hebat${id}! Kita belajar hal baru! Masih banyak lagi yang bisa kita pelajari.`,en:`Great${en}! We learned something new! There’s lots more we can learn.`,zh:`真棒${zh}！我们学到了新知识！还有好多知识等着我们去学呢。`,ar:`رائع${ar}! تعلّمنا شيئًا جديدًا! وما زال أمامنا الكثير لنتعلّمه.`};
}
export const normalizeVoiceText=(text:string)=>text.normalize('NFC').trim().replace(/\s+/g,' ');
export async function voiceTextKey(text:string){const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(normalizeVoiceText(text)));return Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('')}
