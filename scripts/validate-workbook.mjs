import fs from 'node:fs';
import assert from 'node:assert/strict';
const directory='content/worksheets';
const cats=JSON.parse(fs.readFileSync('app/data/worksheet-categories.json','utf8'));
const records=cats.flatMap(c=>JSON.parse(fs.readFileSync(`${directory}/${c.id}.json`,'utf8')));
const atlases=JSON.parse(fs.readFileSync('app/data/art-atlases.json','utf8'));
const external=JSON.parse(fs.readFileSync('app/data/external-art.json','utf8'));
const assets=new Set([...atlases.flatMap(a=>a.assets),...Object.keys(external)]);
for(const art of Object.values(external))assert(fs.existsSync('public'+art.src));
const report=JSON.parse(fs.readFileSync('public/specs/workbook-catalogue-report.json','utf8'));
const index=JSON.parse(fs.readFileSync('app/data/worksheet-index.json','utf8'));
assert.equal(cats.length,report.categories);assert.equal(records.length,report.worksheets);assert.equal(new Set(records.map(w=>w.id)).size,records.length);
assert.deepEqual(index.map(w=>w.id),records.map(w=>w.id));
for(const atlas of atlases){assert.equal(atlas.assets.length,atlas.size**2);assert(fs.existsSync(`public/assets/workbook/${atlas.file}.webp`),`Missing atlas ${atlas.file}`)}
for(const category of cats)assert(assets.has(category.asset),`Unknown category artwork ${category.asset}`);

let rounds=0;
function inspect(v){if(Array.isArray(v))return v.forEach(inspect);if(v&&typeof v==='object'){if(v.countAsset)assert(assets.has(v.countAsset));if(v.asset)assert(assets.has(v.asset),`Unknown asset ${v.asset}`);if(v.groupAsset)assert(assets.has(v.groupAsset));Object.values(v).forEach(inspect)}}
for(const c of cats)assert.equal(records.filter(w=>w.category===c.id).length,c.worksheetCount||24);
for(const w of records){assert.equal(w.rounds?.length||1,w.partCount||4);for(const source of w.rounds||[{}]){const r={...w,...source};const engine=r.engine;rounds++;inspect(r);assert(r.instruction.en&&r.instruction.id);const ids=r.options.map(o=>o.id);assert.equal(new Set(ids).size,ids.length);for(const o of [...r.options,...(r.rightOptions||[])])assert(o.label?.id&&o.label?.en,`Missing label ${w.id}`);if(['identify','count','compare','pattern','map'].includes(engine)){assert(r.answer.length);r.answer.forEach(id=>assert(ids.includes(id)));}if(engine==='map'){assert.equal(r.answer.length,1);assert.equal(r.map.places.length,ids.length);assert.deepEqual(r.map.places.map(p=>p.option).sort(),[...ids].sort());for(const p of r.map.places){assert(p.lat>=-90&&p.lat<=90);assert(p.lng>=-180&&p.lng<=180)}}if(engine==='sequence')assert.deepEqual([...r.answer].sort(),[...ids].sort());if(engine==='pair'){assert.equal(r.pairs.length,r.options.length);assert.equal(new Set(r.pairs.map(p=>p.right)).size,r.options.length);for(const p of r.pairs){assert(ids.includes(p.left));assert(r.rightOptions.some(o=>o.id===p.right))}}if(engine==='sort'){assert(r.bins.length>=2);assert.equal(r.pairs.length,r.options.length);assert.equal(new Set(r.pairs.map(p=>p.left)).size,r.options.length);for(const p of r.pairs){assert(ids.includes(p.left));assert(r.bins.some(b=>b.id===p.right))}}if(engine==='memory')assert(r.options.length>=2&&r.options.length<=6);if(engine==='pattern')assert.equal(r.patternItems.filter(x=>x===null).length,1);if(engine==='count'){assert.equal(Number(r.options.find(o=>o.id===r.answer[0]).symbol),r.countTarget);if(r.operation)assert.equal(r.countTarget,r.operation==='add'?r.operands[0]+r.operands[1]:r.operands[0]-r.operands[1]);}if(['draw','trace'].includes(engine))assert(Array.isArray(r.canvas.guide));}}
assert.equal(rounds,report.rounds);
console.log(JSON.stringify({worksheets:records.length,categories:cats.length,rounds,engines:new Set(records.map(w=>w.engine)).size,valid:true}));
