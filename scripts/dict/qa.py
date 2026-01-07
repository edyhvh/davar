#!/usr/bin/env python3
"""
Consolidated QA Script for Lexicon
Combines all QA functionality into a single script
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
import xml.etree.ElementTree as ET

# Project paths
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'dict'
LEXICON_DIR = DATA_DIR / 'lexicon'
LEXICON_DRAFT = LEXICON_DIR / 'words'  # Now called 'words' instead of 'draft'
LEXICON_ROOTS = LEXICON_DIR / 'roots'
RAW_DIR = DATA_DIR / 'raw'
STRONGS_FILE = RAW_DIR / 'strongs_hebrew_dict_en.json'
STRONG_REFS_FILE = RAW_DIR / 'strong_refs.json'
BDB_XML = RAW_DIR / 'BrownDriverBriggs.xml'

NS = {'bdb': 'http://openscriptures.github.com/morphhb/namespace'}


def load_strongs_data() -> Dict:
    """Load Strong's dictionary data"""
    if STRONGS_FILE.exists():
        with open(STRONGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_strong_refs() -> Dict:
    """Load Strong's references data"""
    if STRONG_REFS_FILE.exists():
        with open(STRONG_REFS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_bdb_xml():
    """Load BDB XML file"""
    if not BDB_XML.exists():
        return None
    try:
        tree = ET.parse(BDB_XML)
        return tree.getroot()
    except Exception:
        return None


def validate_file_structure(filepath: Path, is_root: bool) -> Dict:
    """Validate structure of a lexicon file"""
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            'file': filepath.name,
            'status': 'error',
            'errors': [f'Invalid JSON: {e}'],
            'warnings': []
        }
    except Exception as e:
        return {
            'file': filepath.name,
            'status': 'error',
            'errors': [f'Error reading file: {e}'],
            'warnings': []
        }
    
    # Required fields
    required_fields = ['strong_number', 'lemma', 'definitions', 'occurrences', 'sources']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
    
    # Validate strong_number matches filename
    if 'strong_number' in data:
        expected_filename = f"{data['strong_number']}.json"
        if filepath.name != expected_filename:
            errors.append(f'Filename mismatch: expected {expected_filename}, got {filepath.name}')
    
    # Validate is_root matches directory
    if 'is_root' in data:
        if is_root and not data['is_root']:
            errors.append(f'File in roots/ but is_root=False')
        elif not is_root and data['is_root']:
            errors.append(f'File in draft/ but is_root=True')
    elif is_root:
        warnings.append('Missing is_root field (should be True for roots/)')
    
    # Validate definitions
    if 'definitions' in data:
        definitions = data['definitions']
        if not isinstance(definitions, list):
            errors.append('definitions must be a list')
        else:
            for i, defn in enumerate(definitions):
                if not isinstance(defn, dict):
                    errors.append(f'Definition {i} is not a dictionary')
                    continue
                
                # Check required definition fields
                if 'text_en' not in defn:
                    errors.append(f'Definition {i} missing "text_en" field')
                if 'source' not in defn:
                    errors.append(f'Definition {i} missing "source" field')
                if 'order' not in defn:
                    errors.append(f'Definition {i} missing "order" field')
                
                # Validate source
                if 'source' in defn:
                    valid_sources = ['bdb', 'strongs', 'strongs_kjv']
                    if defn['source'] not in valid_sources:
                        warnings.append(f'Definition {i} has unknown source: {defn["source"]}')
                
                # Validate sense for BDB definitions
                if defn.get('source') == 'bdb':
                    if 'sense' not in defn:
                        warnings.append(f'BDB definition {i} missing "sense" field')
                    else:
                        sense = defn.get('sense')
                        if sense is None:
                            warnings.append(f'BDB definition {i} has sense=None (should be "0" or number)')
                        elif sense == '':
                            errors.append(f'BDB definition {i} has empty sense string')
                        elif not isinstance(sense, str):
                            warnings.append(f'BDB definition {i} has non-string sense: {sense}')
    
    # Validate occurrences
    if 'occurrences' in data:
        occ = data['occurrences']
        if not isinstance(occ, dict):
            errors.append('occurrences must be a dictionary')
        else:
            if 'total' not in occ:
                errors.append('occurrences missing "total" field')
            if 'references' not in occ:
                errors.append('occurrences missing "references" field')
            elif isinstance(occ.get('references'), list):
                total = occ.get('total', 0)
                ref_count = len(occ['references'])
                if total != ref_count:
                    errors.append(f'occurrences.total ({total}) != len(references) ({ref_count})')
                
                # Validate reference format
                for ref in occ['references'][:10]:
                    if not isinstance(ref, str):
                        errors.append(f'Invalid reference format: {ref}')
                    elif not re.match(r'^[a-z0-9]+\.[0-9]+\.[0-9]+$', ref.lower()):
                        warnings.append(f'Reference format might be invalid: {ref}')
    
    # Validate sources
    if 'sources' in data:
        sources = data['sources']
        if not isinstance(sources, dict):
            errors.append('sources must be a dictionary')
        else:
            if 'bdb' not in sources and 'strongs' not in sources:
                warnings.append('No sources marked as available')
    
    # Validate root_ref (should not be in roots/)
    if is_root and 'root_ref' in data:
        errors.append('Root file should not have root_ref field')
    
    # Validate root_ref exists (if present)
    if not is_root and 'root_ref' in data:
        root_ref = data['root_ref']
        root_file = LEXICON_ROOTS / f"{root_ref}.json"
        if not root_file.exists():
            warnings.append(f'root_ref {root_ref} does not exist in roots/')
    
    return {
        'file': filepath.name,
        'status': 'error' if errors else ('warning' if warnings else 'ok'),
        'errors': errors,
        'warnings': warnings,
        'data': data
    }


def validate_cross_references(draft_files: List[Path], root_files: List[Path]) -> Dict:
    """Validate cross-references between draft and roots"""
    root_refs_used = set()
    root_refs_missing = []
    
    for filepath in draft_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'root_ref' in data:
                root_ref = data['root_ref']
                root_refs_used.add(root_ref)
                root_file = LEXICON_ROOTS / f"{root_ref}.json"
                if not root_file.exists():
                    root_refs_missing.append({
                        'file': filepath.name,
                        'root_ref': root_ref
                    })
        except Exception:
            pass
    
    root_numbers = {f.stem for f in root_files}
    orphaned_roots = root_numbers - root_refs_used
    
    return {
        'root_refs_used': len(root_refs_used),
        'root_refs_missing': root_refs_missing,
        'orphaned_roots': len(orphaned_roots),
        'orphaned_root_samples': list(orphaned_roots)[:10]
    }


def validate_strongs_coverage(lexicon_files: Set[str], strongs_data: Dict) -> Dict:
    """Validate that all Strong's entries are covered"""
    strongs_numbers = {k for k in strongs_data.keys() if k.startswith('H')}
    missing = strongs_numbers - lexicon_files
    extra = lexicon_files - strongs_numbers
    
    return {
        'strongs_count': len(strongs_numbers),
        'lexicon_count': len(lexicon_files),
        'coverage': len(lexicon_files) / len(strongs_numbers) * 100 if strongs_numbers else 0,
        'missing': list(missing)[:20],
        'missing_count': len(missing),
        'extra': list(extra)[:20],
        'extra_count': len(extra)
    }


def validate_occurrences_coverage(lexicon_files: List[Path], strong_refs: Dict) -> Dict:
    """Validate occurrences match Strong's references"""
    issues = []
    checked = 0
    
    for filepath in lexicon_files[:100]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            strong_number = data.get('strong_number')
            if not strong_number:
                continue
            
            if strong_number in strong_refs:
                strong_total = len(strong_refs[strong_number].get('references', []))
                lexicon_total = data.get('occurrences', {}).get('total', 0)
                
                if strong_total != lexicon_total:
                    issues.append({
                        'file': filepath.name,
                        'strong_total': strong_total,
                        'lexicon_total': lexicon_total,
                        'difference': lexicon_total - strong_total
                    })
                
                checked += 1
        except Exception:
            pass
    
    return {
        'checked': checked,
        'mismatches': len(issues),
        'sample_issues': issues[:10]
    }


def check_empty_senses(bdb_root) -> Dict:
    """Check for files with empty sense strings"""
    files_with_empty = []
    
    for filepath in list(LEXICON_DRAFT.glob("H*.json")) + list(LEXICON_ROOTS.glob("H*.json")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for defn in data.get('definitions', []):
                if defn.get('source') == 'bdb' and defn.get('sense') == '':
                    files_with_empty.append(filepath.name)
                    break
        except Exception:
            pass
    
    return {
        'count': len(files_with_empty),
        'samples': files_with_empty[:10]
    }


def check_incomplete_sense_hierarchy() -> Dict:
    """
    Check for files with incomplete sense hierarchy (e.g., 'a' instead of '1a')
    
    NOTE: Single-letter senses at top level (e.g., 'a', 'b', 'c') are VALID in BDB XML
    when they are top-level senses. We only flag them if they appear alongside
    numeric senses, which suggests they should be hierarchical.
    """
    files_with_incomplete = []
    
    for filepath in list(LEXICON_DRAFT.glob("H*.json")) + list(LEXICON_ROOTS.glob("H*.json")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            definitions = data.get('definitions', [])
            if not definitions:
                continue
            
            # Get all BDB senses
            bdb_senses = [d.get('sense', '') for d in definitions if d.get('source') == 'bdb']
            
            # Check if we have numeric senses (excluding "0" which is our convention for main defs)
            # and single-letter senses. Single letters are valid as top-level senses,
            # but if they appear with numeric senses (1, 2, 3...), they should be hierarchical
            has_numeric_sense = any(s and s[0].isdigit() and s != "0" for s in bdb_senses)
            has_single_letter = any(s and len(s) == 1 and s.isalpha() and s.islower() for s in bdb_senses)
            
            # Only flag if we have BOTH numeric senses (1+) and single-letter senses
            # (meaning single letters are likely nested, not top-level)
            # Note: "0" + single letters is VALID (single letters are top-level senses)
            if has_numeric_sense and has_single_letter:
                # Find the problematic definitions
                for defn in definitions:
                    if defn.get('source') == 'bdb':
                        sense = defn.get('sense', '')
                        if sense and len(sense) == 1 and sense.isalpha() and sense.islower():
                            files_with_incomplete.append({
                                'file': filepath.name,
                                'sense': sense,
                                'definition': defn.get('text', '')[:50]
                            })
                            break
        except Exception:
            pass
    
    return {
        'count': len(files_with_incomplete),
        'samples': files_with_incomplete[:10]
    }


def check_etymological_definitions(bdb_root) -> Dict:
    """Check for entries with etymological-looking definitions"""
    etymological_patterns = [
        r'^(strong|be in front|go to and fro|stretch out|reach after|swear)',
        r'^(the one whom|trepide confugere)',
        r'^(fear & object|revered one)',
        r'^(leader, lord|be in front)',
    ]
    
    def looks_etymological(def_text: str) -> bool:
        """Check if definition looks etymological"""
        def_lower = def_text.lower().strip()
        for pattern in etymological_patterns:
            if re.match(pattern, def_lower):
                return True
        return False
    
    files_with_etymological = []
    
    for filepath in list(LEXICON_DRAFT.glob("H*.json")) + list(LEXICON_ROOTS.glob("H*.json")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hebrew_word = data.get('lemma', '')
            definitions = data.get('definitions', [])
            
            if not hebrew_word or not definitions:
                continue
            
            # Count etymological-looking definitions
            etymological_count = 0
            etymological_defs = []
            
            for defn in definitions:
                if defn.get('source') == 'bdb':
                    def_text = defn.get('text', '')
                    sense = defn.get('sense', '')
                    
                    if looks_etymological(def_text) and sense == "0":
                        etymological_count += 1
                        etymological_defs.append(def_text)
            
            # Also check: many sense "0" but BDB has no main definitions
            sense_0_count = sum(1 for d in definitions if d.get('source') == 'bdb' and d.get('sense') == '0')
            
            if etymological_count >= 3:
                files_with_etymological.append({
                    'file': filepath.name,
                    'strong_number': data.get('strong_number', filepath.stem),
                    'reason': f"{etymological_count} etymological-looking definitions",
                    'examples': etymological_defs[:3]
                })
            elif sense_0_count >= 5 and bdb_root:
                # Check if BDB entry has main definitions
                # Import here to avoid circular dependency
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from lexicon_builder import find_bdb_entry
                bdb_entry = find_bdb_entry(hebrew_word, bdb_root)
                if bdb_entry:
                    main_defs = bdb_entry.findall('./bdb:def', NS)
                    if len(main_defs) == 0:
                        files_with_etymological.append({
                            'file': filepath.name,
                            'strong_number': data.get('strong_number', filepath.stem),
                            'reason': f"{sense_0_count} sense '0' definitions but BDB has no main defs",
                            'examples': []
                        })
        except Exception:
            pass
    
    return {
        'count': len(files_with_etymological),
        'samples': files_with_etymological[:10]
    }


def check_missing_fields() -> Dict:
    """Check for files missing required fields"""
    missing_occurrences = []
    missing_sources = []
    
    for filepath in list(LEXICON_DRAFT.glob("H*.json")) + list(LEXICON_ROOTS.glob("H*.json")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'occurrences' not in data:
                missing_occurrences.append(filepath.name)
            if 'sources' not in data:
                missing_sources.append(filepath.name)
        except Exception:
            pass
    
    return {
        'missing_occurrences': len(missing_occurrences),
        'missing_sources': len(missing_sources),
        'samples_occ': missing_occurrences[:10],
        'samples_src': missing_sources[:10]
    }


def check_missing_definitions() -> Dict:
    """Check for files without definitions"""
    files_without_defs = []
    files_with_empty_defs = []
    
    for filepath in list(LEXICON_DRAFT.glob("H*.json")) + list(LEXICON_ROOTS.glob("H*.json")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            definitions = data.get('definitions', [])
            if 'definitions' not in data:
                files_without_defs.append({
                    'file': filepath.name,
                    'strong_number': data.get('strong_number', filepath.stem),
                    'lemma': data.get('lemma', 'N/A')
                })
            elif not definitions or len(definitions) == 0:
                files_with_empty_defs.append({
                    'file': filepath.name,
                    'strong_number': data.get('strong_number', filepath.stem),
                    'lemma': data.get('lemma', 'N/A')
                })
        except Exception:
            pass
    
    return {
        'missing_field': len(files_without_defs),
        'empty_definitions': len(files_with_empty_defs),
        'total': len(files_without_defs) + len(files_with_empty_defs),
        'samples': (files_without_defs + files_with_empty_defs)[:20]
    }


def main():
    """Main QA function"""
    import sys
    
    # Check for quick mode
    quick_mode = '--quick' in sys.argv or '-q' in sys.argv
    
    print("=" * 80)
    print("LEXICON QA - COMPLETE VALIDATION")
    print("=" * 80)
    
    # Load reference data
    print("\n📚 Loading reference data...")
    strongs_data = load_strongs_data()
    strong_refs = load_strong_refs()
    bdb_root = load_bdb_xml()
    print(f"   ✅ Strong's entries: {len(strongs_data)}")
    print(f"   ✅ Strong's references: {len(strong_refs)}")
    print(f"   ✅ BDB XML: {'Loaded' if bdb_root else 'Not found'}")
    
    # Get all files
    print("\n📁 Scanning files...")
    draft_files = sorted(list(LEXICON_DRAFT.glob("H*.json")))
    root_files = sorted(list(LEXICON_ROOTS.glob("H*.json")))
    print(f"   Draft files: {len(draft_files)}")
    print(f"   Root files: {len(root_files)}")
    print(f"   Total: {len(draft_files) + len(root_files)}")
    
    # Quick checks
    print("\n🔍 Quick checks...")
    empty_senses = check_empty_senses(bdb_root)
    missing_fields = check_missing_fields()
    incomplete_senses = check_incomplete_sense_hierarchy()
    etymological_defs = check_etymological_definitions(bdb_root)
    missing_defs = check_missing_definitions()
    
    print(f"   Files with empty sense strings: {empty_senses['count']}")
    print(f"   Files with incomplete sense hierarchy: {incomplete_senses['count']}")
    print(f"   Files with etymological definitions: {etymological_defs['count']}")
    print(f"   Files missing occurrences: {missing_fields['missing_occurrences']}")
    print(f"   Files missing sources: {missing_fields['missing_sources']}")
    print(f"   Files without definitions: {missing_defs['total']}")
    
    # Show samples of issues
    if incomplete_senses['count'] > 0:
        print("\n⚠️  Sample incomplete sense hierarchy:")
        for sample in incomplete_senses['samples'][:5]:
            print(f"      {sample['file']}: sense='{sample['sense']}' ({sample['definition']})")
    
    if etymological_defs['count'] > 0:
        print("\n⚠️  Sample etymological definitions:")
        for sample in etymological_defs['samples'][:5]:
            examples = ", ".join(sample['examples'][:2]) if sample['examples'] else "N/A"
            print(f"      {sample['file']}: {sample['reason']} ({examples})")
    
    if missing_defs['total'] > 0:
        print("\n⚠️  Sample files without definitions:")
        for sample in missing_defs['samples'][:10]:
            print(f"      {sample['file']} ({sample['strong_number']}): {sample['lemma']}")
        print(f"\n   💡 Tip: Run 'python3 lexicon_builder.py --fill-missing' to fill missing definitions")
    
    if quick_mode:
        print("\n⚠️  Quick mode: Skipping full validation")
        return
    
    # Validate file structure
    print("\n🔍 Validating file structure...")
    draft_results = []
    root_results = []
    
    for i, filepath in enumerate(draft_files, 1):
        if i % 500 == 0:
            print(f"   Draft progress: {i}/{len(draft_files)}")
        result = validate_file_structure(filepath, is_root=False)
        draft_results.append(result)
    
    for i, filepath in enumerate(root_files, 1):
        if i % 500 == 0:
            print(f"   Roots progress: {i}/{len(root_files)}")
        result = validate_file_structure(filepath, is_root=True)
        root_results.append(result)
    
    # Analyze results
    draft_errors = [r for r in draft_results if r['status'] == 'error']
    draft_warnings = [r for r in draft_results if r['status'] == 'warning']
    draft_ok = [r for r in draft_results if r['status'] == 'ok']
    
    root_errors = [r for r in root_results if r['status'] == 'error']
    root_warnings = [r for r in root_results if r['status'] == 'warning']
    root_ok = [r for r in root_results if r['status'] == 'ok']
    
    # Cross-reference validation
    print("\n🔗 Validating cross-references...")
    cross_ref_issues = validate_cross_references(draft_files, root_files)
    
    # Strong's coverage
    print("\n📊 Validating Strong's coverage...")
    all_lexicon_files = {f.stem for f in draft_files} | {f.stem for f in root_files}
    coverage = validate_strongs_coverage(all_lexicon_files, strongs_data)
    
    # Occurrences validation
    print("\n📖 Validating occurrences...")
    occ_validation = validate_occurrences_coverage(draft_files + root_files, strong_refs)
    
    # Summary
    print("\n" + "=" * 80)
    print("QA SUMMARY")
    print("=" * 80)
    
    print("\n📁 DRAFT DIRECTORY:")
    print(f"   ✅ OK: {len(draft_ok)} ({len(draft_ok)/len(draft_files)*100:.1f}%)")
    print(f"   ⚠️  Warnings: {len(draft_warnings)} ({len(draft_warnings)/len(draft_files)*100:.1f}%)")
    print(f"   ❌ Errors: {len(draft_errors)} ({len(draft_errors)/len(draft_files)*100:.1f}%)")
    
    print("\n📁 ROOTS DIRECTORY:")
    print(f"   ✅ OK: {len(root_ok)} ({len(root_ok)/len(root_files)*100:.1f}%)")
    print(f"   ⚠️  Warnings: {len(root_warnings)} ({len(root_warnings)/len(root_files)*100:.1f}%)")
    print(f"   ❌ Errors: {len(root_errors)} ({len(root_errors)/len(root_files)*100:.1f}%)")
    
    print("\n🔗 CROSS-REFERENCES:")
    print(f"   Root references used: {cross_ref_issues['root_refs_used']}")
    print(f"   Missing root files: {len(cross_ref_issues['root_refs_missing'])}")
    print(f"   Orphaned roots: {cross_ref_issues['orphaned_roots']}")
    
    print("\n📊 STRONG'S COVERAGE:")
    print(f"   Strong's entries: {coverage['strongs_count']}")
    print(f"   Lexicon files: {coverage['lexicon_count']}")
    print(f"   Coverage: {coverage['coverage']:.1f}%")
    print(f"   Missing: {coverage['missing_count']}")
    print(f"   Extra: {coverage['extra_count']}")
    
    print("\n📖 OCCURRENCES VALIDATION:")
    print(f"   Files checked: {occ_validation['checked']}")
    print(f"   Mismatches: {occ_validation['mismatches']}")
    
    print("\n🔍 SENSE HIERARCHY VALIDATION:")
    print(f"   Files with incomplete sense hierarchy: {incomplete_senses['count']}")
    print(f"   Files with etymological definitions: {etymological_defs['count']}")
    
    print("\n📚 DEFINITIONS VALIDATION:")
    print(f"   Files without definitions: {missing_defs['total']}")
    if missing_defs['total'] > 0:
        print(f"      Missing field: {missing_defs['missing_field']}")
        print(f"      Empty definitions: {missing_defs['empty_definitions']}")
    
    # Show sample errors
    if draft_errors or root_errors:
        print("\n❌ SAMPLE ERRORS:")
        print("-" * 80)
        for result in (draft_errors + root_errors)[:10]:
            print(f"   {result['file']}:")
            for error in result['errors'][:3]:
                print(f"      - {error}")
    
    # Show sample warnings
    if draft_warnings or root_warnings:
        print("\n⚠️  SAMPLE WARNINGS:")
        print("-" * 80)
        warning_types = defaultdict(int)
        for result in draft_warnings + root_warnings:
            for warning in result['warnings']:
                warning_types[warning] += 1
        
        for warning, count in sorted(warning_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {warning}: {count} occurrences")
    
    print("\n" + "=" * 80)
    print("QA COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

