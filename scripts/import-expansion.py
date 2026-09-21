"""Merge a normalized, additive curriculum expansion without changing previous IDs."""
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent.parent
source = pathlib.Path(sys.argv[1])
read = lambda p: json.loads(p.read_text())
write = lambda p, data: p.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
new_categories = read(source / ('expansion-categories.json' if (source / 'expansion-categories.json').exists() else 'categories.json'))
new_records = read(source / 'expansion-worksheets.json') if (source / 'expansion-worksheets.json').exists() else [w for c in new_categories for w in read(source / 'bundles' / (c['id'] + '.json'))]
new_ids = {c['id'] for c in new_categories}
categories = [c for c in read(root / 'app/data/worksheet-categories.json') if c['id'] not in new_ids]
assert len(new_ids) == len(new_categories)
assert len({w['id'] for w in new_records}) == len(new_records)
for c in new_categories:
    records = [w for w in new_records if w['category'] == c['id']]
    assert len(records) == 24, c['id']
    assert all(len(w['rounds']) == 4 for w in records)
    if all('activityKind' in w for w in records): c['activityKinds'] = list(dict.fromkeys(w['activityKind'] for w in records))
    c['worksheetCount'] = len(records)
    write(root / 'public/worksheets' / (c['id'] + '.json'), records)
categories = new_categories + categories
records = [w for c in categories for w in read(root / 'public/worksheets' / (c['id'] + '.json'))]
assert len({w['id'] for w in records}) == len(records)
index = []
for w in records:
    item = {k: w[k] for k in ['id', 'category', 'title', 'engine', 'variant', 'age', 'ageRange', 'difficulty', 'instruction']}
    item.update(options=w['options'][:3], answer=[])
    for field in ['activityKind','revision']:
        if field in w: item[field]=w[field]
    index.append(item)
write(root / 'app/data/worksheet-index.json', index)
write(root / 'app/data/worksheet-categories.json', categories)
report = dict(worksheets=len(records), categories=len(categories), rounds=sum(len(w['rounds']) for w in records), engines=sorted({w['engine'] for w in records}), classification='Practice variations, not distinct activity types', editorialReview='not independently reviewed')
(root / 'public/specs/workbook-catalogue-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report))
