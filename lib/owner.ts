import {env} from 'cloudflare:workers';
import {getChatGPTUser} from '../app/chatgpt-auth';
export async function isOwner(){const user=await getChatGPTUser();const owner=(env as unknown as Record<string,string>).LITTLEFINGER_OWNER_EMAIL;return !!(user&&owner&&user.email.toLowerCase()===owner.toLowerCase())}
