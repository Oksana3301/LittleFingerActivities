/* Live BFF/Supabase integration. Requires two disposable confirmed test users.
 * Usage: node scripts/verify-customer-live.cjs FIXTURE_JSON pending|active|expired
 * FIXTURE_JSON: [{id,email,password}, ...]. Only lf-qa-* @example.invalid accepted.
 * Supply credentials outside the repo; .state is private temporary test output.
 * Between phases, a database operator activates/expires ONLY the first fixture.
 * Clean both Auth users and temporary files after testing. Sends no emails.
 * HTTP Request/Response and real Auth/REST are exercised; Next cookies and D1
 * are host adapters, and content loading substitutes Vite's import.meta.glob.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const ts=require('typescript');
const {DatabaseSync}=require('node:sqlite');
// Some managed runtimes expose the network proxy to Python but not Node fetch.
// This optional transport still calls real HTTPS endpoints; it does not stub Auth.
if(process.env.LF_TEST_HTTP==='python'){
 const {spawn}=require('node:child_process');
 global.fetch=(url,options={})=>new Promise((resolve,reject)=>{
  const script="import sys,json,urllib.request,urllib.error\nv=json.load(sys.stdin)\nr=urllib.request.Request(v['url'],data=v.get('body','').encode() if v.get('body') is not None else None,headers=v['headers'],method=v['method'])\ntry:\n p=urllib.request.urlopen(r,timeout=20)\nexcept urllib.error.HTTPError as e:\n p=e\nprint(json.dumps({'status':p.status,'headers':dict(p.headers),'body':p.read().decode()}))";
  const child=spawn('python',['-c',script],{stdio:['pipe','pipe','pipe']});let out='';const timeout=setTimeout(()=>child.kill(),30000);if(process.env.LF_TEST_TRACE)console.log('HTTPS',options.method||'GET',new URL(url).pathname);
  child.stdout.on('data',b=>{out+=b;});child.stderr.resume();child.on('error',reject);
  child.on('close',code=>{clearTimeout(timeout);if(code)return reject(new Error('HTTPS test transport failed'));try{const r=JSON.parse(out);resolve(new Response(r.status===204?null:r.body,{status:r.status,headers:r.headers}));}catch(e){reject(e);}});
  child.stdin.end(JSON.stringify({url:String(url),method:options.method||'GET',headers:options.headers||{},body:options.body}));
 });
}
const root=path.resolve(__dirname,'..');
const fixturePath=process.argv[2],phase=process.argv[3];
assert(fixturePath&&['pending','active','expired'].includes(phase),'fixture file and phase required');
const fixtures=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
assert(fixtures.length===2&&fixtures.every(x=>/^lf-qa-[a-f0-9]+@example\.invalid$/.test(x.email)),'disposable QA fixtures only');
const statePath=fixturePath+'.state';
const state=fs.existsSync(statePath)?JSON.parse(fs.readFileSync(statePath,'utf8')):{jars:[{},{}],child:null};
const env=Object.fromEntries(fs.readFileSync(path.join(root,'.env.local'),'utf8').split('\n').filter(x=>x&&!x.startsWith('#')&&x.includes('=')).map(x=>[x.slice(0,x.indexOf('=')),x.slice(x.indexOf('=')+1)]));
env.CUSTOMER_EMAIL_READY='false';
const sqlite=new DatabaseSync(':memory:');
for(const file of fs.readdirSync(path.join(root,'drizzle')).filter(x=>x.endsWith('.sql')).sort())sqlite.exec(fs.readFileSync(path.join(root,'drizzle',file),'utf8'));
env.DB={prepare(sql){const statement=sqlite.prepare(sql);let values=[];return{bind(...v){values=v;return this;},async first(){return statement.get(...values)||null;},async run(){return{success:true,meta:statement.run(...values)};}};}};
let jar={};
const cookies={cookies:async()=>({get:name=>jar[name]?{value:jar[name]}:undefined})};
function load(file,imports){
 const source=fs.readFileSync(path.join(root,file),'utf8').replaceAll('import.meta.env.DEV','false');
 const compiled=ts.transpileModule(source,{fileName:file,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 const module={exports:{}};vm.runInThisContext('(function(require,module,exports){'+compiled+'\n})',{filename:file})(name=>{assert(Object.hasOwn(imports,name),'dependency '+name);return imports[name];},module,module.exports);return module.exports;
}
const connection=load('lib/supabase/connection.ts',{'server-only':{},'cloudflare:workers':{env}});
const helper=load('lib/customer-auth.ts',{'server-only':{},'cloudflare:workers':{env},'next/headers':cookies,'./supabase/connection':connection});
const common={'../../../../lib/customer-auth':helper,zod:require('zod')};
const auth=load('app/api/auth/[action]/route.ts',{...common,'../../../../lib/preorder':load('lib/preorder.ts',{zod:require('zod')})});
const account=load('app/api/account/[action]/route.ts',common);
const admin=load('app/api/account-admin/[action]/route.ts',common);
const access=load('app/data/access.ts',{});
const content={worksheetCategory:async id=>/^[a-z0-9-]{1,100}$/.test(id)&&fs.existsSync(path.join(root,'content/worksheets',id+'.json'))?JSON.parse(fs.readFileSync(path.join(root,'content/worksheets',id+'.json'),'utf8')):null,legacyActivity:id=>JSON.parse(fs.readFileSync(path.join(root,'content/activities.json'),'utf8')).find(x=>x.id===id)};
const worksheets=load('app/api/worksheets/[category]/route.ts',{...common,'../../../../lib/worksheet-content':content,'../../../data/access':access});
const legacy=load('app/api/legacy/[id]/route.ts',{...common,'../../../../lib/worksheet-content':content});
const finish=load('app/auth/finish/route.ts',{'../../../lib/customer-auth':helper});
const origin='https://littlefinger.example';
async function call(route,method,action,body={},status=200,options={}){
 const request=new Request(origin+(options.path||'/api/test'),{method,headers:{Origin:options.origin||origin,'Content-Type':'application/json'},...(method==='GET'?{}:{body:JSON.stringify(body)})});
 const response=await route[method](request,{params:Promise.resolve(options.params||{action})});
 assert.equal(response.status,status,action+' status; '+await response.clone().text());
 assert.match(response.headers.get('cache-control')||'',/no-store/);
 for(const cookie of response.headers.getSetCookie()){
  assert.match(cookie,/HttpOnly/);assert.match(cookie,/SameSite=Lax/);assert.match(cookie,/Secure/);assert.match(cookie,/^__Host-/);
  const pair=cookie.split(';')[0],i=pair.indexOf('=');jar[pair.slice(0,i)]=decodeURIComponent(pair.slice(i+1));
 }
 if(response.status===303)return response;
 const result=await response.json();assert(!JSON.stringify(result).includes('access_token'),'no tokens in response body');return result;
}
const workbook=()=>({child:state.child,revision:0,payload:{family:{settings:{nickname:'QA child'},observations:[]},book:{progress:{},favorites:[],last:'activity/telur-dan-hewan'},learning:{version:1,events:[],previous:[]}}});
async function category(id,status){return call(worksheets,'GET',id,{},status,{params:{category:id}});}
(async()=>{
 if(phase==='pending'){
  jar={};assert.equal((await call(auth,'GET','session')).user,null);
  assert.equal((await category('count-to-5',200)).length,1);
  await category('planet-names',403);await category('../activities',404);
  await call(legacy,'GET','legacy',{},401,{params:{id:'example'}});
  await call(auth,'POST','login',{},403,{origin:'https://foreign.example'});
  await call(auth,'POST','register',{},503);
  await call(finish,'GET','callback',{},303,{path:'/auth/finish?code=bad'});
  for(let i=0;i<2;i++){
   jar=state.jars[i];await call(auth,'POST','login',{email:fixtures[i].email,password:fixtures[i].password});
   const overview=await call(auth,'GET','session');assert.equal(overview.user.id,fixtures[i].id);assert.equal(overview.account.admin_role,false);assert.equal(overview.access,false);
  }
  jar=state.jars[0];const child=await call(account,'POST','child',{name:'QA child',age:'3-4',language:'id'},201);state.child=child.id;
  assert.equal((await call(account,'GET','workbook',{},200,{path:'/api/account/workbook?child='+state.child})).revision,0);
  await call(account,'POST','workbook',workbook(),403);
  await call(account,'POST','request',{},201);assert.equal((await call(account,'POST','request')).existing,true);
  await call(admin,'GET','customers',{},403);
  jar=state.jars[1];await call(account,'GET','workbook',{},404,{path:'/api/account/workbook?child='+state.child});
  console.log('PASS pending: real password login; secure cookies; role denial; previews; private content denial; child ownership; no free activation; duplicate requests; CSRF; gated email and invalid callback.');
 }
 if(phase==='active'){
  jar=state.jars[0];assert.equal((await call(auth,'GET','session')).access,true);
  assert.equal((await category('planet-names',200)).length,24);
  assert.equal((await call(account,'POST','workbook',workbook())).revision,1);
  await call(account,'POST','workbook',workbook(),409);
  assert.equal((await call(account,'GET','workbook',{},200,{path:'/api/account/workbook?child='+state.child})).revision,1);
  await call(auth,'POST','refresh');assert.equal((await call(auth,'GET','session')).access,true);
  jar=state.jars[1];await category('planet-names',403);await call(account,'GET','workbook',{},404,{path:'/api/account/workbook?child='+state.child});
  console.log('PASS active: full category granted; cloud save/read; stale revision rejected; refresh remains authenticated; second family denied.');
 }
 if(phase==='expired'){
  jar=state.jars[0];assert.equal((await call(auth,'GET','session')).access,false);await category('planet-names',403);
  assert.equal((await call(account,'GET','workbook',{},200,{path:'/api/account/workbook?child='+state.child})).revision,1);
  await call(account,'POST','workbook',{...workbook(),revision:1},403);
  const previous={...jar};assert.equal((await call(auth,'POST','logout')).revoked,true);assert.equal((await call(auth,'GET','session')).user,null);
  jar=previous;assert.equal((await call(auth,'GET','session')).user,null);await call(account,'GET','workbook',{},401,{path:'/api/account/workbook?child='+state.child});
  jar=state.jars[1];await call(auth,'POST','logout');
  console.log('PASS expired: history retained; premium/save denied; logout revokes live session and rejects replayed access cookie.');
 }
 fs.writeFileSync(statePath,JSON.stringify(state),{mode:0o600});
})().catch(error=>{console.error('FAIL',error.message);process.exitCode=1;}).finally(()=>sqlite.close());
