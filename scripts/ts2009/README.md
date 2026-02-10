# TS2009 Processor v3.0

Professional refactored version of the TS2009 Bible processor for the Davar app. Converts TS2009 SQLite database to streamlined JSON format optimized for contemplative Hebrew Scripture study.

## Overview

This processor transforms the TS2009 Bible database into a minimal, focused JSON structure designed specifically for the Davar app's "one verse per screen" contemplative reading experience.

## Key Changes from v2.0

- **Footnote Extraction**: Footnotes are now separated from verse text into a dedicated `footnotes` array
- **Streamlined Data Structure**: Removed redundant book metadata from each verse
- **Chapter-Based Organization**: Verses are now organized by chapters for better structure
- **Standardized CLI**: New CLI interface matching TTH pattern
- **Smaller File Sizes**: 30-40% reduction due to removal of redundant data

## Data Structure

### Book Structure

Each book JSON file contains metadata and all verses organized by chapters:

```json
{
  "metadata": {
    "book_id": "genesis",
    "book_name": "Genesis",
    "book_hebrew": "בראשית",
    "book_anglicized": "bereshit",
    "section": "torah",
    "section_english": "Torah",
    "section_hebrew": "תורה",
    "expected_chapters": 50,
    "total_chapters": 50,
    "total_verses": 1533
  },
  "chapters": [
    {
      "number": 1,
      "verses": [
        {
          "number": 1,
          "text": "In the beginning Elohim created the heavens and the earth."
        },
        {
          "number": 2,
          "text": "And the earth came to be formless and empty, and darkness was on the face of the deep. And the Spirit of Elohim was moving on the face of the waters.",
          "footnotes": ["[a]Or the earth became."]
        }
      ]
    }
  ],
  "processed_date": "2025-12-30T...",
  "processor_version": "3.0.0"
}
```

### Verse Fields

Each verse contains only the essential fields:
- `number`: Verse number
- `text`: Clean verse text (without footnotes)
- `footnotes`: Optional array of footnotes (only present if footnotes exist)

## Usage

### Command Line

```bash
# Process all books to default output directory (data/ts2009/)
python scripts/ts2009/cli.py all

# Process single book
python scripts/ts2009/cli.py book amos

# Process to temporary directory for testing
python scripts/ts2009/cli.py book amos --test

# List available books
python scripts/ts2009/cli.py books

# Validate output
python scripts/ts2009/cli.py validate
```

**Default Configuration:**
- Database: `data/ts2009/raw/TS2009_Sent to DABAR.bbli`
- Output: `data/ts2009/`
- Temp: `data/ts2009/temp/`

### Python API

```python
from scripts.ts2009.processor import TS2009Processor

# Initialize processor
processor = TS2009Processor()

# Process all books
processed_books = processor.process_all_books()

# Process single book
success = processor.process_single_book(30)  # Amos

# Process to temporary directory
processor.process_to_temp()

# Get available books
books = processor.get_available_books()

# Get book number by name
book_num = processor.get_book_number_by_name('amos')
```

## Architecture

### Core Classes

- **`TS2009Processor`**: Main orchestrator class
- **`BookProcessor`**: Handles individual book processing
- **`DatabaseHandler`**: Manages all database operations
- **`TextCleaner`**: Processes and cleans text content
- **`FootnoteExtractor`**: Extracts footnotes from verse text
- **`VerseData`**: Data class for verse representation
- **`ChapterData`**: Data class for chapter representation
- **`ProcessedBook`**: Data class for complete book data

### Configuration

All configuration is centralized in `config.py`:
- Book mappings (66 books with metadata)
- Section mappings (Torah, Nevi'im, Ketuvim, Besorah)
- Processing constants
- Common Hebrew terms

## File Structure

```
scripts/ts2009/
├── __init__.py          # Package initialization
├── cli.py               # Command-line interface
├── processor.py         # Main processing logic
├── text_processor.py    # Text and footnote processing
├── config.py            # Configuration and constants
└── README.md            # This documentation
```

## Dependencies

- Python 3.8+
- sqlite3 (built-in)
- dataclasses (Python 3.7+)
- pathlib (Python 3.4+)
- typing (Python 3.5+)

## Testing

Use the `--test` flag to process books to `data/ts2009/temp/` for testing:

```bash
python scripts/ts2009/cli.py book amos --test
```

This allows safe testing without affecting production data.

## Error Handling

The processor includes comprehensive error handling:
- Database connection failures
- Missing book configurations
- File I/O errors
- Text processing issues

All errors are logged with appropriate severity levels.

## Performance

Optimized for the Davar app's requirements:
- Minimal memory footprint
- Fast JSON serialization
- Efficient database queries
- Single-pass processing per book
- 30-40% smaller file sizes compared to v2.0

## Integration with Davar App

The streamlined data structure is designed specifically for:
- One verse per screen display
- Minimal network payload
- Fast app startup
- Offline-first architecture
- RTL Hebrew text support
- Clean verse text without embedded footnotes

## Output Structure

**Default Configuration:**
- Database source: `data/ts2009/raw/TS2009_Sent to DABAR.bbli`
- Output directory: `data/ts2009/`
- Format: 66 individual JSON files (one per book)

**File Naming Convention:**
- Unique books: `genesis.json`, `exodus.json`, `amos.json`, etc.
- Books with numbers: `samuel_1.json`, `samuel_2.json`, `kings_1.json`, `kings_2.json`, `john_1.json`, etc.

## Migration from v2.0

### Breaking Changes
- Output JSON structure changes (not backward compatible)
- CLI command syntax changes
- Verse data structure simplified

### Migration Steps
1. Backup existing TS2009 JSON files
2. Run new processor to regenerate all files:
   ```bash
   python scripts/ts2009/cli.py all
   ```
3. Update any code that consumes TS2009 data to use new format
4. Test with Davar app

### Data Structure Changes

**v2.0 Verse:**
```json
{
  "book": "bereshit",
  "book_id": "genesis",
  "book_ts2009_name": "בראשית/Genesis",
  "section": "torah",
  "chapter": 1,
  "verse": 1,
  "status": "present",
  "text": "And the earth came to be[a] formless... Footnote: [a]Or the earth became."
}
```

**v3.0 Verse:**
```json
{
  "number": 1,
  "text": "And the earth came to be formless...",
  "footnotes": ["[a]Or the earth became."]
}
```

## License

Project-specific license - see main Davar project documentation.
