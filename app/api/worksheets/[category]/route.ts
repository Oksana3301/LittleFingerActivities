import {customerSession,hasCustomerAccess,accountFailure,result} from '../../../../lib/customer-auth';
import {worksheetCategory} from '../../../../lib/worksheet-content';
import {freeWorksheetIds} from '../../../data/access';
export const dynamic='force-dynamic';
export async function GET(_request:Request,context:{params:Promise<{category:string}>}){
  try{
    const {category}=await context.params;
    const session=await customerSession();const access=session?await hasCustomerAccess(session):false;
    const list=await worksheetCategory(category);if(!list)return result({error:'Koleksi tidak ditemukan.'},404);
    const visible=access?list:list.filter(a=>freeWorksheetIds.has(a.id));
    if(!visible.length)return result({error:'Masuk dan aktifkan akses tahunan untuk membuka koleksi ini.',code:'subscription_required'},403);
    return result(visible);
  }catch(error){return accountFailure(error);}
}
