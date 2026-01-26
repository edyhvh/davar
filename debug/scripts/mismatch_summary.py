import json
from pathlib import Path
from collections import Counter

path = Path('/Users/jhonny/davar/scripts/dict/lexicon_audit_results.json')
if not path.exists():
    raise SystemExit('lexicon_audit_results.json not found')

mismatches = json.loads(path.read_text(encoding='utf-8'))


def categorize(def_text: str) -> str:
    t = (def_text or '').lower()
    if 'a place' in t or 'place in' in t or 'place of' in t:
        return 'place'
    if 'a person' in t or 'a man' in t or 'a woman' in t or 'a son' in t or 'a daughter' in t:
        return 'person'
    if 'a city' in t or 'a town' in t:
        return 'place'
    if 'a king' in t or 'a priest' in t or 'a prophet' in t:
        return 'person'
    if 'an angel' in t:
        return 'person'
    if 'a people' in t or 'a nation' in t or 'a tribe' in t:
        return 'people'
    if 'a river' in t or 'a mountain' in t or 'a valley' in t or 'a desert' in t:
        return 'place'
    return 'other'


counts = Counter()
for item in mismatches:
    counts[categorize(item.get('raw_strongs_def', ''))] += 1

summary_path = Path('/Users/jhonny/davar/debug/output/mismatch_summary.txt')
with summary_path.open('w', encoding='utf-8') as f:
    f.write('Mismatch category counts:\n')
    for key, value in counts.most_common():
        f.write(f'{key}: {value}\n')
    f.write('\nTop 20 with 0 BDB defs:\n')
    zero_defs = [m for m in mismatches if m.get('lexicon_bdb_count') == 0][:20]
    for entry in zero_defs:
        f.write(f"{entry.get('strong_number')} {entry.get('lemma')} | raw: {entry.get('raw_strongs_def')}\n")

print(f'Wrote {summary_path}')
