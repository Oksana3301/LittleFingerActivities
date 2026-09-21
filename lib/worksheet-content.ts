import 'server-only';
import type {Worksheet} from '../app/data/workbook';
import legacy from '../content/activities.json';
const bundles=import.meta.glob('../content/worksheets/*.json',{import:'default'}) as Record<string,()=>Promise<Worksheet[]>>;
export async function worksheetCategory(category:string){
  if(!/^[a-z0-9-]{1,100}$/.test(category))return null;
  const load=bundles['../content/worksheets/'+category+'.json'];return load?await load():null;
}
export const legacyActivity=(id:string)=>legacy.find(a=>a.id===id);
