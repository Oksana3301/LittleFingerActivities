import type {Worksheet,WorksheetState} from './workbook';

export function spatialComplete(a:Worksheet,state:WorksheetState){
 if(a.engine==='route')return !!a.route?.points.length&&JSON.stringify(state.selected||[])===JSON.stringify(a.route.points.map((_,i)=>'step-'+i));
 const pairs=a.pairs||[];
 return pairs.length>0&&pairs.length===a.options.length&&pairs.every(p=>a.options.some(o=>o.id===p.left)&&state.sorted?.[p.left]===p.right);
}
export function placePiece(a:Worksheet,sorted:Record<string,string>,piece:string,target:string){
 const slots=a.puzzle?a.puzzle.missing.map(i=>'slot-'+i):a.placement?Array.from({length:a.placement.rows*a.placement.columns},(_,i)=>'cell-'+i):[];
 if(!a.options.some(o=>o.id===piece)||!slots.includes(target))return sorted;
 return {...Object.fromEntries(Object.entries(sorted).filter(([id,cell])=>id!==piece&&cell!==target)),[piece]:target};
}
