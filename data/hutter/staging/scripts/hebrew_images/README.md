# Hebrew Text Column Extractor

Extracts the central Hebrew text column from biblical manuscript images using OpenCV.

## Usage

Process books by name (similar to `get_images_from_pdfs.py`):

```bash
# List available books
python scripts/hebrew_images/main.py --list

# Process a single book
python scripts/hebrew_images/main.py matthew

# Process multiple books
python scripts/hebrew_images/main.py matthew mark luke

# Process all books
python scripts/hebrew_images/main.py all
```

**Default directories:**
- Input: `data/images/raw_images/<book_name>/`
- Output: `data/images/hebrew_images/<book_name>/` (created automatically)

**Special case**: When processing `colossians`, pages 000026.png, 000028.png, and 000030.png are automatically saved to `data/images/hebrew_images/laodikim/` as they contain Paul's letter to Laodicea.

**Custom directories:**
```bash
python scripts/hebrew_images/main.py matthew \
    --input-dir data/images/raw_images \
    --output-dir data/images/hebrew_images
```

## How It Works

Automatically detects and extracts the second Hebrew column from manuscript pages using a fallback detection chain:

1. **Contour Detection** - Primary method using morphological operations
2. **Hough Line Detection** - Detects vertical column boundaries
3. **Projection-Based Detection** - Analyzes pixel density patterns
4. **Fallback Coordinates** - Uses estimated coordinates if detection fails

The tool preserves titles, enumeration markers, and ensures full column height (always starts from y=0).

## Features

- Extracts second column (not first) - the main Hebrew text column
- Preserves titles and top markers
- Handles wide regions by splitting to extract correct column
- Skips blank images automatically
- Special handling for `john1` manuscript
- Post-processing validation to fix common issues (text cutoff, wrong column selection)

## Module Structure

```
hebrew_images/
├── main.py          # CLI entry point
├── extractor.py     # Main processing logic
├── detection.py     # Detection algorithms
├── validation.py    # Post-processing fixes
├── logger.py        # Logging system
└── utils.py         # Utilities and constants
```

## Programmatic Usage

```python
from pathlib import Path
from scripts.hebrew_images import HebrewTextExtractor

extractor = HebrewTextExtractor(
    input_dir=Path("data/images/raw_images/matthew"),
    output_dir=Path("data/images/hebrew_images/matthew")
)
extractor.process_all_images()
```






