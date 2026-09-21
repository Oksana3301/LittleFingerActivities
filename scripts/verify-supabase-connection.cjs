/* Live read-only integration verification. Uses ignored local env; never logs keys. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
const values = Object.fromEntries(fs.readFileSync(path.join(root, '.env.local'), 'utf8').split('\n').filter(x => x && !x.startsWith('#') && x.includes('=')).map(x => [x.slice(0, x.indexOf('=')), x.slice(x.indexOf('=') + 1)]));
let owner = false;
let calls = 0;
let offline = false;
const observedFetch = (...args) => {calls++; if (offline) return Promise.reject(new Error('unavailable')); return fetch(...args);};
function load(filename, dependencies) {
  const source = ts.transpileModule(fs.readFileSync(path.join(root, filename), 'utf8'), {compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022}}).outputText;
  const module = {exports: {}};
  const requireStub = key => {if (!(key in dependencies)) throw new Error('Unexpected dependency: '+key); return dependencies[key];};
  vm.runInNewContext(source, {module, exports: module.exports, require: requireStub, fetch: observedFetch, URL, Response, Request, AbortSignal}, {filename});
  return module.exports;
}
(async () => {
  const connection = load('lib/supabase/connection.ts', {'server-only': {}, 'cloudflare:workers': {env: values}});
  const route = load('app/api/admin/integrations/route.ts', {'../../../../lib/owner': {isOwner: async () => owner}, '../../../../lib/supabase/connection': connection});
  let result = await route.GET();
  assert.equal(result.status, 403); assert.equal(calls, 0); assert.equal(result.headers.get('cache-control'), 'private, no-store');
  owner = true;
  result = await route.GET();
  assert.equal(result.status, 200);
  const body = await result.json();
  assert.equal(body.connected, true); assert.equal(body.schemaVersion, 1); assert.equal(body.authReachable, true);
  assert(!JSON.stringify(body).includes(values.SUPABASE_PUBLISHABLE_KEY));
  offline = true;
  result = await route.GET(); assert.equal(result.status, 503); assert.equal((await result.json()).connected, false);
  offline = false;
  const correctUrl = values.SUPABASE_URL;
  values.SUPABASE_URL = 'https://unrelated-project.supabase.co';
  result = await route.GET(); assert.equal(result.status, 503); assert.equal((await result.json()).configured, false);
  values.SUPABASE_URL = correctUrl;
  const headers = {apikey: values.SUPABASE_PUBLISHABLE_KEY};
  for (const table of ['profiles', 'marketing_leads', 'admin_audit_logs']) {
    const denied = await fetch(correctUrl+'/rest/v1/'+table+'?select=id&limit=1', {headers, signal: AbortSignal.timeout(20000)});
    assert([401,403].includes(denied.status), 'Anonymous table must be denied: '+table);
  }
  const privateSchema = await fetch(correctUrl+'/rest/v1/legacy_voice_links?select=user_id&limit=1', {headers: {...headers, 'Accept-Profile':'private'}, signal: AbortSignal.timeout(20000)});
  assert.equal(privateSchema.status, 406, 'Private schema must not be exposed');
  console.log('PASS: owner-only route; live Auth/schema; no key disclosure; outage/wrong-project failure; anonymous denial; private schema unexposed.');
})().catch(error => {console.error('Supabase verification failed:', error.name, typeof error.actual === 'number' ? error.actual : '', typeof error.expected === 'number' ? error.expected : '', error.cause?.code || '');process.exitCode=1;});
