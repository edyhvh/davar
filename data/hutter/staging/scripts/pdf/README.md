# PDF Downloader for Hutter Polyglot Bible

A modular Python package for downloading PDF files from the Hutter Polyglot Bible archive using aria2 for optimal performance.

## Requirements

- Python 3.8+
- aria2c installed on your system

### Installing aria2

```bash
# macOS
brew install aria2

# Ubuntu/Debian
sudo apt install aria2

# Windows
choco install aria2
```

## Usage

```bash
# List all available books
python -m scripts.pdf --list

# Download a single book (to data/source)
python -m scripts.pdf matthew

# Download multiple books
python -m scripts.pdf matthew mark luke john

# Download all books
python -m scripts.pdf all

# Test mode (downloads to data/temp)
python -m scripts.pdf --test matthew

# Force re-download existing files
python -m scripts.pdf --force matthew

# Resume incomplete downloads
python -m scripts.pdf --resume matthew

# Custom aria2 settings
python -m scripts.pdf -c 32 -j 10 matthew  # 32 connections/file, 10 concurrent
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--list` | | List all available books |
| `--output DIR` | `-o` | Output directory (default: `data/source`) |
| `--test` | | Download to `data/temp` for testing |
| `--force` | `-f` | Force re-download even if files exist |
| `--resume` | `-r` | Resume incomplete downloads |
| `--connections N` | `-c` | Connections per file (default: 16) |
| `--concurrent N` | `-j` | Concurrent downloads (default: 5) |
| `--verbose` | `-v` | Enable verbose logging |

## Available Books

All 27 books of the New Testament:

- **Gospels**: matthew, mark, luke, john
- **History**: acts
- **Pauline Epistles**: romans, corinthians1, corinthians2, galatians, ephesians, philippians, colossians, thessalonians1, thessalonians2, timothy1, timothy2, titus, philemon, hebrews
- **General Epistles**: james, peter1, peter2, john1, john2, john3, jude
- **Prophecy**: revelation

## Module Structure

```
scripts/pdf/
├── __init__.py      # Package exports
├── __main__.py      # Module entry point
├── cli.py           # Command-line interface
├── constants.py     # Book mappings and configuration
├── downloader.py    # aria2 download logic
├── main.py          # Main entry point
└── README.md        # This file
```

## Programmatic Usage

```python
from scripts.pdf import download_books, BOOK_NAMES

# Download specific books
download_books(
    book_names=["matthew", "mark"],
    output_dir="data/source",
    force_redownload=False,
)

# Get list of available books
print(list(BOOK_NAMES.keys()))
```

