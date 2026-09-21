const fs=require('fs'),path=require('path'),vm=require('vm'),ts=require('typescript'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
function load(file){const full=path.join(root,file),module={exports:{}};const code=ts.transpileModule(fs.readFileSync(full,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;vm.runInNewContext(code,{module,exports:module.exports,require:n=>JSON.parse(fs.readFileSync(path.resolve(path.dirname(full),n),'utf8'))});return module.exports}
const {worksheetProgressKey,getActivityKind,interleaveActivities}=load('app/data/activity-kinds.ts');
const {resolveWorksheetRound}=load('app/data/workbook.ts');
const oldKey=worksheetProgressKey('animal-names-17',0),newKey=worksheetProgressKey('animal-names-17',0,'variety-1');
const saved={[oldKey]:{complete:true,selected:['old-card']}};
assert.equal(oldKey,'animal-names-17~0');assert.notEqual(newKey,oldKey);assert.equal(saved[newKey],undefined);assert.equal(saved[oldKey].complete,true);
const base={id:'example',category:'math-stories',title:{id:'Contoh',en:'Example'},engine:'identify',options:[],answer:[],reference:{id:'stale'},map:{places:[{option:'stale',lat:0,lng:0,country:'id'}]},operation:'add',operands:[1,2],rounds:[{engine:'identify',reference:{id:'first'},options:[],answer:[]},{engine:'pair',options:[],answer:[],pairs:[]}]};
const active=resolveWorksheetRound(base,1);assert.equal(active.engine,'pair');assert.equal(active.reference,undefined);assert.equal(active.operation,undefined);assert.equal(active.operands,undefined);assert.equal(active.map,undefined);assert.equal(active.title,base.title);assert.equal(resolveWorksheetRound(base,0).reference.id,'first');
assert.equal(getActivityKind({engine:'identify',answer:['a','b','c']}),'choose-many');assert.equal(getActivityKind({engine:'identify',activityKind:'odd-one-out',answer:['a']}),'odd-one-out');
console.log('PASS revised activities isolate previous progress while preserving history');
console.log('PASS rounds clear stale reference/arithmetic fields and preserve metadata');
console.log('PASS selection kinds preserve multi-answer and exception semantics');

const choices=[{id:'a',engine:'identify'},{id:'b',engine:'identify'},{id:'c',engine:'pair'},{id:'d',engine:'pair'},{id:'e',engine:'memory'}];
assert.equal(interleaveActivities(choices).map(x=>x.id).join(','),'a,c,e,b,d');
assert.equal(choices.map(x=>x.id).join(','),'a,b,c,d,e');
console.log('PASS activity order alternates types without changing source IDs or order');
