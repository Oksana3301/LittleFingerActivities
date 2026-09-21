import {requirePremium,accountFailure,result} from '../../../../lib/customer-auth';
import {legacyActivity} from '../../../../lib/worksheet-content';
export const dynamic='force-dynamic';
export async function GET(_request:Request,context:{params:Promise<{id:string}>}){
  try{await requirePremium();const {id}=await context.params;const activity=legacyActivity(id);return activity?result(activity):result({error:'Aktivitas tidak ditemukan.'},404);}catch(error){return accountFailure(error);}
}
