const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const project = require('path').resolve(__dirname,'..');
const ts = require(project + '/node_modules/typescript');
const file = project + '/app/components/narration.tsx';
const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.ReactJSX}}).outputText;
const label={en:'Apple',id:'Apel'};
const textContent=node=>node==null||node===false?'':typeof node==='string'?node:Array.isArray(node)?node.map(textContent).join(''):typeof node==='object'?textContent(node.props?.children):String(node);
function find(node,type){if(!node||typeof node!=='object')return; if(node.type===type)return node; for(const child of [node.props?.children].flat(Infinity)){const result=find(child,type);if(result)return result}}

function harness(initial={}){
 const slots=[];let index=0,dirty=false,effects=[],output;
 let settings={lang:'en',audioLang:'ar',mute:false,...initial};
 const requests=[],spoken=[],muted=[];
 const equal=(a,b)=>a&&b&&a.length===b.length&&a.every((v,i)=>Object.is(v,b[i]));
 const react={
  useState(init){const i=index++;if(!(i in slots))slots[i]={v:typeof init==='function'?init():init};return[slots[i].v,v=>{const next=typeof v==='function'?v(slots[i].v):v;if(!Object.is(next,slots[i].v)){slots[i].v=next;dirty=true}}]},
  useEffect(fn,deps){const i=index++;if(!slots[i]||!equal(slots[i].deps,deps)){const old=slots[i];slots[i]={deps,cleanup:old?.cleanup};effects.push(()=>{slots[i].cleanup?.();slots[i].cleanup=fn()})}}
 };
 const jsx=(type,props)=>({type,props});
 const voice={activeKey:'',message:'',say:(text,key,lang)=>spoken.push({text,key,lang}),stop:()=>{},available:[]};
 const fetch=url=>new Promise((resolve,reject)=>requests.push({url,resolve,reject,done:false}));
 const module={exports:{}};
 vm.runInNewContext(compiled,{module,exports:module.exports,fetch,require:name=>name==='react'?react:name==='react/jsx-runtime'?{jsx,jsxs:jsx,Fragment:'Fragment'}:name==='lucide-react'?{Square:'Square',Volume2:'Volume2'}:name==='./device-voice'?{useDeviceVoice:()=>voice}:(()=>{throw Error('Unexpected import '+name)})()},{filename:file});
 function flush(){let runs=0;do{dirty=false;index=0;output=module.exports.useNarration(settings,value=>muted.push(value));const queue=effects;effects=[];queue.forEach(effect=>effect());assert(++runs<20,'hook render loop')}while(dirty);return output}
 flush();
 return {
  get hook(){return output},flush,requests,spoken,muted,
  settings(patch){settings={...settings,...patch};return flush()},
  async settle(){await new Promise(setImmediate);return flush()},
  answer(lang,data,ok=true){const path='/audio/'+(lang==='ar'?'arabic':'mandarin')+'.json';const request=requests.find(r=>r.url===path&&!r.done);assert.ok(request,'pending request '+path);request.done=true;request.resolve({ok,json:()=>Promise.resolve(data)})},
  reject(lang){const path='/audio/'+(lang==='ar'?'arabic':'mandarin')+'.json';const request=requests.find(r=>r.url===path&&!r.done);assert.ok(request);request.done=true;request.reject(Error('network'))},
  unmount(){slots.forEach(slot=>slot.cleanup?.())}
 };
}

const tests=[];const test=(name,fn)=>tests.push({name,fn});
test('Arabic loading never uses visible English or Indonesian text as audio fallback',async()=>{
 for(const lang of ['en','id']){
  const h=harness({lang,mute:true});assert.equal(h.hook.text(label),'');assert.equal(h.hook.audio(label,'apple').props.disabled,true);
  h.hook.play(label,'apple');h.flush();assert.equal(h.spoken.length,0);assert.equal(h.muted.length,0);
  h.answer('ar',{Apple:'تفاحة'});await h.settle();h.hook.play(label,'apple');h.flush();
  assert.equal(h.spoken[0].text,'تفاحة');assert.equal(h.spoken[0].lang,'ar');assert.equal(h.muted[0],false);
  assert.equal(h.hook.textLang,'ar');assert.equal(h.hook.textDirection,'rtl');
 }
});
test('cached Arabic and Mandarin switch synchronously without stale dictionary text',async()=>{
 const h=harness();h.answer('ar',{Apple:'تفاحة'});await h.settle();assert.equal(h.hook.text(label),'تفاحة');
 h.settings({audioLang:'zh'});assert.equal(h.hook.text(label),'');assert.equal(h.hook.audio(label,'apple').props.disabled,true);
 h.answer('zh',{Apple:'苹果'});await h.settle();assert.equal(h.hook.text(label),'苹果');
 h.settings({audioLang:'ar'});assert.equal(h.hook.text(label),'تفاحة');assert.equal(h.hook.textDirection,'rtl');
 h.settings({audioLang:'zh'});assert.equal(h.hook.text(label),'苹果');assert.equal(h.hook.textDirection,'ltr');
 await h.settle();assert.equal(h.requests.length,2);
});
test('late Arabic response cannot overwrite the current Mandarin dictionary',async()=>{
 const h=harness();h.settings({audioLang:'zh'});h.answer('zh',{Apple:'苹果'});await h.settle();
 h.answer('ar',{Apple:'تفاحة'});await h.settle();assert.equal(h.hook.text(label),'苹果');assert.equal(h.hook.textLang,'zh-CN');
 h.hook.play(label,'apple');assert.equal(h.spoken.at(-1).lang,'zh');assert.equal(h.spoken.at(-1).text,'苹果');
 h.settings({audioLang:'ar'});await h.settle();assert.equal(h.hook.text(label),'تفاحة');assert.equal(h.requests.length,2);
});
test('late Mandarin response cannot overwrite Arabic and rapid switching deduplicates requests',async()=>{
 const h=harness({audioLang:'zh'});h.settings({audioLang:'ar'});h.settings({audioLang:'zh'});h.settings({audioLang:'ar'});assert.equal(h.requests.length,2);
 h.answer('ar',{Apple:'تفاحة'});await h.settle();h.answer('zh',{Apple:'苹果'});await h.settle();
 assert.equal(h.hook.text(label),'تفاحة');h.hook.play(label,'apple');assert.equal(h.spoken.at(-1).text,'تفاحة');
 assert.equal(h.spoken.at(-1).lang,'ar');
});
test('obsolete translation failure does not replace the active language status',async()=>{
 const h=harness();h.settings({audioLang:'zh'});h.reject('ar');await h.settle();
 assert.match(textContent(h.hook.status),/Preparing Mandarin/);assert.doesNotMatch(textContent(h.hook.status),/Arabic|could not load/);
 h.answer('zh',{Apple:'苹果'});await h.settle();assert.equal(h.hook.text(label),'苹果');
 h.settings({audioLang:'ar'});assert.equal(h.requests.length,3);h.answer('ar',{Apple:'تفاحة'});await h.settle();assert.equal(h.hook.text(label),'تفاحة');
});
test('current-language failure offers retry and successful retry enables Arabic audio',async()=>{
 const h=harness();h.answer('ar',{},false);await h.settle();assert.match(textContent(h.hook.status),/Arabic text could not load/);
 const retry=find(h.hook.status,'button');assert.ok(retry);retry.props.onClick();h.flush();assert.equal(h.requests.length,2);
 h.answer('ar',{Apple:'تفاحة'});await h.settle();assert.equal(h.hook.audio(label,'apple').props.disabled,false);
 h.hook.play(label,'apple');assert.equal(h.spoken.at(-1).text,'تفاحة');
});
test('explicit Arabic is immediately usable and missing dictionary entry never speaks English',async()=>{
 const h=harness();const explicit={...label,ar:'تفاحة مباشرة'};assert.equal(h.hook.text(explicit),'تفاحة مباشرة');assert.equal(h.hook.audio(explicit,'apple').props.disabled,false);
 h.hook.play(explicit,'apple');assert.equal(h.spoken.at(-1).text,'تفاحة مباشرة');
 h.answer('ar',{});await h.settle();h.hook.play(label,'missing');h.flush();assert.equal(h.spoken.length,1);assert.match(textContent(h.hook.status),/Audio text is unavailable/);
 h.settings({audioLang:'en'});assert.equal(h.hook.text(label),'Apple');assert.equal(h.hook.translated,false);assert.equal(h.hook.textDirection,'ltr');
 h.settings({audioLang:'id'});assert.equal(h.hook.text(label),'Apel');
});
test('unmount prevents late translation response from updating hook state',async()=>{
 const h=harness();h.unmount();h.answer('ar',{Apple:'تفاحة'});await h.settle();assert.equal(h.hook.text(label),'');
});

(async()=>{let passed=0;for(const {name,fn} of tests){try{await fn();passed++;console.log('PASS '+name)}catch(error){console.error('FAIL '+name+'\n'+error.stack);process.exitCode=1}}console.log(`${passed}/${tests.length} checks passed against actual transpiled useNarration source.`)})();
