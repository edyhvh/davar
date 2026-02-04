# Lexicon Root Transliteration

Add simplified bilingual transliteration (`translit_en`/`translit_es`) to Hebrew root entries in the lexicon.

## Quick Start

```bash
# Transliterate all roots (adds translit_en and translit_es to each H*.json file)
python -m scripts.translit.main --corpus lexicon

# Test with a single root first (dry run)
python -m scripts.translit.main --corpus lexicon --strong-number H1 --dry-run

# Test with a single root (actual run)
python -m scripts.translit.main --corpus lexicon --strong-number H1

# Verbose output for debugging
python -m scripts.translit.main --corpus lexicon --verbose
```

## What It Does

1. **Reads root lemmas** from `data/dict/lexicon/roots/H*.json`
2. **Transliterates** each lemma using the same rules as verse-level transliteration
3. **Adds two new fields** to each root entry:
   - `translit_en`: Simplified English transliteration (e.g., "av")
   - `translit_es`: Simplified Spanish transliteration (e.g., "av")
4. **Preserves all existing fields** (definitions, occurrences, sources, etc.)
5. **Skips entries** that already have transliteration

## Workflow

```bash
# Step 1: Add transliteration to individual root files
python -m scripts.translit.main --corpus lexicon

# Step 2: Rebuild consolidated roots.json (includes new fields automatically)
python -m scripts.dict.rebuild_lexicon_consolidated

# Step 3: Restart backend to load updated lexicon
# (Backend automatically returns root_translit_en and root_translit_es)
```

## Output Example

Before:
```json
{
  "strong_number": "H1",
  "lemma": "אָב",
  "normalized": "אב",
  "pronunciation": "awb",
  "transliteration": "ʼâb",
  "definitions": [...],
  "is_root": true
}
```

After:
```json
{
  "strong_number": "H1",
  "lemma": "אָב",
  "normalized": "אב",
  "pronunciation": "awb",
  "transliteration": "ʼâb",
  "translit_en": "av",
  "translit_es": "av",
  "definitions": [...],
  "is_root": true
}
```

## Safety

- **Non-destructive**: Only adds fields, never removes or modifies existing ones
- **Idempotent**: Safe to run multiple times (skips already-done entries)
- **Fast**: Uses local rules, no API calls (cost: $0.00)
- **Dry-run mode**: Test before making changes

## Integration

- **Backend**: `LexiconResponse` now includes `root_translit_en` and `root_translit_es`
- **Frontend**: `WordCard` displays root transliteration and conditionally shows meaning
- **DSS**: Dead Sea Scrolls variants also get on-demand transliteration
