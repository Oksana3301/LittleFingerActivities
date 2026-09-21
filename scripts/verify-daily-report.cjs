const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const { createRequire } = require('module');
const root = process.argv[2] || path.resolve(__dirname, '..');
const ts = createRequire(path.join(root, 'package.json'))('typescript');
const moduleObject = { exports: {} };
const code = ts.transpileModule(fs.readFileSync(path.join(root, 'app/data/daily-report.ts'), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
vm.runInNewContext(code, { module: moduleObject, exports: moduleObject.exports, Date, Intl });
const { addEvent, mergeLogs, summarize, localDay } = moduleObject.exports;
const today = '2026-09-19', yesterday = '2026-09-18';
let sequence = 0, failures = 0, successes = 0;
const empty = () => ({ version: 1, events: [], previous: [] });
function event(type, overrides = {}) {
  const id = ++sequence;
  return { id: String(id), at: `${today}T01:${String(Math.floor(id / 60)).padStart(2, '0')}:${String(id % 60).padStart(2, '0')}.000Z`, day: today,
    timezone: 'Asia/Jakarta', worksheet: 'food-01', roundKey: 'food-01@v1~0', category: 'food', engine: 'identify', parts: 4,
    type, ...overrides };
}
function logOf(...events) { return events.reduce(addEvent, empty()); }
function test(name, fn) {
  try { fn(); console.log('PASS', name); successes++; }
  catch (error) { console.error('FAIL', name, '\n ', error.message); failures++; }
}
test('correct submission and completion produce one distinct success and accomplishment', () => {
  const r = summarize(logOf(event('attempt', { correct: true, signature: 'right' }), event('complete')), today);
  assert.equal(r.correct, 1); assert.equal(r.firstTry, 1); assert.equal(r.attempts, 1); assert.equal(r.completed, 1); assert.equal(r.newWins, 1); assert.equal(r.sheets, 0);
});
test('wrong then right remains corrected after repeating the round', () => {
  const log = logOf(event('attempt', { correct: false, signature: 'wrong' }), event('attempt', { correct: true, signature: 'right' }), event('complete'), event('attempt', { correct: true, signature: 'right' }), event('complete'));
  const r = summarize(log, today);
  assert.equal(r.correct, 1); assert.equal(r.firstTry, 0); assert.equal(r.attempts, 2); assert.equal(r.completed, 1); assert.equal(r.newWins, 1);
});
test('unchanged wrong submissions cannot inflate attempts', () => {
  const log = logOf(event('attempt', { correct: false, signature: 'wrong' }), event('attempt', { correct: false, signature: 'wrong' }));
  assert.equal(summarize(log, today).attempts, 1);
});
test('pair and memory mistakes prevent first-try claims', () => {
  for (const engine of ['pair', 'memory']) {
    const r = summarize(logOf(event('mistake', { engine }), event('attempt', { engine, correct: true, signature: 'solved' }), event('complete', { engine })), today);
    assert.equal(r.correct, 1); assert.equal(r.firstTry, 0);
  }
});
test('creative completion never supplies a scored answer', () => {
  const r = summarize(logOf(event('complete', { engine: 'draw' }), event('complete', { engine: 'trace', roundKey: 'food-01@v1~1' })), today);
  assert.equal(r.creative, 2); assert.equal(r.completed, 2); assert.equal(r.correct, 0); assert.equal(r.attempts, 0); assert.equal(r.firstTry, 0);
});
test('undated old progress supplies no daily metrics or new accomplishment', () => {
  const log = empty(); log.previous = ['food-01@v1~0'];
  assert.equal(summarize(log, today).completed, 0); assert.equal(summarize(log, today).newWins, 0);
  const next = addEvent(log, event('complete'));
  assert.equal(summarize(next, today).completed, 1); assert.equal(summarize(next, today).newWins, 0);
});
test('completing the final part of an old partial worksheet counts one full worksheet', () => {
  const log = empty(); log.previous = [0, 1, 2].map(i => `food-01@v1~${i}`);
  const next = addEvent(log, event('complete', { roundKey: 'food-01@v1~3' }));
  const r = summarize(next, today); assert.equal(r.sheets, 1); assert.equal(r.newWins, 1);
});
test('four new parts count one worksheet; repeat completion stays one', () => {
  let log = empty();
  for (let i = 0; i < 4; i++) log = addEvent(log, event('complete', { roundKey: `food-01@v1~${i}` }));
  log = addEvent(log, event('complete', { roundKey: 'food-01@v1~3' }));
  const r = summarize(log, today); assert.equal(r.sheets, 1); assert.equal(r.completed, 4); assert.equal(r.newWins, 4);
});
test('fully old completed worksheet gets no new full-sheet reward', () => {
  const log = empty(); log.previous = [0, 1, 2, 3].map(i => `food-01@v1~${i}`);
  const r = summarize(addEvent(log, event('complete')), today); assert.equal(r.sheets, 0); assert.equal(r.newWins, 0);
});
test('old content revision cannot complete a new revision', () => {
  const log = empty(); log.previous = [0, 1, 2].map(i => `food-01@old~${i}`);
  const r = summarize(addEvent(log, event('complete', { roundKey: 'food-01@v1~3' })), today); assert.equal(r.sheets, 0);
});
test('one-part featured worksheet completes once', () => {
  const r = summarize(logOf(event('complete', { worksheet: 'featured', roundKey: 'featured~0', parts: 1 })), today); assert.equal(r.sheets, 1);
});
test('replaying tomorrow can count daily practice but no new accomplishment', () => {
  const log = logOf(event('attempt', { day: yesterday, at: `${yesterday}T01:00:00Z`, correct: true, signature: 'right' }), event('complete', { day: yesterday, at: `${yesterday}T01:00:01Z` }), event('attempt', { correct: true, signature: 'right' }), event('complete'));
  const r = summarize(log, today); assert.equal(r.correct, 1); assert.equal(r.completed, 1); assert.equal(r.newWins, 0);
});
test('a mistake before midnight followed by success after midnight is not first try', () => {
  for (const type of ['attempt', 'mistake']) {
    const log = logOf(event(type, { day: yesterday, at: `${yesterday}T16:59:59Z`, correct: false, signature: 'wrong' }), event('attempt', { day: today, at: `${yesterday}T17:00:01Z`, correct: true, signature: 'right' }));
    assert.equal(summarize(log, today).firstTry, 0);
  }
});
test('prior success cannot hide corrections on a new day', () => {
  const log = logOf(event('attempt', { day: yesterday, at: `${yesterday}T01:00:00Z`, correct: true, signature: 'right' }), event('complete', { day: yesterday, at: `${yesterday}T01:00:01Z` }), event('attempt', { correct: false, signature: 'wrong' }), event('attempt', { correct: true, signature: 'right' }));
  const r = summarize(log, today); assert.equal(r.firstTry, 0); assert.equal(r.categories[0].firstTry, 0);
});
test('a fresh correct practice after a corrected previous day is without correction today', () => {
  const log = logOf(event('attempt', { day: yesterday, at: `${yesterday}T01:00:00Z`, correct: false, signature: 'wrong' }), event('attempt', { day: yesterday, at: `${yesterday}T01:00:01Z`, correct: true, signature: 'right' }), event('complete', { day: yesterday, at: `${yesterday}T01:00:02Z` }), event('attempt', { correct: true, signature: 'right' }));
  assert.equal(summarize(log, today).firstTry, 1);
});
test('day uses local calendar at Jakarta UTC rollover', () => {
  const original = process.env.TZ;
  try { process.env.TZ = 'Asia/Jakarta'; assert.equal(localDay(new Date('2026-09-18T18:30:00Z')), '2026-09-19'); }
  finally { if (original === undefined) delete process.env.TZ; else process.env.TZ = original; }
});
test('same event ID is idempotent when merging tabs', () => {
  const e = event('attempt', { correct: true, signature: 'right' });
  const r = summarize(mergeLogs(logOf(e), logOf(e)), today); assert.equal(r.attempts, 1); assert.equal(r.correct, 1);
});
test('simultaneous identical submissions from two tabs count once', () => {
  const a = logOf(event('attempt', { correct: true, signature: 'right' }));
  const b = logOf(event('attempt', { correct: true, signature: 'right' }));
  const r = summarize(mergeLogs(a, b), today); assert.equal(r.attempts, 1); assert.equal(r.correct, 1);
});
test('simultaneous creative completion in two tabs counts one creative part', () => {
  const a = logOf(event('complete', { engine: 'draw' })), b = logOf(event('complete', { engine: 'draw' }));
  const r = summarize(mergeLogs(a, b), today); assert.equal(r.completed, 1); assert.equal(r.creative, 1); assert.equal(r.newWins, 1);
});
test('too little evidence does not generate category strengths or interests', () => {
  const r = summarize(logOf(event('open'), event('attempt', { correct: true, signature: 'right' })), today);
  assert.equal(r.strong.length, 0); assert.equal(r.interests.length, 0);
});
test('one-part guided exploration counts an accomplishment without a correct answer', () => {
  const r = summarize(logOf(event('complete', { worksheet: 'lf-a-story', roundKey: 'lf-a-story@paths-v1~0', engine: 'explore', parts: 1 })), today);
  assert.equal(r.sheets, 1); assert.equal(r.newWins, 1); assert.equal(r.creative, 1); assert.equal(r.correct, 0); assert.equal(r.attempts, 0);
});
console.log(`\n${successes} passed; ${failures} failed`);
process.exitCode = failures ? 1 : 0;
