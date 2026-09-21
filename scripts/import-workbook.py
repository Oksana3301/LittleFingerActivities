"""Import the authored four-round practice catalogue; preserve answer keys."""
import json, sys, pathlib, copy
source=pathlib.Path(sys.argv[1])
root=pathlib.Path(__file__).resolve().parent.parent
raw=json.loads((source/'worksheets-flat.json').read_text())
curr=json.loads((source/'curriculum.json').read_text())
colors={x['id']:x.get('hex',x.get('value','#73955c')) for x in curr.get('colors',[]) } if isinstance(curr.get('colors'),list) else {}
colors.update({'red':'#cc735f','blue':'#719ab7','green':'#789963','yellow':'#e2b947','orange':'#dc9862','purple':'#9f85ad','pink':'#d99aab','brown':'#986f50','black':'#464b43','white':'#eee9db'})
shapeNames={'circle':('lingkaran','circle'),'square':('persegi','square'),'triangle':('segitiga','triangle'),'rectangle':('persegi panjang','rectangle'),'star':('bintang','star'),'heart':('hati','heart'),'oval':('oval','oval'),'diamond':('belah ketupat','diamond'),'hexagon':('segienam','hexagon'),'pentagon':('segilima','pentagon')}
def pic(o):
 o=copy.deepcopy(o)
 if o.get('color') in colors:o['color']=colors[o['color']]
 if not o.get('label'):
  if o.get('kind')=='measurement':o['label']={'id':'Bentuk','en':'Shape'}
  elif o.get('direction'):o['label']={'id':{'up':'Atas','down':'Bawah','left':'Kiri','right':'Kanan'}[o['direction']],'en':o['direction'].title()}
  else:
   n=shapeNames.get(o.get('shape'),(o.get('symbol','Gambar'),o.get('symbol','Picture')));o['label']={'id':n[0],'en':n[1]}
 if o.get('kind')=='quantity':o['label']={'id':'Kelompok gambar','en':'Picture group'}
 return o
def normalize(r,engine):
 d={k:copy.deepcopy(v) for k,v in r.items() if k in ['instruction','answer','countTarget','countAsset','operation','operands','expression','languageOfTask','scene','layout','completion']}
 d['options']=[pic(o) for o in r.get('options',[])]
 if engine=='memory':
  used=set();opts=[]
  for o in d['options']:
   key=o.get('pairKey',o['id'])
   if key not in used: used.add(key);o['id']=key;opts.append(o)
  d['options']=opts
 if 'rightOptions' in r:d['rightOptions']=[pic(o) for o in r['rightOptions']]
 if 'pairs' in r:d['pairs']=[{'left':p[0],'right':p[1]} for p in r['pairs']]
 if 'patternItems' in r:d['patternItems']=[pic(o) if o else None for o in r['patternItems']]
 if 'reference' in r:d['reference']=pic(r['reference'])
 if 'canvas' in r:
  d['canvas']=copy.deepcopy(r['canvas'])
  for g in d['canvas'].get('guide',[]):
   if g.get('kind')=='pattern-strip':g['items']=[pic(p) for p in g['items']]
 return d
out=[]
for w in raw:
 base={k:w[k] for k in ['id','category','title','engine','variant','difficulty']}
 base['age']=w['minAge'];base['ageRange']=w['age']
 base['title']={k:v.split(' · ')[0] for k,v in base['title'].items()}
 base['rounds']=[normalize(r,w['engine']) for r in w['rounds']]
 base.update(base['rounds'][0]);out.append(base)
assets={'animal-names':'hen','produce-names':'carrot','garden-names':'watering-can','vehicle-names':'car','sky-names':'rocket','home-names':'umbrella','colors':'flower','shapes':'star','size':'lion','length':'cucumber','height':'tree','thickness':'trowel','same-different':'butterfly','directions':'boat','positions':'ladybug','symmetry':'butterfly','object-pairs':'rabbit','silhouette-pairs':'dog','color-pairs':'flower','shape-pairs':'star','number-pairs':'apple','uppercase-pairs':'bird','lowercase-pairs':'cat','letter-case':'squirrel','initial-letters':'apple','vowels':'sun','consonants':'leaf','count-to-5':'duck','count-to-10':'apple','count-6-to-15':'bee','quantity-pairs':'carrot','compare-quantity':'banana','ascending':'sprout','descending':'leaf','missing-number':'moon','add-to-5':'tomato','add-to-10':'carrot','subtract-to-5':'banana','subtract-to-10':'apple','pattern-ab':'train','pattern-abc':'butterfly','pattern-aab-abb':'flower','growing-pattern':'tree','memory-objects':'cat','memory-shapes':'star','memory-colors':'butterfly','trace-lines':'boat','trace-curves':'snail','trace-shapes':'star','trace-numbers':'duck','trace-letters':'bird','finish-picture':'flower','draw-to-count':'apple','draw-pattern':'leaf','spatial-drawing':'rocket','imagine-draw':'sun'}
categories=[]
for c in curr['categories']:
 categories.append({**c,'asset':assets[c['id']],'age':c['ageRange'][0],'description':{'id':'24 lembar · 4 bagian singkat per lembar','en':'24 sheets · 4 short parts per sheet'}})
pub=root/'content/worksheets';pub.mkdir(exist_ok=True)
for c in categories:
 (pub/(c['id']+'.json')).write_text(json.dumps([w for w in out if w['category']==c['id']],ensure_ascii=False,separators=(',',':')))
index=[]
for w in out:
 v={k:w[k] for k in ['id','category','title','engine','variant','age','ageRange','difficulty','instruction']};v['options']=w['options'][:3];v['answer']=[];index.append(v)
(root/'app/data/worksheet-index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')))
(root/'app/data/worksheet-categories.json').write_text(json.dumps(categories,ensure_ascii=False,separators=(',',':')))
report={'worksheets':len(out),'categories':len(categories),'rounds':sum(len(x['rounds']) for x in out),'engines':sorted(set(x['engine'] for x in out)),'classification':'Practice variations, not 1,344 distinct activity types','editorialReview':'not independently reviewed'}
(root/'public/specs/workbook-catalogue-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
