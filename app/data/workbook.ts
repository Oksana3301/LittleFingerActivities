import type {Picture} from '../components/artwork';
import type {Text} from './types';
import index from './worksheet-index.json';
import categoryIndex from './worksheet-categories.json';

export type Guide={kind:string;d?:string;x?:number;y?:number;x1?:number;y1?:number;x2?:number;y2?:number;cx?:number;cy?:number;r?:number;width?:number;height?:number;fill?:string;stroke?:string;strokeWidth?:number;text?:string;fontSize?:number;shape?:string;asset?:string;dashed?:boolean;items?:Picture[]};
export type Worksheet={partCount?:number;duration?:number;skills?:string[];faith?:boolean;map?:{places:{option:string;lat:number;lng:number;country:string}[]};puzzle?:{image:Picture;columns:number;rows:number;missing:number[]};placement?:{columns:number;rows:number;example:{option:string;cell:number}[];cells:Text[]};route?:{start:Picture;end:Picture;points:{x:number;y:number;label:Text}[];decoys:{x:number;y:number;label:Text}[]};id:string;category:string;title:Text;instruction:Text;engine:string;activityKind?:string;revision?:string;age:number;ageRange?:number[];variant?:number;difficulty?:number;options:Picture[];rightOptions?:Picture[];bins?:{id:string;label:Text;asset:string}[];answer:string[];pattern?:string[];patternItems?:(Picture|null)[];reference?:Picture;languageOfTask?:string;layout?:string;countTarget?:number;countAsset?:string;operation?:string;operands?:number[];expression?:string;trace?:string;guide?:string;pairs?:{left:string;right:string}[];offscreen?:Text;note?:Text;rounds?:Partial<Worksheet>[];canvas?:{viewBox:number[];guide:Guide[]};completion?:{mode:string;goals:Text[]}};
export type Category={id:string;title:Text;description:Text;asset:string;group:string;engine:string;activityKinds?:string[];age:number};
export type WorksheetState={observation?:string;selected?:string[];sorted?:Record<string,string>;matches?:string[];flipped?:number[];counted?:string[];paths?:{color:string;points:string}[];complete?:boolean;checked?:boolean;stickers?:{asset:string;x:number;y:number}[];seconds?:number};
// The authored practice catalogue is imported below once generated and validated.
export const categories=categoryIndex as Category[];
export const worksheets=index as Worksheet[];
export const featured:Worksheet={id:'telur-dan-hewan',category:'animal-names',title:{id:'Siapa menetas dari telur?',en:'Who hatches from an egg?'},instruction:{id:'Lingkari ayam, bebek, dan penyu.',en:'Circle the hen, duck, and turtle.',zh:'圈出母鸡、鸭子和海龟。',ar:'ضع دائرة حول الدجاجة والبطة والسلحفاة البحرية.'},engine:'identify',age:3,options:[['hen','Ayam','Hen'],['duck','Bebek','Duck'],['turtle','Penyu','Turtle'],['cat','Kucing','Cat'],['rabbit','Kelinci','Rabbit'],['goat','Kambing','Goat']].map(([asset,id,en])=>({id:asset,asset,label:{id,en,...(asset==='turtle'?{zh:'海龟',ar:'سلحفاة بحرية'}:{})}})),answer:['hen','duck','turtle'],offscreen:{id:'Cari gambar hewan di buku bersama. Ceritakan hewan mana yang pernah kamu lihat.',en:'Look for animals in a book together. Talk about an animal you have seen.'}};

export function worksheetInstruction(a:Worksheet):Text{return a.category==='height'&&a.instruction.en==='Choose the shortest one.'?{...a.instruction,zh:'选出最矮的那个。',ar:'اختر الأقصر ارتفاعًا.'}:a.instruction}

// Round content is complete; optional game fields must never leak from round one.
export function resolveWorksheetRound(a:Worksheet,round=0):Worksheet{
 if(!a.rounds?.length)return a;
 const empty=Object.fromEntries(['reference','rightOptions','patternItems','pattern','countAsset','countTarget','canvas','guide','trace','pairs','bins','operation','operands','expression','languageOfTask','layout','puzzle','placement','route','map'].map(key=>[key,undefined]));
 return {...a,...empty,...a.rounds[Math.max(0,Math.min(a.rounds.length-1,round))],rounds:undefined};
}
