# TTH2 Processing System

Modern pipeline for converting TTH (Traducción Textual del Hebreo) DOCX files into simplified JSON format for the Davar app.

## ✨ Key Improvements

- ✅ **Single file per book** - One JSON instead of 9-50 chapter files
- ✅ **67% smaller files** - No redundant metadata per verse
- ✅ **Super fast** - Optimized processing (~0.1-0.4s per book)
- ✅ **Clean logging** - Progress bars, minimal output
- ✅ **Automated workflow** - One command does everything

## 🚀 Quick Start

```bash
cd ~/davar

# Install dependencies (first time only)
pip install mammoth tqdm

# Process all books
python scripts/tth_2/main.py all
```

Output will be in `data/tth_2/json/`

## 📖 Commands

### Process Everything (Recommended)
```bash
python scripts/tth_2/main.py all
```
Converts all DOCX → Markdown → JSON in one go.

### Step by Step
```bash
# Step 1: Split DOCX into per-book markdown
python scripts/tth_2/main.py split

# Step 2: Convert specific book to JSON
python scripts/tth_2/main.py convert bereshit

# Or convert all markdown to JSON
python scripts/tth_2/main.py convert all

# Step 3: Post-process JSON (fix formatting, convert italics to <em>)
python scripts/tth_2/main.py postprocess all

# Or post-process specific book
python scripts/tth_2/main.py postprocess lukas

# Post-process with options
python scripts/tth_2/main.py postprocess all --dry-run  # Preview changes
python scripts/tth_2/main.py postprocess all --backup   # Create .bak backups
```

### List Available Books
```bash
python scripts/tth_2/main.py books
```

### Help
```bash
python scripts/tth_2/main.py --help
```

## 📁 Directory Structure

```
data/tth_2/
├── raw/           # Source DOCX files (4 files)
├── markdown/      # Per-book markdown (38 files)
└── json/          # Final JSON output (38 files)

scripts/tth_2/
├── __init__.py         # Package initialization
├── config.py           # Book definitions & Hebrew terms
├── docx_to_md.py       # DOCX → Markdown converter
├── book_splitter.py    # Split complete markdown into books
├── md_to_json.py       # Markdown → JSON (optimized)
├── json_postprocess.py # Post-process JSON (fix italics → <em>)
├── text_cleaner.py     # Text cleaning utilities
└── main.py             # CLI interface
```

## 📊 Output Structure

Each book is **one JSON file** with clean structure:

```json
{
  "book_info": {
    "book_id": "amos",
    "tth_name": "Amós",
    "hebrew_name": "עמוס",
    "section": "neviim",
    "total_chapters": 10,
    "total_verses": 166
  },
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        {
          "verse": 1,
          "tth": "Palabras de Amós...",
          "footnotes": [
            {"marker": "¹", "word": "Con", "explanation": "O, Por medio de."}
          ],
          "hebrew_terms": []
        }
      ]
    }
  ]
}
```

### Structure Features
- **Book metadata once** - At top level, not repeated per verse
- **Hierarchical** - Clear book → chapters → verses structure
- **Clean verses** - Only essential fields: `verse`, `tth`, `footnotes`, `hebrew_terms`
- **Superscript markers** - Footnotes use ¹²³ instead of [^1]
- **Hebrew terms** - Currently empty array for performance (can be enabled later)

## 📚 Supported Books

### 38 Books Extracted
- **Torah (5):** bereshit, shemot, vaikra, bamidbar, devarim
- **Neviim (18):** iehoshua, shoftim, shemuel (1-2), melajim (1-2), ieshaiahu, irmeiahu, iejezkel, and 12 minor prophets
- **Ketuvim (2):** tehilim, mishlei
- **Besorah (11):** matityahu, markos, lukas, iojanan, maasei_hashlijim, romaim, iaacob, iehudah, sodot, tesaloniquim (1-2)

View full list: `python scripts/tth_2/main.py books`

## ⚡ Performance

**Before (TTH v1):**
- Multiple files per book (9-50 chapter files)
- Slow processing (~2-5s per book)
- Large files with redundant metadata

**After (TTH2 - Optimized):**
- One file per book
- Fast processing with footnotes only
- 67% smaller files

**Actual Times:**
- Small books (~50 verses): ~0.1s
- Medium books (~500 verses): ~0.2s  
- Large books (1500+ verses): ~0.4s
- Largest book (Tehilim, 2458 verses): ~0.2s
- **Total pipeline: ~30 seconds** for all 38 books

## 🛠️ Troubleshooting

### Missing mammoth library
```bash
pip install mammoth
```

### No progress bar
```bash
pip install tqdm
```
Progress bars are optional. System works with basic text output if tqdm is not installed.

### Conversion hangs or is slow
The system has been optimized with pre-compiled regex patterns. If you're using an older version, pull the latest code which includes performance improvements.

### File not found errors
Ensure you're in the project root (`~/davar`) when running commands.

## 🔧 Advanced Usage

### Convert Single Book
```bash
python scripts/tth_2/main.py convert bereshit
```

### Re-process Specific Book
```bash
rm data/tth_2/json/amos.json
python scripts/tth_2/main.py convert amos
```

### Check Output
```bash
# View book info
python -c "import json; d=json.load(open('data/tth_2/json/amos.json')); print(d['book_info'])"

# Count verses
python -c "import json; d=json.load(open('data/tth_2/json/amos.json')); print(f\"Verses: {d['book_info']['total_verses']}\")"
```

## 📋 Example Output

```
============================================================
TTH2 Processing System - Davar Project
============================================================

Running full TTH2 pipeline...

STEP 1: Splitting DOCX files
Processing DOCX files: 100%|████████| 4/4 [00:20<00:00, 5.0s/file]

📄 tanaj.docx
  Converting to markdown... ✓
  Extracting books:
  ✓ bereshit
  ✓ shemot
  ... (27 books total)
  ✓ Extracted 27 books

============================================================
✓ Split complete! Extracted 43 books total
============================================================

STEP 2: Converting to JSON
Converting to JSON: 100%|████████| 38/38 [00:45<00:00, 1.2s/book]
  ✓ amos
  ✓ bamidbar
  ✓ bereshit
  ... (38 books)

============================================================
✓ Conversion complete! 38 books converted
============================================================

🎉 Pipeline completed successfully!
```

## 🏗️ Architecture

```
DOCX Files → docx_to_md.py → Complete MD → book_splitter.py 
  → Per-Book MD → md_to_json.py → JSON Files
```

### Module Responsibilities
- **docx_to_md.py** - Converts DOCX using mammoth, normalizes markdown
- **book_splitter.py** - Extracts individual books from complete markdown
- **md_to_json.py** - Parses markdown, extracts footnotes/terms, generates JSON
- **text_cleaner.py** - Cleans soft hyphens, punctuation, connectors
- **config.py** - Book metadata and Hebrew term definitions
- **main.py** - CLI orchestration with progress bars

## 🔄 Comparison: TTH v1 vs TTH2

| Feature | TTH v1 | TTH2 |
|---------|--------|------|
| Files per book | 9-50 | 1 |
| File size | Large | 67% smaller |
| Structure | Flat array | Hierarchical |
| Metadata | Per verse | Once at top |
| Processing | ~2-5s/book | ~0.1-2s/book |
| Workflow | Multi-step | One command |
| Output | Verbose | Clean + progress |

## 📝 Notes

- **ISR License:** One verse per screen, visible attribution required
- **TTH License:** Permission from Natanael Doldan required
- **Text cleaning:** Handles soft hyphens, punctuation spacing, stuck connectors
- **Post-processing:** Converts markdown italics to `<em>` tags for React Native
- **Hebrew terms:** Disabled for performance (always returns empty array)
- **Footnotes:** Converted to superscript markers (¹²³) with full explanations

## 🔄 Post-Processing

The `postprocess` command fixes formatting issues from DOCX conversion:

**What it fixes:**
- Converts `*word*` → `<em>word</em>` (for react-native-render-html)
- Fixes broken italics: `*word *` → `<em>word</em>`
- Adds proper spacing around `<em>` tags: `escribírte<em>las</em>` → `escribírte <em>las</em>`
- Removes escaped parentheses: `\(Lit.: ...\)` → `(Lit.: ...)`
- Removes soft hyphens (invisible word-break characters)
- Cleans underscore artifacts from conversion

**Before:**
```json
{
  "tth": "Vi *esta *noche... \\(Lit.: lugar sombrío\\), para escribírte*las*"
}
```

**After:**
```json
{
  "tth": "Vi <em>esta</em> noche... (Lit.: lugar sombrío), para escribírte <em>las</em>"
}
```

**Stats from full processing:**
- 22,628 verses processed
- 14,454 soft hyphens removed
- 6,620 escaped parentheses fixed
- 12,696 italics converted to `<em>`
- ~525 `<em>` spacing issues fixed

## 🎯 For Davar App Integration

Load books from `data/tth_2/json/{book}.json`:

```python
import json

# Load a book
with open('data/tth_2/json/bereshit.json') as f:
    book = json.load(f)

# Access metadata
print(f"{book['book_info']['tth_name']}")
print(f"Chapters: {book['book_info']['total_chapters']}")

# Access verses
for chapter in book['chapters']:
    for verse in chapter['verses']:
        print(f"{chapter['chapter']}:{verse['verse']} - {verse['tth']}")
```

## 🤝 Contributing

When adding new books:
1. Add book info to `config.py` → `BOOKS_INFO`
2. Add Hebrew terms to `config.py` → `HEBREW_TERMS` if needed
3. Update `book_splitter.py` → `BOOK_PATTERNS` for extraction patterns

---

**Davar Project** - A kadosh, distraction-free digital altar for engaging Hebrew Scriptures
