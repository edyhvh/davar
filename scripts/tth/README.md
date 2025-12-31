# TTH Processing System

A modular system for processing Hebrew Scriptures from DOCX/Markdown to JSON format for the Davar app.

## Overview

The TTH (Textual Translation of Hebrew) Processing System converts TTH source documents into structured JSON format compatible with the Davar Bible study application. The system handles the complete pipeline from raw DOCX files to validated JSON output.

## Architecture

The system is built with a modular architecture:

```
tth/
├── __init__.py          # Package initialization
├── converter.py         # DOCX to Markdown conversion
├── extractor.py         # Book section extraction
├── processor.py         # Markdown to JSON processing
├── validator.py         # Quality assurance and validation
├── cli.py              # Command-line interface
├── main.py             # Main entry point
└── README.md           # This documentation
```

## Features

- **DOCX Processing**: Converts Microsoft Word documents to normalized Markdown
- **Book Extraction**: Intelligently extracts individual books from complete documents
- **JSON Generation**: Creates structured JSON output with proper metadata
- **Hebrew Term Detection**: Automatically identifies and explains Hebrew terms
- **Footnote Processing**: Handles inline footnotes and definitions
- **Quality Validation**: Comprehensive QA checks for data integrity
- **Multi-language Support**: Hebrew, Spanish, and English text handling

## Installation

1. Install required dependencies:
```bash
pip install mammoth
```

2. Ensure the package is in your Python path or run from the scripts directory.

## Usage

### Command Line Interface

The system provides a comprehensive CLI for all operations:

```bash
cd scripts/tth
python cli.py <command> [args...]
```

### Available Commands

#### Convert DOCX to Markdown
```bash
python cli.py convert <docx_file> [output_file]
```
Converts a DOCX file to normalized Markdown format.

#### Extract Book from Document
```bash
python cli.py extract <book_key> <docx_file> [output_dir]
```
Extracts a specific book from a complete DOCX document.

#### Process Markdown to JSON
```bash
python cli.py process <book_key> <markdown_file> [output_dir]
```
Converts a Markdown file to structured JSON format.

#### Validate Results
```bash
python cli.py validate [output_dir]
```
Runs comprehensive validation on processed books.

#### Complete Pipeline
```bash
python cli.py full <docx_file> <output_dir> [book_keys...]
```
Runs the complete processing pipeline from DOCX to validated JSON.

#### List Available Books
```bash
python cli.py books
```
Displays all supported books organized by section.

### Examples

#### Process All Books
```bash
python cli.py full data/tth/raw/tanaj.docx output/
```

#### Process Specific Books
```bash
python cli.py full data/tth/raw/tanaj.docx output/ bereshit shemot vaigra
```

#### Individual Steps
```bash
# Convert DOCX to Markdown
python cli.py convert data/tth/raw/tanaj.docx temp/tanaj.md

# Extract a book
python cli.py extract amos data/tth/raw/tanaj.docx extracted/

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

## Output Format

### JSON Structure
Each chapter generates a separate JSON file:

```json
[
  {
    "book": "amos",
    "book_id": "amos",
    "book_tth_name": "Amós",
    "book_hebrew_name": "עמוס",
    "book_english_name": "Amos",
    "book_spanish_name": "Amós",
    "section": "neviim",
    "chapter": 1,
    "verse": 1,
    "status": "present",
    "tth": "Verse text content...",
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
```

### Book Info File
Each book directory contains a `book_info.json` with metadata:

```json
{
  "tth_name": "Amós",
  "hebrew_name": "עמוס",
  "english_name": "Amos",
  "spanish_name": "Amós",
  "book_code": "amos",
  "expected_chapters": 9,
  "section": "neviim",
  "total_chapters": 9,
  "total_verses": 146,
  "processed_date": "2024-01-15T10:30:00",
  "processor_version": "2.0.0"
}
```

## Validation

The system includes comprehensive validation:

- **Structural Validation**: Ensures JSON format compliance
- **Content Validation**: Checks for required fields and data types
- **Hebrew Text Verification**: Confirms presence of Hebrew characters
- **Chapter/Verse Counting**: Validates against expected counts
- **Footnote Integrity**: Verifies footnote references and definitions

### Validation Report
```bash
python cli.py validate draft/
```

Generates a detailed QA report with:
- Processing statistics
- Issues found
- Recommendations for fixes

## Development

### Adding New Books

1. Add book information to `processor.py` BOOKS_INFO dictionary
2. Add extraction patterns to `extractor.py` BOOK_PATTERNS
3. Test extraction and processing
4. Update validation rules if needed

### Extending Functionality

The modular design allows easy extension:

- **New Input Formats**: Add converters in the `converter` module
- **Enhanced Processing**: Extend the `processor` module
- **Additional Validation**: Add rules to the `validator` module
- **New Output Formats**: Modify the `processor` output generation

## Error Handling

The system includes robust error handling:

- **File Not Found**: Clear error messages for missing inputs
- **Format Errors**: Validation catches malformed data
- **Encoding Issues**: UTF-8 handling for Hebrew text
- **Partial Failures**: Continues processing other books if one fails

## Performance

- **Memory Efficient**: Processes books individually to manage memory usage
- **Incremental Processing**: Can process single books without full reprocessing
- **Validation Caching**: Avoids redundant validation checks

## Troubleshooting

### Common Issues

1. **Missing mammoth library**
   ```bash
   pip install mammoth
   ```

2. **Hebrew text not recognized**
   - Ensure DOCX contains proper Unicode Hebrew characters
   - Check font encoding in source document

3. **Chapter count mismatch**
   - Verify source document structure
   - Check for missing or extra chapter markers

4. **Footnote processing errors**
   - Ensure footnotes are properly formatted in DOCX
   - Check for special characters in footnote text

### Debug Mode

Enable verbose output by modifying the logging level in individual modules.

## Contributing

1. Follow the existing modular structure
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Ensure all code and comments are in English
5. Validate changes against existing test data

## License

Project-specific license - see main project documentation.

## Version History

- **2.0.0**: Complete modular refactor with CLI interface
- **1.0.0**: Initial monolithic processor
