"""Merge reviewed, disjoint category bundles and refresh the lazy catalogue index."""
import json, pathlib, sys
root=pathlib.Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
engines={'pair':'match','identify':'choose-one','compare':'choose-one'}
def kind(w):
 if w.get('activityKind'):return w['activityKind']
 if w['category']=='silhouette-pairs' and w['engine']=='pair':return 'shadow-match'
 if w['engine']=='identify' and len(w['answer'])>1:return 'choose-many'
 return engines.get(w['engine'],w['engine'])
cats=read(root/'app/data/worksheet-categories.json');known={c['id'] for c in cats};used=set()
for src in map(pathlib.Path,sys.argv[1:]):
 directory=src/'bundles' if (src/'bundles').is_dir() else src
 for p in sorted(directory.glob('*.json')):
  if p.stem not in known:continue
  assert p.stem not in used,p.stem;used.add(p.stem)
  incoming=read(p);old=read(root/'public/worksheets'/p.name)
  assert [w['id'] for w in incoming]==[w['id'] for w in old],p.stem
  assert len(incoming)==24 and all(len(w['rounds'])==4 for w in incoming)
  write(root/'public/worksheets'/p.name,incoming)
assert used==known,{'missing':list(known-used)}
records=[];coverage=[]
for c in cats:
 p=root/'public/worksheets'/(c['id']+'.json');items=read(p)
 for w in items:w['activityKind']=kind(w)
 kinds=sorted({w['activityKind'] for w in items});renders=sorted({w['engine'] for w in items})
 assert len(kinds)>=4,(c['id'],kinds)
 assert len(renders)>=3,(c['id'],renders)
 c['activityKinds']=kinds;coverage.append({'category':c['id'],'kinds':kinds,'engines':renders,'revised':sum(bool(w.get('revision')) for w in items)})
 write(p,items);records.extend(items)
index=[]
for w in records:
 item={k:w[k] for k in ['id','category','title','engine','variant','age','ageRange','difficulty','instruction','activityKind'] if k in w}
 item.update(options=w['options'][:3],answer=[])
 if w.get('revision'):item['revision']=w['revision']
 index.append(item)
write(root/'app/data/worksheet-index.json',index);write(root/'app/data/worksheet-categories.json',cats)
report={'categories':len(cats),'worksheets':len(records),'rounds':sum(len(w['rounds']) for w in records),'minimumKindsPerCategory':min(len(x['kinds']) for x in coverage),'minimumEnginesPerCategory':min(len(x['engines']) for x in coverage),'revisedWorksheets':sum(x['revised'] for x in coverage),'coverage':coverage}
(root/'public/specs/activity-variety-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='coverage'}))
