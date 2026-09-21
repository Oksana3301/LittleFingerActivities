import {voiceDb,voiceBucket,voiceOwner,validVoiceLanguage,audioMime,canSaveVoice} from '../../../lib/parent-voice';
import {normalizeVoiceText,voiceTextKey} from '../../data/personalization';
const headers={'Cache-Control':'private, no-store'};
const fail=(error:string,status:number)=>Response.json({error},{status,headers});
export async function GET(request:Request){
 const owner=await voiceOwner();if(!owner)return fail('Masuk untuk menggunakan rekaman pribadi.',401);
 const q=new URL(request.url).searchParams,language=q.get('lang')||'id';if(!validVoiceLanguage(language))return fail('Bahasa tidak sesuai.',400);
 try{const db=voiceDb();if(q.get('list')==='1'){const {results}=await db.prepare('SELECT text_key AS key, transcript AS text, language, updated_at AS updatedAt, bytes FROM voice_recordings WHERE owner = ? AND language = ? ORDER BY updated_at DESC LIMIT 2000').bind(owner,language).all();return Response.json({recordings:results},{headers})}
 const key=q.get('key')||'';if(!/^[a-f0-9]{64}$/.test(key))return fail('Rekaman tidak ditemukan.',404);
 const row=await db.prepare('SELECT object_key FROM voice_recordings WHERE id = ? AND owner = ?').bind(owner+'/'+language+'/'+key,owner).first<{object_key:string}>();if(!row)return fail('Belum ada rekaman.',404);
 const object=await voiceBucket().get(row.object_key);if(!object)return fail('Rekaman belum tersedia.',404);
 return new Response(object.body,{headers:{...headers,'Content-Type':object.httpMetadata?.contentType||'audio/webm','X-Content-Type-Options':'nosniff','Content-Disposition':'inline'}});
 }catch{return fail('Rekaman belum dapat dimuat. Coba lagi.',503)}
}
export async function PUT(request:Request){
 const owner=await voiceOwner();if(!owner)return fail('Masuk untuk menyimpan rekaman pribadi.',401);
 if(!await canSaveVoice())return fail('Aktifkan akses untuk menyimpan rekaman baru.',403);
 if(request.headers.get('origin')!==new URL(request.url).origin)return fail('Buka rekaman dari Littlefinger.',403);
 if(Number(request.headers.get('content-length')||0)>5_500_000)return fail('Maksimal 5 MB per rekaman.',413);
 try{const reader=request.body?.getReader();if(!reader)return fail('Audio belum dikirim.',400);const chunks:Uint8Array[]=[];let size=0;while(true){const part=await reader.read();if(part.done)break;size+=part.value.length;if(size>5_500_000){await reader.cancel();return fail('Maksimal 5 MB per rekaman.',413)}chunks.push(part.value)}const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length}const form=await new Response(bytes,{headers:{'Content-Type':request.headers.get('content-type')||''}}).formData(),file=form.get('audio'),language=String(form.get('lang')||''),text=normalizeVoiceText(String(form.get('text')||''));
 if(!(file instanceof File)||file.size<32||file.size>5_000_000||!validVoiceLanguage(language)||!text||text.length>1200)return fail('Periksa bahasa, kalimat, dan file audio (maksimal 5 MB).',400);
 const data=await file.arrayBuffer(),mime=audioMime(new Uint8Array(data));if(!mime)return fail('Gunakan audio WAV, MP3, M4A, OGG, atau WebM.',415);
 const db=voiceDb(),key=await voiceTextKey(text),id=owner+'/'+language+'/'+key,objectKey='voices/'+id+'/'+crypto.randomUUID();
 const existing=await db.prepare('SELECT id, bytes, object_key FROM voice_recordings WHERE id = ? AND owner = ?').bind(id,owner).first<{id:string;bytes:number;object_key:string}>();
 {const total=await db.prepare('SELECT count(*) AS n, coalesce(sum(bytes),0) AS size FROM voice_recordings WHERE owner = ?').bind(owner).first<{n:number;size:number}>();if(total&&((!existing&&total.n>=2000)||total.size-(existing?.bytes||0)+file.size>250_000_000))return fail('Koleksi rekaman penuh. Hapus rekaman yang tidak dipakai.',409)}
 await voiceBucket().put(objectKey,data,{httpMetadata:{contentType:mime}});
 try{await db.prepare('INSERT INTO voice_recordings (id,owner,language,text_key,transcript,object_key,mime,bytes,updated_at) VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET transcript=excluded.transcript,object_key=excluded.object_key,mime=excluded.mime,bytes=excluded.bytes,updated_at=excluded.updated_at').bind(id,owner,language,key,text,objectKey,mime,file.size,new Date().toISOString()).run()}catch(error){await voiceBucket().delete(objectKey).catch(()=>{});throw error}
 if(existing?.object_key)await voiceBucket().delete(existing.object_key).catch(()=>{});
 return Response.json({ok:true,key},{headers});
 }catch{return fail('Rekaman belum tersimpan. Silakan coba lagi.',503)}
}
export async function DELETE(request:Request){
 const owner=await voiceOwner();if(!owner)return fail('Masuk untuk mengelola rekaman.',401);
 if(request.headers.get('origin')!==new URL(request.url).origin)return fail('Permintaan tidak sesuai.',403);
 try{const {lang,key}=await request.json() as {lang:string;key:string};if(!validVoiceLanguage(lang)||!/^[a-f0-9]{64}$/.test(key))return fail('Rekaman tidak sesuai.',400);const id=owner+'/'+lang+'/'+key;const row=await voiceDb().prepare('DELETE FROM voice_recordings WHERE id = ? AND owner = ? RETURNING object_key').bind(id,owner).first<{object_key:string}>();if(row)await voiceBucket().delete(row.object_key);return Response.json({ok:true},{headers})}catch{return fail('Rekaman belum terhapus.',503)}
}
