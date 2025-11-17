# Lexicon Builder - Documentation

## 📁 Project Structure

```
lexicon/
├── lexicon_builder.py          # Main script to build/regenerate lexicon entries
├── qa.py                        # QA/validation script for lexicon quality
├── lexicon_100_percent_list.json # Complete list of Strong's numbers
│
├── draft/                       # Lexicon entries (derived words)
│   ├── H1.json
│   ├── H2.json
│   └── ...
│
├── roots/                       # Primitive roots (root words)
│   ├── H1.json
│   ├── H103.json
│   └── ...
│
└── testing/                     # Testing mode (1% of data)
    ├── draft/
    └── roots/
```

---

## 🚀 Lexicon Builder Usage

### Main Script: `lexicon_builder.py`

Consolidated script that builds complete lexicon entries with:
- BDB definitions with `sense` assignment
- Occurrences from Strong's references
- Automatic root identification
- Root extraction and their definitions

### Usage Modes

#### 1. Single Entry
```bash
# Build a specific entry
python3 lexicon_builder.py H7965

# Update an existing entry
python3 lexicon_builder.py H7965 --update
```

#### 2. Batch Processing
```bash
# Process all entries from JSON file
python3 lexicon_builder.py lexicon_100_percent_list.json

# Update all existing entries
python3 lexicon_builder.py lexicon_100_percent_list.json --update

```

#### 3. Testing Mode (1% of data)
```bash
# Generate only 1% of data in testing/ folder (doesn't modify existing data)
python3 lexicon_builder.py lexicon_100_percent_list.json --testing

# Testing with update
python3 lexicon_builder.py lexicon_100_percent_list.json --testing --update
```

**Testing mode features:**
- ✅ Automatically limits to 1% of data
- ✅ Saves to `testing/draft/` and `testing/roots/`
- ✅ Doesn't modify existing data in `draft/` and `roots/`
- ✅ Useful for testing changes before processing the entire lexicon

#### 4. Fill Missing Definitions Mode
```bash
# Fill missing definitions for all files without definitions
python3 lexicon_builder.py --fill-missing

# Only process draft/ directory
python3 lexicon_builder.py --fill-missing --draft-only

# Only process testing/ directory
python3 lexicon_builder.py --fill-missing --testing-only
```

**Fill missing mode features:**
- ✅ Searches BDB by Hebrew lemma (not just Strong's number)
- ✅ Includes root-type entries when needed (e.g., H776 אֶרֶץ)
- ✅ Automatically finds and fills definitions for files without them
- ✅ Updates `sources.bdb` flag when definitions are found
- ✅ Processes `draft/` and `testing/` directories by default

---

## 🔍 QA and Validation

### Main Script: `qa.py`

Consolidated script that combines all validations:
- File structure
- Required fields
- `sense` validation for BDB definitions
- **Incomplete sense hierarchy detection** (e.g., "a" instead of "1a")
- **Etymological definitions detection** (incorrect root entries)
- Cross-references between draft and roots
- Strong's coverage
- Occurrences validation

### Usage

```bash
# Quick QA (basic checks)
python3 qa.py --quick

# Complete QA (exhaustive validation)
python3 qa.py
```

### What It Validates

1. **File Structure:**
   - Required fields present
   - Valid JSON format
   - Filename matches `strong_number`
   - `is_root` matches directory

2. **Definitions:**
   - All BDB definitions have `sense` field
   - `sense: "0"` for main definitions
   - `sense: "1"`, `"2"`, etc. for specific senses
   - **Hierarchical senses** (e.g., "1a", "2b") are complete (not just "a", "b")
   - **Missing definitions detection** - Identifies files without definitions

3. **Sense Hierarchy:**
   - Detects incomplete sense paths (single letters without parent)
   - Validates that nested senses have proper parent paths

4. **Etymological Definitions:**
   - Detects entries using etymological root entries instead of actual word entries
   - Identifies patterns like "strong", "be in front of", "go to and fro"
   - Flags entries with many sense "0" definitions when BDB has no main definitions

5. **Occurrences:**
   - `total` field matches `len(references)`
   - Valid reference format

6. **Cross-References:**
   - `root_ref` points to existing files in `roots/`
   - No orphaned roots

7. **Coverage:**
   - All Strong's numbers are covered
   - No extra files

8. **Missing Definitions:**
   - Detects files without definitions field
   - Detects files with empty definitions array
   - Provides tip to use `--fill-missing` mode

---

## 📋 File Format

### Entry Structure

```json
{
  "strong_number": "H7965",
  "lemma": "שָׁלוֹם",
  "normalized": "שלום",
  "pronunciation": "shaw-lome'",
  "transliteration": "shâlôwm",
  
  "definitions": [
    {
      "text": "completeness",
      "source": "bdb",
      "order": 1,
      "sense": "1"
    },
    {
      "text": "peace",
      "source": "bdb",
      "order": 2,
      "sense": "0"
    },
    {
      "text": "welfare",
      "source": "bdb",
      "order": 3,
      "sense": "0"
    }
  ],
  
  "occurrences": {
    "total": 209,
    "references": [
      "gen.15.15",
      "gen.26.29",
      "gen.28.21"
    ]
  },
  
  "sources": {
    "strongs": false,
    "bdb": true
  },
  
  "is_root": false,
  "root_ref": "H7999"
}
```

### Important Fields

- **`sense`**: Required field for all BDB definitions
  - `"0"` = Main definition (not in a specific sense)
  - `"1"`, `"2"`, etc. = Specific sense numbers from BDB
  - `"1a"`, `"2b"`, etc. = Hierarchical senses (nested senses)
  - **IMPORTANT**: Hierarchical senses must include parent (e.g., "1a" not just "a")

- **`is_root`**: 
  - `true` = Word is a primitive root (goes in `roots/`)
  - `false` = Derived word (goes in `draft/`)

- **`root_ref`**: 
  - Only present in derived words (`is_root: false`)
  - Points to the Strong's number of the root in `roots/`

---

## 🔄 Workflow

### 1. Initial Generation

```bash
# Generate entire lexicon (may take a long time)
python3 lexicon_builder.py lexicon_100_percent_list.json
```

### 2. Testing Changes

```bash
# Test changes with 1% of data
python3 lexicon_builder.py lexicon_100_percent_list.json --testing

# Review results
python3 qa.py --quick

# If everything looks good, apply to entire lexicon
python3 lexicon_builder.py lexicon_100_percent_list.json --update
```

### 3. Continuous Validation

```bash
# Quick QA after changes
python3 qa.py --quick

# Complete QA periodically
python3 qa.py
```

### 4. Updating Existing Entries

```bash
# Update all entries with new logic
python3 lexicon_builder.py lexicon_100_percent_list.json --update
```

### 5. Filling Missing Definitions

```bash
# Fill definitions for files that don't have any
python3 lexicon_builder.py --fill-missing

# Check which files are missing definitions
python3 qa.py --quick

# Fill only draft/ directory
python3 lexicon_builder.py --fill-missing --draft-only
```

**When to use:**
- After initial generation, some files may not have definitions (e.g., H776)
- When BDB entries don't have `strongs` attribute but exist by lemma
- To complete definitions for root-type entries

---

## 📊 Current Statistics

- **Total Strong's entries**: 8,674
- **Files in draft/**: 6,312
- **Files in roots/**: 3,131
- **Total files**: 9,443
- **Coverage**: 100% of Strong's numbers

---

## 🛠️ Technical Features

### Lexicon Builder

- ✅ **Complete BDB definition extraction** - Extracts ALL definitions from ALL senses
- ✅ **Hierarchical sense paths** - Correctly builds "1a", "2b" instead of incomplete "a", "b"
- ✅ **Etymological entry avoidance** - Skips `type="root"` entries, prioritizes actual word entries
- ✅ **Duplicate definitions across senses** - Allows same definition in different senses (e.g., "sky" in sense "0" and "1a")
- ✅ **Text extraction from sense elements** - Extracts definitions even when no explicit `<def>` tags
- ✅ **BDB search by lemma** - Searches BDB by Hebrew lemma, not just Strong's number
- ✅ **Root entry support** - Includes root-type entries when needed (e.g., H776 אֶרֶץ)
- ✅ **Fill missing definitions mode** - Automatically finds and fills definitions for files without them
- ✅ Automatic `sense` assignment from BDB XML
- ✅ Automatic root identification
- ✅ Root extraction and their definitions
- ✅ Reference normalization (lowercase, sorted)
- ✅ Batch mode with progress
- ✅ Safe testing mode
- ✅ Fallback to direct XML search when extraction module unavailable

### QA Script

- ✅ Complete structure validation
- ✅ `sense` verification in BDB definitions
- ✅ **Incomplete sense hierarchy detection** - Finds entries with "a" instead of "1a"
- ✅ **Etymological definitions detection** - Identifies entries using wrong BDB entries
- ✅ **Missing definitions detection** - Finds files without definitions
- ✅ Cross-reference validation
- ✅ Strong's coverage
- ✅ Occurrences validation
- ✅ Quick mode for basic checks

---

## ⚠️ Important Notes

1. **Testing Mode**: Always use `--testing` to test changes before processing the entire lexicon
2. **Backup**: Consider backing up before using `--update` in production
3. **BDB XML**: Requires access to `BrownDriverBriggs.xml` for `sense` assignment and BDB extraction
4. **Extract Module**: `extract_word_osb.py` in `../oe/` is optional - the script will use direct XML search if the module is not available
5. **Sources Field**: The `sources.bdb` field is automatically set to `true` when BDB definitions are found, and `false` when no definitions are available

---

## 🐛 Problems Discovered & Fixed

### 1. Incomplete Sense Hierarchy
**Problem**: Some entries had incomplete sense paths like `"a"` instead of `"1a"` (e.g., H8064.json)

**Root Cause**: The `build_sense_path` function wasn't properly combining parent and child sense numbers.

**Solution**: 
- Improved `build_sense_path` to correctly build hierarchical paths
- Enhanced `extract_senses_recursive` to track parent paths through nested senses
- Now correctly generates "1a", "2b" instead of just "a", "b"

### 2. Missing Definitions
**Problem**: Not all definitions were being extracted from BDB XML, especially from nested senses.

**Root Cause**: 
- Only extracting from explicit `<def>` tags
- Removing duplicate definitions even when they appeared in different senses
- Not extracting text directly from `<sense>` elements

**Solution**:
- Added `extract_text_from_element` to capture text from sense elements
- Changed duplicate detection to use `(sense, text)` as key, allowing same definition in different senses
- Recursively processes all nested senses to capture complete definition set
- **Philosophy**: "es que la idea de lexicon es que estuvieran todas las definiciones para todas las palabras"

### 3. Etymological Entry Errors
**Problem**: Some entries (e.g., H430, H423) were using etymological root entries instead of actual word entries, resulting in incorrect definitions like "strong", "be in front of", "go to and fro".

**Root Cause**: `find_bdb_entry` was selecting entries with `type="root"` that mentioned the word but didn't actually define it.

**Solution**:
- Skip entries with `type="root"` (etymological discussions)
- Prioritize entries where Hebrew word is a direct child (`./bdb:w` vs `.//bdb:w`)
- Give +1000 bonus score to main word entries
- Example: H430 now correctly uses `a.dl.ad` (actual word) instead of `a.dl.aa` (etymological)

### 4. Detection & Repair
**QA Integration**: 
- Detection of problems is integrated into `qa.py`
- Use `python3 qa.py` to identify problematic entries
- Use `python3 lexicon_builder.py H#### --update` to regenerate specific entries
- Use `python3 lexicon_builder.py lexicon_100_percent_list.json --update` to regenerate all entries

---

## 📝 Change History

### Latest Improvements (2024)
- ✅ **Fixed incomplete sense hierarchy**: Correctly builds hierarchical paths (e.g., "1a", "2b") instead of incomplete "a", "b"
- ✅ **Complete definition extraction**: Extracts ALL definitions from ALL senses, not just main definitions
- ✅ **Etymological entry avoidance**: Skips `type="root"` entries, prioritizes actual word entries
- ✅ **Duplicate definitions across senses**: Allows same definition in different senses (e.g., "sky" in sense "0" and "1a")
- ✅ **Text extraction from sense elements**: Extracts definitions even when no explicit `<def>` tags
- ✅ **BDB search by lemma**: Searches BDB by Hebrew lemma, including root-type entries when needed
- ✅ **Fill missing definitions mode**: Automatically finds and fills definitions for files without them
- ✅ **Automatic duplicate removal**: `save_lexicon_entry` removes files from opposite directory to prevent duplicates
- ✅ **Enhanced QA**: Detects sense hierarchy issues, etymological definitions, and missing definitions
- ✅ **Testing mode**: Safe testing with 1% of data in `testing/` directory

### Consolidated Refactoring
- ✅ Consolidated `lexicon_builder.py` with complete functionality
- ✅ Consolidated `qa.py` with all validations
- ✅ Fixed BDB extraction to work without extraction module (uses direct XML search)
- ✅ Fixed `sources.bdb` field to correctly reflect when definitions are found

---

## 🎯 Next Steps

- [ ] Integration with custom dictionary (72 words)
- [ ] Support for Spanish definitions
- [ ] Performance optimization for batch processing
- [ ] Integration with verse system for `bdb_sense` assignment
