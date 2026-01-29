# DSS Parser

Professional modular parser for Dead Sea Scrolls differences extraction.

## Structure

```
scripts/dss/
├── __init__.py          # Package initialization
├── config.py            # Configuration and constants
├── xml_parsers.py       # DSS and WLC XML parsing
├── notes_parser.py      # Variant notes parsing with Hebrew word extraction
├── book_processor.py    # Book processing logic
├── output_writer.py     # Output file writing
├── main.py              # Main entry point
├── parse.py             # Convenience runner
└── parse_deadseainsights.py  # Backward compatibility wrapper
```

## Usage

### Command Line

```bash
# Run the parser
python3 scripts/dss/parse.py

# Or use the backward-compatible script
python3 scripts/dss/parse_deadseainsights.py
```

### As a Module

```python
from scripts.dss import BookProcessor, parse_notes_file
from scripts.dss.config import NOTES_FILE, BOOK_NAMES

# Parse notes
notes = parse_notes_file(NOTES_FILE)

# Process a book
processor = BookProcessor(notes)
book_data = processor.process_book("Genesis")
```

## Features

- **Modular Design**: Separated concerns for better maintainability
- **Type Hints**: Full type annotations for better IDE support
- **Error Handling**: Proper exception handling throughout
- **Hebrew Word Extraction**: Intelligent extraction of Masoretic and DSS words from XML commentary
- **Flexible Output**: Clean JSON output with metadata
- **Testing-Ready**: Easy to unit test individual components

## Components

### config.py
Configuration, paths, and constants.

### xml_parsers.py
Parses DSS and WLC XML files to extract text and variants.

### notes_parser.py
Extracts variant notes with intelligent Hebrew word identification using regex patterns.

### book_processor.py
`BookProcessor` class that orchestrates the parsing and difference extraction for each book.

### output_writer.py
`OutputWriter` class for writing JSON files and printing summaries.

### main.py
Main orchestration logic that ties everything together.
