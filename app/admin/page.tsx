import {getChatGPTUser,chatGPTSignInPath} from '../chatgpt-auth';
import {isOwner} from '../../lib/owner';
import AdminPreorders from '../components/admin-preorders';
export const dynamic='force-dynamic';
export default async function AdminPage(){const user=await getChatGPTUser();if(!user)return <main className="lf-admin"><h1>Pengelola Littlefinger</h1><p>Masuk dengan akun pemilik untuk melihat pendaftar dan mengatur grup WhatsApp.</p><a className="lf-primary" target="_top" href={chatGPTSignInPath('/admin')}>Masuk dengan ChatGPT</a><a href="/preorder">Kembali ke preorder</a></main>;if(!await isOwner())return <main className="lf-admin"><h1>Akses khusus pemilik</h1><p>Akun ini tidak memiliki akses ke data pendaftar.</p><a href="/preorder">Kembali ke preorder</a></main>;return <AdminPreorders/>}
