import {env} from 'cloudflare:workers';
import {getChatGPTUser} from '../app/chatgpt-auth';
import {voiceTextKey} from '../app/data/personalization';
import {customerSession,hasCustomerAccess} from './customer-auth';
export const voiceDb=()=> (env as unknown as {DB:D1Database}).DB;
export const voiceBucket=()=> (env as unknown as {AUDIO:R2Bucket}).AUDIO;
export async function voiceOwner(){const customer=await customerSession();if(customer){const link=await voiceDb().prepare('SELECT legacy_owner FROM voice_account_links WHERE customer_id=?').bind(customer.user.id).first<{legacy_owner:string}>();return link?.legacy_owner||voiceTextKey('supabase:'+customer.user.id);}const user=await getChatGPTUser();return user?voiceTextKey(user.userId):null}
export async function canSaveVoice(){const customer=await customerSession();return customer?hasCustomerAccess(customer):!!await getChatGPTUser();}
export const validVoiceLanguage=(value:string)=>['id','en','zh','ar'].includes(value);
export function audioMime(bytes:Uint8Array){const ascii=(start:number,end:number)=>String.fromCharCode(...bytes.slice(start,end));if(ascii(0,4)==='RIFF'&&ascii(8,12)==='WAVE')return 'audio/wav';if(ascii(0,4)==='OggS')return 'audio/ogg';if(ascii(4,8)==='ftyp')return 'audio/mp4';if(bytes[0]===0x1a&&bytes[1]===0x45&&bytes[2]===0xdf&&bytes[3]===0xa3)return 'audio/webm';if(ascii(0,3)==='ID3'||bytes[0]===0xff&&(bytes[1]&0xe0)===0xe0)return 'audio/mpeg';return null}
