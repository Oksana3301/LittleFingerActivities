import {getChatGPTUser,chatGPTSignInPath} from '../chatgpt-auth';
import {customerSession} from '../../lib/customer-auth';
import ParentVoiceLibrary from '../components/parent-voice';
import VoiceAccountLink from '../components/voice-account-link';
export const dynamic='force-dynamic';
export default async function ParentVoicePage(){const [user,customer]=await Promise.all([getChatGPTUser(),customerSession()]);if(!user&&!customer)return <main className="parent-voice-library"><h1>Suara orang tua</h1><p>Masuk untuk menyimpan dan mendengarkan rekaman pribadi.</p><a className="finish-button" href="/login">Masuk dengan email</a><a className="text-button" href={chatGPTSignInPath('/parent-voice')} target="_top">Buka rekaman lama dengan ChatGPT</a><a className="text-button" href="/">Kembali bermain</a></main>;return <>{customer&&user?<VoiceAccountLink/>:customer?<div className="lf-voice-link"><a className="text-button" target="_top" href={chatGPTSignInPath('/parent-voice')}>Masuk ke ChatGPT untuk mengaitkan rekaman lama</a></div>:null}<ParentVoiceLibrary/></>;}
