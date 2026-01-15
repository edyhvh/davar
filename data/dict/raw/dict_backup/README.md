# Hebrew Scripture Data Repository

This directory contains all processed Hebrew Scripture data for the Davar study app. It implements a hybrid architecture separating lexical definitions from verse-level data for optimal performance and maintainability.

## 📁 Directory Structure

```
data/dict/
├── README.md                    # This documentation
├── HYBRID_SYSTEM_EXPLANATION.md # Technical system explanation
├── README_VERSES.md            # Legacy verse documentation
│
├── lexicon/                     # 🧠 LEXICON DATA - Word definitions & roots
│   ├── README.md               # Lexicon documentation
│   ├── words/                  # Derived words (6312+ entries)
│   │   ├── H1.json            # אָב (father)
│   │   ├── H7965.json         # שָׁלוֹם (peace)
│   │   └── ...
│   ├── roots/                  # Primitive roots (3131+ entries)
│   │   ├── H1.json            # אָב (root)
│   │   ├── H103.json          # אָגַר (root)
│   │   └── ...
│   └── testing/                # Development samples (1% of data)
│       ├── words/              # Test derived words
│       └── roots/              # Test primitive roots
│
├── verses/                      # 📖 VERSE DATA - Lightweight verse files
│   ├── genesis/                # Genesis verses (1533 files)
│   │   ├── genesis.1.1.json   # Lightweight verse format
│   │   ├── genesis.1.2.json
│   │   └── ...
│   ├── exodus/                 # Exodus verses
│   ├── leviticus/              # Leviticus verses
│   └── ...                     # All Tanakh books
│
└── raw/                        # 📚 RAW SOURCE DATA - Read-only
    ├── morphus/                # BDB morphological analysis (39 XML files)
    │   ├── Gen.xml            # Genesis morphology
    │   ├── Exod.xml           # Exodus morphology
    │   └── ...
    ├── bdb_full.json           # Complete BDB dictionary
    ├── bdb_dict_en.json        # BDB English definitions
    ├── BrownDriverBriggs.xml   # Original BDB XML source
    ├── HebrewStrong.xml        # Strong's Hebrew dictionary
    ├── strongs_hebrew_dict_en.json # Strong's English definitions
    └── strong_refs.json        # Strong's reference mapping
```

## 🎯 System Architecture

### Hybrid Design Philosophy

**Challenge**: Storing complete definitions in every verse creates massive data duplication and performance issues.

**Solution**: Two-tier architecture:
1. **📚 Lexicon Layer** (`lexicon/`) - Complete word definitions stored once per lemma
2. **📖 Verse Layer** (`verses/`) - Lightweight references to lexicon entries

### Key Benefits
- 🚀 **Performance**: Fast verse loading with lazy lexicon resolution
- 💾 **Efficiency**: No definition duplication across ~31,000 verses
- 🔧 **Maintainability**: Update definitions in one central location
- 🔄 **Flexibility**: Multiple definition sources (ISR, BDB, Strong's)
- 📱 **Scalability**: Optimal for mobile app data requirements

## 📚 Data Sources

### Primary Data Sources

| Source | Description | Location | Status |
|--------|-------------|----------|---------|
| **ISR Scriptures** | Hebrew Tanakh text | `../oe/` | ✅ Processed |
| **Open Scriptures MorphHB** | Morphological analysis (39 books) | `raw/morphus/` | ✅ Integrated |
| **Brown-Driver-Briggs** | Comprehensive Hebrew lexicon | `raw/BrownDriverBriggs.xml` | ✅ Processed |
| **Strong's Dictionary** | Standard Hebrew word numbering | `raw/HebrewStrong.xml` | ✅ Referenced |

### Supporting Sources

| Source | Description | Purpose |
|--------|-------------|---------|
| **TTH Translation** | Spanish translation | Multi-language support |
| **TS2009 Translation** | Hebrew transliteration | Book name standardization |
| **Custom Dictionary** | Curated 72-word definitions | Enhanced definitions |

### Data Processing Pipeline

```
📥 Raw Sources ──→ 🔄 Processing Scripts ──→ 📤 Processed Data
├── ISR text         ├── build_lexicon.py      ├── lexicon/words+roots/
├── BDB XML          ├── build_verses.py       └── verses/*/
├── Morphus XML      └── qa.py validation
└── Strong's refs
```

### Processing Workflow

```
🎯 INPUT SOURCES                    🔄 PROCESSING SCRIPTS                📤 OUTPUT DATA
├── ISR Hebrew Text (oe/)         ├── scripts/dict/build_lexicon.py    ├── lexicon/words/
├── BDB XML (raw/)                ├── scripts/dict/build_verses.py     ├── lexicon/roots/
├── Morphological Data (morphus/) └── scripts/dict/qa.py              └── verses/*/
├── Strong's References (raw/)       validation & QA
└── Custom Definitions (tth/)

📊 RESULT: ~9,400 lexicon entries + ~31,000 verse files
```

## 🚀 Processing Scripts

**📍 Location**: All processing scripts are located in `scripts/dict/`

### 1. Verse Builder (`scripts/dict/build_verses.py`)

**Purpose**: Generates lightweight verse JSON files for all Hebrew Scripture books.

```bash
# Process ALL books (complete Tanakh)
python scripts/dict/build_verses.py

# Process specific book
python scripts/dict/build_verses.py --book genesis

# Process specific chapter
python scripts/dict/build_verses.py --book exodus --chapter 1

# Verbose output
python scripts/dict/build_verses.py --verbose
```

**Core Features:**
- 📖 Processes all 39 Tanakh books automatically
- 🔍 Integrates BDB morphological analysis from `raw/morphus/`
- 🔢 Extracts and validates Strong's numbers
- 🎯 Validates senses against lexicon definitions
- 💾 Outputs optimized JSON format (~31,000 files)

### 2. Lexicon Builder (`scripts/dict/build_lexicon.py`)

**Purpose**: Builds complete Hebrew lexicon with definitions, senses, and references.

```bash
# Build ALL lexicon entries (production)
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json

# Update existing entries
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json --update

# Testing mode (1% sample)
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json --testing

### 3. Quality Assurance (`scripts/dict/qa.py`)

**Purpose**: Validates lexicon data quality, structure, and integrity.

```bash
# Full validation
python scripts/dict/qa.py

# Quick validation
python scripts/dict/qa.py --quick
```

**Validation Checks:**
- 📁 File structure and naming conventions
- 🔗 Cross-references between words and roots
- 📊 Strong's coverage completeness
- 📖 Occurrence validation and accuracy
- 🎯 Sense hierarchy validation
- 🎭 Definition completeness checking

# Quick validation
python3 lexicon/qa.py --quick
```

## 📄 Data Formats

### Lightweight Verse Format

```json
{
  "reference": "genesis.1.1",
  "book_id": "genesis",
  "chapter": 1,
  "verse": 1,
  "hebrew_text": "בְּ רֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַ שָּׁמַ֖יִם וְ אֵ֥ת הָ אָֽרֶץ",
  "words": [
    {
      "position": 1,
      "hebrew": "בְּרֵאשִׁ֖ית",
      "strong_number": "H7225",
      "sense": "1"
    },
    {
      "position": 2,
      "hebrew": "בָּרָ֣א",
      "strong_number": "H1254",
      "sense": null
    }
  ]
}
```

### Lexicon Entry Format

```json
{
  "strong_number": "H7965",
  "lemma": "שָׁלוֹם",
  "normalized": "שלום",
  "pronunciation": "shaw-lome'",
  "definitions": [
    {
      "sense": "1",
      "primary": "completeness, soundness, welfare, peace",
      "variants": ["peace", "wellness", "completeness"],
      "bdb_definition": "safety, well-being, health, prosperity...",
      "occurrences": 237
    }
  ],
  "sources": {
    "bdb": true,
    "strong": true,
    "custom": true
  },
  "root": "H7999"
}
```

## 🔄 Data Generation Workflow

### Initial Setup

1. **Verify raw data sources** are in `raw/` directory
2. **Ensure Hebrew text** is available in `../oe/` directory
3. **Check lexicon dependencies** in `lexicon/` directory

### Generate Verses

```bash
# Generate all lightweight verses
python scripts/dict/build_verses.py

# Verify output in verses/ directory
ls verses/genesis/ | head -5
```

### Generate Lexicon (if needed)

```bash
# Build complete lexicon (production)
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json

# Validate quality
python scripts/dict/qa.py
```

## 📊 Statistics

| Component | Count | Notes |
|-----------|-------|-------|
| **Verses** | ~31,000 | All Tanakh verses |
| **Unique Words** | ~8,600 | Strong's numbered lemmas |
| **Lexicon Entries** | ~9,400 | Including roots and derivatives |
| **Morphus Files** | 39 | One per book |
| **Raw XML Files** | 3 | BDB, Strong's, LexicalIndex |

## ⚠️ Important Notes

### Licensing Restrictions
- **ISR Text**: Attribution required, one verse per screen
- **TTH Translation**: Permission from Natanael Doldan requires manual processing
- **Raw Data**: Never modify files in `raw/` directory

### File Organization
- **`raw/`**: Source data - read-only, never modify
- **`lexicon/`**: Processed definitions - generated from raw data
- **`verses/`**: Lightweight references - generated from oe/ + morphus/

### Dependencies
- Python 3.8+
- XML parsing libraries (built-in)
- JSON processing (built-in)
- Path manipulation (pathlib)

## 🔧 Troubleshooting

### Common Issues

**"Morphus directory not found"**
- Ensure `raw/morphus/` contains XML files
- Check file permissions

**"Book not found in mapping"**
- Verify book name spelling
- Check available books in `BookMapper.BOOK_MAPPING`

**"Lexicon validation failed"**
- Run `python scripts/dict/qa.py` for detailed diagnostics
- Check `lexicon/testing/` for sample data

### Data Validation

```bash
# Quick validation
python scripts/dict/qa.py --quick

# Full validation
python scripts/dict/qa.py

# Test verse generation
python scripts/dict/build_verses.py --book genesis --chapter 1 --verbose
```

## 📝 Development Guidelines

### Data Management
- **🔒 Raw sources** (`raw/`) - Never modify, read-only reference data
- **📤 Generated data** (`verses/`, `lexicon/words+roots/`) - Can be committed to version control
- **🧪 Testing data** (`lexicon/testing/`) - Development only, exclude from commits
- **🔧 Scripts** (`scripts/dict/`) - Processing tools and utilities

### Production Workflow
```bash
# 1. Build lexicon
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json

# 2. Generate verses
python scripts/dict/build_verses.py

# 3. Quality assurance
python scripts/dict/qa.py
```

### Development Workflow
```bash
# Test with small sample
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json --testing

# Validate and iterate
python scripts/dict/qa.py --quick
```

---

*Last updated: December 2025*

*Hebrew Scripture Data Repository - Core data for the Davar study app. Balancing technical excellence with spiritual sensitivity for deep engagement with sacred texts.*
