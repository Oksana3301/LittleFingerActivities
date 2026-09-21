import {eq,lt,sql} from 'drizzle-orm';
import {getDb} from '../../../db';
import {preorders,siteSettings,submissionLimits} from '../../../db/schema';
import {preorderSchema,validGroupUrl} from '../../../lib/preorder';
export async function GET(){try{const row=await getDb().select().from(siteSettings).where(eq(siteSettings.key,'whatsapp_group')).get();return Response.json({groupUrl:row?validGroupUrl(row.value):null},{headers:{'Cache-Control':'no-store'}})}catch{return Response.json({groupUrl:null},{headers:{'Cache-Control':'no-store'}})}}
export async function POST(request:Request){
 if(request.headers.get('origin')&&request.headers.get('origin')!==new URL(request.url).origin)return Response.json({error:'Buka formulir dari website Littlefinger.'},{status:403});
 if(!request.headers.get('content-type')?.includes('application/json'))return Response.json({error:'Format tidak sesuai.'},{status:415});
 try{
  const raw=await request.text();if(raw.length>2048)return Response.json({error:'Data terlalu panjang.'},{status:413});let body;try{body=JSON.parse(raw)}catch{return Response.json({error:'Periksa isi formulir.'},{status:400})}
  const parsed=preorderSchema.safeParse(body);if(!parsed.success)return Response.json({error:parsed.error.issues[0]?.message||'Periksa nama dan nomor WhatsApp.'},{status:400});
  const db=getDb(),now=Date.now(),ip=request.headers.get('cf-connecting-ip')||'local',windowId=Math.floor(now/600000);
  const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(ip+':'+windowId));const key=Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('');
  await db.delete(submissionLimits).where(lt(submissionLimits.expires,now));
  const rate=await db.insert(submissionLimits).values({key,count:1,expires:now+600000}).onConflictDoUpdate({target:submissionLimits.key,set:{count:sql`${submissionLimits.count}+1`}}).returning();
  if(rate[0].count>8)return Response.json({error:'Terlalu banyak percobaan. Coba lagi dalam 10 menit.'},{status:429});
  await db.insert(preorders).values({id:crypto.randomUUID(),name:parsed.data.name,whatsapp:parsed.data.whatsapp,createdAt:new Date().toISOString(),consentVersion:'launch-updates-v1',price:39000,status:'registered'}).onConflictDoNothing({target:preorders.whatsapp});
  const row=await db.select().from(siteSettings).where(eq(siteSettings.key,'whatsapp_group')).get();
  return Response.json({ok:true,groupUrl:row?validGroupUrl(row.value):null},{status:201,headers:{'Cache-Control':'no-store'}});
 }catch{return Response.json({error:'Pendaftaran belum tersimpan. Silakan coba lagi.'},{status:503})}
}
