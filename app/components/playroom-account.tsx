'use client';
import {useEffect,useState} from 'react';
import {loadAccount,signedOut,type AccountOverview} from '../../lib/customer-client';
import Playroom from '../playroom';
export default function PlayroomAccount(){
 const [account,setAccount]=useState<AccountOverview>(signedOut),[ready,setReady]=useState(false),[error,setError]=useState(''),[childId,setChildId]=useState('');
 useEffect(()=>{
  setChildId(new URLSearchParams(location.search).get('child')||'');let cancelled=false;
  const sync=async()=>{try{const data=await loadAccount();if(!cancelled){setAccount(data);setError('');}}catch{if(!cancelled){setAccount(previous=>({...previous,access:false}));setError('Akun belum dapat diperiksa. Contoh gratis tetap tersedia; coba muat ulang untuk membuka akses akun.');}}finally{if(!cancelled)setReady(true);}};
  void sync();const timer=setInterval(sync,60000);window.addEventListener('focus',sync);return()=>{cancelled=true;clearInterval(timer);window.removeEventListener('focus',sync);};
 },[]);
 if(!ready)return <main className="lf-account-loading"><p>Membuka ruang bermain…</p></main>;
 const child=account.children.find(c=>c.id===childId)||account.children[0]||null;
 return <>{error&&<p className="storage-notice" role="alert">{error}</p>}<Playroom key={(account.user?.id||'guest')+':'+(child?.id||'none')} account={account} child={child}/></>;
}
