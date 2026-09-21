import {env} from 'cloudflare:workers';
import {getChatGPTUser} from '../app/chatgpt-auth';
import {voiceTextKey} from '../app/data/personalization';
export const voiceDb=()=> (env as unknown as {DB:D1Database}).DB;
export const voiceBucket=()=> (env as unknown as {AUDIO:R2Bucket}).AUDIO;
export async function voiceOwner(){const user=await getChatGPTUser();return user?voiceTextKey(user.userId):null}
export const validVoiceLanguage=(value:string)=>['id','en','zh','ar'].includes(value);
export function audioMime(bytes:Uint8Array){const ascii=(start:number,end:number)=>String.fromCharCode(...bytes.slice(start,end));if(ascii(0,4)==='RIFF'&&ascii(8,12)==='WAVE')return 'audio/wav';if(ascii(0,4)==='OggS')return 'audio/ogg';if(ascii(4,8)==='ftyp')return 'audio/mp4';if(bytes[0]===0x1a&&bytes[1]===0x45&&bytes[2]===0xdf&&bytes[3]===0xa3)return 'audio/webm';if(ascii(0,3)==='ID3'||bytes[0]===0xff&&(bytes[1]&0xe0)===0xe0)return 'audio/mpeg';return null}
