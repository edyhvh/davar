# Missing BDB Sense Audit

Issue #18 tracks incomplete lexicon entries where LexicalIndex maps a Strong's number to multiple BDB senses, but the processed lexicon does not expose all of those glosses.

## Summary

- LexicalIndex Strong's numbers checked: 8681
- Lexicon entries checked: 8674
- Affected entries: 0
- Missing definition glosses: 0
- Entries missing 1 gloss: 0
- Entries missing 2 glosses: 0
- Entries missing 3+ glosses: 0
- Bani auto-transliteration coverage for assessed missing glosses: 0%

## Transliteration Decision

Do not backfill definitions in this phase. Future definition additions should reuse lemma-level translit_en/translit_es unless product requirements demand per-definition pronunciation fields.

The missing definitions are English glosses, while `translit_en` and `translit_es` are lemma pronunciation guides. For the next phase, the lower-risk strategy is to reuse the entry's lemma-level transliteration on any new definition records instead of trying to transliterate English gloss text.

## Top 0 Affected Entries

| Strong | Lemma | Missing | Missing glosses | Bani coverage | File |
| --- | --- | ---: | --- | --- | --- |
