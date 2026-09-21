#!/usr/bin/env python3
"""Independent validator for published JSON: never imports the authoring generator.
Answers are inferred from bilingual prompts, public picture data, basic arithmetic,
and an explicit independent category taxonomy. Also checks semantic variation and
negative mutation fixtures for every category.
"""
from __future__ import annotations
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import re

CARD_CATEGORIES={
 'road-vehicles':('identify','vehicles'), 'air-water-vehicles':('sort','vehicles'),
 'construction-vehicles':('pair','vehicles'), 'vehicle-count':('count','vehicles'),
 'garage-tools':('pair','mechanics'), 'machine-parts':('identify','mechanics'),
 'build-a-vehicle':('sequence','mechanics'), 'workshop-sort':('sort','mechanics'),
 'sports-kit':('pair','hobbies'), 'camping-kit':('memory','hobbies'),
 'hobby-patterns':('pattern','hobbies'), 'vehicle-paths':('trace','vehicles'),
 'dinosaur-names':('identify','hobbies'), 'robot-drawing':('draw','mechanics'),
 'build-blocks':('compare','hobbies'), 'adventure-sort':('sort','hobbies'),
}
AIR={'airplane','helicopter'}
WATER={'ship','sailboat','submarine','boat'}
TOOLS={'hammer','wrench','screwdriver','pliers','saw','drill'}
PARTS={'gear','wheel','bolt','nut','spring','pulley'}
DINOSAURS={'t-rex','triceratops','stegosaurus'}
CAMP={'tent','backpack','compass','binoculars','flashlight'}
ROAD={'bus','fire-truck','ambulance','police-car','tractor','motorcycle','scooter','dump-truck','car','bicycle'}
CONSTRUCTION={'excavator','bulldozer','crane','dump-truck','tractor'}
SPORT={'football','basketball','badminton-racket','tennis-racket','kite','skateboard','bicycle','helmet'}
ALL_VEHICLES=ROAD|AIR|WATER|CONSTRUCTION|{'train'}
ALLOWED_ASSETS=ALL_VEHICLES|TOOLS|PARTS|DINOSAURS|CAMP|SPORT|{'robot','traffic-cone','helmet','toolbox','building-blocks','fossil','water-glass','umbrella','book','pencil'}
SORT_RULES={
 'air-water-vehicles':({'air':AIR,'water':WATER},{'air':('Kendaraan udara','Air vehicles'),'water':('Kendaraan air','Water vehicles')}),
 'workshop-sort':({'tools':TOOLS,'parts':PARTS},{'tools':('Perkakas','Tools'),'parts':('Bagian mesin','Machine parts')}),
 'adventure-sort':({'camp':CAMP,'dino':DINOSAURS|{'fossil'}},{'camp':('Perlengkapan berkemah','Camping kit'),'dino':('Dinosaurus dan fosil','Dinosaurs and fossils')}),
}
POOLS={
 'road-vehicles':ROAD,'construction-vehicles':CONSTRUCTION,'garage-tools':TOOLS|{'toolbox'},
 'machine-parts':PARTS,'sports-kit':SPORT,'camping-kit':CAMP|{'water-glass','umbrella'},
 'dinosaur-names':DINOSAURS,
}


def fingerprint(r,engine):
    """Ignore IDs, card order, and stylistic prompt rewording for variation counts."""
    def identity(o):
        return o.get('asset') or f"{o.get('kind')}:{o.get('value')}:{o.get('shape')}"
    byid={o['id']:o for o in r['options']}
    chosen=[identity(byid[x]) for x in r['answer'] if x in byid]
    result={'options':sorted(identity(o) for o in r['options']),
            'answer':chosen if engine=='sequence' else sorted(chosen)}
    if engine=='count': result.update(asset=r.get('countAsset'),target=r.get('countTarget'))
    if engine=='pattern': result['pattern']=[identity(o) if o else None for o in r['patternItems']]
    if engine=='sort':
        result['pairs']=sorted((identity(byid[p['left']]),p['right']) for p in r['pairs'] if p['left'] in byid)
    if r.get('reference'): result['reference']=identity(r['reference'])
    if engine in ('trace','draw'): result.update(canvas=r.get('canvas'),instruction=r['instruction'])
    return json.dumps(result,ensure_ascii=False,sort_keys=True)


def validate(categories,worksheets,check_variation=True):
    errors=[]; category_rules=collections.Counter(); first_targets={}; variation={}
    def check(ok,message):
        if not ok: errors.append(message)
    def text_ok(x,where):
        check(isinstance(x,dict) and set(('id','en'))<=set(x) and all(isinstance(x[k],str) and x[k].strip() for k in ('id','en')),where+': bilingual text missing')
    check(len(categories)==16,'Expected 16 categories')
    check(len(worksheets)==384,'Expected 384 worksheets')
    check({c['id'] for c in categories}==set(CARD_CATEGORIES),'Category set mismatch')
    check(len({w['id'] for w in worksheets})==len(worksheets),'Duplicate worksheet IDs')
    counts=collections.Counter(w['category'] for w in worksheets)
    for c in categories:
        cid=c['id']; engine,group=CARD_CATEGORIES[cid]
        check((c['engine'],c['group'])==(engine,group),cid+': engine/group mismatch')
        check(counts[cid]==24 and c.get('worksheetCount')==24,cid+': expected 24 worksheets')
        check(2<=c['age']<=6 and c.get('ageRange')==[c['age'],6],cid+': age range invalid')
        check(c['asset'] in ALLOWED_ASSETS,cid+': unknown category asset')
        text_ok(c['title'],cid+' title'); text_ok(c['description'],cid+' description')
        rows=[w for w in worksheets if w['category']==cid]
        signatures={tuple(fingerprint(r,engine) for r in w['rounds']) for w in rows}
        variation[cid]=len(signatures)
        if check_variation: check(len(signatures)==24,cid+': repeated semantic round set, unique='+str(len(signatures)))
        targets=[]
        for w in rows:
            r=w['rounds'][0]; byid={o['id']:o for o in r['options']}
            target=tuple(byid[a].get('asset',byid[a].get('value')) for a in r['answer'] if a in byid)
            if target: targets.append(target)
        first_targets[cid]=len(set(targets))
        if check_variation and engine in ('identify','count','pattern','sequence','compare'):
            check(len(set(targets))>=3,cid+': first-round target variety below three')
    for w in worksheets:
        cid=w['category']; engine=CARD_CATEGORIES[cid][0]
        check(w['engine']==engine,w['id']+': engine mismatch')
        check(len(w['rounds'])==4,w['id']+': expected four rounds')
        check(w['id']==f'{cid}-{w["variant"]:02d}' and 1<=w['variant']<=24,w['id']+': stable ID mismatch')
        check(2<=w['age']<=6 and w['ageRange']==[w['age'],6],w['id']+': age invalid')
        for k,value in w['rounds'][0].items(): check(w.get(k)==value,w['id']+': root differs from round 1: '+k)
        for k in ('title','offscreen','note'): text_ok(w.get(k),w['id']+' '+k)
        for ri,r in enumerate(w['rounds']):
            at=f'{w["id"]} round {ri+1}'; category_rules[cid]+=1
            text_ok(r.get('instruction'),at+' instruction')
            options=r['options']; byid={o['id']:o for o in options}
            check(len(byid)==len(options),at+': duplicate option ID')
            check(set(r['answer'])<=set(byid),at+': answer references missing option')
            check(len(set(r['answer']))==len(r['answer']),at+': duplicate answer')
            if engine in ('trace','draw'): check(options==[] and r['answer']==[],at+': canvas must not have card options or answers')
            else: check(3<=len(options)<=6,at+': expected 3–6 options')
            allpics=options+r.get('rightOptions',[])+([r['reference']] if r.get('reference') else [])+[o for o in r.get('patternItems',[]) if o]
            for o in allpics:
                text_ok(o.get('label'),at+' label')
                if 'ariaLabel' in o: text_ok(o['ariaLabel'],at+' accessible label')
                if 'asset' in o:
                    check(o['asset'] in ALLOWED_ASSETS,at+': unknown asset '+o['asset'])
                    check(o.get('showLabel') is True,at+': naming label hidden')
                if 'groupAsset' in o: check(o['groupAsset'] in ALLOWED_ASSETS,at+': unknown quantity asset')
            if cid in POOLS:
                check(all(o.get('asset') in POOLS[cid] for o in options),at+': category vocabulary mismatch')
            actual=[byid[a] for a in r['answer'] if a in byid]
            if engine=='identify':
                for lang,prefix in [('id','Pilih: '),('en','Choose: ')]:
                    prompt=r['instruction'][lang]
                    check(prompt.startswith(prefix) and prompt.endswith('.'),at+': identification prompt unsupported')
                    names=prompt[len(prefix):-1].split(', ')
                    check(len(names)==len(set(names)),at+': repeated requested name')
                    expected={o['id'] for o in options if o['label'][lang] in names}
                    check(len(expected)==len(names) and set(r['answer'])==expected,at+': named answer mismatch '+lang)
                if cid=='dinosaur-names':
                    check(all(o['label']['en'] in {'T. rex','Triceratops','Stegosaurus'} for o in options),at+': unsupported dinosaur name')
            elif engine=='pair':
                right={o['id']:o for o in r.get('rightOptions',[])}
                ps=r.get('pairs',[])
                check(r['answer']==[],at+': pair answer should be empty')
                check(len(ps)==len(options)==len(right),at+': pair count mismatch')
                check({p['left'] for p in ps}==set(byid) and {p['right'] for p in ps}==set(right),at+': pairs are not a bijection')
                for p in ps:
                    if p['left'] not in byid or p['right'] not in right: continue
                    a,b=byid[p['left']],right[p['right']]
                    check(a.get('asset')==b.get('asset') and a['label']==b['label'],at+': pair does not match picture and name')
            elif engine=='sort':
                taxonomy,labels=SORT_RULES[cid]
                bins={b['id']:b for b in r.get('bins',[])}; ps=r.get('pairs',[])
                check(set(bins)==set(taxonomy),at+': exactly two expected bins required')
                check(r['answer']==[] and 'rightOptions' not in r,at+': sort contract mismatch')
                for key,b in bins.items():
                    text_ok(b.get('label'),at+' bin')
                    if key in labels: check(tuple(b['label'][x] for x in ('id','en'))==labels[key],at+': bin label mismatch')
                    check(b.get('asset') in ALLOWED_ASSETS,at+': bin asset unsupported')
                check(len(ps)==len(options) and {p['left'] for p in ps}==set(byid),at+': sort must map each card once')
                check({p['right'] for p in ps}==set(bins),at+': both bins need an item')
                for p in ps:
                    check(p['right'] in bins,at+': missing destination bin')
                    if p['left'] in byid and p['right'] in taxonomy:
                        a=byid[p['left']].get('asset')
                        memberships=[k for k,pool in taxonomy.items() if a in pool]
                        check(memberships==[p['right']],at+': classification incorrect or ambiguous')
            elif engine=='count':
                n=r.get('countTarget'); check(isinstance(n,int) and 1<=n<=6,at+': count must be 1–6')
                check(r.get('countAsset') in ALL_VEHICLES,at+': counting asset is not a vehicle')
                check(len(actual)==1 and actual[0].get('value')==n and actual[0].get('symbol')==str(n),at+': count answer mismatch')
                check(len({o['value'] for o in options})==len(options),at+': duplicate numeric choices')
                if 'operands' in r:
                    a,b=r['operands']; expected=a+b if r.get('operation')=='add' else a-b
                    check(n==expected,at+': arithmetic result mismatch')
            elif engine=='sequence':
                check(len(actual)==len(options) and len(actual) in (3,4),at+': sequence missing a step')
                for lang,prefix,suffix in [('id','Urutan kartu rakitan kendaraan mainan kali ini: ','. Pilih sesuai urutan.'),('en','This pretend toy vehicle uses this card order: ','. Choose in that order.')]:
                    prompt=r['instruction'][lang]
                    check(prompt.startswith(prefix) and prompt.endswith(suffix),at+': pretend assembly order not explicit')
                    names=prompt[len(prefix):-len(suffix)].split(' → ')
                    check([o['label'][lang] for o in actual]==names,at+': sequence differs from stated card order '+lang)
                check(actual[-1].get('asset') in ROAD if actual else False,at+': final toy vehicle missing')
                check(all(o.get('asset') in PARTS|{'building-blocks'} for o in actual[:-1]),at+': non-toy building-card vocabulary')
                check('not instructions for assembling a real vehicle' in w['note']['en'],at+': pretend framing missing from adult guide')
            elif engine=='memory':
                check(r['answer']==[],at+': canonical memory answer must be empty')
                check(len({o.get('asset') for o in options})==len(options),at+': memory cards must be canonical unique pictures')
            elif engine=='pattern':
                items=r.get('patternItems',[]); blanks=[j for j,p in enumerate(items) if p is None]
                check(len(blanks)==1,at+': pattern must have one blank')
                if len(blanks)==1:
                    m=blanks[0]; prefix=[o['asset'] for o in items[:m]]
                    periods=[p for p in (2,3) if len(prefix)>=2*p and all(a==prefix[j%p] for j,a in enumerate(prefix))]
                    check(m==len(items)-1 and bool(periods),at+': must show at least two complete visible repetitions')
                    if periods:
                        p=min(periods); target=prefix[m%p]
                        check(len(actual)==1 and actual[0].get('asset')==target,at+': repeated-pattern answer mismatch')
                    check(len({o['asset'] for o in options})==len(options),at+': duplicate picture options')
            elif engine=='compare':
                vals=[o.get('value') for o in options]
                check(all(o.get('kind')=='quantity' and 'groupAsset' not in o and 'asset' not in o for o in options),at+': block amounts must count independent dots')
                check(all(isinstance(n,int) and 1<=n<=6 for n in vals) and len(set(vals))==len(vals),at+': comparison amounts invalid or tied')
                prompt=r['instruction']['en']
                if 'the most dots' in prompt: target=max(vals)
                elif 'the fewest dots' in prompt: target=min(vals)
                elif 'the same number of dots as the example' in prompt: target=r.get('reference',{}).get('value')
                else: target=None; check(False,at+': comparison relation missing')
                check(len(actual)==1 and actual[0].get('value')==target,at+': comparison answer mismatch')
                id_prompt=r['instruction']['id']; check(('paling banyak' in id_prompt)==('the most dots' in prompt) and ('paling sedikit' in id_prompt)==('the fewest dots' in prompt),at+': bilingual comparison relation mismatch')
            elif engine in ('trace','draw'):
                canvas=r.get('canvas',{}); guides=canvas.get('guide',[])
                check(canvas.get('viewBox')==[0,0,400,300] and bool(guides),at+': geometry canvas invalid')
                check(r.get('completion',{}).get('mode')=='self-check' and bool(r.get('completion',{}).get('goals')),at+': self-check completion missing')
                for goal in r.get('completion',{}).get('goals',[]): text_ok(goal,at+' goal')
                for g in guides:
                    check(g.get('kind') in {'path','line','circle','shape-outline'},at+': unsupported or representational canvas guide')
                    check(not any(k in g for k in ('asset','items','text')),at+': representational canvas content')
                    if g.get('kind')=='circle':
                        check(0<=g['cx']-g['r'] and g['cx']+g['r']<=400 and 0<=g['cy']-g['r'] and g['cy']+g['r']<=300,at+': circle guide out of bounds')
                    if g.get('kind')=='path':
                        # Conservative y bound covers every generated path coordinate too.
                        coords=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',g.get('d',''))]
                        check(len(coords)>=4 and min(coords)>=0 and max(coords)<=400,at+': path coordinates invalid')
                if engine=='draw':
                    m=re.fullmatch(r'Imagine a robot panel\. Draw ([1-4]) (circle|circles|line|lines|square|squares) inside the frame\.',r['instruction']['en'])
                    check(bool(m),at+': drawing task missing concrete count/shape')
                    if m:
                        number=int(m.group(1)); word=m.group(2)
                        check((' '+str(number)+' ') in r['instruction']['id'],at+': bilingual drawing amount mismatch')
                        shape={'circle':'lingkaran','line':'garis','square':'persegi'}[word.rstrip('s')]
                        check(shape in r['instruction']['id'],at+': bilingual drawing shape mismatch')
                        check(any(str(number) in goal['en'] and word in goal['en'] for goal in r['completion']['goals']),at+': drawing self-check goal differs')
                else:
                    check('Trace the ' in r['instruction']['en'] and 'Telusuri garis' in r['instruction']['id'],at+': trace action missing')
    return {'status':'pass' if not errors else 'fail','categories':len(categories),'worksheets':len(worksheets),
            'rounds':sum(len(w['rounds']) for w in worksheets),'worksheetsPerCategory':dict(counts),
            'categoryRulesChecked':dict(category_rules),'uniqueSemanticRoundSets':variation,
            'uniqueFirstRoundTargets':first_targets,'errors':errors}


def mutation_checks(categories,worksheets):
    results={}
    for cid,(engine,_) in CARD_CATEGORIES.items():
        # Mutate a later round so root-normalization checks cannot mask a semantic failure.
        changed=copy.deepcopy(worksheets)
        w=next(w for w in changed if w['category']==cid); r=w['rounds'][1]
        if engine in ('identify','count','pattern','compare'):
            wrong=next(o['id'] for o in r['options'] if o['id'] not in r['answer']); r['answer']=[wrong]
        elif engine=='sequence': r['answer'].reverse()
        elif engine=='pair': r['pairs'][0]['right'],r['pairs'][1]['right']=r['pairs'][1]['right'],r['pairs'][0]['right']
        elif engine=='sort': r['pairs'][0]['right']=next(b['id'] for b in r['bins'] if b['id']!=r['pairs'][0]['right'])
        elif engine=='memory':
            r['options'][1]['asset']=r['options'][0]['asset']; r['options'][1]['label']=copy.deepcopy(r['options'][0]['label'])
        elif engine=='trace': r['canvas']['guide'][0]={'kind':'unsupported-drawing','asset':'car'}
        elif engine=='draw': r['completion']['goals']=[{'id':'Aku menggambar 99 bentuk.','en':'I drew 99 triangles.'}]
        failures=validate(categories,changed,check_variation=False)['errors']
        semantic=[x for x in failures if x.startswith(w['id']+' round 2:')]
        results[cid]={'caught':bool(semantic),'rule':semantic[0] if semantic else 'NOT CAUGHT'}
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
    args=p.parse_args()
    categories=json.loads((args.out/'expansion-categories.json').read_text())
    worksheets=json.loads((args.out/'expansion-worksheets.json').read_text())
    result=validate(categories,worksheets)
    if not result['errors']:
        result['negativeMutationChecks']=mutation_checks(categories,worksheets)
        result['errors'] += [cid+': bad answer mutation escaped validation' for cid,d in result['negativeMutationChecks'].items() if not d['caught']]
    result['status']='fail' if result['errors'] else 'pass'
    result['checks']=['Exact 16/384/1536 counts and normalized round 1','All 16 category semantics','Independent literal bilingual naming answers',
                      'Pair bijection and matching labels','Two-bin complete unambiguous sort taxonomy','Counts and arithmetic','Stated pretend toy sequence order',
                      'Canonical unique memory cards','One gap after two full pattern repetitions','Dot quantity comparisons',
                      'Supported geometric canvases and self-check goals','24 semantic round sets per category','Varied first-round targets',
                      'Ages, bilingual content, and supported assets','Deliberately wrong answer rejected for every category']
    (args.out/'semantic-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    manifest_path=args.out/'expansion-manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        for name in ('expansion-categories.json','expansion-worksheets.json','semantic-audit.json'):
            manifest['sha256'][name]=hashlib.sha256((args.out/name).read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'categories':result['categories'],'worksheets':result['worksheets'],'rounds':result['rounds'],'errors':result['errors']},ensure_ascii=False))
    raise SystemExit(bool(result['errors']))


if __name__=='__main__': main()
