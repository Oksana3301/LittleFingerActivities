"""Integrate hand-authored additions without changing existing worksheet IDs or art."""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/curriculum/learning-paths'
def read(path): return json.loads((ROOT / path).read_text())
def write(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')

parts = [json.loads(p.read_text()) for p in sorted(SOURCE.glob('expansion-*.json'))]
assert len(parts) == 4
groups = sorted([g for p in parts for g in p['groups']], key=lambda g:g['letter'])
coverage = [c for p in parts for c in p['coverage']]
added = sorted([w for p in parts for w in p['worksheets']], key=lambda w:w['category'])
old = [w for w in read('app/data/worksheet-index.json') if not w['id'].startswith('lf-')]
categories = [c for c in read('app/data/worksheet-categories.json') if not c['id'].startswith('path-')]
taxonomy = read('app/data/discovery-taxonomy.json')
taxonomy['categories'] = [c for c in taxonomy['categories'] if not c['id'].startswith('path-')]
extras = {'Q':['vehicle-count','vehicle-paths','vehicle-names'], 'W':['garage-tools','build-a-vehicle'],
 'I':['sports-kit','build-blocks'], 'U':['camping-kit','adventure-sort'], 'G':['hobby-patterns'],
 'K':['dinosaur-names'], 'V':['space-pairs','sky-names'], 'H':['memory-objects','memory-shapes','memory-colors']}
default_skills = {'H':['logic-math','memory'],'I':['creative-motor'],'J':['visual','spatial'],
 'K':['language','visual'],'L':['language','life-social'],'M':['language','life-social'],
 'N':['language','life-social'],'O':['language','life-social'],'P':['language','logic-math'],
 'Q':['visual','spatial'],'R':['language','logic-math'],'S':['language','life-social'],'T':['language','spatial']}
for g in groups:
    letter=g['letter']; category='path-'+letter.lower()
    g['skills'] = g['skills'] or default_skills.get(letter,['language'])
    g['categories'] = list(dict.fromkeys(g['categories']+extras.get(letter,[])+[category]))
    sheets=[w for w in added if w['category']==category]
    assert sheets, category
    kinds=[]
    for w in sheets:
        if w['engine'] in ['pair','sequence']:
            for option in w['options']+w.get('rightOptions',[]):
                if str(option.get('symbol','')).isdigit() and option['label']['en']!=option['symbol']:
                    option['symbol']='•'
        if w['engine']=='pair':
            right=list(reversed(w['rightOptions']))
            targets={p['left']:p['right'] for p in w['pairs']}
            if all(targets[o['id']]==right[i]['id'] for i,o in enumerate(w['options'])):
                w['rightOptions']=w['rightOptions'][1:]+w['rightOptions'][:1]
        w['partCount']=1
        w['duration']=10 if w['engine']=='explore' else 5
        w['skills']=g['skills']
        w['revision']='paths-v1'
        if w['id'].startswith('lf-z-islam-'): w['faith']=True
        kind=w.get('activityKind') or ('match' if w['engine']=='pair' else ('choose-many' if len(w['answer'])>1 else 'choose-one') if w['engine']=='identify' else w['engine'])
        w['activityKind']=kind
        kinds.append(kind)
    write('public/worksheets/'+category+'.json',sheets)
    title={l:label+suffix for l,label,suffix in [(l,g['title'][l],{'id':' · Penemuan baru','en':' · New discoveries','zh':' · 新发现','ar':' · اكتشافات جديدة'}[l]) for l in ['id','en','zh','ar']]}
    categories.append({'id':category,'group':'learning','asset':g['asset'],'title':title,
      'description':{'id':'Tujuan belajar baru melalui pilihan, kreasi, dan eksplorasi bersama pendamping.',
      'en':'New learning goals through choices, creating, and exploring with a grown-up.',
      'zh':'通过选择、创作和与大人一起探索，体验新的学习目标。','ar':'أهداف تعلم جديدة عبر الاختيار والإبداع والاستكشاف مع شخص بالغ.'},
      'engine':sheets[0]['engine'],'age':min(w['age'] for w in sheets),'worksheetCount':len(sheets),'activityKinds':list(dict.fromkeys(kinds))})
    theme=next((c['theme'] for c in taxonomy['categories'] if c['id'] in g['categories']),'logic')
    taxonomy['categories'].append({'id':category,'theme':theme,'skills':g['skills']})
ids={w['id'] for w in old+added}
assert len(ids)==len(old)+len(added), 'Duplicate worksheet ID'
assert len({(c['group'],c['subtopic']) for c in coverage})==len(coverage)
assert all(i in ids or i=='telur-dan-hewan' for c in coverage for i in c['links']), 'Unknown coverage link'
assert {c['id'] for c in categories}<={c for g in groups for c in g['categories']}, 'Ungrouped category'
assert all(c in {x['id'] for x in categories} for g in groups for c in g['categories'])
write('app/data/worksheet-index.json',old+added)
write('app/data/worksheet-categories.json',categories)
write('app/data/discovery-taxonomy.json',taxonomy)
write('app/data/learning-groups.json',groups)
write('public/specs/learning-subtopics.json',coverage)
write('app/data/learning-coverage.json',[{k:c[k] for k in ['group','subtopic','label','links','status']} for c in coverage])
summary={'worksheets':len(old)+len(added),'categories':len(categories),'learningGroups':len(groups),
 'subtopics':len(coverage),'newWorksheets':len(added),'newEngines':dict(Counter(w['engine'] for w in added)),
 'coverage':dict(Counter(c['status'] for c in coverage)),
 'limits':'Coverage is introductory, not mastery or exhaustive curriculum certification. Guided exploration is caregiver-reported and excluded from answer accuracy.'}
report=read('public/specs/workbook-catalogue-report.json')
report.update({'worksheets':len(old)+len(added),'categories':len(categories),'rounds':sum(w.get('partCount',4) for w in old+added),'engines':sorted({w['engine'] for w in old+added})})
write('public/specs/workbook-catalogue-report.json',report)
write('public/specs/learning-paths-coverage.json',summary)
print(json.dumps(summary,ensure_ascii=False))
