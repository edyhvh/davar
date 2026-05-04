# PDF to Images Converter

A modular Python package for converting PDF pages to images for OCR processing using the pdf2image library.

## Requirements

- Python 3.8+
- poppler (for pdf2image)
- pdf2image
- tqdm

### Installing poppler

```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt install poppler-utils

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

## Usage

```bash
# List all available books
python -m scripts.images --list

# Convert a single book (to data/images/raw_images)
python -m scripts.images matthew

# Convert multiple books
python -m scripts.images matthew mark luke john

# Convert all books
python -m scripts.images all

# Test mode (converts first 2 pages to data/temp)
python -m scripts.images --test matthew

# Convert specific page range
python -m scripts.images --pages 1-5 matthew

# Custom DPI (150-200 recommended for OCR)
python -m scripts.images --dpi 150 matthew

# Different image format
python -m scripts.images --format JPEG matthew

# Larger batch size (faster, uses more memory)
python -m scripts.images --batch-size 20 matthew

# Force re-conversion of existing pages
python -m scripts.images --force matthew

# Check PDF integrity for all books
python -m scripts.images --check-integrity

# Convert a custom PDF file
python -m scripts.images --pdf-path /path/to/custom.pdf
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--list` | | List all available books |
| `--output DIR` | `-o` | Output directory (default: `data/images/raw_images`) |
| `--test` | | Convert to `data/temp` for testing (first 2 pages) |
| `--pages RANGE` | | Page range to convert (e.g., "1-5" or "3") |
| `--format FMT` | `-f` | Image format: PNG, JPEG, TIFF, BMP (default: PNG) |
| `--dpi N` | | DPI for conversion (default: 300, recommended: 150-200) |
| `--batch-size N` | | Pages to process at once (default: 10) |
| `--force` | | Force re-conversion of existing pages |
| `--check-integrity` | | Check PDF integrity for all books |
| `--pdf-path PATH` | | Convert a specific PDF file |
| `--verbose` | `-v` | Enable verbose logging |

## Features

- **Resume capability**: Automatically skips already converted pages
- **Batch processing**: Processes multiple pages at once for better performance
- **Progress tracking**: Shows ETA and conversion speed
- **Performance stats**: Learns from previous runs to estimate conversion time
- **PDF integrity check**: Validates PDF files before conversion

## Module Structure

```
scripts/images/
├── __init__.py      # Package exports
├── __main__.py      # Module entry point
├── cli.py           # Command-line interface
├── constants.py     # Configuration constants
├── converter.py     # PDF to image conversion logic
├── main.py          # Main entry point
├── stats.py         # Performance statistics tracking
├── utils.py         # Utility functions
└── README.md        # This file
```

## Programmatic Usage

```python
from scripts.images import convert_pdf_to_images, process_books, AVAILABLE_BOOKS

# Convert a single PDF
convert_pdf_to_images(
    pdf_path="data/source/matthew.pdf",
    output_dir="data/images/raw_images",
    book_name="matthew",
    dpi=200,
)

# Process multiple books
process_books(
    book_names=["matthew", "mark"],
    output_dir="data/images/raw_images",
    dpi=200,
    batch_size=15,
)

# Get list of available books
print(AVAILABLE_BOOKS)
```

## Performance Tips

- **Lower DPI**: Use 150-200 DPI for OCR (faster than 300 DPI)
- **Larger batch size**: Use `--batch-size 20` or higher if you have enough RAM
- **SSD storage**: Output to an SSD for faster write speeds

