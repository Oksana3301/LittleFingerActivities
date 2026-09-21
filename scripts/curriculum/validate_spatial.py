import json, math, itertools, collections
from pathlib import Path
from PIL import Image
import numpy as np
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
SITE=args.site
records=[w for category in ['transport-play','picture-details','picture-puzzles','spatial-layouts','route-adventures'] for w in json.loads((SITE/'public/worksheets'/f'{category}.json').read_text())]
atlases=json.loads((SITE/'app/data/art-atlases.json').read_text())
asset_map={asset:(a,i) for a in atlases for i,asset in enumerate(a['assets'])}
errors=[];warnings=[];stats=collections.Counter();images={};semsets=collections.defaultdict(list);roundsets=collections.defaultdict(list);pixelstats=[]
def ck(v,msg,ctx):
 if not v:errors.append({'task':ctx,'issue':msg})
def textcheck(d,ctx):
 if isinstance(d,dict):
  if 'en' in d and 'id' in d:
   ck(all(isinstance(d.get(k),str) and d[k].strip() for k in ['id','en','zh','ar']),'missing four-language text',ctx)
  for k,v in d.items():textcheck(v,ctx+'.'+k)
 elif isinstance(d,list):
  for i,v in enumerate(d):textcheck(v,ctx+f'[{i}]')
def visual(p):
 return json.dumps({k:p[k] for k in ['asset','shape','symbol','rotation','color','scale','crop','silhouette','value','kind'] if k in p},sort_keys=True)
def assetpixels(asset,crop=None):
 a,i=asset_map[asset];f=a['file'];n=a['size']
 if f not in images:images[f]=np.asarray(Image.open(SITE/'public/assets/workbook'/f'{f}.webp').convert('RGB'))
 im=images[f];h,w=im.shape[:2];x,y=i%n,i//n
 cell=im[round(y*h/n):round((y+1)*h/n),round(x*w/n):round((x+1)*w/n)]
 if crop:
  hh,ww=cell.shape[:2];cell=cell[round(crop['y']*hh):round((crop['y']+crop['height'])*hh),round(crop['x']*ww):round((crop['x']+crop['width'])*ww)]
 return cell
def inspect(d,ctx):
 if isinstance(d,dict):
  if 'asset' in d:ck(d['asset'] in asset_map,'unknown asset '+d['asset'],ctx)
  if 'crop' in d:
   c=d['crop'];ck(all(isinstance(c.get(k),(int,float)) and math.isfinite(c[k]) for k in ['x','y','width','height']),'crop nonnumeric',ctx)
   ck(c['x']>=0 and c['y']>=0 and c['width']>0 and c['height']>0 and c['x']+c['width']<=1 and c['y']+c['height']<=1,'crop outside normalized bounds',ctx)
   px=assetpixels(d['asset'],c);ink=float((px.min(axis=2)<220).mean());pixelstats.append({'task':ctx,'asset':d['asset'],'inkFraction':round(ink,4)})
   ck(ink>.02,'crop mostly blank',ctx)
  for k,v in d.items():inspect(v,ctx+'.'+k)
 elif isinstance(d,list):
  for i,v in enumerate(d):inspect(v,ctx+f'[{i}]')
def semantic(r):
 e=r['engine'];opts={p['id']:visual(p) for p in r['options']};z={'engine':e,'kind':r['activityKind']}
 if e=='puzzle':z.update(image=r['puzzle']['image']['asset'],grid=[r['puzzle']['columns'],r['puzzle']['rows']],missing=sorted(r['puzzle']['missing']))
 elif e=='placement':z.update(grid=[r['placement']['columns'],r['placement']['rows']],target=sorted([(opts[p['left']],p['right']) for p in r['pairs']]))
 elif e=='route':z.update(start=r['route']['start']['asset'],end=r['route']['end']['asset'],geometry=[(p['x'],p['y']) for p in r['route']['points']],decoys=[(p['x'],p['y']) for p in r['route']['decoys']])
 elif e=='pair':z['pairs']=sorted((opts[p['left']],visual(next(o for o in r['rightOptions'] if o['id']==p['right']))) for p in r['pairs'])
 elif e=='memory':z['cards']=sorted(opts.values())
 elif e=='sequence':z['order']=[opts[o] for o in r['answer']]
 elif e=='pattern':z.update(pattern=[visual(p) if p else None for p in r['patternItems']],choices=sorted(opts.values()),answer=[opts[o] for o in r['answer']])
 elif e=='trace':z['guide']=r['canvas']['guide']
 else:z.update(instruction=r['instruction']['en'],choices=sorted(opts.values()),answer=sorted(opts[o] for o in r['answer']),reference=visual(r['reference']) if r.get('reference') else None)
 return json.dumps(z,sort_keys=True)
ck(len(records)==120,'expected120worksheets','root');ck(len({w['id'] for w in records})==120,'duplicateworksheetids','root')
for w in records:
 ck(len(w['rounds'])==4,'expected4rounds',w['id']);fingerprints=[]
 for i,r in enumerate(w['rounds']):
  ctx=w['id']+f'/{i}';stats[r['engine']]+=1;textcheck(r,ctx);inspect(r,ctx);ids=[p['id'] for p in r['options']]
  ck(len(ids)==len(set(ids)),'duplicate option ids',ctx)
  e=r['engine'];v=[visual(p) for p in r['options']]
  ck(len(v)==len(set(v)),'visually duplicate choices',ctx)
  if e in ['identify','pattern']:
   ck(bool(r['answer']) and len(set(r['answer']))==len(r['answer']) and set(r['answer'])<=set(ids),'invalid answer IDs',ctx)
  if r['activityKind']=='picture-detail':
   answer=next(o for o in r['options'] if o['id']==r['answer'][0]);ck(answer['asset']==r['reference']['asset'] and len(r['answer'])==1,'crop reference does not match answer',ctx)
   ck(r['reference']['label']['en']=='Picture detail' and r['reference'].get('showLabel') is False,'crop reference reveals answer',ctx)
  if r['activityKind']=='choose-many':
   wheels={'car','bus','bicycle','train','tractor','fire-truck','police-car','ambulance','scooter','motorcycle','dump-truck'}
   ck({o['id'] for o in r['options'] if o['asset'] in wheels}==set(r['answer']) and len(r['answer'])==3,'wheel grouping contradicts answer',ctx)
  if r['activityKind']=='odd-one-out':
   ins=r['instruction']['en'];negative='cannot fly' in ins or 'is not' in ins or 'has no' in ins
   allowed={'helicopter','airplane'} if 'cannot fly' in ins else {'boat','sailboat','submarine'} if 'water vehicle' in ins else {'car','bus','bicycle','train','tractor','fire-truck','police-car','ambulance','scooter','motorcycle','dump-truck'} if 'no wheels' in ins else {'car','bus','bicycle','train','tractor','fire-truck','police-car','ambulance','scooter','motorcycle','dump-truck','boat','sailboat','submarine','airplane','helicopter'}
   ck(negative and {o['id'] for o in r['options'] if o['asset'] not in allowed}==set(r['answer']),'exception rule contradicts answer',ctx)
  if e in ['pair','puzzle','placement']:
   pairs=r['pairs'];ck(len(pairs)==len(ids) and {p['left'] for p in pairs}==set(ids),'pair coverage',ctx);ck(len({p['right'] for p in pairs})==len(pairs),'duplicate target',ctx)
  if e=='pair':
   right={p['id']:p for p in r['rightOptions']};ck(len(right)==len(r['rightOptions']),'duplicate right IDs',ctx)
   for p in pairs:ck(p['right'] in right and next(o for o in r['options'] if o['id']==p['left'])['asset']==right[p['right']]['asset'],'mismatched picture pairs',ctx)
  if e=='puzzle':
   p=r['puzzle'];n=p['rows']*p['columns'];ck(p['rows'] in [2,3] and p['columns'] in [2,3],'puzzle grid range',ctx);ck(len(set(p['missing']))==len(p['missing']) and all(isinstance(t,int) and 0<=t<n for t in p['missing']),'badmissing',ctx);ck(len(ids)==len(p['missing']),'missingpiececoverage',ctx)
   for pair in pairs:
    o=next(o for o in r['options'] if o['id']==pair['left']);target=int(pair['right'].replace('slot-',''));expected={'x':target%p['columns']/p['columns'],'y':target//p['columns']/p['rows'],'width':1/p['columns'],'height':1/p['rows']}
    ck(target in p['missing'] and o['crop']==expected and o['asset']==p['image']['asset'],'piece crop mismatches target',ctx)
  if e=='placement':
   p=r['placement'];n=p['rows']*p['columns'];ck(p['rows'] in [2,3] and p['columns'] in [2,3],'placement grid range',ctx);ck(len(p['cells'])==n,'cell labels missing',ctx);ck(len({x['cell'] for x in p['example']})==len(p['example']),'duplicate examplecell',ctx)
   expected={x['option']:'cell-'+str(x['cell']) for x in p['example']};ck(expected=={p['left']:p['right'] for p in pairs},'example answer mismatch',ctx)
   for x in p['example']:ck(isinstance(x['cell'],int) and 0<=x['cell']<n,'cell outsidegrid',ctx)
  if e=='route':
   p=r['route'];ck(3<=len(p['points'])<=6,'route length',ctx);ck(r['answer']==['step-'+str(j) for j in range(len(p['points']))],'route answer mismatch',ctx)
   for x in p['points']+p['decoys']:ck(all(isinstance(x[k],(int,float)) and math.isfinite(x[k]) and 8<=x[k]<=92 for k in ['x','y']),'route coordinates',ctx)
   points=[(x['x'],x['y']) for x in p['points']];ck(all(math.dist(a,b)>=18 for a,b in itertools.combinations(points,2)),'overlapping route targets',ctx)
   for d in p['decoys']:ck(all(math.dist((d['x'],d['y']),x)>24 for x in points),'decoy overlaps target',ctx)
   for d in p['decoys']:
    for a,b in zip(points,points[1:]):
     dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((d['x']-a[0])*dx+(d['y']-a[1])*dy)/(dx*dx+dy*dy)))
     ck(math.hypot(d['x']-a[0]-t*dx,d['y']-a[1]-t*dy)>10,'outside-route decoy is on line',ctx)
  if e=='memory':ck(2<=len(ids)<=6,'memory size',ctx)
  if e=='sequence':ck(sorted(r['answer'])==sorted(ids),'sequence coverage',ctx)
  if e=='pattern':
   pattern=r['patternItems'];ck(sum(p is None for p in pattern)==1,'patternblankcount',ctx)
   filled=[next(o['asset'] for o in r['options'] if o['id']==r['answer'][0]) if p is None else p['asset'] for p in pattern]
   ck(any(all(filled[j]==filled[j%k] for j in range(len(filled))) for k in [2,3]),'pattern answer rule',ctx)
  sem=semantic(r);fingerprints.append(sem);roundsets[(w['category'],sem)].append(ctx)
 ck(len(set(fingerprints))==4,'repeated taskwithinworksheet',w['id']);semsets[(w['category'],tuple(sorted(fingerprints)))].append(w['id'])
report={'worksheets':len(records),'rounds':sum(stats.values()),'engineCounts':dict(stats),'errors':errors,'warnings':warnings,'sameCategoryDuplicateWorksheets':[v for v in semsets.values() if len(v)>1],'sameCategoryRepeatedRounds':[v for v in roundsets.values() if len(v)>1],'lowestCropInk':sorted(pixelstats,key=lambda p:p['inkFraction'])[:15]}
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))

if errors or report['sameCategoryDuplicateWorksheets'] or report['sameCategoryRepeatedRounds']: raise SystemExit(1)
