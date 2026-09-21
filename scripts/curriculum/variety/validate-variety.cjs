#!/usr/bin/env node
'use strict';
/* Standalone, dependency-free content audit. No Site writes.
 * Usage: node validate-variety.cjs SITE [--report /tmp/report.json]
 *        node validate-variety.cjs --self-test
 * Exit 1 means a structural, answer-contract, ambiguity, or round-uniqueness error.
 * Duplicate whole-record task sets are reported separately for editorial review.
 * This validator deliberately does not infer real-world answers from prose.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');

const EXPECTED_CATEGORIES = ['temperature','soft-hard','smooth-rough','wet-dry','open-closed','full-empty','heavy-light','bright-dim','fast-slow','loud-quiet','tidy-messy','kind-descriptions','brush-teeth','bath-routine','wash-hands','toilet-care','mealtime-habits','bedtime-routine','tidy-toys','polite-words','helping-family','gentle-with-younger','friendly-choices','daily-routine','road-vehicles','air-water-vehicles','construction-vehicles','vehicle-count','garage-tools','machine-parts','build-a-vehicle','workshop-sort','sports-kit','camping-kit','hobby-patterns','vehicle-paths','dinosaur-names','robot-drawing','build-blocks','adventure-sort','planet-names','planet-facts','space-pairs','body-parts','five-senses','body-care','family-members','family-pairs','kind-words','taking-turns','room-objects','school-objects','object-functions','living-nonliving','plant-needs','weather-choices','math-more-less','math-equal','number-neighbors','math-stories','animal-names','produce-names','garden-names','vehicle-names','sky-names','home-names','colors','shapes','size','length','height','thickness','same-different','directions','positions','symmetry','object-pairs','silhouette-pairs','color-pairs','shape-pairs','number-pairs','uppercase-pairs','lowercase-pairs','letter-case','initial-letters','vowels','consonants','count-to-5','count-to-10','count-6-to-15','quantity-pairs','compare-quantity','ascending','descending','missing-number','add-to-5','add-to-10','subtract-to-5','subtract-to-10','pattern-ab','pattern-abc','pattern-aab-abb','growing-pattern','memory-objects','memory-shapes','memory-colors','trace-lines','trace-curves','trace-shapes','trace-numbers','trace-letters','finish-picture','draw-to-count','draw-pattern','spatial-drawing','imagine-draw'];
const KINDS = new Set(['choose-one','choose-many','odd-one-out','clue','match','shadow-match','sort','sequence','memory','pattern','count','trace','draw']);
const ENGINES = new Set(['identify','compare','pair','sort','sequence','memory','pattern','count','trace','draw']);
const KIND_ENGINES = {
 'choose-one':['identify','compare'], 'choose-many':['identify'], 'odd-one-out':['identify'], clue:['identify','compare','count','pattern'],
 match:['pair'], 'shadow-match':['pair'], sort:['sort'], sequence:['sequence'], memory:['memory'], pattern:['pattern'], count:['count'], trace:['trace'], draw:['draw']
};
const LANGUAGES = ['id','en','zh','ar'];
const SELECT_ENGINES = new Set(['identify','compare','pattern','count']);
const ROUND_FIELDS = ['instruction','options','answer','rightOptions','pairs','bins','patternItems','pattern','reference','countTarget','countAsset','operation','operands','expression','trace','guide','canvas','completion','layout','languageOfTask'];
const clone = v => JSON.parse(JSON.stringify(v));
const norm = v => typeof v === 'string' ? v.normalize('NFKC').replace(/\s+/g,' ').trim() : v;
function stable(v) {
 if (Array.isArray(v)) return v.map(stable);
 if (v && typeof v === 'object') return Object.fromEntries(Object.keys(v).sort().filter(k=>v[k]!==undefined).map(k=>[k,stable(v[k])]));
 return norm(v);
}
const json = v => JSON.stringify(stable(v));
const hash = v => crypto.createHash('sha256').update(json(v)).digest('hex');
const sorted = a => [...a].sort((a,b)=>json(a).localeCompare(json(b)));
const sameSet = (a,b) => json([...a].sort())===json([...b].sort());
const unique = a => new Set(a).size===a.length;
const nonempty = s => typeof s==='string' && s.trim().length>0;
const integer = n => Number.isInteger(n) && n>=0;

/* Mirrors PictureArt's branch order: ignored data fields cannot make two
 * identical rendered cards appear distinct. Default values are normalized. */
function visual(o={}) {
 const transform={scale:o.scale||1,rotation:o.rotation||0};
 const color=o.silhouette?'#4d5948':o.color;
 if (o.asset) return {asset:o.asset,...transform,silhouette:!!o.silhouette};
 if (o.kind==='quantity') return {kind:'quantity',value:o.value||0,groupAsset:o.groupAsset||null};
 if (o.kind==='measurement' && o.measure!=='scale') return {kind:'measurement',measure:o.measure,value:o.value||.5,color:color||'#73955c'};
 if (o.dots!==undefined) return {dots:o.dots,color:color||'#789667'};
 if (o.shape) return {shape:o.shape,color:color||'#db9677',...transform};
 return {symbol:o.symbol??o.value??'?',color:color||'#647f52',...transform};
}
function presentation(o={}, engine='', lang='en') {
 const v=visual(o);
 // Authored position is the visible grid cell, not an irrelevant local ID.
 if(o.position)v.position=o.position;
 // Memory fronts have no object-caption; these labels cannot disambiguate them.
 if (engine!=='memory' && !['quantity','measurement','arrow'].includes(o.kind)) v.caption=norm(o.label?.[lang]||'');
 return v;
}
function semanticPicture(o, engine) {
 if (!o) return null;
 return presentation(o,engine,'en');
}
function guideIdentity(g) {
 const out={};
 for(const [k,v] of Object.entries(g||{})) if(k!=='id') out[k]=k==='items'?v.map(x=>semanticPicture(x,'')):v;
 return out;
}
function taskParts(w,r) {
 const engine=r.engine||w.engine;
 const left=new Map((r.options||[]).map(o=>[o.id,semanticPicture(o,engine)]));
 const right=new Map((r.rightOptions||[]).map(o=>[o.id,semanticPicture(o,engine)]));
 const bins=new Map((r.bins||[]).map(b=>[b.id,{asset:b.asset,label:norm(b.label?.en||'')}]));
 const task={engine,instruction:norm(r.instruction?.en||''),options:sorted([...left.values()])};
 if(r.rightOptions) task.rightOptions=sorted([...right.values()]);
 if(r.bins) task.bins=sorted([...bins.values()]);
 if(r.patternItems) task.patternItems=r.patternItems.map(o=>semanticPicture(o,engine));
 else if(r.pattern) task.patternItems=r.pattern.map(id=>left.get(id)||null);
 if(r.reference) task.reference=semanticPicture(r.reference,engine);
 for(const k of ['countTarget','countAsset','operation','operands','expression','trace','guide']) if(r[k]!==undefined)task[k]=r[k];
 if(r.canvas) task.canvas={viewBox:r.canvas.viewBox,guide:(r.canvas.guide||[]).map(guideIdentity)};
 if(r.completion) task.completion={mode:r.completion.mode,goals:(r.completion.goals||[]).map(x=>norm(x.en||''))};
 let answer;
 if(engine==='pair') answer=sorted((r.pairs||[]).map(p=>[left.get(p.left)||{missing:p.left},right.get(p.right)||{missing:p.right}]));
 else if(engine==='sort') answer=sorted((r.pairs||[]).map(p=>[left.get(p.left)||{missing:p.left},bins.get(p.right)||{missing:p.right}]));
 else if(engine==='memory') answer=sorted([...left.values()]);
 else answer=(r.answer||[]).map(id=>left.get(id)||{missing:id});
 if(engine!=='sequence') answer=sorted(answer);
 return {task,answer};
}
function semanticTask(w,r) {return hash(taskParts(w,r));}
function issue(list,code,at,detail) {list.push({code,at,detail});}
function textChecks(value,langs,at,errors) {
 for(const lang of langs) if(!nonempty(value?.[lang])) issue(errors,'MISSING_INSTRUCTION_LANGUAGE',at,lang);
}
function checkRound(w,r,number,ctx={}) {
 const errors=[],warnings=[],at=`${w.id}/round-${number}`,engine=r.engine||w.engine,kind=r.activityKind||w.activityKind;
 const options=Array.isArray(r.options)?r.options:[],answers=Array.isArray(r.answer)?r.answer:[];
 const ids=options.map(o=>o.id),right=r.rightOptions||[],rids=right.map(o=>o.id),pairs=r.pairs||[],bins=r.bins||[],bids=bins.map(b=>b.id);
 const fail=(code,detail)=>issue(errors,code,at,detail);
 if(!Array.isArray(r.options)||!Array.isArray(r.answer)) fail('ROUND_ARRAYS','options and answer must be arrays');
 textChecks(r.instruction,w.revision==='variety-1'?LANGUAGES:['id','en'],at,errors);
 if(r.engine&&r.engine!==w.engine) fail('ROUND_ENGINE_OVERRIDE','The player selects the worksheet engine; all rounds must use it');
 if(r.activityKind&&r.activityKind!==w.activityKind) fail('ROUND_KIND_OVERRIDE','Each record must have a stable activity kind');
 if(!unique(ids)||ids.some(id=>!nonempty(id))) fail('OPTION_IDS','Option IDs must be unique nonempty strings');
 if(!unique(answers)) fail('ANSWER_IDS','Answer IDs must not repeat');
 if(!unique(rids)||rids.some(id=>!nonempty(id))) fail('RIGHT_IDS','Right IDs must be unique nonempty strings');
 for(const [i,o] of [...options,...right].entries()) {
  if(!nonempty(o.label?.en)||!nonempty(o.label?.id)) fail('OPTION_LABEL',`Option ${i} needs id/en labels`);
  if((o.kind==='quantity'&&!integer(o.value))||(o.dots!==undefined&&!integer(o.dots))) fail('INVALID_QUANTITY',`Option ${o.id}`);
  if(ctx.assets) for(const field of ['asset','groupAsset']) if(o[field]&&!ctx.assets.has(o[field])) fail('UNKNOWN_ASSET',o[field]);
 }
 if(ctx.assets) {
  function inspect(v) {if(Array.isArray(v)){v.forEach(inspect);return;}if(v&&typeof v==='object'){for(const k of ['asset','groupAsset','countAsset'])if(v[k]&&!ctx.assets.has(v[k]))fail('UNKNOWN_ASSET',v[k]);Object.values(v).forEach(inspect);}}
  inspect(r);
 }
 if(SELECT_ENGINES.has(engine)) {
  if(!answers.length) fail('EMPTY_SELECTION_ANSWER','Selection engine needs an answer');
  for(const id of answers) if(!ids.includes(id)) fail('MISSING_ANSWER_OPTION',id);
  if(options.length<=answers.length) fail('NO_DISTRACTOR','At least one option must be incorrect');
  if(['compare','count','pattern'].includes(engine)&&answers.length!==1)fail('SINGLE_ENGINE_ANSWER',`${engine} needs exactly one correct option`);
 }
 if(w.revision==='variety-1'&&['choose-one','clue','odd-one-out'].includes(kind)&&answers.length!==1) fail('SINGLE_KIND_ANSWER',`${kind} needs exactly one answer`);
 if(kind==='choose-many'&&w.revision==='variety-1'&&answers.length<3) fail('CHOOSE_MANY_MINIMUM','Requires 3 correct options');
 if(kind==='odd-one-out') {
  // Explicitly test rule presence, not whether arbitrary prose makes that rule true.
  const s=norm(r.instruction?.en||'').toLowerCase();
  const explicit=r.oddOneOutRule||r.rule||w.oddOneOutRule;
  if(!explicit&&!/(?:not |doesn.t |does not |isn.t |is not |except |unlike |only |others? (?:are|have|show)|rest (?:are|have|show)|three \w+.*(?:share|have|are|show|describe|point)|different (?:color|colour|shape|size|number|kind)|outside that range|pattern: repeat|odd.*:|odd.*\.\s+\w|[.:].*odd|one.*(?:among|from|with|without|while|than))/.test(s)) fail('ODD_RULE_UNSTATED','State the property that makes one option different');
 }
 if(engine==='pair') {
  if(options.length<2||right.length!==options.length) fail('MATCH_SIDE_LENGTH','Equal left/right sides with at least two items required');
  if(pairs.length!==options.length||!sameSet(pairs.map(p=>p.left),ids)||!sameSet(pairs.map(p=>p.right),rids)) fail('MATCH_BIJECTION','Pairs must cover each left and right ID exactly once');
  if(!unique(right.map(o=>json(presentation(o,engine))))) fail('MATCH_TARGET_DUPLICATE','Right targets must have distinct visible pictures/text');
  if(!unique(options.map(o=>json(presentation(o,engine))))) fail('MATCH_SOURCE_DUPLICATE','Left sources must have distinct visible pictures/text');
 }
 if(engine==='sort') {
  if(options.length<2||bins.length<2||!unique(bids)||bids.some(id=>!nonempty(id))) fail('SORT_BINS','At least two options and two unique bins required');
  if(pairs.length!==options.length||!sameSet(pairs.map(p=>p.left),ids)||pairs.some(p=>!bids.includes(p.right))) fail('SORT_COVERAGE','Every option must map exactly once to an existing bin');
  if(bids.some(id=>!pairs.some(p=>p.right===id)))fail('EMPTY_SORT_BIN','Every displayed bin must have an item');
  if(!unique(bins.map(b=>json({asset:b.asset,label:b.label?.en}))))fail('SORT_BIN_DUPLICATE','Bins must be visibly distinct');
 }
 if(engine==='sequence') {
  if(options.length<2||!sameSet(answers,ids)) fail('SEQUENCE_PERMUTATION','Answer must be a permutation of all options');
  if(!unique(options.map(o=>json(presentation(o,engine)))))fail('SEQUENCE_AMBIGUOUS','Sequence positions need distinguishable choices');
 }
 if(engine==='memory') {
  if(options.length<2||options.length>6) fail('MEMORY_SIZE','Memory requires 2–6 distinct pictures');
  if(!unique(options.map(o=>json(visual(o)))))fail('MEMORY_VISUAL_DUPLICATE','Memory cards must differ visually, not only by labels or IDs');
 }
 if(engine==='count') {
  if(!integer(r.countTarget))fail('COUNT_TARGET','countTarget must be a nonnegative integer');
  const winner=options.find(o=>o.id===answers[0]);
  if(!winner||Number(winner.symbol??winner.value)!==r.countTarget)fail('COUNT_ANSWER','Selected number must equal countTarget');
  if(r.operation) {
   if(!['add','subtract'].includes(r.operation)||!Array.isArray(r.operands)||r.operands.length!==2||!r.operands.every(integer))fail('COUNT_OPERATION','Use add/subtract with two nonnegative integers');
   else if(r.countTarget!==(r.operation==='add'?r.operands[0]+r.operands[1]:r.operands[0]-r.operands[1]))fail('COUNT_ARITHMETIC','Operands do not produce countTarget');
  }
 }
 if(engine==='pattern') {
  const strip=r.patternItems||(r.pattern||[]).map(id=>options.find(o=>o.id===id)||null);
  if(strip.length<3||strip.filter(x=>x===null).length!==1) fail('PATTERN_GAP','Pattern needs at least three positions and exactly one missing item');
  if(r.missingIndex!==undefined&&strip[r.missingIndex]!==null)fail('PATTERN_MISSING_INDEX','missingIndex must identify the gap');
  if(Array.isArray(r.patternUnit)&&r.patternUnit.length&&r.missingIndex!==undefined) {
   const winner=options.find(o=>o.id===answers[0]);
   if(winner?.vocabularyKey&&winner.vocabularyKey!==r.patternUnit[r.missingIndex%r.patternUnit.length])fail('PATTERN_UNIT_ANSWER','Answer disagrees with the explicit vocabulary unit');
  }
 }
 if(['draw','trace'].includes(engine)) {
  if(!r.canvas||!Array.isArray(r.canvas.guide)||!Array.isArray(r.canvas.viewBox)||r.canvas.viewBox.length!==4) fail('DRAW_CANVAS','Drawing needs a four-number viewBox and guide array');
  if(engine==='trace'&&!r.canvas?.guide?.length&&!r.trace&&!r.guide) fail('TRACE_GUIDE','Tracing needs a visible guide');
  if(options.length||answers.length)fail('DRAW_OPTIONS','Drawing and tracing do not use option answers');
 }
 if(kind==='shadow-match') {
  if(!right.length)fail('SHADOW_TARGETS','Shadow matching requires right targets');
  const leftById=new Map(options.map(o=>[o.id,o]));
  const rightById=new Map(right.map(o=>[o.id,o]));
  for(const p of pairs) {
   const l=leftById.get(p.left),r=rightById.get(p.right); if(!l||!r)continue;
   if(r.asset) {
    if(!r.silhouette)fail('SHADOW_FLAG',`Target ${r.id} needs silhouette:true`);
    if(l.asset!==r.asset)fail('SHADOW_GEOMETRY',`Asset pair ${p.left}/${p.right} must have matching outlines`);
   } else if(r.shape) {
    const color=String(r.color||'').toLowerCase();
    if(!r.silhouette&&!/^#(?:0{3}|0{6}|[0-5][0-9a-f][0-5][0-9a-f][0-5][0-9a-f])$/.test(color)&&!['black','rgb(0,0,0)'].includes(color.replace(/\s/g,'')))fail('SHADOW_GEOMETRY_FILL',`Geometry target ${r.id} must render a dark silhouette`);
    if(l.shape!==r.shape||(l.rotation||0)!==(r.rotation||0)||(l.scale||1)!==(r.scale||1))fail('SHADOW_GEOMETRY',`Geometry pair ${p.left}/${p.right} must have matching outlines`);
   } else fail('SHADOW_RENDERABLE',`Target ${r.id} needs an asset silhouette or functional dark geometry`);
  }
 }
 // Identical displayed choices cannot be assigned contradictory answers/groups.
 for(const lang of ['id','en']) {
  const seen=new Map();
  for(const o of options) {
   let answer=answers.includes(o.id);
   if(engine==='sort')answer=pairs.find(p=>p.left===o.id)?.right;
   if(engine==='pair')answer=pairs.find(p=>p.left===o.id)?.right;
   if(!SELECT_ENGINES.has(engine)&&!['sort','pair'].includes(engine))continue;
   const key=json(presentation(o,engine,lang));
   if(seen.has(key)&&seen.get(key)!==answer)fail('IDENTICAL_CHOICE_DIFFERENT_ANSWER',`${lang}: identical displayed option ${o.id} has a different answer`);
   seen.set(key,answer);
  }
 }
 return {errors,warnings};
}

function inferredKind(w) {
 if(w.activityKind)return w.activityKind;
 if(w.engine==='identify')return (w.rounds?.[0]?.answer||w.answer||[]).length>1?'choose-many':'choose-one';
 if(w.engine==='compare')return 'choose-one';
 if(w.engine==='pair')return (w.rounds?.[0]?.rightOptions||w.rightOptions||[]).some(o=>o.silhouette)?'shadow-match':'match';
 return w.engine;
}
function audit(site,opts={}) {
 const errors=[],warnings=[],categoryStats=[],recordTaskSets=new Map(),presentations=new Map(),roundDuplicates=[];
 const read=(name)=>JSON.parse(fs.readFileSync(path.join(site,name),'utf8'));
 const cats=read('app/data/worksheet-categories.json'),index=read('app/data/worksheet-index.json'),atlases=read('app/data/art-atlases.json');
 const overlayRecords=new Map();
 for(const directory of opts.overlays||[]) for(const file of fs.readdirSync(directory).filter(f=>f.endsWith('.json'))) {
  const data=JSON.parse(fs.readFileSync(path.join(directory,file),'utf8'));
  if(Array.isArray(data))for(const w of data)if(w?.id&&w?.rounds)overlayRecords.set(w.id,w);
 }
 const assets=new Set(atlases.flatMap(a=>a.assets));
 const catIds=cats.map(c=>c.id);
 if(cats.length!==116||!sameSet(catIds,EXPECTED_CATEGORIES))issue(errors,'CATEGORY_STABILITY','catalogue','Expected the original 116 category IDs');
 if(!unique(catIds))issue(errors,'CATEGORY_IDS','catalogue','Duplicate category IDs');
 const records=[];
 for(const c of cats) {
  const filename=path.join(site,'content/worksheets',`${c.id}.json`);
  if(!fs.existsSync(filename)){issue(errors,'MISSING_CATEGORY_FILE',c.id,filename);continue;}
  const rows=JSON.parse(fs.readFileSync(filename,'utf8')).map(w=>overlayRecords.get(w.id)||w);
  if(opts.overlays?.length)for(const w of rows)w.activityKind=inferredKind(w);
  records.push(...rows);
  const expected=Array.from({length:24},(_,i)=>`${c.id}-${String(i+1).padStart(2,'0')}`);
  if(rows.length!==24||!sameSet(rows.map(w=>w.id),expected))issue(errors,'RECORD_ID_STABILITY',c.id,'Expected the original 24 record IDs, 01–24');
  const kinds=[...new Set(rows.map(w=>w.activityKind))].sort(),engines=[...new Set(rows.map(w=>w.engine))].sort();
  if(kinds.length<4)issue(errors,'CATEGORY_KIND_VARIETY',c.id,`Only ${kinds.length} kinds: ${kinds.join(', ')}`);
  if(engines.length<3)issue(errors,'CATEGORY_ENGINE_VARIETY',c.id,`Only ${engines.length} engines: ${engines.join(', ')}`);
  if(!opts.overlays?.length&&!sameSet(c.activityKinds||[],kinds))issue(errors,'CATEGORY_KIND_INDEX',c.id,'Category activityKinds do not match its records');
  categoryStats.push({id:c.id,records:rows.length,engines,kinds,changed:rows.filter(w=>w.revision==='variety-1').length});
  for(const w of rows) {
   if(w.category!==c.id)issue(errors,'CATEGORY_MEMBERSHIP',w.id,`Expected ${c.id}`);
   if(!KINDS.has(w.activityKind))issue(errors,'ACTIVITY_KIND',w.id,String(w.activityKind));
   if(!ENGINES.has(w.engine))issue(errors,'ENGINE',w.id,String(w.engine));
   if(KIND_ENGINES[w.activityKind]&&!KIND_ENGINES[w.activityKind].includes(w.engine))issue(errors,'KIND_ENGINE_MISMATCH',w.id,`${w.activityKind}/${w.engine}`);
   if(!Array.isArray(w.rounds)||w.rounds.length!==4){issue(errors,'FOUR_ROUNDS',w.id,'Exactly four rounds required');continue;}
   const roundHashes=[];
   for(const [i,r] of w.rounds.entries()) {
    const found=checkRound(w,r,i+1,{assets});errors.push(...found.errors);warnings.push(...found.warnings);
    const roundHash=semanticTask(w,r);roundHashes.push(roundHash);
    const parts=taskParts(w,r),presentHash=hash(parts.task),answerHash=hash(parts.answer);
    const location={id:w.id,round:i+1,changed:w.revision==='variety-1'};
    const prior=presentations.get(presentHash);
    if(prior&&prior.answerHash!==answerHash)issue(errors,'SAME_TASK_DIFFERENT_ANSWER',`${w.id}/round-${i+1}`,`Same presentation/instruction as ${prior.id}/round-${prior.round}, different answer`);
    else if(!prior)presentations.set(presentHash,{...location,answerHash});
   }
   if(!unique(roundHashes)) {
    const duplicateGroups=[...new Set(roundHashes)].map(h=>roundHashes.flatMap((x,i)=>x===h?[i+1]:[])).filter(a=>a.length>1);
    issue(w.revision==='variety-1'?errors:warnings,'DUPLICATE_ROUND_TASK',w.id,duplicateGroups);roundDuplicates.push({id:w.id,changed:w.revision==='variety-1',rounds:duplicateGroups});
   }
   // Record identity ignores record/round order, local IDs, and choice order.
   const setHash=hash(sorted(roundHashes)),group=recordTaskSets.get(setHash)||[];
   group.push({id:w.id,category:w.category,changed:w.revision==='variety-1'});recordTaskSets.set(setHash,group);
   for(const key of ROUND_FIELDS) if(w.rounds[0][key]!==undefined&&json(w[key])!==json(w.rounds[0][key]))issue(errors,'ROOT_ROUND_ZERO_STALE',w.id,`Top-level ${key} differs from first round`);
  }
 }
 if(records.length!==2784||!unique(records.map(w=>w.id)))issue(errors,'CATALOGUE_RECORDS','catalogue','Expected 2,784 unique records');
 if(index.length!==records.length||!sameSet(index.map(w=>w.id),records.map(w=>w.id))||!unique(index.map(w=>w.id)))issue(errors,'WORKSHEET_INDEX_IDS','index','Index IDs must cover records exactly once');
 const byId=new Map(records.map(w=>[w.id,w]));
 for(const item of opts.overlays?.length?[]:index) {
  const w=byId.get(item.id);if(!w)continue;
  for(const field of ['category','engine','activityKind','revision'])if(item[field]!==w[field])issue(errors,'WORKSHEET_INDEX_METADATA',item.id,`Index ${field} differs from full record`);
 }
 const duplicateTaskSets=[...recordTaskSets.values()].filter(a=>a.length>1).map(records=>({relation:records.every(r=>r.changed)?'changed-only':records.every(r=>!r.changed)?'retained-only':'changed-and-retained',records}));
 const counts={categories:cats.length,records:records.length,rounds:records.reduce((n,w)=>n+(w.rounds?.length||0),0),changedRecords:records.filter(w=>w.revision==='variety-1').length,errors:errors.length,warnings:warnings.length,duplicateRoundRecords:roundDuplicates.length,duplicateTaskSetGroups:duplicateTaskSets.length,duplicateTaskSetsChangedAndRetained:duplicateTaskSets.filter(x=>x.relation==='changed-and-retained').length,duplicateTaskSetsChangedOnly:duplicateTaskSets.filter(x=>x.relation==='changed-only').length};
 return {valid:!errors.length,counts,errors,warnings,categoryStats,roundDuplicates,duplicateTaskSets,limitations:['Structural and presentation checks do not certify real-world semantic truth or translation accuracy.','Changed records require four distinct rounds; pre-existing repeated rounds are reported as warnings.','Whole-record duplicate task sets are review findings, not failures; the report distinguishes changed and retained records.','RGB shadow atlases are supported by the existing high-contrast CSS; alpha is not an unconditional requirement.']};
}

function selfTest() {
 const T=s=>({id:s,en:s,zh:s,ar:s});
 const pic=(id,shape='circle')=>({id,shape,label:T(shape)});
 const make=(kind='choose-one',engine='identify')=>({id:'fixture',revision:'variety-1',activityKind:kind,engine});
 const base={instruction:T('Choose the circle.'),options:[pic('a'),pic('b','square')],answer:['a']};
 const tests=[];
 function negative(name,w,r,code){const got=checkRound(w,r,1).errors;assert(got.some(e=>e.code===code),`${name}: expected ${code}; got ${json(got)}`);tests.push(name);}
 assert.equal(checkRound(make(),base,1).errors.length,0);
 negative('selection references an absent ID',make(),{...base,answer:['missing']},'MISSING_ANSWER_OPTION');
 negative('new multi-select has at least three answers',make('choose-many'),{...base,options:[pic('a'),pic('b','square'),pic('c','star')],answer:['a','b']},'CHOOSE_MANY_MINIMUM');
 negative('multi-select requires a distractor',make('choose-many'),{...base,options:[pic('a'),pic('b','square'),pic('c','star')],answer:['a','b','c']},'NO_DISTRACTOR');
 negative('odd one out states its rule',make('odd-one-out'),{...base,instruction:T('Find the odd one out.')},'ODD_RULE_UNSTATED');
 negative('changed content has all four instruction languages',make(),{...base,instruction:{id:'Pilih',en:'Choose',zh:'选择'}},'MISSING_INSTRUCTION_LANGUAGE');
 const matching={instruction:T('Match each shape.'),options:[pic('a'),pic('b','square')],rightOptions:[pic('x'),pic('y','square')],pairs:[{left:'a',right:'x'},{left:'b',right:'y'}],answer:[]};
 assert.equal(checkRound(make('match','pair'),matching,1).errors.length,0);
 negative('matching is bijective',make('match','pair'),{...matching,pairs:[{left:'a',right:'x'},{left:'b',right:'x'}]},'MATCH_BIJECTION');
 negative('matching targets differ visibly',make('match','pair'),{...matching,rightOptions:[pic('x'),pic('y')]},'MATCH_TARGET_DUPLICATE');
 negative('memory pictures differ without labels',make('memory','memory'),{instruction:T('Find each pair.'),options:[pic('a'),{...pic('b'),label:T('Different text')}],answer:[]},'MEMORY_VISUAL_DUPLICATE');
 negative('count answer matches target',make('count','count'),{...base,countTarget:2,options:[{id:'a',symbol:'1',label:T('1')},{id:'b',symbol:'2',label:T('2')}]},'COUNT_ANSWER');
 negative('count operands agree',make('count','count'),{...base,countTarget:1,operation:'add',operands:[1,1],options:[{id:'a',symbol:'1',label:T('1')},{id:'b',symbol:'2',label:T('2')}]},'COUNT_ARITHMETIC');
 negative('sequence covers every option',make('sequence','sequence'),base,'SEQUENCE_PERMUTATION');
 negative('sort covers every option',make('sort','sort'),{...base,answer:[],bins:[{id:'x',label:T('x')},{id:'y',label:T('y')}],pairs:[{left:'a',right:'x'}]},'SORT_COVERAGE');
 negative('pattern has one gap',make('pattern','pattern'),{...base,patternItems:[pic('p'),null,null]},'PATTERN_GAP');
 negative('same presentation cannot carry another answer',make(),{...base,options:[pic('a'),pic('b')]},'IDENTICAL_CHOICE_DIFFERENT_ANSWER');
 negative('shadow target must actually render dark',make('shadow-match','pair'),matching,'SHADOW_GEOMETRY_FILL');
 const shadow={...matching,rightOptions:matching.rightOptions.map(o=>({...o,color:'#222222',silhouette:true}))};
 assert.equal(checkRound(make('shadow-match','pair'),shadow,1).errors.length,0);
 const permuted=clone(base);permuted.options.reverse();permuted.options.forEach(o=>o.id=`new-${o.id}`);permuted.answer=['new-a'];
 assert.equal(semanticTask(make(),base),semanticTask(make(),permuted),'Task identity ignores option order and local IDs');tests.push('task identity ignores option order and local IDs');
 assert.notEqual(semanticTask(make(),base),semanticTask(make(),{...base,answer:['b']}),'Task identity keeps answer relationships');tests.push('task identity preserves the answer mapping');
 assert.equal(json(taskParts(make(),base).task),json(taskParts(make(),{...base,answer:['b']}).task));tests.push('same-presentation fingerprint detects different answers');
 return {valid:true,negativeFixtures:tests.length,tests};
}

if(require.main===module) {
 const args=process.argv.slice(2);
 if(args.includes('--self-test')) console.log(JSON.stringify(selfTest(),null,2));
 else {
  const site=args.find(a=>!a.startsWith('--'));
  if(!site){console.error('Usage: node validate-variety.cjs SITE [--report report.json] | --self-test');process.exitCode=2;}
  else {
   try {
    const overlays=args.flatMap((x,i)=>x==='--overlay'?[args[i+1]]:[]);
    const result=audit(path.resolve(site),{overlays});
    const reportIndex=args.indexOf('--report');
    if(reportIndex>=0){if(!args[reportIndex+1])throw new Error('--report requires a path');fs.writeFileSync(args[reportIndex+1],JSON.stringify(result,null,2)+'\n');}
    console.log(JSON.stringify({valid:result.valid,...result.counts,errorCodes:result.errors.reduce((s,e)=>(s[e.code]=(s[e.code]||0)+1,s),{}),errorExamples:result.errors.slice(0,30)},null,2));
    process.exitCode=result.valid?0:1;
   }catch(e){console.error(e.stack||String(e));process.exitCode=2;}
  }
 }
}
module.exports={audit,checkRound,taskParts,semanticTask,visual,presentation,selfTest};
