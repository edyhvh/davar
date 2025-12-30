# TS2009 Processor v2.0

Professional refactored version of the TS2009 Bible processor for the Davar app. Converts TS2009 SQLite database to streamlined JSON format optimized for contemplative Hebrew Scripture study.

## Overview

This processor transforms the TS2009 Bible database into a minimal, focused JSON structure designed specifically for the Davar app's "one verse per screen" contemplative reading experience.

## Key Changes from v1.0

- **Streamlined Data Structure**: Reduced from 15+ fields to 8 essential fields per verse
- **Single File per Book**: Consolidated chapter files into one JSON per book
- **Professional Architecture**: Modular, testable, and maintainable codebase
- **Enhanced Metadata**: Focused book metadata for app integration
- **Improved Error Handling**: Robust error handling and logging

## Data Structure

### Verse Fields
Each verse contains only the essential fields needed for the Davar app:

```json
{
  "book": "amos",
  "book_id": "amos",
  "book_ts2009_name": "עמוס/Amos",
  "section": "neviim",
  "chapter": 1,
  "verse": 1,
  "status": "present",
  "text": "The words of Amos..."
}
```

### Book Structure
Each book JSON file contains metadata and all verses:

```json
{
  "metadata": {
    "book_id": "amos",
    "expected_chapters": 9,
    "section": "neviim",
    "section_english": "Prophets",
    "total_chapters": 9,
    "total_verses": 146
  },
  "verses": [...],
  "processed_date": "2025-12-30T...",
  "processor_version": "2.0.0"
}
```

## Usage

### Command Line

```bash
# Process all books to default output directory (data/ts2009/)
python scripts/ts2009/processor.py

# Process to temporary directory for testing
python scripts/ts2009/processor.py --temp

# Process to custom directory (e.g., ts2009/)
python scripts/ts2009/processor.py --output-dir ts2009

# Custom database and output paths
python scripts/ts2009/processor.py --db-path /path/to/db.bbli --output-dir /path/to/output
```

**Default Configuration:**
- Database: `data/ts2009/raw/TS2009_Sent to DABAR.bbli`
- Output: `data/ts2009/` (ruta absoluta desde la raíz del proyecto)

**Comportamiento de Rutas:**
- Rutas absolutas: Se usan tal cual
- Rutas relativas: Se convierten automáticamente a absolutas desde la raíz del proyecto
- Ejemplo: `--output-dir ts2009` → guarda en `/ruta/del/proyecto/ts2009/`

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
```

## Architecture

### Core Classes

- **`TS2009Processor`**: Main orchestrator class
- **`BookProcessor`**: Handles individual book processing
- **`DatabaseHandler`**: Manages all database operations
- **`TextCleaner`**: Processes and cleans text content
- **`VerseData`**: Data class for verse representation
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
├── processor.py         # Main processing logic
├── config.py           # Configuration and constants
└── README.md           # This documentation
```

## Dependencies

- Python 3.8+
- sqlite3 (built-in)
- dataclasses (Python 3.7+)
- pathlib (Python 3.4+)
- typing (Python 3.5+)

## Testing

Use the `--temp` flag to process books to `data/ts2009/temp/` for testing:

```bash
python scripts/ts2009/processor.py --temp
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

## Integration with Davar App

The streamlined data structure is designed specifically for:
- One verse per screen display
- Minimal network payload
- Fast app startup
- Offline-first architecture
- RTL Hebrew text support

## Output Structure

**Default Configuration:**
- Database source: `data/ts2009/raw/TS2009_Sent to DABAR.bbli`
- Output directory: `data/ts2009/`
- Format: 66 archivos JSON individuales (uno por libro)

**File Naming Convention:**
- Libros únicos: `genesis.json`, `exodus.json`, `amos.json`, etc.
- Libros con números: `samuel_1.json`, `samuel_2.json`, `kings_1.json`, `kings_2.json`, `john_1.json`, etc.

**JSON Structure:**
```json
{
  "metadata": {
    "book_id": "samuel_1",
    "expected_chapters": 31,
    "section": "neviim",
    "section_english": "Prophets",
    "total_chapters": 31,
    "total_verses": 810
  },
  "verses": [
    {
      "book": "samuel_1",
      "book_id": "samuel_1",
      "book_ts2009_name": "שמואל א/samuel_1",
      "section": "neviim",
      "chapter": 1,
      "verse": 1,
      "status": "present",
      "text": "Verse content..."
    }
  ],
  "processed_date": "2025-12-30T...",
  "processor_version": "2.0.0"
}
```

## License

Project-specific license - see main Davar project documentation.
