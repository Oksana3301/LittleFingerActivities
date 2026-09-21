import {desc,eq} from 'drizzle-orm';
import {isOwner} from '../../../../lib/owner';
import {getDb} from '../../../../db';
import {preorders,siteSettings} from '../../../../db/schema';
import {validGroupUrl} from '../../../../lib/preorder';
export async function GET(){if(!await isOwner())return Response.json({error:'Akses khusus pemilik.'},{status:403});const db=getDb();return Response.json({leads:await db.select().from(preorders).orderBy(desc(preorders.createdAt)),groupUrl:(await db.select().from(siteSettings).where(eq(siteSettings.key,'whatsapp_group')).get())?.value||''},{headers:{'Cache-Control':'no-store'}})}
export async function PATCH(request:Request){if(!await isOwner())return Response.json({error:'Akses khusus pemilik.'},{status:403});if(request.headers.get('origin')!==new URL(request.url).origin)return Response.json({error:'Permintaan tidak sesuai.'},{status:403});try{const body=await request.json() as {groupUrl?:string};const url=validGroupUrl(body.groupUrl||'');if(!url)return Response.json({error:'Gunakan tautan undangan https://chat.whatsapp.com/… yang aktif.'},{status:400});await getDb().insert(siteSettings).values({key:'whatsapp_group',value:url}).onConflictDoUpdate({target:siteSettings.key,set:{value:url}});return Response.json({ok:true,groupUrl:url})}catch{return Response.json({error:'Tautan belum tersimpan.'},{status:500})}}
