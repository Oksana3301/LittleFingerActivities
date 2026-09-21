import type {Lang} from './types';

export const activityKinds={
 explore:{id:'Eksplorasi bersama',en:'Explore together'},
 'map-find':{id:'Jelajahi peta',en:'Explore the map'},
 'choose-one':{id:'Pilih gambar',en:'Choose a picture'},
 'choose-many':{id:'Pilih beberapa',en:'Choose several'},
 'odd-one-out':{id:'Cari yang berbeda',en:'Find the odd one out'},
 clue:{id:'Tebak petunjuk',en:'Guess from clues'},
 'picture-detail':{id:'Tebak potongan',en:'Guess the detail'},
 'complete-picture':{id:'Lengkapi gambar',en:'Complete the picture'},
 'copy-layout':{id:'Salin posisi',en:'Copy the positions'},
 'follow-route':{id:'Ikuti jalur',en:'Follow the route'},
 match:{id:'Pasangkan',en:'Match pairs'},
 'shadow-match':{id:'Cocokkan bayangan',en:'Match shadows'},
 sort:{id:'Kelompokkan',en:'Sort into groups'},
 sequence:{id:'Susun urutan',en:'Put in order'},
 memory:{id:'Ingat pasangan',en:'Remember pairs'},
 pattern:{id:'Lanjutkan pola',en:'Continue a pattern'},
 count:{id:'Ayo berhitung',en:'Count together'},
 trace:{id:'Telusuri garis',en:'Trace the lines'},
 draw:{id:'Gambar & kreasi',en:'Draw & create'},
} as const;
export type ActivityKind=keyof typeof activityKinds;
export function getActivityKind(a:{engine:string;activityKind?:string;answer?:string[]}):ActivityKind{
 if(a.activityKind&&a.activityKind in activityKinds)return a.activityKind as ActivityKind;
 if(a.engine==='pair')return 'match';
 if(a.engine==='identify'||a.engine==='compare')return (a.answer?.length||0)>1?'choose-many':'choose-one';
 return a.engine in activityKinds?a.engine as ActivityKind:'choose-one';
}
export function activityKindLabel(a:{engine:string;activityKind?:string;answer?:string[]},lang:Lang){return activityKinds[getActivityKind(a)][lang]}
export function worksheetProgressKey(id:string,round=0,revision?:string){return id+(revision?'@'+revision:'')+'~'+round}

// Put different ways of playing next to each other without changing worksheet IDs.
export function interleaveActivities<T extends {engine:string;activityKind?:string;answer?:string[]}>(items:T[]):T[]{
 const groups=new Map<ActivityKind,T[]>();
 for(const item of items){const kind=getActivityKind(item);if(!groups.has(kind))groups.set(kind,[]);groups.get(kind)!.push(item)}
 const queues=[...groups.values()],result:T[]=[];
 for(let i=0;i<Math.max(0,...queues.map(q=>q.length));i++)for(const queue of queues)if(queue[i])result.push(queue[i]);
 return result;
}
