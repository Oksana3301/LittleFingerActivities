#!/usr/bin/env node
'use strict';

// Isolated route regressions. Reads application sources; never edits the site,
// calls external services, or uses real accounts/storage.
// Usage: node verify-parent-voice.cjs [/absolute/path/to/site]
// Requires Node 22.13+ (node:sqlite) and the site's installed TypeScript.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createRequire} = require('node:module');
const {DatabaseSync} = require('node:sqlite');
const {createHash} = require('node:crypto');

const project = path.resolve(process.argv[2] || '/workspace/sites/little-world-playroom');
const projectRequire = createRequire(path.join(project, 'package.json'));
const ts = projectRequire('typescript');
const origin = 'https://littlefinger.example';
const endpoint = origin + '/api/parent-voice';
let state;

function loadSource(relative, imports) {
  const filename = path.join(project, relative);
  const source = fs.readFileSync(filename, 'utf8');
  const compiled = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022},
  }).outputText;
  const module = {exports: {}};
  const requireInjected = name => {
    if (!Object.hasOwn(imports, name)) throw new Error('Unexpected source dependency: ' + name);
    return imports[name];
  };
  vm.runInThisContext('(function(require,module,exports){' + compiled + '\n})', {filename})(requireInjected, module, module.exports);
  return module.exports;
}

const personalization = loadSource('app/data/personalization.ts', {});
const env = {
  get DB() { return state.d1; },
  get AUDIO() { return state.bucket; },
};
const voice = loadSource('lib/parent-voice.ts', {
  'cloudflare:workers': {env},
  '../app/chatgpt-auth': {getChatGPTUser: async () => state.user},
  '../app/data/personalization': personalization,
  './customer-auth': {customerSession:async()=>null,hasCustomerAccess:async()=>false},
});
const route = loadSource('app/api/parent-voice/route.ts', {
  '../../../lib/parent-voice': voice,
  '../../data/personalization': personalization,
});

function reset() {
  state?.sqlite.close();
  const sqlite = new DatabaseSync(':memory:');
  // Execute the actual migration containing this table, including its indexes.
  const migrationDirectory = path.join(project, 'drizzle');
  const migration = fs.readdirSync(migrationDirectory).filter(name => name.endsWith('.sql')).map(name => fs.readFileSync(path.join(migrationDirectory, name), 'utf8')).find(sql => /CREATE TABLE [`"]?voice_recordings/.test(sql));
  assert.ok(migration, 'voice_recordings migration exists');
  sqlite.exec(migration);
  state = {sqlite, user: null, objects: new Map(), storageOps: [], dbOps: [], failNextInsert: false};
  state.d1 = {
    prepare(sql) {
      const statement = sqlite.prepare(sql);
      let bindings = [];
      const execute = method => {
        state.dbOps.push({sql, method, bindings: [...bindings]});
        if (state.failNextInsert && /^\s*INSERT\b/i.test(sql)) {
          state.failNextInsert = false;
          throw new Error('Injected D1 write failure');
        }
        return statement[method](...bindings);
      };
      return {
        bind(...values) { bindings = values; return this; },
        async first() { return execute('get') || null; },
        async all() { return {results: execute('all'), success: true}; },
        async run() { const result = execute('run'); return {success: true, meta: {changes: Number(result.changes)}}; },
      };
    },
  };
  state.bucket = {
    async put(key, data, options) {
      state.storageOps.push({method: 'put', key});
      state.objects.set(key, {bytes: Buffer.from(data).subarray(0), httpMetadata: {...options?.httpMetadata}});
    },
    async get(key) {
      state.storageOps.push({method: 'get', key});
      const value = state.objects.get(key);
      return value ? {body: new Uint8Array(value.bytes), httpMetadata: {...value.httpMetadata}} : null;
    },
    async delete(key) {
      state.storageOps.push({method: 'delete', key});
      state.objects.delete(key);
    },
  };
}

function login(userId = 'account-A') {
  state.user = {userId, email: userId + '@example.test', displayName: userId, fullName: null};
}
function rows() { return state.sqlite.prepare('SELECT * FROM voice_recordings ORDER BY id').all(); }
function wav(size = 64, marker = 11) {
  const data = Buffer.alloc(size, marker);
  data.write('RIFF', 0);
  data.writeUInt32LE(size - 8, 4);
  data.write('WAVE', 8);
  return data;
}
function putRequest({text = 'Hello Ada!', lang = 'en', data = wav(), requestOrigin = origin} = {}) {
  const form = new FormData();
  form.set('text', text);
  form.set('lang', lang);
  form.set('audio', new Blob([data], {type: 'audio/wav'}), 'recording.wav');
  return new Request(endpoint, {method: 'PUT', headers: requestOrigin === null ? {} : {Origin: requestOrigin}, body: form});
}
function getRequest(key, lang = 'en') { return new Request(endpoint + '?lang=' + lang + '&key=' + key); }
function deleteRequest(key, lang = 'en', requestOrigin = origin) {
  return new Request(endpoint, {method: 'DELETE', headers: {'Content-Type': 'application/json', ...(requestOrigin === null ? {} : {Origin: requestOrigin})}, body: JSON.stringify({lang, key})});
}
async function expectStatus(response, status) {
  assert.equal(response.status, status, 'HTTP status; actual body: ' + await response.clone().text());
  assert.equal(response.headers.get('cache-control'), 'private, no-store');
  return response;
}
async function save(options) {
  const response = await expectStatus(await route.PUT(putRequest(options)), 200);
  const body = await response.json();
  assert.equal(body.ok, true);
  assert.match(body.key, /^[a-f0-9]{64}$/);
  return body.key;
}
async function read(key, lang = 'en') {
  const response = await expectStatus(await route.GET(getRequest(key, lang)), 200);
  assert.equal(response.headers.get('content-type'), 'audio/wav');
  assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
  return Buffer.from(await response.arrayBuffer());
}
async function list(lang = 'en') {
  const response = await expectStatus(await route.GET(new Request(endpoint + '?list=1&lang=' + lang)), 200);
  return (await response.json()).recordings;
}

const cases = [
  ['unauthenticated GET/list/PUT/DELETE reject before storage access', async () => {
    const key = 'a'.repeat(64);
    for (const [method, request] of [
      ['GET', getRequest(key)],
      ['GET', new Request(endpoint + '?list=1&lang=en')],
      ['PUT', putRequest()],
      ['DELETE', deleteRequest(key)],
    ]) await expectStatus(await route[method](request), 401);
    assert.equal(state.dbOps.length, 0);
    assert.equal(state.storageOps.length, 0);
  }],
  ['trusted account boundaries isolate identical text and prevent cross-owner deletion', async () => {
    login('account-A');
    const audioA = wav(64, 21), audioB = wav(96, 33);
    const key = await save({data: audioA});
    const aPointer = rows()[0].object_key;
    login('account-B');
    await expectStatus(await route.GET(getRequest(key)), 404);
    assert.deepEqual(await list(), []);
    await expectStatus(await route.DELETE(deleteRequest(key)), 200);
    assert.ok(state.objects.has(aPointer), 'other account cannot delete A object');
    assert.equal(await save({data: audioB}), key);
    assert.deepEqual(await read(key), audioB);
    assert.equal((await list()).length, 1);
    login('account-A');
    assert.deepEqual(await read(key), audioA);
    assert.equal((await list()).length, 1);
    assert.equal(rows().length, 2);
    assert.equal(new Set(rows().map(row => row.owner)).size, 2);
  }],
  ['language boundaries preserve separate playback, lists, and deletion for one text key', async () => {
    login();
    const en = wav(64, 4), id = wav(96, 8);
    const key = await save({data: en, lang: 'en'});
    await expectStatus(await route.GET(getRequest(key, 'id')), 404);
    assert.equal(await save({data: id, lang: 'id'}), key);
    assert.deepEqual(await read(key, 'en'), en);
    assert.deepEqual(await read(key, 'id'), id);
    assert.deepEqual((await list('en')).map(row => row.language), ['en']);
    assert.deepEqual((await list('id')).map(row => row.language), ['id']);
    await expectStatus(await route.DELETE(deleteRequest(key, 'en')), 200);
    await expectStatus(await route.GET(getRequest(key, 'en')), 404);
    assert.deepEqual(await read(key, 'id'), id);
  }],
  ['headerless oversized stream is canceled and rejected with 413 before parsing/storage', async () => {
    login();
    let canceled = false;
    const body = new ReadableStream({
      start(controller) { controller.enqueue(new Uint8Array(5_500_001)); },
      cancel() { canceled = true; },
    });
    const request = new Request(endpoint, {method: 'PUT', headers: {Origin: origin, 'Content-Type': 'multipart/form-data; boundary=unused'}, body, duplex: 'half'});
    assert.equal(request.headers.has('content-length'), false);
    await expectStatus(await route.PUT(request), 413);
    assert.equal(canceled, true);
    assert.equal(state.dbOps.length, 0);
    assert.equal(state.storageOps.length, 0);
  }],
  ['declared oversize rejects with 413 and mismatched audio signature rejects with 415', async () => {
    login();
    const oversized = putRequest();
    oversized.headers.set('Content-Length', '5500001');
    await expectStatus(await route.PUT(oversized), 413);
    await expectStatus(await route.PUT(putRequest({data: Buffer.alloc(64)})), 415);
    assert.equal(rows().length, 0);
    assert.equal(state.storageOps.length, 0);
  }],
  ['invalid language, empty text, undersized file, and oversized file reject without writes', async () => {
    login();
    for (const options of [{lang: 'fr'}, {text: ' \n '}, {data: Buffer.alloc(12)}, {data: wav(5_000_001)}]) {
      await expectStatus(await route.PUT(putRequest(options)), 400);
    }
    assert.equal(rows().length, 0);
    assert.equal(state.storageOps.length, 0);
  }],
  ['duplicate normalized text upserts one row, replaces pointer, and removes old object', async () => {
    login();
    const first = wav(64, 18), replacement = wav(128, 31);
    const key = await save({text: '  Hello  \n Ada!  ', data: first});
    assert.equal(key, createHash('sha256').update('Hello Ada!').digest('hex'));
    const oldPointer = rows()[0].object_key;
    assert.equal(await save({text: 'Hello Ada!', data: replacement}), key);
    const [row] = rows();
    assert.equal(rows().length, 1);
    assert.equal(row.transcript, 'Hello Ada!');
    assert.equal(row.bytes, replacement.length);
    assert.notEqual(row.object_key, oldPointer);
    assert.equal(state.objects.has(oldPointer), false);
    assert.equal(state.objects.size, 1);
    assert.deepEqual(await read(key), replacement);
  }],
  ['replacement respects total byte quota and accepts the exact 250 MB boundary', async () => {
    login();
    const key = await save();
    const original = {...rows()[0]};
    // Seed storage accounting for a different recording without allocating 249 MB.
    state.sqlite.prepare('INSERT INTO voice_recordings SELECT ?, owner, language, ?, ?, ?, mime, ?, updated_at FROM voice_recordings WHERE id = ?').run(
      original.owner + '/en/' + 'b'.repeat(64), 'b'.repeat(64), 'Other recording', 'quota-fixture', 249_000_000, original.id);
    await expectStatus(await route.PUT(putRequest({data: wav(1_100_000)})), 409);
    assert.equal(state.sqlite.prepare('SELECT object_key FROM voice_recordings WHERE id = ?').get(original.id).object_key, original.object_key);
    assert.ok(state.objects.has(original.object_key));
    assert.equal(state.storageOps.filter(op => op.method === 'put').length, 1, 'rejected replacement writes no object');
    assert.equal(await save({data: wav(1_000_000)}), key);
    assert.equal(state.sqlite.prepare('SELECT sum(bytes) AS total FROM voice_recordings').get().total, 250_000_000);
  }],
  ['full recording-count quota blocks new text but permits an existing replacement', async () => {
    login();
    const key = await save();
    const existing = rows()[0];
    const insert = state.sqlite.prepare('INSERT INTO voice_recordings VALUES (?,?,?,?,?,?,?,?,?)');
    state.sqlite.exec('BEGIN');
    for (let index = 1; index < 2000; index++) {
      const extra = createHash('sha256').update('fixture-' + index).digest('hex');
      insert.run(existing.owner + '/en/' + extra, existing.owner, 'en', extra, 'Fixture ' + index, 'fixture/' + extra, 'audio/wav', 64, existing.updated_at);
    }
    state.sqlite.exec('COMMIT');
    await expectStatus(await route.PUT(putRequest({text: 'Another new phrase'})), 409);
    assert.equal(await save({data: wav(80)}), key);
    assert.equal(rows().length, 2000);
  }],
  ['D1 upsert failure preserves old pointer/audio and removes only the failed upload', async () => {
    login();
    const oldAudio = wav(64, 42);
    const key = await save({data: oldAudio});
    const oldRow = {...rows()[0]};
    state.failNextInsert = true;
    await expectStatus(await route.PUT(putRequest({data: wav(128, 71)})), 503);
    assert.deepEqual({...rows()[0]}, oldRow);
    assert.deepEqual(await read(key), oldAudio);
    assert.equal(state.objects.size, 1);
    assert.ok(state.objects.has(oldRow.object_key));
    const puts = state.storageOps.filter(op => op.method === 'put');
    assert.equal(puts.length, 2, 'failure occurs after new object upload');
    assert.notEqual(puts[1].key, oldRow.object_key);
    assert.ok(state.storageOps.some(op => op.method === 'delete' && op.key === puts[1].key));
    assert.equal(state.storageOps.some(op => op.method === 'delete' && op.key === oldRow.object_key), false);
  }],
  ['DELETE removes the stored object pointer, preserves unrelated keys, and is idempotent', async () => {
    login();
    const key = await save();
    const row = rows()[0];
    const guessedLegacyKey = 'voices/' + row.id;
    assert.notEqual(row.object_key, guessedLegacyKey);
    state.objects.set(guessedLegacyKey, {bytes: Buffer.from('unrelated sentinel'), httpMetadata: {contentType: 'audio/wav'}});
    await expectStatus(await route.DELETE(deleteRequest(key)), 200);
    assert.equal(rows().length, 0);
    assert.equal(state.objects.has(row.object_key), false);
    assert.ok(state.objects.has(guessedLegacyKey));
    const deletes = state.storageOps.filter(op => op.method === 'delete');
    assert.deepEqual(deletes.map(op => op.key), [row.object_key]);
    await expectStatus(await route.DELETE(deleteRequest(key)), 200);
    assert.equal(state.storageOps.filter(op => op.method === 'delete').length, 1);
  }],
  ['foreign and absent origins cannot upload or delete an authenticated user recording', async () => {
    login();
    const key = await save();
    const original = {...rows()[0]};
    const operations = state.storageOps.length;
    for (const requestOrigin of ['https://other.example', null]) {
      await expectStatus(await route.PUT(putRequest({requestOrigin})), 403);
      await expectStatus(await route.DELETE(deleteRequest(key, 'en', requestOrigin)), 403);
    }
    assert.deepEqual({...rows()[0]}, original);
    assert.equal(state.storageOps.length, operations);
  }],
];

(async () => {
  let failures = 0;
  console.log('Parent voice route regressions against ' + project);
  for (const [name, run] of cases) {
    reset();
    try { await run(); console.log('PASS ' + name); }
    catch (error) { failures++; console.error('FAIL ' + name + '\n' + error.stack); }
  }
  state?.sqlite.close();
  console.log('\n' + (cases.length - failures) + '/' + cases.length + ' regression cases passed.');
  if (failures) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
