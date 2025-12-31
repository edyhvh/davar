# TTH Processor v2.1.0

Simplified system for processing TTH (Textual Translation of Hebrew) biblical texts to JSON format for the Davar app.

## 🚀 Quick Start

### 1. Setup (First Time Only)
```bash
# Convert DOCX to Markdown for faster processing (optional but recommended)
cd ~/davar
python scripts/tth/cli.py convert ~/davar/data/tth/raw/tanaj.docx ~/davar/data/tth/raw/tanaj.md

# Create individual book Markdown files (optional, for even faster processing)
# The system will automatically extract books from the complete tanaj.md when needed
```

### 2. Run Commands
**Important**: Always run commands from the project root directory (`cd ~/davar`), not from `scripts/tth/`.

```bash
# 🧪 TEST a book (output goes to ~/davar/~/davar/data/tth/temp/)
python scripts/tth/main.py test amos

# 📚 PROCESS all books (output goes to ~/davar/data/tth/)
python scripts/tth/main.py all

# 📖 PROCESS specific books
python scripts/tth/main.py book amos iehudah
```

## ✨ v2.1.0 Improvements

- **Automatic text cleaning**: Fixes soft hyphens (`Is\-rael` → `Israel`), punctuation spacing, and stuck connectors
- **Enhanced footnote processing**: Properly handles multiple footnotes in verses without text truncation
- **Simplified JSON structure**: No redundant book info, lowercase keys
- **Optimized workflow**: `temp/` for testing, main directory for production
- **Clean code**: Removed temporary scripts and development files

## 📋 Main Commands

**Important**: All commands must be run from the project root directory.

### Option 1: Simple Interface (Recommended)
```bash
# 🧪 TEST a book (output: ~/davar/data/tth/temp/)
python scripts/tth/main.py test <book>          # Ex: python scripts/tth/main.py test amos

# 📚 PROCESS specific books (output: ~/davar/data/tth/)
python scripts/tth/main.py book <book1> [book2] # Ex: python scripts/tth/main.py book amos iehudah

# 🌍 PROCESS ALL books (output: ~/davar/data/tth/)
python scripts/tth/main.py all                  # Process all available books

# ✅ VALIDATE results
python scripts/tth/main.py validate [directory] # Validate processed JSON

# 📋 LIST available books
python scripts/tth/main.py books                # Show all supported books
```

### Option 2: Full CLI
```bash
# Same commands but with cli.py
python scripts/tth/cli.py test amos
python scripts/tth/cli.py book amos iehudah
python scripts/tth/cli.py all
python scripts/tth/cli.py validate
python scripts/tth/cli.py books
```

**Use `main.py` for everyday use - it's simpler and shows helpful hints when run without arguments.**

## 🎯 Recommended Workflow

1. **Development/Testing**: Use `test` to try changes → results in `temp/`
2. **Production**: Use `book` or `all` for final processing → results in `~/davar/data/tth/`
3. **Validation**: Always validate after processing with `validate`

### Examples

#### Process All Books
```bash
python cli.py full ~/davar/data/tth/raw/tanaj.docx output/
```

#### Process Specific Books
```bash
python cli.py full ~/davar/data/tth/raw/tanaj.docx output/ bereshit shemot vaigra
```

#### Individual Steps
```bash
# Convert DOCX to Markdown
python cli.py convert ~/davar/data/tth/raw/tanaj.docx temp/tanaj.md

# Extract a book
python cli.py extract amos ~/davar/data/tth/raw/tanaj.docx extracted/

# Process to JSON
python cli.py process amos extracted/amos.md draft/

# Validate results
python cli.py validate draft/
```

## Supported Books

### Torah (Pentateuch)
- `bereshit` - Genesis
- `shemot` - Exodus
- `vaikra` - Leviticus
- `bamidbar` - Numbers
- `devarim` - Deuteronomy

### Neviim (Prophets)
- `iehosua` - Joshua
- `shoftim` - Judges
- `shemuel_alef` - 1 Samuel
- `shemuel_bet` - 2 Samuel
- `melajim_alef` - 1 Kings
- `melajim_bet` - 2 Kings
- `ieshaiahu` - Isaiah
- `irmeiahu` - Jeremiah
- `iejezkel` - Ezekiel
- `hoshea` - Hosea
- `ioel` - Joel
- `amos` - Amos
- `ionah` - Jonah
- `micah` - Micah
- `najum` - Nahum
- `jabakuk` - Habakkuk
- `tzefaniah` - Zephaniah
- `jagai` - Haggai
- `zejariah` - Zechariah
- `malaji` - Malachi

### Ketuvim (Writings)
- `tehilim` - Psalms
- `mishlei` - Proverbs

## Input Format

### DOCX Documents
- Complete TTH documents containing multiple books
- Must include Hebrew text with proper Unicode characters
- Footnotes should be in Word's footnote format

### Markdown Format
The system expects Markdown with specific formatting:

```markdown
# __BOOK_NAME__ HebrewName*

## Chapter Markers
__1__

## Verses
**1** Verse text here[^1]

## Footnotes
[^1]: Footnote definition text
```

## 📄 Output Format

### Simplified JSON Structure
Each book generates a single JSON file with clean, simplified structure:

```json
{
  "book_info": {
    "tth_name": "Amós",
    "hebrew_name": "עמוס",
    "english_name": "Amos",
    "spanish_name": "Amós",
    "book_code": "amos",
    "expected_chapters": 9,
    "section": "neviim",
    "section_hebrew": "נביאים",
    "section_english": "Prophets",
    "section_spanish": "Profetas",
    "total_chapters": 9,
    "total_verses": 146,
    "processed_date": "2024-12-31T09:52:09.737355",
    "processor_version": "2.1.0"
  },
  "verses": [
    {
      "chapter": 1,
      "verse": 1,
      "status": "present",
      "tth": "Cleaned verse text with proper spacing and joined words...",
      "footnotes": [
        {
          "marker": "¹",
          "number": "1",
          "word": "associated_word",
          "explanation": "Footnote explanation text"
        }
      ],
      "hebrew_terms": [
        {
          "term": "YEHOVAH",
          "explanation": "Tetragrámaton - Nombre de Elohim"
        }
      ]
    }
  ]
}
```

**Key improvements:**
- Book metadata in separate `book_info` section with lowercase keys
- Verses contain only verse-specific data (no redundant book info)
- Automatic text cleaning applied to verse content

## 🔧 Text Cleaning Features

The processor includes advanced text cleaning that automatically fixes common conversion issues:

- **Soft hyphens**: `Is\-rael` → `Israel`
- **Punctuation spacing**: `dijo:יהוה` → `dijo: יהוה`
- **Stuck connectors**: `Ashdody al` → `Ashdod y al`
- **Double spaces**: Automatic cleanup

## 🐛 Troubleshooting

### Permission Denied Error
If you get permission errors, you're running commands from the wrong directory:

**❌ Wrong:**
```bash
cd scripts/tth
python main.py test amos  # DON'T DO THIS
```

**✅ Correct:**
```bash
cd ~/davar  # Go to project root first
python scripts/tth/main.py test amos
```

### Missing Markdown File
If processing is slow, create the Markdown file first:
```bash
python scripts/tth/cli.py convert ~/davar/data/tth/raw/tanaj.docx ~/davar/data/tth/raw/tanaj.md
```

**Note**: The complete `tanaj.md` file is now stored in `~/davar/data/tth/raw/` alongside other source files.

### Missing mammoth Library
For DOCX processing: `pip install mammoth`

### Verses appearing truncated
If verse text appears cut off (e.g., showing only "Con¹" instead of full text), this was a footnote processing bug in versions prior to v2.1.0. The issue has been fixed - verses with multiple footnotes now display complete text.

## ✅ Validation

```bash
python cli.py validate [output_dir]
```

Validates processed JSON for:
- Structural integrity
- Required fields presence
- Hebrew text verification
- Chapter/verse counts
- Footnote consistency

## 📚 Supported Books

**Torah**: bereshit, shemot, vaikra, bamidbar, devarim
**Prophets**: iehosua, shoftim, shemuel_alef/bet, melajim_alef/bet, ieshaiahu, irmeiahu, iejezkel, hosea, ioel, amos, ionah, micah, najum, jabakuk, tzefaniah, jagai, zejariah, malaji
**Writings**: tehilim, mishlei

## 🐛 Troubleshooting

**Missing mammoth**: `pip install mammoth`

**Text not recognized**: Ensure proper Unicode Hebrew in source

**Version**: 2.1.0 - Text cleaning + simplified JSON structure
