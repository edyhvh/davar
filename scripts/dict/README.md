# Hebrew Scripture Processing Scripts

This directory contains the main scripts for processing Hebrew Scripture data, including lexicon building and verse generation. These scripts provide a complete pipeline for transforming raw Hebrew text data into structured JSON files.

## 📁 Directory Structure

```
scripts/dict/
├── README.md                    # This documentation
├── lexicon_100_percent_list.json # Complete Strong's numbers list
├── qa.py                        # Lexicon quality assurance
├── build_lexicon.py             # Main lexicon builder script
├── build_verses.py              # Main verse builder script
├── config.py                    # Configuration and paths
├── book_mappings.py             # Book name mappings
├── strong_processor.py          # Strong's number processing
├── morphus_loader.py            # Morphological data loader
├── verse_processor.py           # Verse processing logic
├── lexicon_builder.py           # Legacy lexicon builder (backup)
└── verse_builder_backup.py      # Legacy verse builder (backup)
```

## 🚀 Main Scripts

### 1. `build_lexicon.py` - Lexicon Builder

**Purpose**: Builds complete Hebrew lexicon entries with definitions, senses, and references.

```bash
# Build complete lexicon (production)
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json

# Build complete lexicon (update existing)
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json --update

# Testing mode (1% sample for development)
python scripts/dict/build_lexicon.py lexicon_100_percent_list.json --testing

# Single entry
python scripts/dict/build_lexicon.py H7965

# Fill missing definitions
python scripts/dict/build_lexicon.py --fill-missing
```

**Features:**
- ✅ BDB (Brown-Driver-Briggs) definitions with sense assignment
- ✅ Strong's concordance references
- ✅ Automatic root identification and linking
- ✅ Morphological analysis integration
- ✅ Quality validation and cross-referencing

### 2. `build_verses.py` - Verse Builder

**Purpose**: Generates lightweight verse JSON files for all Hebrew Scripture books.

```bash
# Build all books
python scripts/dict/build_verses.py

# Build specific book
python scripts/dict/build_verses.py --book genesis

# Build specific chapter
python scripts/dict/build_verses.py --book exodus --chapter 1

# Verbose output
python scripts/dict/build_verses.py --verbose
```

**Features:**
- ✅ ISR Hebrew text processing
- ✅ Morphological analysis integration (BDB senses)
- ✅ Strong's number extraction and validation
- ✅ Multi-book support (Genesis through Malachi)
- ✅ Lightweight JSON format for optimal performance

## 🔧 Support Scripts

### `qa.py` - Quality Assurance

**Purpose**: Validates lexicon data quality and structure.

```bash
# Full validation
python scripts/dict/qa.py

# Quick validation
python scripts/dict/qa.py --quick
```

**Validates:**
- File structure and naming conventions
- JSON validity and required fields
- Cross-references between words and roots
- Strong's coverage and occurrences
- Sense hierarchy completeness
- Definition completeness

## 📊 Data Flow

```
Raw Data (data/dict/raw/)
    ├── ISR Hebrew text (oe/)
    ├── BDB XML (BrownDriverBriggs.xml)
    ├── Strong's dictionaries
    └── Morphological analysis (morphus/)

           ↓ build_lexicon.py

Lexicon Data (data/dict/lexicon/)
    ├── words/ - Derived words with definitions
    ├── roots/ - Primitive roots
    └── testing/ - Development samples

           ↓ build_verses.py

Verse Data (data/dict/verses/)
    ├── genesis/ - Lightweight verse files
    ├── exodus/ - ...
    └── ... (all books)
```

## ⚙️ Configuration

### `config.py`

Central configuration file containing:
- Project paths and directories
- File locations for raw data
- Output directory settings
- Lexicon processing parameters

### `book_mappings.py`

Contains mappings for:
- Book names across different sources (ISR, TS2009, TTH)
- Normalized book identifiers
- Morphological analysis file mappings
- Multilingual book names

## 🔧 Development Guidelines

### Adding New Features

1. **Modular Design**: Keep functionality in separate modules
2. **Configuration**: Use `config.py` for paths and settings
3. **Testing**: Use `--testing` mode for development
4. **Validation**: Run `qa.py` after changes

### Code Organization

- **`config.py`**: All paths and configuration
- **`book_mappings.py`**: Book-related mappings and metadata
- **`strong_processor.py`**: Strong's number processing logic
- **`morphus_loader.py`**: XML morphological data loading
- **`verse_processor.py`**: Verse generation logic
- **`build_*.py`**: Main entry points and orchestration

### Data Validation

Always run QA checks after making changes:

```bash
# Quick validation
python scripts/dict/qa.py --quick

# Full validation
python scripts/dict/qa.py
```

## 📈 Production Usage

### Complete Pipeline

```bash
# 1. Build complete lexicon
cd scripts/dict
python build_lexicon.py lexicon_100_percent_list.json

# 2. Build all verse files
python build_verses.py

# 3. Validate results
python qa.py
```

### Development Workflow

```bash
# 1. Test with small sample
python build_lexicon.py lexicon_100_percent_list.json --testing

# 2. Validate testing data
python qa.py

# 3. Run on full dataset when ready
python build_lexicon.py lexicon_100_percent_list.json
```

## 🛠️ Troubleshooting

### Common Issues

**Permission Errors**
- Run scripts with appropriate permissions
- Check file/directory access rights

**Missing Dependencies**
- Ensure all required data files exist in `data/dict/raw/`
- Check that `data/dict/lexicon/` directories exist

**Path Errors**
- Scripts expect to be run from `scripts/dict/` directory
- Use relative paths or update `config.py` if needed

**Memory Issues**
- Large datasets may require significant RAM
- Consider processing in batches for very large operations

## 📋 File Descriptions

| File | Purpose |
|------|---------|
| `build_lexicon.py` | Main lexicon generation script |
| `build_verses.py` | Main verse generation script |
| `qa.py` | Quality assurance and validation |
| `config.py` | Configuration and path management |
| `book_mappings.py` | Book name mappings and metadata |
| `strong_processor.py` | Strong's number processing |
| `morphus_loader.py` | Morphological XML data loading |
| `verse_processor.py` | Verse processing logic |
| `lexicon_100_percent_list.json` | Complete Strong's numbers list |
| `*backup.py` | Legacy versions (for reference) |

## 🔄 Version History

- **v1.0**: Initial modular refactor
- **Legacy**: `lexicon_builder.py` and `verse_builder.py` (preserved as backup)

---

*This modular architecture ensures maintainable, testable, and scalable Hebrew Scripture processing.*


