# Archived Scripts

This directory contains one-time use scripts that have completed their purpose and are preserved for historical reference.

## Directory Structure

### diagnostics/
One-time diagnostic scripts that identified issues in the lexicon data:

- `audit_lexicon.py` - Audited mismatches between Strong's and BDB definitions
- `diagnose_homonyms.py` - Identified Strong's numbers with multiple BDB entries (found 254 words)
- `homograph_audit.py` - Found Strong's entries with multiple BDB entries sharing same lemma
- `validate_root_refs.py` - Validated root_ref integrity between words.json and roots.json
- `verify_ready_for_translation.py` - Pre-translation verification checklist
- `check_empty_translations.py` - Checked for empty Spanish translations after API mismatches
- `final_quality_check.py` - Final translation quality check before deployment

### fixes/
One-time fix scripts that corrected data issues:

- `fix_homonyms.py` - Regenerated 254 lexicon entries affected by homonym issues
- `fix_empty_translations.py` - Re-translated 10 empty Spanish definitions
- `translate_fixed_homonyms.py` - Translated only the 254 homonym-fixed words to Spanish

### legacy/
Older versions of main scripts, preserved as backups:

- `lexicon_builder.py` - Legacy lexicon builder (older version of build_lexicon.py)
- `verse_builder_backup.py` - Legacy verse builder (backup copy)

### tests/
Manual test scripts:

- `test_bdb_parse.py` - Quick test for BDB XML parsing with/without namespace

### migration/
Data migration scripts (already in temp/ from previous work):

- `migrate_lexicon.py` - Consolidated individual lexicon files into roots.json/words.json
- `migrate_verses.py` - Consolidated individual verse files into book JSON files
- `optimize_json.py` - Minifies JSON files for production

## Status

All scripts in this directory have **completed their one-time purpose** as of February 2026:

- ✅ Homonym issues fixed (254 words regenerated)
- ✅ Spanish translations complete (15,101 definitions)
- ✅ Empty translations fixed (10 entries)
- ✅ Migrations completed (lexicon and verses)
- ✅ Quality checks passed

## Usage

These scripts are archived for reference and should not be run again unless:

1. **Diagnostics**: You need to re-audit the lexicon data structure
2. **Fixes**: You encounter similar issues with new data
3. **Legacy**: You need to reference older implementation approaches

## Current Active Scripts

For ongoing lexicon work, use the main directory scripts:

- `build_lexicon.py` - Main lexicon builder
- `build_verses.py` - Main verse builder
- `qa.py` - Quality assurance
- `integrate_custom_dict.py` - Custom dictionary integration
- `rebuild_lexicon_consolidated.py` - Rebuild consolidated files
- `translation/` - Translation management package

## Historical Context

### Homonym Fix (February 2026)

The most significant fix addressed BDB homonym handling. The diagnostic found 254 Strong's numbers with multiple BDB entries (mod="I", mod="II", etc.). The fix script:

1. Prioritized mod="I" entries over mod="II"+ entries
2. Preserved existing Spanish translations
3. Generated detailed report (`homonym_fixes_report.md`)
4. Most notable fix: H1254 (ברא "bara") now correctly shows "shape, create" instead of "be fat"

### Translation Issues (February 2026)

The Grok API translation experienced 35% batch mismatch rate (count mismatch between input/output). Solutions implemented:

1. Padding with empty strings for short responses
2. Truncation for long responses  
3. Re-translation of 10 affected definitions
4. Statistics tracking for quality monitoring

See `translation_final_report.md` in `data/dict/` for complete details.
