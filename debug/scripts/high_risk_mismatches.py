import json
from pathlib import Path
import re

mismatch_path = Path('/Users/jhonny/davar/scripts/dict/lexicon_audit_results.json')
if not mismatch_path.exists():
    raise SystemExit('lexicon_audit_results.json not found')

mismatches = json.loads(mismatch_path.read_text(encoding='utf-8'))


def tokens(text: str) -> set[str]:
    if not text:
        return set()
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return {t for t in cleaned.split() if len(t) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

high_risk = []
for entry in mismatches:
    bdb_defs = entry.get('lexicon_bdb_defs', [])
    if not bdb_defs:
        continue

    raw_parts = [entry.get('raw_strongs_def', ''), entry.get('raw_kjv_def', '')]
    raw_tokens = tokens(' '.join(raw_parts))
    bdb_tokens = tokens(' '.join(bdb_defs))

    score = jaccard(raw_tokens, bdb_tokens)
    if score < 0.1:
        high_risk.append({
            'strong_number': entry.get('strong_number'),
            'lemma': entry.get('lemma'),
            'score': score,
            'raw_strongs_def': entry.get('raw_strongs_def'),
            'raw_kjv_def': entry.get('raw_kjv_def'),
            'lexicon_bdb_defs': bdb_defs[:5],
        })

high_risk.sort(key=lambda x: x['score'])

out_txt = Path('/Users/jhonny/davar/debug/output/high_risk_mismatches.txt')
out_json = Path('/Users/jhonny/davar/debug/output/high_risk_mismatches.json')

with out_txt.open('w', encoding='utf-8') as f:
    f.write(f'High-risk mismatches (score < 0.1): {len(high_risk)}\n\n')
    for entry in high_risk[:200]:
        f.write(f"{entry['strong_number']} {entry['lemma']} | score={entry['score']:.3f}\n")
        f.write(f"  raw strongs: {entry['raw_strongs_def']}\n")
        f.write(f"  raw kjv: {entry['raw_kjv_def']}\n")
        f.write(f"  bdb defs: {', '.join(entry['lexicon_bdb_defs'])}\n\n")

out_json.write_text(json.dumps(high_risk, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'Wrote {out_txt}')
print(f'Wrote {out_json}')
