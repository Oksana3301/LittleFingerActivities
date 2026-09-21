#!/usr/bin/env python3
"""Independent semantic audit of generated JSON. Never imports the authoring code.

Checks answer meanings against separately written fixtures, literal three-step
story order in all languages, exact pair mappings, independent sort taxonomy,
memory uniqueness, translations, ages, root mirrors and semantic variation.
Also deliberately corrupts one answer in every category to verify detection.
"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re

LANGS = ('en','id','zh')
ENGINES = {
 'brush-teeth':'identify','bath-routine':'sequence','wash-hands':'identify',
 'toilet-care':'sequence','mealtime-habits':'memory','bedtime-routine':'sequence',
 'tidy-toys':'sort','polite-words':'identify','helping-family':'pair',
 'gentle-with-younger':'identify','friendly-choices':'identify','daily-routine':'sequence',
}
EXPECTED_IDENTIFY = {
 'brush-teeth': {
  'tool':'Toothbrush','food':'Food on a tooth','clean':'Clean tooth','paste':'Toothpaste',
  'together':'Brush with a grown-up','personal':'Use your own toothbrush',
  'gentle':'Brush gently with a grown-up','comfort':'Tell a grown-up it feels uncomfortable',
  'after':'Rinse the toothbrush with help','holder':'Put the brush in its holder',
  'prepare':'Let a grown-up prepare the toothpaste','evening':'Brush with a grown-up',
 },
 'wash-hands': {
  'meal':'Wash hands with soap and water','toilet':'Wash hands with soap and water',
  'soil':'Wash hands with soap and water','soap':'Soap','wet':'Wet hands with clean running water',
  'rub':'Rub soapy hands together','back':'Rub the backs of the hands',
  'between':'Rub between the fingers','rinse':'Rinse the soap away',
  'dry':'Dry hands with a clean towel','reach':'Ask a trusted grown-up to help',
  'nose':'Wash hands with soap and water',
 },
 'polite-words': {
  'gift':'Thank you!','arrive':'Hello!','leave':'Goodbye!','bedtime':'Good night!',
  'turn':'May I have a turn, please?','help':'Please help me.','decline':'No, thank you.',
  'pass':'Excuse me, may I pass?','bump':'Sorry, I bumped you.',
  'boundary':'Please stop. I need space.','check':'Are you okay?',"reply":"You're welcome!",
 },
 'gentle-with-younger': {
  'sleep':'Use a quiet voice','no-touch':'Give some space','ball':'Roll a soft ball gently',
  'show':'Show slowly and wait','cry':'Ask a trusted grown-up to help','greeting':'Wave if you want to',
  'offer':'Offer and listen to the answer','talk':'Listen without rushing','touch':'Use gentle hands',
  'play-choice':'Let them choose differently','turn':'Wait for a turn','heavy':'Ask a trusted grown-up to help',
 },
 'friendly-choices': {
  'join':'Would you like to play?','borrow':'Ask before taking','return':'Return the borrowed toy',
  'wait':'Wait for a turn','share':'Offer a turn','tower':'Offer to help rebuild','space':'Give some space',
  'different':'Let them choose differently','upset':'Take a quiet break',
  'problem':'Ask a trusted grown-up to help','story':'Listen without rushing','comfort':'Wave if you want to',
 },
}

PAIR_TARGETS = {
 'habit-towel':'Fold a clean towel','book':'Put a book on a low shelf',
 'spoon':'Set a spoon beside a plate','habit-plate':'Set a light plate on the table',
 'habit-cup':'Set an empty unbreakable cup down','building-blocks':'Put large blocks in a basket',
 'habit-clean-shirt':'Fold a clean shirt with help','pencil':'Put pencils in their box',
 'bag':'Put a light bag in its place','watering-can':'Use a small watering can with help',
 'football':'Return a football to the basket','habit-tissue':'Bring a clean tissue when asked',
}
SORT_MEMBERS = {
 'toys': {'building-blocks','car','football','basketball'},
 'meal': {'habit-plate','habit-cup','spoon'},
 'washing': {'habit-soap','habit-towel','habit-toothbrush','habit-toothpaste'},
 'drawing': {'pencil','ruler','book'},
}
SORT_LABELS = {
 'toys':('Toy pictures','Gambar mainan','玩具图片'),
 'meal':('Tableware pictures','Gambar peralatan makan','餐具图片'),
 'washing':('Body-care item pictures','Gambar benda perawatan tubuh','身体护理用品图片'),
 'drawing':('Book and stationery pictures','Gambar buku dan alat tulis','书和文具图片'),
}
MEMORY_ALLOWED = {
 'Plate','Drinking cup','Spoon','Wash hands with soap and water','Dry hands with a clean towel',
 'Sit for a meal','Drink water','Thank you!','Say when you feel full','Ask for more water',
 'Wipe a small spill with a grown-up','Trusted grown-up',
}
ALLOWED_ASSETS = {
 'habit-toothbrush','habit-toothpaste','habit-clean-tooth','habit-food-tooth','habit-soap',
 'habit-shower','habit-towel','habit-clean-shirt','habit-handwash','habit-tissue','habit-toilet',
 'habit-flush','habit-plate','habit-cup','habit-bed','habit-toy-basket','habit-brushing',
 'habit-bathing','habit-drying','habit-sleeping','habit-eating','habit-drinking','habit-tidying',
 'habit-helping','habit-sharing','habit-waiting','habit-greeting','habit-thanking',
 'habit-apologizing','habit-asking-help','habit-gentle','habit-cover-cough',
 'book','spoon','chair','table','apple','banana','water-glass','building-blocks','car','football',
 'basketball','pencil','ruler','bag','family','watering-can',
}


def identity(option):
    # Shared scenes can intentionally depict distinct labeled actions. Labels are
    # part of the visible teaching material, not hidden implementation metadata.
    return (option.get('asset'), tuple(option['label'][k] for k in LANGS))


def fingerprint(round, engine):
    byid = {o['id']:o for o in round['options']}
    f = {'cards':sorted(identity(o) for o in round['options'])}
    if engine == 'sequence':
        f['orderedAnswer'] = [identity(byid[x]) for x in round['answer']]
    elif engine == 'identify':
        f['answer'] = sorted(identity(byid[x]) for x in round['answer'])
    elif engine == 'sort':
        f['mapping'] = sorted((identity(byid[p['left']]),p['right']) for p in round['pairs'])
    elif engine == 'pair':
        right = {o['id']:o for o in round['rightOptions']}
        f['mapping'] = sorted((identity(byid[p['left']]),identity(right[p['right']])) for p in round['pairs'])
    return json.dumps(f, ensure_ascii=False, sort_keys=True)


def validate(categories, worksheets, check_variation=True):
    errors = []; checks = Counter(); variation = {}; task_sets = {}; scenarios = {}
    def check(ok, where, rule):
        checks[rule] += 1
        if not ok: errors.append(f'{where}: {rule}')
    def text_ok(value, where):
        check(isinstance(value,dict) and all(isinstance(value.get(k),str) and value[k].strip() for k in LANGS), where,'trilingual text')
        if isinstance(value,dict) and isinstance(value.get('zh'),str):
            check(bool(re.search('[\u3400-\u9fff]',value['zh'])),where,'Chinese text has Han characters')
    def recursive_texts(value, where):
        if isinstance(value,dict):
            if 'en' in value or 'zh' in value: text_ok(value,where)
            else:
                for key, child in value.items(): recursive_texts(child,where+'/'+key)
        elif isinstance(value,list):
            for n, child in enumerate(value): recursive_texts(child,where+f'/{n}')

    check(len(categories)==12,'catalogue','12 categories')
    check(len(worksheets)==288,'catalogue','288 worksheets')
    check(set(c['id'] for c in categories)==set(ENGINES),'catalogue','exact category IDs')
    check(len({w['id'] for w in worksheets})==len(worksheets),'catalogue','unique worksheet IDs')
    for c in categories:
        cid = c['id']; rows = [w for w in worksheets if w['category']==cid]
        check(c['engine']==ENGINES[cid],cid,'category engine')
        check(len(rows)==24 and c.get('worksheetCount')==24,cid,'24 worksheets')
        check({w['variant'] for w in rows}==set(range(1,25)),cid,'all variant numbers')
        check(c['asset'] in ALLOWED_ASSETS,cid,'known category art')
        recursive_texts(c,cid)
        if check_variation:
            signatures = {tuple(fingerprint(r,w['engine']) for r in w['rounds']) for w in rows}
            sets = {tuple(sorted(fingerprint(r,w['engine']) for r in w['rounds'])) for w in rows}
            variation[cid] = len(signatures); task_sets[cid] = len(sets)
            check(len(signatures)==24,cid,'24 semantic four-round signatures ignoring option order')
            check(len(sets)==24,cid,'24 semantic task sets ignoring round order')
        scenarios[cid] = len({r.get('scenarioId') for w in rows for r in w['rounds'] if r.get('scenarioId')})
        for w in rows:
            where = w['id']; engine = w['engine']
            recursive_texts(w,where)
            check(2<=w['age']<=6 and w['ageRange']==[w['age'],6],where,'age guidance')
            check(w['difficulty'] in (1,2,3),where,'difficulty guidance')
            check(engine==c['engine'],where,'worksheet engine')
            check(len(w['rounds'])==4,where,'four rounds')
            if check_variation:
                check(len({fingerprint(r,engine) for r in w['rounds']})==4,where,'four distinct tasks within worksheet')
            check(all(w.get(k)==v for k,v in w['rounds'][0].items()),where,'root mirrors first round')
            for i, r in enumerate(w['rounds']):
                at = where+f'/round-{i+1}'
                options = r['options']; byid = {o['id']:o for o in options}
                check(len(options)==len(byid),at,'unique option IDs')
                check(len(set(identity(o) for o in options))==len(options),at,'unique visible cards')
                check(all(o['asset'] in ALLOWED_ASSETS for o in options),at,'known option art')
                check(all(o.get('kind')=='asset' and o.get('showLabel') is True for o in options),at,'visible action labels')
                check(all(x in byid for x in r['answer']),at,'answer IDs exist')
                check(len(set(r['answer']))==len(r['answer']),at,'unique answer IDs')
                if engine=='identify':
                    check(r.get('layout')=='story-choices',at,'wide story-choice layout')
                    scenario = r.get('scenarioId','').split(':')
                    check(len(scenario)==2 and scenario[0]==cid and scenario[1] in EXPECTED_IDENTIFY[cid],at,'known independent scenario')
                    if len(scenario)==2 and scenario[1] in EXPECTED_IDENTIFY[cid]:
                        expected = EXPECTED_IDENTIFY[cid][scenario[1]]
                        inferred = [o['id'] for o in options if o['label']['en']==expected]
                        check(len(inferred)==1 and r['answer']==inferred,at,'exact scenario answer meaning')
                elif engine=='sequence':
                    check(len(options)==3 and len(r['answer'])==3 and set(r['answer'])==set(byid),at,'exact three-card permutation')
                    for lang in LANGS:
                        labels = [byid[x]['label'][lang] for x in r['answer'] if x in byid]
                        check(' → '.join(labels) in r['instruction'][lang],at+'/'+lang,'answer follows stated story order')
                    check([o['id'] for o in options]!=r['answer'],at,'sequence starts shuffled')
                elif engine=='pair':
                    right = {o['id']:o for o in r['rightOptions']}
                    pairs = r['pairs']; expected = []
                    for o in options:
                        target = PAIR_TARGETS.get(o['asset'])
                        found = [x['id'] for x in r['rightOptions'] if x['label']['en']==target]
                        check(len(found)==1,at,'one named helper task per item')
                        if found: expected.append((o['id'],found[0]))
                    check(sorted((p['left'],p['right']) for p in pairs)==sorted(expected),at,'exact independent pair mapping')
                    check(len(pairs)==len(options)==len(right) and len({p['right'] for p in pairs})==len(right),at,'pair bijection')
                    check(r['answer']==[],at,'pair answer array empty')
                elif engine=='sort':
                    bins = {b['id']:b for b in r['bins']}; pairs = r['pairs']; expected = []
                    check(len(bins)==2,at,'two sort bins')
                    for bid,b in bins.items():
                        check(bid in SORT_MEMBERS,at,'known sorting group')
                        if bid in SORT_LABELS:
                            check(tuple(b['label'][k] for k in LANGS)==SORT_LABELS[bid],at,'exact sorting labels')
                    for o in options:
                        found = [bid for bid in bins if o['asset'] in SORT_MEMBERS.get(bid,set())]
                        check(len(found)==1,at,'one unambiguous group per card')
                        if found: expected.append((o['id'],found[0]))
                    check(sorted((p['left'],p['right']) for p in pairs)==sorted(expected),at,'exact independent sort mapping')
                    check(len(pairs)==len(options),at,'all sort cards mapped once')
                    check(r['answer']==[],at,'sort answer array empty')
                elif engine=='memory':
                    check(2<=len(options)<=3,at,'two or three canonical memory cards')
                    check(all(o['label']['en'] in MEMORY_ALLOWED for o in options),at,'known mealtime cards')
                    check(r['answer']==[],at,'memory answer array empty')
    # These checks assess authored wording, not real children's behavior.
    for w in worksheets:
        for r in w['rounds']:
            text = r['instruction']['en'].lower()
            check(not any(x in text for x in ['bad child','dirty child','will get sick','must hug','must obey','finish your plate']),w['id'],'no fear shame coercion in prompts')
    return {'passed':not errors,'errors':errors,'checks':dict(checks),'semanticVariants':variation,
            'semanticTaskSets':task_sets,'distinctAuthoredScenarios':scenarios}


def mutation_checks(categories, worksheets):
    results = {}
    for cid in ENGINES:
        altered = copy.deepcopy(worksheets)
        w = next(w for w in altered if w['category']==cid)
        r = w['rounds'][0]
        if w['engine']=='identify':
            r['answer'] = [next(o['id'] for o in r['options'] if o['id'] not in r['answer'])]
        elif w['engine']=='sequence':
            r['answer'] = list(reversed(r['answer']))
        elif w['engine']=='pair':
            r['pairs'][0]['right'],r['pairs'][1]['right'] = r['pairs'][1]['right'],r['pairs'][0]['right']
        elif w['engine']=='sort':
            r['pairs'][0]['right'] = next(b['id'] for b in r['bins'] if b['id']!=r['pairs'][0]['right'])
        elif w['engine']=='memory':
            r['options'][1] = {**copy.deepcopy(r['options'][0]),'id':r['options'][1]['id']}
        w.update(copy.deepcopy(r))  # keep root mirror valid, isolate semantic fault
        result = validate(categories,altered,False)
        results[cid] = {'detected':not result['passed'],'errors':result['errors'][:3]}
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
    args = p.parse_args()
    categories = json.loads((args.out/'expansion-categories.json').read_text())
    worksheets = json.loads((args.out/'expansion-worksheets.json').read_text())
    report = validate(categories,worksheets)
    report['negativeMutations'] = mutation_checks(categories,worksheets)
    report['passed'] = report['passed'] and all(r['detected'] for r in report['negativeMutations'].values())
    report['counts'] = {'categories':len(categories),'worksheets':len(worksheets),'rounds':sum(len(w['rounds']) for w in worksheets)}
    report['sha256'] = {name:hashlib.sha256((args.out/name).read_bytes()).hexdigest() for name in ['expansion-categories.json','expansion-worksheets.json']}
    report['limits'] = ['Cannot verify visual identity, crop fidelity, browser rendering or interaction.',
                        'Text completeness and Chinese character coverage do not replace native-speaker review.',
                        'Instruction-following sequences are short stories, not complete medical or care protocols.',
                        'Independent identify fixtures verify selected action meanings; they do not clinically validate advice.']
    (args.out/'semantic-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'errors':report['errors'],'counts':report['counts'],'semanticVariants':report['semanticVariants'],'semanticTaskSets':report['semanticTaskSets']},ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':
    main()
