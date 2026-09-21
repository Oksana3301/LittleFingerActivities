export type Lang='en'|'id';
export type AudioLang=Lang|'zh'|'ar';
export type Text={en:string;id:string;zh?:string;ar?:string};
export type Option={id:string;label:Text;symbol?:string;shape?:string;color?:string;group?:string};
export type Activity={id:string;title:Text;description:Text;age:string;pack:string;engine:string;objective:Text;instruction:Text;duration:number;materials:Text;offscreen:Text;safety:Text;adaptation:Text;prompt:Text;options:Option[];answer?:string|string[];groups?:{id:string;label:Text}[];steps?:Text[];pattern?:string[];countTarget?:number;traceShape?:string;traceLetter?:string;editorialState:string;publicationState:string;version?:string};
export type Stroke={color:string;points:string};
export type PlayState={selected?:string[];matched?:string[];flipped?:number[];step?:number;complete?:boolean;stage?:number;paths?:Stroke[];seconds?:number;explored?:boolean};
export type Observation={id:string;activity:string;date:string;status:string;note:string};
export type Settings={lang:Lang;audioLang?:AudioLang;parentVoice?:boolean;recordMode?:boolean;age:string;nickname:string;mute:boolean;voiceId?:string;voiceRate?:number;reduced:boolean;seated:boolean;limit:string;stickers:boolean;interest:string;faith:boolean};
export type Saved={settings:Settings;progress:Record<string,PlayState>;observations:Observation[];favorites:string[];routines:{id:string;text:string;done:boolean}[];trip:{name:string;date:string;packing:string[]};bucket:{id:string;text:string;done:boolean}[]};
export const defaults:Saved={settings:{lang:'en',age:'2',nickname:'Little explorer',mute:true,voiceId:'auto',voiceRate:.86,reduced:false,seated:false,limit:'5',stickers:false,interest:'all',faith:false},progress:{},observations:[],favorites:[],routines:[],trip:{name:'',date:'',packing:[]},bucket:[]};
export function textOf(t:Text|string|undefined,l:Lang):string{return typeof t==='string'?t:t?.[l]||''}

export function newId():string{return typeof crypto.randomUUID==='function'?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint32Array(4))).map(n=>n.toString(16).padStart(8,'0')).join('')}
