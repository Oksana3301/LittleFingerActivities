"""Bounded semantic audit of actual generated questions, independent of renderer."""
import json
from pathlib import Path
from collections import Counter,defaultdict

P=Path(__file__).parent
worksheets=json.loads((P/'worksheets.json').read_text())
flat=json.loads((P/'worksheets-flat.json').read_text())
errors=[]; counts=Counter(); guide_kinds=Counter(); scene_kinds=Counter(); visual_kinds=Counter()
def fail(w,k,msg): errors.append(f"{w['id']} round {k+1}: {msg}")
def key(v,criterion='identity'):
    kind=v['kind']
    if criterion=='color': return v.get('color')
    if criterion=='shape': return v.get('shape')
    if criterion=='letter-case': return v.get('text','').lower()
    if criterion=='quantity': return str(v.get('count',v.get('text')))
    if kind=='asset': return ('asset',v['asset'])
    if kind=='glyph': return ('glyph',v['text'])
    if kind=='shape': return ('shape',v['shape'],v['color'])
    if kind=='measurement': return ('measure',v['measure'],v['value'])
    if kind=='quantity': return ('quantity',v['count'])
    if kind=='arrow': return ('arrow',v['direction'])
    raise ValueError(v)

for w in worksheets:
    cid=w['categoryId']
    for k,r in enumerate(w['rounds']):
        counts[w['engine']]+=1
        for o in r.get('options',[]): visual_kinds[o['visual']['kind']]+=1
        for g in r.get('canvas',{}).get('guide',[]): guide_kinds[g['kind']]+=1
        if 'scene' in r: scene_kinds[r['scene']['kind']]+=1
        if 'options' in r and 'correctIds' in r and cid!='positions':
            # Visually equivalent options must never receive contradictory marks.
            by_visual=defaultdict(set)
            for o in r['options']: by_visual[key(o['visual'])].add(o['id'] in r['correctIds'])
            if any(len(x)>1 for x in by_visual.values()): fail(w,k,'Identical rendered choices have inconsistent answers')
        if 'correctPairs' in r:
            criterion=r.get('criterion','identity')
            l={x['id']:key(x['visual'],criterion) for x in r['left']}; rr={x['id']:key(x['visual'],criterion) for x in r['right']}
            if len(set(l.values()))!=len(l) or len(set(rr.values()))!=len(rr): fail(w,k,'Ambiguous matching key')
            if any(l[a]!=rr[b] for a,b in r['correctPairs']): fail(w,k,'Mismatched pair answer')
        if 'cards' in r:
            pairs=defaultdict(list)
            for card in r['cards']: pairs[card['pairKey']].append(key(card['visual']))
            if any(len(v)!=2 or v[0]!=v[1] for v in pairs.values()): fail(w,k,'Invalid memory pair')
            if len({v[0] for v in pairs.values()})!=len(pairs): fail(w,k,'Duplicate memory pair artwork')
        if cid=='same-different':
            reference=key(r['reference']); same='sama persis' in r['prompt']['id']; expected=[o['id'] for o in r['options'] if (key(o['visual'])==reference)==same]
            if set(expected)!=set(r['correctIds']): fail(w,k,'Same/different incorrect')
        if cid=='initial-letters':
            initial=r['reference']['text']; expected=[o['id'] for o in r['options'] if o['visual']['label']['id'].upper().startswith(initial)]
            if set(expected)!=set(r['correctIds']): fail(w,k,'Incorrect Indonesian initial')
        if cid in ['vowels','consonants']:
            expected=[o['id'] for o in r['options'] if (o['visual']['text'].upper() in 'AEIOU')==(cid=='vowels')]
            if set(expected)!=set(r['correctIds']): fail(w,k,'Vowel/consonant answer incorrect')
        if cid in ['size','length','height','thickness','compare-quantity']:
            field='count' if cid=='compare-quantity' else 'value'; vals={o['id']:o['visual'][field] for o in r['options']}; maximize=(w['variant']-1)*4+k; target=max(vals.values()) if maximize%2==0 else min(vals.values())
            if r['correctIds']!=[id for id,n in vals.items() if n==target]: fail(w,k,'Wrong comparison extreme')
        if 'scene' in r:
            s=r['scene']
            answer=s['count'] if s['kind']=='quantity' else s['a']+s['b'] if s['operation']=='add' else s['a']-s['b']
            if r['correctIds']!=[f'n{answer}']: fail(w,k,'Wrong counted/arithmetic result')
        if 'sequence' in r:
            seq=r['sequence']; missing=seq.index(None); selected=next(o['visual'] for o in r['options'] if o['id']==r['correctIds'][0]); rule=r['rule']
            if rule['type']=='repeating':
                unit=rule['unit']; equivalent=[key(item) for i,item in enumerate(seq) if item and unit[i%len(unit)]==unit[missing%len(unit)]]
                if not equivalent or any(x!=key(selected) for x in equivalent): fail(w,k,'Repeating pattern incorrect or underdetermined')
            elif rule['type']=='number-step':
                numbers=[int(item['text']) if item else int(selected['text']) for item in seq]
                if any(b-a!=rule['step'] for a,b in zip(numbers,numbers[1:])): fail(w,k,'Missing number incorrect')
            elif rule['type']=='quantity-step':
                numbers=[item['count'] if item else int(selected['text']) for item in seq]
                if any(b-a!=rule['step'] for a,b in zip(numbers,numbers[1:])): fail(w,k,'Growing pattern incorrect')
        if 'correctOrder' in r:
            vals={o['id']:int(o['visual']['text']) for o in r['options']}; seq=[vals[id] for id in r['correctOrder']]
            if seq!=sorted(seq,reverse=cid=='descending'): fail(w,k,'Wrong numerical order')

for w in flat:
    for k,r in enumerate(w['rounds']):
        for o in r['options']+r.get('rightOptions',[]):
            if 'label' not in o: fail(w,k,f"Missing normalized label: {o['kind']}")
            if o['kind']=='quantity' and not o.get('hideLabel'): fail(w,k,'Quantity numeric label could reveal answer')

report=dict(status='passed' if not errors else 'failed',errors=errors,roundsByEngine=dict(counts),optionVisualKinds=dict(visual_kinds),sceneKinds=dict(scene_kinds),canvasGuideKinds=dict(guide_kinds),checks=['Equivalent appearances receive consistent answers','Matching keys are unique and paired correctly','Memory uses exactly two cards per unique picture','Same/different, Indonesian initials, vowels/consonants agree with answers','Measurement extremes agree with answer','Counting and arithmetic agree with rendered scenes','Repeating patterns have observed evidence and a correct fill','Number/growing patterns satisfy their numeric step','Number ordering is correct','Flat options have labels; quantity labels are hidden'])
(P/'semantic-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)); print(json.dumps(report,ensure_ascii=False,indent=2))
assert not errors
