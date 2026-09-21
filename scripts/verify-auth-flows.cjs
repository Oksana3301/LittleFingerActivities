/* Auth flow regression checks. Auth/email responses are controlled fixtures;
 * these tests do not send email or establish real email delivery readiness. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const ts=require('typescript');
const root=path.resolve(__dirname,'..');
function load(file,imports={}){
  const source=fs.readFileSync(path.join(root,file),'utf8').replaceAll('import.meta.env.DEV','false');
  const code=ts.transpileModule(source,{fileName:file,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  const module={exports:{}};
  vm.runInThisContext('(function(require,module,exports){'+code+'\n})',{filename:file})(name=>{assert(Object.hasOwn(imports,name),'Unexpected import: '+name);return imports[name];},module,module.exports);
  return module.exports;
}
const env={CUSTOMER_EMAIL_READY:'false',DB:{prepare(){return{bind(){return this;},async first(){return{count:1};},async run(){return{};}};}}};
let jar={},upstream=[];
const helper=load('lib/customer-auth.ts',{'server-only':{},'cloudflare:workers':{env},'next/headers':{cookies:async()=>({get:name=>jar[name]?{value:jar[name]}:undefined})},'./supabase/connection':{supabaseConfiguration:()=>({url:'https://auth.example.invalid',publishableKey:'sb_publishable_fixture'})}});
const auth=load('app/api/auth/[action]/route.ts',{'../../../../lib/customer-auth':helper,zod:require('zod'),'../../../../lib/preorder':load('lib/preorder.ts',{zod:require('zod')})});
const finish=load('app/auth/finish/route.ts',{'../../../lib/customer-auth':helper});
const client=load('lib/customer-client.ts');
const origin='https://littlefinger.example.invalid';
const request=(action,body)=>new Request(origin+'/api/auth/'+action,{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify(body)});
const call=(action,body)=>auth.POST(request(action,body),{params:Promise.resolve({action})});
let count=0;
async function test(name,fn){upstream=[];jar={};await fn();count++;console.log('PASS '+name);}
function responses(...items){global.fetch=async(url,options={})=>{upstream.push({url:String(url),options});assert(items.length,'Unexpected upstream call');const [body,status=200]=items.shift();return Response.json(body,{status});};}
const login={email:'test@example.invalid',password:'fixture-password-only'};
const tokens={access_token:'fixture-access',refresh_token:'fixture-refresh',expires_in:3600};
const user={id:'fixture-user',email:login.email,email_confirmed_at:'2026-09-21T00:00:00Z'};
(async()=>{
  await test('registration stays closed until delivery is configured',async()=>{
    responses();const response=await call('register',{});assert.equal(response.status,503);assert.equal((await response.json()).code,'email_setup_pending');assert.equal(upstream.length,0);
  });
  await test('unverified login keeps its verification error and creates no session',async()=>{
    responses([{error_code:'email_not_confirmed'},400]);const response=await call('login',login);assert.equal(response.status,403);assert.equal((await response.json()).code,'email_not_confirmed');assert.equal(response.headers.getSetCookie().length,0);
  });
  await test('incorrect password is distinguished from unavailable authentication',async()=>{
    responses([{error_code:'invalid_credentials'},400]);let response=await call('login',login);assert.equal(response.status,400);assert.equal((await response.json()).code,'invalid_credentials');
    responses([{error_code:'validation_failed'},400]);response=await call('login',login);assert.equal((await response.json()).code,'validation_failed');
  });
  await test('verified login initializes the family before setting secure cookies',async()=>{
    responses([tokens],[user],[true],[{}]);const response=await call('login',login);assert.equal(response.status,200);assert.deepEqual(await response.json(),{ok:true});assert.equal(upstream.length,4);
    const cookies=response.headers.getSetCookie();assert.equal(cookies.length,2);for(const cookie of cookies){assert.match(cookie,/^__Host-lf-/);assert.match(cookie,/HttpOnly/);assert.match(cookie,/SameSite=Lax/);assert.match(cookie,/Secure/);}
  });
  await test('signup creates a browser proof and does not sign in before verification',async()=>{
    env.CUSTOMER_EMAIL_READY='true';responses([{user:{id:'fixture-unverified'}}]);
    const response=await call('register',{...login,confirmPassword:login.password,name:'Test parent',whatsapp:'081234567890',language:'id',childAge:'2-3',terms:true,marketing:false,website:''});
    assert.equal(response.status,202);assert.equal(response.headers.getSetCookie().length,1);assert.match(response.headers.getSetCookie()[0],/^__Host-lf-verifier=signup%3A/);
    const body=JSON.parse(upstream[0].options.body);assert.equal(body.code_challenge_method,'s256');assert.equal(body.code_challenge.length,43);assert.equal(upstream[0].url.includes('redirect_to=https%3A%2F%2Flittle-world-playroom.atikadewi.chatgpt.site%2Fauth%2Ffinish'),true);
    env.CUSTOMER_EMAIL_READY='false';
  });
  await test('failed recovery link returns to password recovery',async()=>{
    jar={'__Host-lf-verifier':'recovery:'+'a'.repeat(96)};responses([{error_code:'flow_state_expired'},403]);const response=await finish.GET(new Request(origin+'/auth/finish?code=expired'));assert.equal(response.status,303);assert.equal(new URL(response.headers.get('location')).pathname,'/forgot-password');assert.equal(response.headers.getSetCookie().length,0);
  });
  await test('unknown proof type is rejected without contacting Auth',async()=>{
    jar={'__Host-lf-verifier':'unknown:'+'a'.repeat(96)};responses();await finish.GET(new Request(origin+'/auth/finish?code=anything'));assert.equal(upstream.length,0);
  });
  await test('successful recovery leads to password reset with secure session',async()=>{
    jar={'__Host-lf-verifier':'recovery:'+'a'.repeat(96)};responses([tokens],[user],[true],[{}]);const response=await finish.GET(new Request(origin+'/auth/finish?code=fixture-code'));assert.equal(new URL(response.headers.get('location')).pathname,'/reset-password');assert.equal(response.headers.getSetCookie().length,3);
  });
  await test('client preserves actionable verification errors',async()=>{
    responses([{error:'Verify first',code:'email_not_confirmed'},403]);await assert.rejects(client.jsonAction('/api/auth/login',login),error=>error instanceof client.AccountActionError&&error.code==='email_not_confirmed'&&error.status===403);
  });
  await test('client handles gateway and offline failures without exposing technical errors',async()=>{
    global.fetch=async()=>new Response('<html>Bad Gateway</html>',{status:502});await assert.rejects(client.jsonAction('/api/auth/login',login),error=>error instanceof client.AccountActionError&&error.code==='unavailable');
    global.fetch=async()=>{throw new TypeError('network failure');};await assert.rejects(client.jsonAction('/api/auth/login',login),error=>error instanceof client.AccountActionError&&error.code==='unavailable');
  });
  console.log(`PASS ${count} auth flow regression checks. Real email delivery is a separate acceptance check.`);
})().catch(error=>{console.error('FAIL',error.message);process.exitCode=1;});
