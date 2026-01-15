# Hebrew Prefix Dictionary System

A comprehensive dictionary system for Hebrew prefixes (inseparable prepositions) in the Davar Bible study app.

## Overview

This system processes Hebrew particles from CSV data and integrates them into the OE (OpenScripture Enhanced) text files. The system consists of:

1. **Dictionary Entries** - Individual JSON files for each particle with bilingual meanings
2. **Forms Discovery** - Automatic scanning of OE files to find all particle variants
3. **OE Integration** - Adding `particles` field to word objects for app lookup
4. **Validation** - Comprehensive checks for data integrity

## Directory Structure

```
data/dict/particles/
├── entries/              # Individual particle definitions
│   ├── Hb.json          # בְּ (preposition)
│   ├── Hd.json          # הַ (definite article)
│   ├── Hc.json          # וְ (conjunction)
│   └── ...              # 12 total entries
├── particles.json       # Master index
└── forms_lookup.json    # Quick form→ID mapping

scripts/particles/
├── import_csv.py        # Step 1: Import from CSV
├── scan_oe_forms.py     # Step 2: Discover forms
├── update_oe_files.py   # Step 3: Add particles field
├── validate.py          # Step 4: Validate system
└── README.md           # This file
```

## Hebrew Prefix Types

### Inseparable Prefixes (7)
- `Hb` = בְּ (be - in/with/by/against/into/during/because of)
- `Hd` = הַ (ha - definite article)
- `Hc` = וְ (ve - conjunction: and/but/then/so/waw-consecutive)
- `Hl` = לְ (le - to/for/toward/belonging to/according to)
- `Hm` = מִ (mi - from/out of/than/because of)
- `Hk` = כְּ (ke - as/like/according to/about/when)
- `Ht` = אֵת (et - direct object marker for definite nouns)

**Note:** Only inseparable prefixes are included. Standalone particles (נָא, אַל, אֵין, הִנֵּה, כִּי) are excluded as they have Strong's dictionary definitions.

## Usage

### Step 1: Import CSV Data

Parse bilingual CSV files and create dictionary entries:

```bash
# Test mode - show what would be created
python scripts/particles/import_csv.py --test --verbose

# Production - create the files
python scripts/particles/import_csv.py --verbose
```

**Input:** `data/not_strong/chart_en.csv`, `data/not_strong/chart_es.csv`
**Output:** 12 JSON entries + master index

### Step 2: Scan OE Files for Forms

Discover all particle forms and calculate frequencies:

```bash
# Test mode - scan only Genesis 1
python scripts/particles/scan_oe_forms.py --test --verbose

# Scan specific book
python scripts/particles/scan_oe_forms.py --book genesis --verbose

# Full scan (production)
python scripts/particles/scan_oe_forms.py --verbose
```

**Input:** All OE JSON files
**Output:** Updated dictionary entries with forms/frequencies + forms lookup

### Step 3: Update OE Files

Add `particles` array to word objects:

```bash
# Test mode - update only Genesis 1
python scripts/particles/update_oe_files.py --test --dry-run --verbose

# Update specific book
python scripts/particles/update_oe_files.py --book genesis --verbose

# Full update (production)
python scripts/particles/update_oe_files.py --verbose
```

**Input:** OE JSON files
**Output:** OE files with `particles` field added

### Step 4: Validate System

Check data integrity and coverage:

```bash
# Test mode - validate only Genesis
python scripts/particles/validate.py --test --verbose

# Validate specific book
python scripts/particles/validate.py --book genesis

# Full validation
python scripts/particles/validate.py --verbose
```

**Output:** Comprehensive validation report

## Example Data

### Dictionary Entry (`data/dict/particles/entries/Hb.json`)

```json
{
  "id": "Hb",
  "main_form": "בְּ",
  "type": "Inseparable preposition",
  "meanings": {
    "en": ["in", "at", "with", "by", "among", "against", "into", "during", "because of"],
    "es": ["en", "con", "por", "entre", "contra", "dentro de", "durante", "a causa de"]
  },
  "notes": {
    "en": "Highly polysemous; many semantic fields",
    "es": "Muy polisémica; muchos campos semánticos"
  },
  "forms": ["בְּ", "בָּ", "בְ", "ב"],
  "frequency": 15432
}
```

### OE Word Object (updated)

```json
{
  "text": "וְ/הָ/אָ֗רֶץ",
  "text_no_nikud": "ו/ה/ארץ",
  "lemma": "Hc/Hd/H776",
  "strong": "Hc/Hd/H776",
  "morph": "HC/Td/Ncbsa",
  "particles": ["Hc", "Hd"]
}
```

## Key Features

### Maqqef Handling
- CSV forms like `אֵת־` are normalized to `אֵת`
- OE files use slash separators (`/`), no maqqef needed

### Form Discovery
- Automatically finds all variants (with/without nikud)
- Calculates frequency from actual usage
- Updates dictionary with discovered forms

### Validation
- Checks particle ID validity
- Verifies coverage (words with particle lemmas have particles field)
- Validates forms lookup consistency
- Reports orphaned particles and missing fields

## Command Flow

```bash
# 1. Import dictionary from CSV
python scripts/particles/import_csv.py

# 2. Scan OE files to discover forms
python scripts/particles/scan_oe_forms.py

# 3. Update OE files with particles field
python scripts/particles/update_oe_files.py

# 4. Validate everything
python scripts/particles/validate.py
```

## Testing

All scripts support `--test` for safe testing:

```bash
# Test each step individually
python scripts/particles/import_csv.py --test
python scripts/particles/scan_oe_forms.py --test --dry-run
python scripts/particles/update_oe_files.py --test --dry-run
python scripts/particles/validate.py --test
```

## Troubleshooting

### Common Issues

1. **CSV file not found**: Check `data/not_strong/` directory exists
2. **Invalid particle ID**: Check PARTICLE_MAPPING in scripts
3. **Missing forms**: Run scan script to discover forms
4. **Low coverage**: Check lemma parsing logic

### Debug Mode

Use `--verbose` flag with any script for detailed output:

```bash
python scripts/particles/scan_oe_forms.py --test --verbose
```

## Integration with Davar App

The React Native app can now:

1. **Look up particles** by ID from `particles.json`
2. **Find particle meanings** in English/Spanish
3. **Display forms** discovered from actual usage
4. **Query by form** using `forms_lookup.json`

Example app usage:
```typescript
// Get particle definition
const particle = particles[particleId];

// Get all forms for a particle
const forms = particle.forms;

// Find particle IDs for a form
const particleIds = formsLookup[form];
```