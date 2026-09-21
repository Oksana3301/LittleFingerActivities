import {getChatGPTUser,chatGPTSignInPath} from '../chatgpt-auth';
import ParentVoiceLibrary from '../components/parent-voice';
export const dynamic='force-dynamic';
export default async function ParentVoicePage(){const user=await getChatGPTUser();if(!user)return <main className="parent-voice-library"><h1>Suara orang tua</h1><p>Masuk untuk menyimpan dan mendengarkan rekaman pribadi.</p><a className="finish-button" href={chatGPTSignInPath('/parent-voice')} target="_top">Masuk dengan ChatGPT</a><a className="text-button" href="/">Kembali bermain</a></main>;return <ParentVoiceLibrary/>}
