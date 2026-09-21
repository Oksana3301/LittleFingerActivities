import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text())
coverage=read('public/specs/learning-subtopics.json')
expected=read('scripts/curriculum/learning-paths/source-subtopics.json')
assert {(c['group'],c['subtopic']) for c in expected}=={(c['group'],c['subtopic']) for c in coverage}
assert len(coverage)==len(expected)==583
groups=read('app/data/learning-groups.json')
assert ''.join(g['letter'] for g in groups)=='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
assets=read('app/data/art-labels.json')
index=read('app/data/worksheet-index.json')
ids={w['id'] for w in index}
assert len(ids)==len(index)
def text4(value,context):
    assert isinstance(value,dict) and all(isinstance(value.get(l),str) and value[l].strip() for l in ['id','en','zh','ar']),context
for c in coverage:
    assert all(i in ids or i=='telur-dan-hewan' for i in c['links']),c
    text4(c['label'],c['subtopic']);text4(c['note'],c['subtopic'])
    assert c['label']['id']==c['subtopic']
count=0; fingerprints=set()
for category in read('app/data/worksheet-categories.json'):
    if not category['id'].startswith('path-'):continue
    data=read('content/worksheets/'+category['id']+'.json')
    assert len(data)==category['worksheetCount']
    for w in data:
        count+=1
        assert w['partCount']==1 and not w.get('rounds')
        assert w['category']==category['id']
        assert w['faith'] if w['id'].startswith('lf-z-islam-') else not w.get('faith')
        for field in ['title','instruction','offscreen']:text4(w[field],w['id']+'.'+field)
        fingerprint=(w['engine'],w['instruction']['en'])
        assert fingerprint not in fingerprints, w['id']+' duplicates new task'
        fingerprints.add(fingerprint)
        options=w['options'];optionids={o['id'] for o in options}
        assert len(options)==len(optionids)
        for o in options+w.get('rightOptions',[])+w.get('bins',[]):
            text4(o['label'],w['id']+' '+o['id'])
            if o.get('asset'):assert o['asset'] in assets,(w['id'],o['asset'])
        if w['engine']=='identify':assert w['answer'] and set(w['answer'])<=optionids
        if w['engine']=='sequence':assert set(w['answer'])==optionids and len(w['answer'])==len(options)
        if w['engine']=='pair':
            right={o['id'] for o in w['rightOptions']}
            assert {p['left'] for p in w['pairs']}==optionids
            assert {p['right'] for p in w['pairs']}==right
        if w['engine']=='sort':
            assert {p['left'] for p in w['pairs']}==optionids
            assert {p['right'] for p in w['pairs']}<={b['id'] for b in w['bins']}
        if w['engine']=='explore':assert not w['answer'] and 2<=len(options)<=4 and w['completion']['mode']=='exploration'
        for goal in w.get('completion',{}).get('goals',[]):text4(goal,w['id']+' goal')
        if w.get('canvas'):
            assert w['canvas']['viewBox']==[0,0,400,300]
            assert all(g['kind'] in ['line','circle','path','trace-glyph','shape-outline','asset','pattern-strip'] for g in w['canvas']['guide']),w['id']
print(f'PASS {count} new worksheets; 583 exact subtopics; 26 groups; four-language content; references; answer contracts; supported canvas guides')
print('Coverage:',dict(Counter(c['status'] for c in coverage)))
