export type LearningEvent={id:string;at:string;day:string;timezone:string;worksheet:string;roundKey:string;category:string;engine:string;type:'open'|'attempt'|'mistake'|'complete';correct?:boolean;signature?:string;parts:number};
export type LearningLog={version:1;events:LearningEvent[];previous:string[]};
export const emptyLog:LearningLog={version:1,events:[],previous:[]};
export const reportStorage='littlefinger-learning-v1';
export function localDay(d=new Date()){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
export function mergeLogs(a:LearningLog,b:LearningLog):LearningLog{const seen=new Set<string>();const events=[...new Map([...a.events,...b.events].map(e=>[e.id,e])).values()].sort((x,y)=>x.at.localeCompare(y.at)).filter(e=>{const key=e.type==='attempt'?`${e.day}|${e.roundKey}|attempt|${e.signature}`:e.type==='complete'?`${e.day}|${e.roundKey}|complete`:e.id;if(seen.has(key))return false;seen.add(key);return true});return {version:1,previous:[...new Set([...a.previous,...b.previous])],events}}

export function addEvent(log:LearningLog,e:LearningEvent):LearningLog{
 const relevant=log.events.filter(x=>x.day===e.day&&x.roundKey===e.roundKey);
 if(e.type==='attempt'&&relevant.some(x=>x.type==='attempt'&&x.signature===e.signature))return log;
 if(e.type==='complete'&&relevant.some(x=>x.type==='complete'))return log;
 if(e.type==='open'){const last=log.events.filter(x=>x.type==='open').at(-1);if(last?.worksheet===e.worksheet&&Date.parse(e.at)-Date.parse(last.at)<30000)return log}
 return {...log,events:[...log.events,e]};
}
export function summarize(log:LearningLog,day:string){
 const today=log.events.filter(e=>e.day===day),attempts=today.filter(e=>e.type==='attempt');
 const solved=new Set(attempts.filter(e=>e.correct).map(e=>e.roundKey));
 const tried=new Set(attempts.map(e=>e.roundKey));
 const first=new Set([...solved].filter(key=>{
  const history=log.events.filter(e=>e.roundKey===key&&e.day<=day).sort((a,b)=>a.at.localeCompare(b.at));
  // A completed earlier-day practice starts a fresh daily attempt. An unfinished
  // attempt crossing midnight retains its corrections until it is solved.
  const priorSuccess=history.filter(e=>e.day<day&&(e.type==='complete'||e.type==='attempt'&&e.correct)).at(-1)?.at;
  const events=history.filter(e=>!priorSuccess||e.at>priorSuccess),a=events.find(e=>e.type==='attempt');
  return a?.correct&&!events.some(e=>e.type==='mistake'&&e.at<=a.at);
 }));
 const complete=new Set(today.filter(e=>e.type==='complete').map(e=>e.roundKey));
 const prior=new Set([...log.previous,...log.events.filter(e=>e.type==='complete'&&e.day<day).map(e=>e.roundKey)]);
 const newWins=[...complete].filter(k=>!prior.has(k)).length;
 const doneThroughDay=new Set([...prior,...complete]);
 const sheets=new Set(today.filter(e=>e.type==='complete').filter(e=>{const prefix=e.roundKey.slice(0,e.roundKey.lastIndexOf('~'));return Array.from({length:e.parts},(_,i)=>prefix+'~'+i).every(k=>doneThroughDay.has(k))&& !Array.from({length:e.parts},(_,i)=>prefix+'~'+i).every(k=>prior.has(k))}).map(e=>e.worksheet));
 const categoryIds=[...new Set(today.map(e=>e.category))];
 const categories=categoryIds.map(id=>{const events=today.filter(e=>e.category===id),keys=new Set(events.filter(e=>e.type==='attempt').map(e=>e.roundKey)),correct=[...keys].filter(k=>solved.has(k)).length,firstTry=[...keys].filter(k=>first.has(k)).length;return {id,opens:events.filter(e=>e.type==='open').length,opened:new Set(events.filter(e=>e.type==='open').map(e=>e.worksheet)).size,tried:keys.size,correct,firstTry,completed:new Set(events.filter(e=>e.type==='complete').map(e=>e.roundKey)).size}});
 const strong=categories.filter(c=>c.tried>=3&&c.firstTry/c.tried>=.7).sort((a,b)=>b.firstTry/b.tried-a.firstTry/a.tried||b.tried-a.tried);
 const interests=categories.filter(c=>c.opens>=2&&c.correct>=2).sort((a,b)=>(b.opened+b.correct)-(a.opened+a.correct)||b.opens-a.opens);
 return {correct:solved.size,firstTry:first.size,tried:tried.size,attempts:attempts.length,completed:complete.size,newWins,sheets:sheets.size,creative:new Set(today.filter(e=>e.type==='complete'&&['draw','trace','explore'].includes(e.engine)).map(e=>e.roundKey)).size,categories,strong,interests};
}
