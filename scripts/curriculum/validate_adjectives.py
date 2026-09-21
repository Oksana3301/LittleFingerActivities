#!/usr/bin/env python3
"""Independent audit; reads exports and never imports the authoring module.

Checks the actual options, references, stated pattern rules, pairs, bins,
translations, root mirrors, semantic task-set variation, and negative fixtures.
"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re

LANGS=('en','id','zh','ar')
FOCAL={
 'temperature':('hot','cold'),'soft-hard':('soft','hard'),'smooth-rough':('smooth','rough'),
 'wet-dry':('wet','dry'),'open-closed':('open','closed'),'full-empty':('full','empty'),
 'heavy-light':('heavy','light'),'bright-dim':('bright','dim'),'fast-slow':('fast','slow'),
 'loud-quiet':('loud','quiet'),'tidy-messy':('tidy','messy'),'kind-descriptions':('handsome','beautiful'),
}
# Independent expected picture/word inventory. Labels are part of the visible
# semantics, and cannot be repaired by changing hidden answer metadata.
ROWS=[
 ('hot','adj-hot-cup','Hot cup',('hot','panas','热','ساخن'),'having a high temperature'),
 ('cold','adj-cold-cup','Cold cup',('cold','dingin','冷','بارد'),'having a low temperature'),
 ('soft','adj-soft-pillow','Soft pillow',('soft','empuk','软','طري'),'easy to press gently'),
 ('hard','adj-hard-rock','Hard rock',('hard','keras','硬','صلب'),'not easy to press'),
 ('smooth','adj-smooth-ball','Smooth ball',('smooth','halus','光滑','أملس'),'surface without bumps'),
 ('rough','adj-rough-stone','Rough stone',('rough','kasar','粗糙','خشن'),'an uneven surface'),
 ('wet','adj-wet-shirt','Wet shirt',('wet','basah','湿','مبلل'),'Water is still on this shirt'),
 ('dry','adj-dry-shirt','Dry shirt',('dry','kering','干','جاف'),'no water left'),
 ('open','adj-open-box','Open box',('open','terbuka','打开','مفتوح'),'lid lifted'),
 ('closed','adj-closed-box','Closed box',('closed','tertutup','合上','مغلق'),'lid shut'),
 ('full','adj-full-basket','Full basket',('full','penuh','满','ممتلئ'),'things filling it'),
 ('empty','adj-empty-basket','Empty basket',('empty','kosong','空','فارغ'),'nothing inside'),
 ('heavy','adj-heavy-box','Story label: heavy box',('heavy','berat','重','ثقيل'),'much effort to lift'),
 ('light','adj-light-feather','Story label: light feather',('light','ringan','轻','خفيف'),'little effort to lift'),
 ('bright','adj-bright-lamp','Bright lamp',('bright','terang','明亮','ساطع'),'much light'),
 ('dim','adj-dim-lamp','Dim lamp',('dim','redup','昏暗','خافت'),'little light'),
 ('fast','adj-fast-car','Story label: fast car',('fast','cepat','快','سريع'),'same path in less time'),
 ('slow','adj-slow-car','Story label: slow car',('slow','lambat','慢','بطيء'),'same path in more time'),
 ('loud','adj-loud-drum','Drum card: loud in this story',('loud','keras','声音大','عال'),'sound with high volume'),
 ('quiet','adj-quiet-book','Book card: quiet in this story',('quiet','pelan','声音小','هادئ'),'reading voice by this book has low volume'),
 ('tidy','adj-tidy-shelf','Tidy shelf',('tidy','rapi','整齐','مرتب'),'arranged in their places'),
 ('messy','adj-messy-shelf','Messy shelf',('messy','berantakan','凌乱','غير مرتب'),'scattered out of place'),
 ('fresh','adj-fresh-flower','Fresh flower',('fresh','segar','新鲜','نضر'),'fresh petals'),
 ('wilted','adj-wilted-flower','Wilted flower',('wilted','layu','枯萎','ذابل'),'wilted petals'),
 ('open-book','adj-open-book','Open book',('open','terbuka','打开','مفتوح'),'pages spread apart'),
 ('closed-book','adj-closed-book','Closed book',('closed','tertutup','合上','مغلق'),'covers together'),
 ('full-cup','adj-full-cup','Full cup',('full','penuh','满','ممتلئ'),'filled with a drink'),
 ('empty-cup','adj-empty-cup','Empty cup',('empty','kosong','空','فارغ'),'no drink'),
 ('clean','adj-clean-shoe','Clean shoe',('clean','bersih','干净','نظيف'),'no mud'),
 ('muddy','adj-muddy-shoe','Muddy shoe',('muddy','berlumpur','沾泥','مغطى بالطين'),'There is mud'),
 ('handsome','adj-neat-boy','“You look handsome today.”',('handsome','ganteng','英俊','وسيم'),None),
 ('beautiful','adj-neat-girl','“You look beautiful today.”',('beautiful','cantik','漂亮','جميل'),None),
 ('self-look','adj-neat-boy','“I like how I look.”',('liking my own look','suka penampilan sendiri','喜欢自己的样子','الإعجاب بمظهري'),None),
 ('self-choice','adj-neat-girl','“I chose clothes I like.”',('my clothing choice','pilihan bajuku','自己的衣服选择','اختيار ملابسي'),None),
 ('neat-clothes','adj-neat-boy','“Your clothes look neat.”',('neat clothes','baju rapi','衣服整齐','ملابس مرتبة'),None),
 ('kind-words','adj-neat-girl','“Thank you for your kind words.”',('kind words','kata yang ramah','友善的话','كلمات لطيفة'),None),
 ('flower-beauty','adj-fresh-flower','“This flower is beautiful.”',('a beautiful flower','bunga yang cantik','漂亮的花','زهرة جميلة'),None),
 ('own-comfort','adj-neat-girl','“I feel comfortable in these clothes.”',('comfortable clothes','baju yang nyaman','舒服的衣服','ملابس مريحة'),None),
]
INVENTORY={key:{'asset':asset,'en':en,'word':dict(zip(LANGS,words)),'clue':clue} for key,asset,en,words,clue in ROWS}
KIND_KEYS={row[0] for row in ROWS[-8:]}
OPPOSITES={}
for a,b in list(FOCAL.values())[:-1]+[('fresh','wilted')]: OPPOSITES[a]=b; OPPOSITES[b]=a
SORTS={
 'open-closed':{'open':{'open','open-book'},'closed':{'closed','closed-book'}},
 'full-empty':{'full':{'full','full-cup'},'empty':{'empty','empty-cup'}},
}

def identity(o): return (o.get('asset'),tuple(o.get('label',{}).get(k,'') for k in LANGS))
def signature(r,engine):
    byid={o['id']:o for o in r['options']}
    f={'engine':engine,'cards':sorted(identity(o) for o in r['options'])}
    if engine=='identify':
        f.update({'scenario':r.get('scenarioId'),'answer':sorted(identity(byid[x]) for x in r['answer'] if x in byid),
                  'reference':identity(r['reference']) if r.get('reference') else None})
    if engine=='pair':
        right={o['id']:o for o in r['rightOptions']}
        f['pairs']=sorted((identity(byid[p['left']]),identity(right[p['right']])) for p in r['pairs'] if p['left'] in byid and p['right'] in right)
    if engine=='sort': f['groups']=sorted((identity(byid[p['left']]),p['right']) for p in r['pairs'] if p['left'] in byid)
    if engine=='pattern': f['strip']=[identity(o) if o else None for o in r['patternItems']]
    return json.dumps(f,sort_keys=True,ensure_ascii=False)

def validate(categories,worksheets,variation=True):
    errors=[]; checks=Counter(); tasksets={}; scenarios={}; per_engine=Counter()
    def check(ok,where,rule):
        checks[rule]+=1
        if not ok: errors.append(f'{where}: {rule}')
    def texts(value,where):
        if isinstance(value,dict):
            if 'en' in value or 'zh' in value or 'ar' in value:
                check(set(value)==set(LANGS) and all(isinstance(value.get(l),str) and value[l].strip() for l in LANGS),where,'four-language Text')
                for lang,rx in [('zh',r'[\u3400-\u9fff]'),('ar',r'[\u0600-\u06ff]')]:
                    check(isinstance(value.get(lang),str) and bool(re.search(rx,value.get(lang,''))),where+'/'+lang,'native-script text')
                check(not any(token in value.get('ar','') for token in ('TODO','fallback','undefined')),where,'no Arabic placeholder')
            else:
                for k,v in value.items(): texts(v,where+'/'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value): texts(v,where+f'/{i}')
    def inspect_card(o,where):
        key=o.get('vocabularyKey'); expected=INVENTORY.get(key)
        check(expected is not None,where,'known vocabulary key')
        check(o.get('kind')=='asset' and o.get('showLabel') is True,where,'asset card with visible label')
        if expected:
            check(o.get('asset')==expected['asset'],where,'picture asset matches named subject')
            check(o.get('label',{}).get('en')==expected['en'],where,'exact independently expected English label')
        if key in ('heavy','light','fast','slow','loud','quiet'):
            for lang,word in [('en','story'),('id','cerita'),('zh','故事'),('ar','القصة')]:
                check(word in o.get('label',{}).get(lang,'').lower(),where+'/'+lang,'explicit story label for variable properties')
        return key

    check(len(categories)==12,'catalogue','12 new categories')
    check({c['id'] for c in categories}==set(FOCAL),'catalogue','exact category membership')
    check(len(worksheets)==288,'catalogue','288 worksheets')
    check(len({w['id'] for w in worksheets})==288,'catalogue','unique worksheet IDs')
    check(sum(len(w.get('rounds',[])) for w in worksheets)==1152,'catalogue','1152 rounds')
    for c in categories:
        cid=c['id']; texts(c,cid); rows=[w for w in worksheets if w['category']==cid]
        check(len(rows)==24 and c.get('worksheetCount')==24,cid,'24 worksheets per category')
        check({w['variant'] for w in rows}==set(range(1,25)),cid,'complete variant sequence')
        check(c['age']==2 and c['ageRange']==[2,6],cid,'category age guidance')
        if variation:
            signatures={tuple(sorted(signature(r,w['engine']) for r in w['rounds'])) for w in rows}
            tasksets[cid]=len(signatures); check(len(signatures)==24,cid,'24 unordered semantic task sets')
        scenarios[cid]=len({r.get('scenarioId') for w in rows for r in w['rounds'] if r.get('scenarioId')})
        for w in rows:
            at=w['id']; texts(w,at); engine=w['engine']; per_engine[engine]+=1
            check(engine in ('identify','pair','sort','memory','pattern'),at,'supported worksheet engine')
            check(w['age'] in (2,3,4) and w['ageRange']==[w['age'],6],at,'worksheet age guidance')
            check(w['difficulty'] in (1,2,3),at,'difficulty guidance')
            check(len(w['rounds'])==4,at,'four rounds')
            check(all(w.get(k)==v for k,v in w['rounds'][0].items()),at,'root mirrors first round')
            if variation: check(len({signature(r,engine) for r in w['rounds']})==4,at,'four distinct semantic tasks')
            if cid=='kind-descriptions':
                check(engine in ('identify','pair'),at,'kind words use literal quotation tasks')
                check('never rank people' in w['note']['en'] and 'not rules about gender' in w['note']['en'],at,'non-ranking optional compliment note')
            else:
                check('do not touch, taste, heat, or cool' in w['note']['en'],at,'picture-only temperature safety across review cards')
                check('size alone does not tell' in w['note']['en'],at,'no object-type inference note')
                check('draw two picture cards' in w['offscreen']['en'],at,'offscreen remains picture play')
            for n,r in enumerate(w['rounds']):
                where=at+f'/round-{n+1}'; options=r['options']; byid={o['id']:o for o in options}
                keys=[inspect_card(o,where+'/'+o['id']) for o in options]
                check(len(options)==len(byid),where,'unique option IDs')
                check(len({identity(o) for o in options})==len(options),where,'distinct visible options')
                check(all(x in byid for x in r['answer']) and len(set(r['answer']))==len(r['answer']),where,'answer IDs exist and are unique')
                prompt=r['instruction']['en'].lower()
                check(not any(bad in prompt for bad in ('prettiest','most handsome','more beautiful','ugly','which person is beautiful','touch the hot','taste the hot','lift the heavy')),where,'no ranking or unsafe action prompts')
                if engine in ('identify','pair','pattern'): check(r.get('layout')=='story-choices',where,'wide layout for word phrases')
                if engine=='identify':
                    parts=r.get('scenarioId','').split(':'); check(len(parts)==3 and parts[0]==cid,where,'structured identification scenario')
                    if len(parts)!=3: continue
                    _,mode,target=parts; expected=INVENTORY.get(target)
                    check(expected is not None,where,'independent target vocabulary')
                    if expected is None: continue
                    if cid=='kind-descriptions':
                        check(target in KIND_KEYS and mode in ('meaning','quote'),where,'quotation-only prompt purpose')
                        check(set(keys)<=KIND_KEYS and len(keys)==3,where,'three quoted choices')
                        for lang in LANGS:
                            term=expected['word'][lang] if mode=='meaning' else next(o['label'][lang] for o in options if o.get('vocabularyKey')==target)
                            check(term in r['instruction'].get(lang,''),where+'/'+lang,'kind prompt names exact meaning or quote')
                    else:
                        check(set(keys)==set(FOCAL[cid]),where,'two focal opposite cards')
                        check(mode in ('word','clue','opposite-word','same-picture','opposite-picture','story-quote'),where,'six meaningful prompt modes')
                        if mode=='clue': check(expected['clue'] in r['instruction']['en'],where,'clue independently matches target')
                        if mode in ('word','opposite-word','opposite-picture'):
                            key=OPPOSITES[target] if mode.startswith('opposite') else target
                            for lang in LANGS: check(INVENTORY[key]['word'][lang] in r['instruction'].get(lang,''),where+'/'+lang,'requested describing word matches task')
                        if mode in ('same-picture','story-quote'):
                            for lang in LANGS: check(next(o['label'][lang] for o in options if o['vocabularyKey']==target) in r['instruction'].get(lang,''),where+'/'+lang,'prompt names the pictured label')
                        if mode in ('same-picture','opposite-picture'):
                            reference=r.get('reference',{}); refkey=inspect_card(reference,where+'/reference')
                            check(refkey==(target if mode=='same-picture' else OPPOSITES[target]),where,'reference has correct meaning')
                    actual=[o['id'] for o in options if o['asset']==expected['asset'] and o['label']['en']==expected['en']]
                    check(len(actual)==1 and r['answer']==actual,where,'exact independent identify answer')
                elif engine=='pair':
                    right={o['id']:o for o in r['rightOptions']}
                    for o in right.values(): inspect_card(o,where+'/'+o['id'])
                    inferred=[]
                    for left in options:
                        target=left['vocabularyKey'] if cid=='kind-descriptions' else OPPOSITES.get(left['vocabularyKey'])
                        found=[o['id'] for o in right.values() if o['vocabularyKey']==target]
                        check(len(found)==1,where,'one independently defined partner per card')
                        if len(found)==1: inferred.append((left['id'],found[0]))
                    check(sorted((p['left'],p['right']) for p in r['pairs'])==sorted(inferred),where,'exact independent pair mapping')
                    check(len(r['pairs'])==len(options)==len(right) and len({p['right'] for p in r['pairs']})==len(right),where,'bijective pair mapping')
                    check(r['answer']==[],where,'pair answer uses mapping only')
                    if cid!='kind-descriptions': check(any(k in FOCAL[cid] for k in keys),where,'matching includes focal vocabulary')
                elif engine=='sort':
                    groups=SORTS.get(cid,{}); bins={b['id']:b for b in r['bins']}
                    check(set(bins)==set(groups),where,'two correct opposite bins')
                    expected=[]
                    for bid,b in bins.items():
                        for lang in LANGS: check(b['label'][lang]==INVENTORY[bid]['word'][lang],where+'/'+lang,'exact independent bin words')
                    for o in options:
                        found=[bid for bid,values in groups.items() if o['vocabularyKey'] in values]
                        check(len(found)==1,where,'one independent sorting group')
                        if len(found)==1: expected.append((o['id'],found[0]))
                    check(sorted((p['left'],p['right']) for p in r['pairs'])==sorted(expected),where,'exact independent sorting mapping')
                    check(r['answer']==[],where,'sort answer uses mapping only')
                elif engine=='memory':
                    check(len(options)==3 and len({o['asset'] for o in options})==3,where,'three visually distinct canonical memory cards')
                    check(set(FOCAL[cid])<=set(keys),where,'both focal words in memory')
                    check(r['answer']==[],where,'memory answer array empty')
                elif engine=='pattern':
                    words=r['instruction']['en'].removeprefix('Repeat this word pattern: ').split('. Fill the one missing picture.')[0].split(' → ')
                    word_to_key={INVENTORY[k]['word']['en']:k for k in FOCAL[cid]}
                    check(all(x in word_to_key for x in words),where,'stated pattern rule uses focal words')
                    if not all(x in word_to_key for x in words): continue
                    unit=[word_to_key[x] for x in words]; strip=r['patternItems']; gaps=[i for i,x in enumerate(strip) if x is None]
                    check(2<=len(unit)<=4 and set(unit)==set(FOCAL[cid]),where,'explicit two-state repeating unit')
                    check(r.get('patternUnit')==unit,where,'pattern metadata agrees with visible rule')
                    check(len(strip)==7 and len(gaps)==1 and len(strip)-len(gaps)<=6,where,'six visible pictures and one gap')
                    for i,o in enumerate(strip):
                        if o: check(inspect_card(o,where+f'/strip-{i}')==unit[i%len(unit)],where,'strip follows stated repeating rule')
                    if len(gaps)==1:
                        answer=unit[gaps[0]%len(unit)]
                        check(r['answer']==[o['id'] for o in options if o['vocabularyKey']==answer],where,'pattern answer inferred from stated rule')
                        check(r.get('missingIndex')==gaps[0],where,'pattern gap metadata matches picture')
                    for lang in LANGS:
                        check((' ثم ' if lang=='ar' else ' → ').join(INVENTORY[k]['word'][lang] for k in unit) in r['instruction'].get(lang,''),where+'/'+lang,'pattern rule translated consistently')
    return {'passed':not errors,'errors':errors,'checks':dict(checks),'semanticTaskSets':tasksets,'distinctIdentifyScenarios':scenarios,'worksheetsByEngine':dict(per_engine)}

def mutation_checks(categories,worksheets):
    results={}
    def attempt(name,modify):
        changed=copy.deepcopy(worksheets); modify(changed)
        # Copy changed round to root so a semantic failure cannot merely be a
        # stale-root mirror failure. All corruptions are inside readable JSON.
        for w in changed: w.update(copy.deepcopy(w['rounds'][0]))
        audit=validate(categories,changed,False)
        results[name]={'detected':not audit['passed'],'rules':sorted({s.rsplit(': ',1)[-1] for s in audit['errors']})}
    for cid in FOCAL:
        def wrong_answer(rows,cid=cid):
            r=next(w for w in rows if w['category']==cid and w['engine']=='identify')['rounds'][0]
            r['answer']=[next(o['id'] for o in r['options'] if o['id'] not in r['answer'])]
        attempt('wrong-answer-'+cid,wrong_answer)
    def pair_swap(rows):
        r=next(w for w in rows if w['engine']=='pair')['rounds'][0]
        r['pairs'][0]['right'],r['pairs'][1]['right']=r['pairs'][1]['right'],r['pairs'][0]['right']
    attempt('opposite-pair-swapped',pair_swap)
    def wrong_bin(rows):
        r=next(w for w in rows if w['engine']=='sort')['rounds'][0]
        r['pairs'][0]['right']=next(b['id'] for b in r['bins'] if b['id']!=r['pairs'][0]['right'])
    attempt('sort-bin-wrong',wrong_bin)
    def duplicate_memory(rows):
        r=next(w for w in rows if w['engine']=='memory')['rounds'][0]
        r['options'][1]={**copy.deepcopy(r['options'][0]),'id':r['options'][1]['id']}
    attempt('memory-visible-duplicate',duplicate_memory)
    def wrong_pattern(rows):
        r=next(w for w in rows if w['engine']=='pattern')['rounds'][0]
        r['answer']=[next(o['id'] for o in r['options'] if o['id'] not in r['answer'])]
    attempt('pattern-rule-wrong-answer',wrong_pattern)
    def missing_arabic(rows): del rows[0]['rounds'][0]['instruction']['ar']
    attempt('missing-arabic',missing_arabic)
    def wrong_art(rows): rows[0]['rounds'][0]['options'][0]['asset']='adj-neat-girl'
    attempt('art-subject-mismatch',wrong_art)
    def ranking(rows): next(w for w in rows if w['category']=='kind-descriptions')['rounds'][0]['instruction']['en']='Choose the prettiest person.'
    attempt('appearance-ranking-prompt',ranking)
    def touch(rows): rows[0]['rounds'][0]['instruction']['en']='Touch the hot cup.'
    attempt('unsafe-temperature-experiment',touch)
    # Deliberately repeat a task and a whole worksheet set after shuffling.
    changed=copy.deepcopy(worksheets); changed[0]['rounds'][1]=copy.deepcopy(changed[0]['rounds'][0]); changed[0]['rounds'][1]['options'].reverse()
    report=validate(categories,changed,True)
    results['option-shuffle-is-not-new-task']={'detected':any('four distinct semantic tasks' in e for e in report['errors'])}
    changed=copy.deepcopy(worksheets); changed[1]['rounds']=list(reversed(copy.deepcopy(changed[0]['rounds']))); changed[1].update(copy.deepcopy(changed[1]['rounds'][0]))
    report=validate(categories,changed,True)
    results['round-shuffle-is-not-new-worksheet']={'detected':any('24 unordered semantic task sets' in e for e in report['errors'])}
    return results

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent); args=parser.parse_args()
    cats=json.loads((args.out/'expansion-categories.json').read_text()); sheets=json.loads((args.out/'expansion-worksheets.json').read_text())
    report=validate(cats,sheets); report['negativeFixtures']=mutation_checks(cats,sheets)
    report['negativeFixturesPassed']=all(x['detected'] for x in report['negativeFixtures'].values())
    report['passed']=report['passed'] and report['negativeFixturesPassed']
    report['sha256']={name:hashlib.sha256((args.out/name).read_bytes()).hexdigest() for name in ('expansion-categories.json','expansion-worksheets.json')}
    report['limits']=['Illustration identity and crop fidelity require visual review.','This audit checks authored language completeness and semantic consistency, not a child’s development or professional translation certification.']
    (args.out/'semantic-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'errors':report['errors'][:20],'negativeFixtures':len(report['negativeFixtures']),'semanticTaskSets':report['semanticTaskSets']}))
    raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__': main()
