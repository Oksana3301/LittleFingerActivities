const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const project = require('path').resolve(__dirname,'..');
const ts = require(project + '/node_modules/typescript');
const file = project + '/app/components/device-voice.tsx';
const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS, target:ts.ScriptTarget.ES2020, jsx:ts.JsxEmit.ReactJSX}}).outputText;
const mkVoice=(name,lang,isDefault=false)=>({name,lang,default:isDefault,voiceURI:name,localService:true});
const david=mkVoice('Microsoft David','en-US',true), zira=mkVoice('Microsoft Zira','en-US');
const andika=mkVoice('Microsoft Andika','id-ID',true), gadis=mkVoice('Microsoft Gadis Online (Natural)','id-ID');

function harness(initial={}) {
 const slots=[];let index=0,dirty=false,effects=[],output;
 let settings={lang:'en',mute:false,voiceId:'auto',voiceRate:.86,...initial};
 let voices=[andika,david,gadis,zira];const calls=[];const timers=new Map();let timerId=0;
 const listeners=new Map(),docListeners=new Map();
 const equal=(a,b)=>a&&b&&a.length===b.length&&a.every((v,i)=>Object.is(v,b[i]));
 const react={
  useState(init){const i=index++;if(!(i in slots))slots[i]={v:typeof init==='function'?init():init};return[slots[i].v,v=>{const next=typeof v==='function'?v(slots[i].v):v;if(!Object.is(next,slots[i].v)){slots[i].v=next;dirty=true}}]},
  useRef(init){const i=index++;if(!(i in slots))slots[i]={current:init};return slots[i]},
  useCallback(fn,deps){const i=index++;if(!slots[i]||!equal(slots[i].deps,deps))slots[i]={v:fn,deps};return slots[i].v},
  useEffect(fn,deps){const i=index++;if(!slots[i]||!equal(slots[i].deps,deps)){const old=slots[i];slots[i]={deps,cleanup:old?.cleanup};effects.push(()=>{slots[i].cleanup?.();slots[i].cleanup=fn()})}}
 };
 const synth={getVoices:()=>voices,cancel(){calls.push({type:'cancel'})},speak(u){calls.push({type:'speak',u});if(synth.throwOnSpeak)throw Error('engine failure')},addEventListener:(n,f)=>listeners.set(n,f),removeEventListener:(n,f)=>{if(listeners.get(n)===f)listeners.delete(n)}};
 class Utterance {constructor(text){this.text=text}}
 const document={hidden:false,addEventListener:(n,f)=>docListeners.set(n,f),removeEventListener:(n,f)=>{if(docListeners.get(n)===f)docListeners.delete(n)}};
 const module={exports:{}};
 const context={module,exports:module.exports,require:n=>n==='react'?react:n==='react/jsx-runtime'?{}:n==='lucide-react'?{}:(()=>{throw Error('Unexpected import '+n)})(),window:{speechSynthesis:synth,SpeechSynthesisUtterance:Utterance},SpeechSynthesisUtterance:Utterance,document,setTimeout:(fn,ms)=>{const id=++timerId;timers.set(id,{fn,ms});return id},clearTimeout:id=>timers.delete(id)};
 vm.runInNewContext(compiled,context,{filename:file});
 function flush(){let runs=0;do{dirty=false;index=0;output=module.exports.useDeviceVoice(settings);const queue=effects;effects=[];queue.forEach(f=>f());assert(++runs<20,'hook render loop')}while(dirty);return output}
 flush();
 return {get hook(){return output},flush,settings:patch=>{settings={...settings,...patch};return flush()},batchSettings:patch=>{settings={...settings,...patch}},calls,synth,timers,
  latest:()=>calls.filter(x=>x.type==='speak').at(-1)?.u,
  fireTimers(){const pending=[...timers.values()];timers.clear();pending.forEach(x=>x.fn());flush()},
  voices(next){voices=next;listeners.get('voiceschanged')?.();flush()},
  hide(){document.hidden=true;docListeners.get('visibilitychange')?.();flush()},
  unmount(){slots.forEach(s=>s.cleanup?.())}
 };
}
let passed=0,total=0;
function test(name,fn){total++;try{fn();passed++;console.log('PASS '+name)}catch(e){console.error('FAIL '+name+'\n'+e.stack);process.exitCode=1}}

test('language first; known female preferred over male default',()=>{
 const h=harness();assert.equal(h.hook.selectedVoice,zira);assert.equal(h.hook.available.length,2);
 h.settings({lang:'id'});assert.equal(h.hook.selectedVoice,gadis);
 h.settings({lang:'en',voiceId:gadis.voiceURI});assert.equal(h.hook.selectedVoice,zira);
});
test('explicit matching-language override wins',()=>{
 const h=harness({voiceId:david.voiceURI});assert.equal(h.hook.selectedVoice,david);
 h.hook.say('Hello','a');h.flush();assert.equal(h.latest().voice,david);
});
test('per-option spoken language overrides settings language',()=>{
 const h=harness({voiceId:david.voiceURI});h.hook.say('Awan','indonesian-option','id');h.flush();
 assert.equal(h.latest().voice,gadis);assert.equal(h.latest().lang,'id-ID');
});
test('no matching installed language gives message, never wrong-language voice',()=>{
 const h=harness();h.voices([david,zira]);h.hook.say('Awan','id-option','id');h.flush();
 assert.equal(h.latest(),undefined);assert.equal(h.hook.activeKey,'');assert.match(h.hook.message,/Indonesia/);
});
test('manual play, same-control toggle, stop and ended-state cleanup',()=>{
 const h=harness();h.hook.say('Hello','a');h.flush();assert.equal(h.hook.activeKey,'a');assert.equal(h.latest().text,'Hello');
 h.latest().onstart();h.flush();assert.equal(h.hook.message,'Reading aloud…');assert.equal(h.timers.size,0);
 h.hook.say('Hello','a');h.flush();assert.equal(h.hook.activeKey,'');assert.equal(h.calls.filter(x=>x.type==='speak').length,1);
 h.hook.say('Second','b');h.flush();h.latest().onend();h.flush();assert.equal(h.hook.activeKey,'');assert.equal(h.hook.message,'');
});
test('manual unmute batched with play does not cancel new speech',()=>{
 const h=harness({mute:true});h.batchSettings({mute:false});h.hook.say('Hello','manual');h.flush();
 assert.equal(h.hook.activeKey,'manual');assert.equal(h.calls.at(-1).type,'speak');
 h.settings({mute:true});assert.equal(h.hook.activeKey,'');assert.equal(h.calls.at(-1).type,'cancel');
});
test('stale start/end/error cannot alter a newer utterance',()=>{
 const h=harness();h.hook.say('Old','old');h.flush();const old=h.latest();
 h.hook.say('New','new');h.flush();const current=h.latest();current.onstart();h.flush();
 old.onstart();old.onend();old.onerror({error:'network'});h.flush();
 assert.equal(h.hook.activeKey,'new');assert.equal(h.hook.message,'Reading aloud…');
});
test('genuine engine error clears active and gives recoverable message',()=>{
 const h=harness();h.hook.say('Hello','a');h.flush();h.latest().onerror({error:'synthesis-failed'});h.flush();
 assert.equal(h.hook.activeKey,'');assert.match(h.hook.message,/unavailable/);assert.equal(h.timers.size,0);
});
test('intentional cancel event clears active without error message',()=>{
 const h=harness();h.hook.say('Hello','a');h.flush();h.latest().onerror({error:'interrupted'});h.flush();
 assert.equal(h.hook.activeKey,'');assert.equal(h.hook.message,'');
});
test('startup timeout cancels synthesis, clears active and offers fallback',()=>{
 const h=harness();h.hook.say('Hello','a');h.flush();assert.equal([...h.timers.values()][0].ms,8000);const old=h.latest();
 h.fireTimers();assert.equal(h.hook.activeKey,'');assert.match(h.hook.message,/unavailable/);assert.equal(h.calls.at(-1).type,'cancel');
 old.onstart();h.flush();assert.match(h.hook.message,/unavailable/);
});
test('synchronous speak failure clears active and pending timer',()=>{
 const h=harness();h.synth.throwOnSpeak=true;h.hook.say('Hello','a');h.flush();
 assert.equal(h.hook.activeKey,'');assert.match(h.hook.message,/unavailable/);assert.equal(h.timers.size,0);
});
test('voiceschanged refreshes; language change, hidden tab and unmount stop speech',()=>{
 const h=harness();h.voices([david]);assert.equal(h.hook.selectedVoice,david);h.voices([david,zira]);assert.equal(h.hook.selectedVoice,zira);
 h.hook.say('Hello','a');h.flush();h.settings({lang:'id'});assert.equal(h.hook.activeKey,'');
 h.voices([gadis]);h.hook.say('Halo','b');h.flush();h.hide();assert.equal(h.hook.activeKey,'');
 h.hook.say('Halo','c');h.flush();h.unmount();assert.equal(h.calls.at(-1).type,'cancel');assert.equal(h.timers.size,0);
});


const kangkang=mkVoice('Microsoft Kangkang','zh-CN',true);
const xiaoxiao=mkVoice('Microsoft Xiaoxiao Online (Natural)','zh-CN');
const huihui=mkVoice('Microsoft Huihui','zh-CN');
const yaoyao=mkVoice('Microsoft Yaoyao','zh-CN');
const xiaoyi=mkVoice('Microsoft Xiaoyi Online (Natural)','zh-CN');
const tracy=mkVoice('Microsoft Tracy','zh-HK',true);
const cantonese=mkVoice('Cantonese','yue-CN',true);

test('audio language is independent from Indonesian UI language',()=>{
 const h=harness({lang:'id',audioLang:'en'});assert.equal(h.hook.selectedVoice,zira);
 h.hook.say('Hello','en');h.flush();assert.equal(h.latest().voice,zira);assert.equal(h.latest().lang,'en-US');
});
test('audio language is independent from English UI language',()=>{
 const h=harness({lang:'en',audioLang:'id'});assert.equal(h.hook.selectedVoice,gadis);
 h.hook.say('Halo','id');h.flush();assert.equal(h.latest().voice,gadis);assert.equal(h.latest().lang,'id-ID');
});
test('Mandarin audio language works with each UI language and chooses known female',()=>{
 for(const lang of ['id','en']){
  const h=harness({lang,audioLang:'zh'});h.voices([tracy,cantonese,kangkang,xiaoxiao,zira,gadis]);
  assert.equal(h.hook.selectedVoice,xiaoxiao);assert.equal(h.hook.available.length,2);
  h.hook.say('你好，小朋友。','zh');h.flush();assert.equal(h.latest().voice,xiaoxiao);assert.equal(h.latest().lang,'zh-CN');
 }
});
test('all four verified Mandarin female names override male default',()=>{
 for(const female of [huihui,yaoyao,xiaoxiao,xiaoyi]){
  const h=harness({audioLang:'zh'});h.voices([kangkang,female]);assert.equal(h.hook.selectedVoice,female);
 }
});
test('explicit Mandarin voice choice wins but explicit Cantonese choice is rejected',()=>{
 const h=harness({audioLang:'zh',voiceId:kangkang.voiceURI});h.voices([tracy,kangkang,xiaoxiao]);
 assert.equal(h.hook.selectedVoice,kangkang);h.settings({voiceId:tracy.voiceURI});assert.equal(h.hook.selectedVoice,xiaoxiao);
});
test('Mandarin accepts CN TW SG and cmn locale variants',()=>{
 for(const locale of ['zh-CN','zh-TW','zh-SG','zh-Hans-CN','zh-Hant-TW','cmn','cmn-CN','cmn-TW','zh_CN','ZH_hant_TW']){
  const h=harness({audioLang:'zh'}),mandarin=mkVoice('Mandarin '+locale,locale);h.voices([david,mandarin]);
  assert.equal(h.hook.selectedVoice,mandarin,locale);h.hook.say('你好','zh');h.flush();assert.equal(h.latest().voice,mandarin,locale);assert.equal(h.latest().lang,locale);
 }
});
test('Mandarin rejects Cantonese locales including script and extlang forms',()=>{
 for(const locale of ['zh-HK','zh-Hant-HK','zh-MO','zh-Hant-MO','yue','yue-HK','yue-CN','zh-yue','zh-yue-HK']){
  const h=harness({audioLang:'zh'}),wrong=mkVoice('Installed regional voice',locale,true);h.voices([wrong,david]);
  assert.equal(h.hook.available.length,0,locale);assert.equal(h.hook.selectedVoice,undefined,locale);
  h.hook.say('你好','zh');h.flush();assert.equal(h.latest(),undefined,locale);assert.ok(h.hook.message,locale);
 }
});
test('changing audio language cancels active speech and ignores old callbacks',()=>{
 const h=harness({lang:'en',audioLang:'en'});h.voices([zira,xiaoxiao]);h.hook.say('Hello','en');h.flush();const old=h.latest();
 h.settings({audioLang:'zh'});assert.equal(h.hook.activeKey,'');assert.equal(h.calls.at(-1).type,'cancel');assert.equal(h.timers.size,0);
 h.hook.say('你好','zh');h.flush();old.onstart();old.onend();old.onerror({error:'network'});h.flush();
 assert.equal(h.hook.activeKey,'zh');assert.equal(h.latest().voice,xiaoxiao);
});
test('changing UI language preserves independent selected audio language',()=>{
 const h=harness({lang:'en',audioLang:'zh'});h.voices([zira,xiaoxiao]);h.settings({lang:'id'});
 assert.equal(h.hook.selectedVoice,xiaoxiao);h.hook.say('你好','zh');h.flush();assert.equal(h.latest().voice,xiaoxiao);
});
test('explicit spoken language can override a Mandarin audio preference',()=>{
 const h=harness({lang:'id',audioLang:'zh'});h.voices([gadis,xiaoxiao]);h.hook.say('Halo','id','id');h.flush();
 assert.equal(h.latest().voice,gadis);assert.equal(h.latest().lang,'id-ID');
});

test('legacy Mandarin extlang and named bare Chinese voice are recognized',()=>{
 for(const locale of ['zh-cmn','zh-cmn-Hans-CN','zh-cmn-Hant-TW','zh','zh-Hans','zh-Hant']){
  const h=harness({audioLang:'zh'}),mandarin=mkVoice('Installed Mandarin voice',locale);h.voices([mandarin]);
  assert.equal(h.hook.selectedVoice,mandarin,locale);
 }
});
test('ambiguous bare Chinese voice and mislabeled Cantonese names are rejected',()=>{
 for(const [name,locale] of [['Chinese','zh'],['Chinese','zh-Hans'],['Chinese','zh-Hant'],['Cantonese','zh-CN'],['粵語','zh-TW'],['广东话','cmn-CN']]){
  const h=harness({audioLang:'zh'});h.voices([mkVoice(name,locale)]);assert.equal(h.hook.available.length,0,name+' '+locale);
 }
});
test('terminal disallowed locale components are rejected without relying on name',()=>{
 for(const locale of ['cmn-HK','cmn-MO','zh-cmn-Hant-HK','zh-cmn-Hant-MO']){
  const h=harness({audioLang:'zh'});h.voices([mkVoice('Installed Chinese voice',locale)]);assert.equal(h.hook.available.length,0,locale);
 }
});

const naayf=mkVoice('Microsoft Naayf','ar-SA',true);
const hamed=mkVoice('Microsoft Hamed Online (Natural)','ar-SA',true);
const shakir=mkVoice('Microsoft Shakir Online (Natural)','ar-EG',true);
const hoda=mkVoice('Microsoft Hoda','ar-EG');
const salma=mkVoice('Microsoft Salma Online (Natural)','ar-EG');
const zariyah=mkVoice('Microsoft Zariyah Online (Natural)','ar-SA');

test('Arabic audio stays independent of either UI language',()=>{
 for(const lang of ['en','id']){
  const h=harness({lang,audioLang:'ar'});h.voices([david,gadis,naayf,hoda]);
  assert.equal(h.hook.selectedVoice,hoda);assert.equal(h.hook.available.length,2);
  h.hook.say('مرحبًا يا صغيري.','arabic');h.flush();
  assert.equal(h.latest().text,'مرحبًا يا صغيري.');assert.equal(h.latest().voice,hoda);assert.equal(h.latest().lang,'ar-EG');
  h.settings({lang:lang==='en'?'id':'en'});assert.equal(h.hook.selectedVoice,hoda);assert.equal(h.hook.activeKey,'arabic');
 }
});
test('all verified Arabic female names beat Naayf Hamed and Shakir defaults',()=>{
 const females=[['Hoda','ar-EG'],['Salma','ar-EG'],['Zariyah','ar-SA'],['Fatima','ar-AE'],['Laila','ar-BH'],['Amina','ar-DZ'],['Rana','ar-IQ'],['Sana','ar-JO'],['Noura','ar-KW'],['Layla','ar-LB'],['Iman','ar-LY'],['Mouna','ar-MA'],['Aysha','ar-OM'],['Amal','ar-QA'],['Amany','ar-SY'],['Reem','ar-TN'],['Maryam','ar-YE']];
 for(const [name,locale] of females)for(const male of [naayf,hamed,shakir])for(const label of [`Microsoft ${name} Online (Natural)`,`${locale}-${name}Neural`]){
  const female=mkVoice(label,locale),h=harness({audioLang:'ar'});h.voices([male,female]);
  assert.equal(h.hook.selectedVoice,female,`${label} vs ${male.name}`);
 }
});
test('female-name fragments in unrelated names do not override Arabic male default',()=>{
 for(const name of ['Mohoda','Salman','Fatimah','Kamal','Reemington','Nouran','Zakaria']){
  const h=harness({audioLang:'ar'}),unknown=mkVoice(name,'ar-SA');h.voices([unknown,naayf]);
  assert.equal(h.hook.selectedVoice,naayf,name);
 }
});
test('Arabic recognizes regional and script variants and retains exact selected voice locale',()=>{
 for(const locale of ['ar','ar-EG','ar-SA','ar-AE','ar-BH','ar-DZ','ar-IQ','ar-JO','ar-KW','ar-LB','ar-LY','ar-MA','ar-OM','ar-QA','ar-SY','ar-TN','ar-YE','ar-Arab-EG','ar-EG-u-nu-arab','ar_EG','AR_sa']){
  const h=harness({audioLang:'ar'}),regional=mkVoice('Installed Arabic '+locale,locale);h.voices([zira,regional]);
  assert.equal(h.hook.selectedVoice,regional,locale);assert.equal(h.hook.available.length,1);
  h.hook.say('أرنب','arabic');h.flush();assert.equal(h.latest().voice,regional,locale);assert.equal(h.latest().lang,locale);
 }
});
test('explicit Arabic male or female override wins across regional variants',()=>{
 for(const chosen of [naayf,hamed,shakir,hoda,salma,zariyah]){
  const h=harness({audioLang:'ar',voiceId:chosen.voiceURI});h.voices([naayf,hamed,shakir,hoda,salma,zariyah]);
  assert.equal(h.hook.selectedVoice,chosen);h.hook.say('اختر صورة.','arabic');h.flush();
  assert.equal(h.latest().voice,chosen);assert.equal(h.latest().lang,chosen.lang);
 }
});
test('wrong-language explicit voice and familiar names never escape Arabic filtering',()=>{
 const fakeHoda=mkVoice('Microsoft Hoda','en-US',true);
 const h=harness({audioLang:'ar',voiceId:fakeHoda.voiceURI});h.voices([fakeHoda,david,salma]);
 assert.equal(h.hook.selectedVoice,salma);h.hook.say('تفاحة','arabic');h.flush();assert.equal(h.latest().voice,salma);
});
test('unavailable Arabic provides UI-language message and never speaks wrong language',()=>{
 for(const lang of ['en','id']){
  const h=harness({lang,audioLang:'ar'});h.voices([david,gadis,xiaoxiao]);h.hook.say('تفاحة','arabic');h.flush();
  assert.equal(h.hook.available.length,0);assert.equal(h.hook.selectedVoice,undefined);assert.equal(h.latest(),undefined);
  assert.equal(h.hook.activeKey,'');assert.equal(h.timers.size,0);assert.match(h.hook.message,lang==='en'?/Arabic voice is not available/:/Suara Arab belum tersedia/);
 }
 for(const locale of ['fa-IR','ur-PK','arc','arn-CL','en-Arab','arb']){
  const h=harness({audioLang:'ar'});h.voices([mkVoice('Arabic sounding voice',locale,true)]);h.hook.say('تفاحة','arabic');h.flush();
  assert.equal(h.latest(),undefined,locale);
 }
});
test('empty asynchronous voice list requests Arabic locale without choosing wrong voice',()=>{
 const h=harness({audioLang:'ar'});h.voices([]);h.hook.say('أرنب','arabic');h.flush();
 assert.equal(h.latest().voice,undefined);assert.equal(h.latest().lang,'ar-SA');
 h.voices([naayf,salma]);assert.equal(h.hook.selectedVoice,salma);
});
test('switching into and out of Arabic cancels old speech and ignores stale callbacks',()=>{
 const h=harness({audioLang:'en'});h.voices([zira,salma]);h.hook.say('Hello','en');h.flush();const en=h.latest();
 h.settings({audioLang:'ar'});assert.equal(h.hook.activeKey,'');assert.equal(h.calls.at(-1).type,'cancel');assert.equal(h.timers.size,0);
 h.hook.say('مرحبًا','ar');h.flush();const ar=h.latest();ar.onstart();h.flush();
 en.onstart();en.onend();en.onerror({error:'network'});h.flush();assert.equal(h.hook.activeKey,'ar');assert.equal(h.latest().lang,'ar-EG');
 h.settings({audioLang:'en'});assert.equal(h.hook.activeKey,'');assert.equal(h.calls.at(-1).type,'cancel');
 h.hook.say('Again','en2');h.flush();ar.onstart();ar.onend();ar.onerror({error:'network'});h.flush();
 assert.equal(h.hook.activeKey,'en2');assert.equal(h.latest().voice,zira);
});
test('changing Arabic voice cancels pending utterance and keeps new regional locale',()=>{
 const h=harness({audioLang:'ar',voiceId:salma.voiceURI});h.voices([salma,zariyah]);h.hook.say('تفاحة','eg');h.flush();const eg=h.latest();
 h.settings({voiceId:zariyah.voiceURI});assert.equal(h.hook.activeKey,'');assert.equal(h.calls.at(-1).type,'cancel');assert.equal(h.timers.size,0);
 h.hook.say('أرنب','sa');h.flush();eg.onstart();eg.onend();eg.onerror({error:'network'});h.flush();
 assert.equal(h.hook.activeKey,'sa');assert.equal(h.latest().voice,zariyah);assert.equal(h.latest().lang,'ar-SA');
});
test('per-option Arabic and non-Arabic spoken overrides remain independent',()=>{
 const h=harness({lang:'id',audioLang:'en',voiceId:david.voiceURI});h.voices([david,gadis,naayf,salma]);
 h.hook.say('تفاحة','ar','ar');h.flush();assert.equal(h.latest().voice,salma);assert.equal(h.latest().lang,'ar-EG');
 h.settings({audioLang:'ar',voiceId:salma.voiceURI});h.hook.say('Halo','id','id');h.flush();assert.equal(h.latest().voice,gadis);assert.equal(h.latest().lang,'id-ID');
});
console.log(`${passed}/${total} checks passed against actual transpiled useDeviceVoice source.`);
