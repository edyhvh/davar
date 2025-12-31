# TTH Processor - Modified Version (temp)

Modified version of the TTH processing system with text cleaning improvements.

## Changes from Original

This version includes a new `text_cleaner.py` module that fixes common conversion issues:

### 1. Soft Hyphens (Word Breaks)
Words split across lines in the source document like `Is\-rael` are now joined correctly:
- **Before**: `Is\-rael` → **After**: `Israel`
- **Before**: `fami\-lias` → **After**: `familias`

### 2. Punctuation Spacing
Ensures proper spacing after punctuation marks (`:`, `;`, `,`, `?`, `!`):
- **Before**: `dijo:יהוה` → **After**: `dijo: יהוה`
- **Before**: `Amón,y por` → **After**: `Amón, y por`
- **Before**: `temerá?Adonai` → **After**: `temerá? Adonai`

### 3. Stuck Connectors
Words stuck to connectors are separated:
- **Before**: `Ashdody al que` → **After**: `Ashdod y al que`

## Files

- `text_cleaner.py` - New module with text cleaning functions
- `processor.py` - Modified processor that uses text_cleaner
- `test_amos.py` - Test script to verify changes
- `__init__.py` - Module initialization

## Usage

### Test with Amos
```bash
cd scripts/tth/temp
python test_amos.py
```

### Use in code
```python
from scripts.tth.temp import process_book_to_json

# Process a book with the improved processor
process_book_to_json('amos', 'path/to/amos.md', 'output/')
```

### Use just the text cleaner
```python
from scripts.tth.temp.text_cleaner import clean_text

# Clean a verse text
cleaned = clean_text("Y dijo:יהוה desde Is\\-rael")
# Result: "Y dijo: יהוה desde Israel"
```

## Integration

Once validated, the `text_cleaner.py` module can be integrated into the main 
`scripts/tth/processor.py` by:

1. Copy `text_cleaner.py` to `scripts/tth/`
2. Add import at top of `processor.py`:
   ```python
   from .text_cleaner import TTHTextCleaner
   ```
3. Initialize in `__init__`:
   ```python
   self.text_cleaner = TTHTextCleaner()
   ```
4. Call in `clean_text_preserve_comments`:
   ```python
   modified_text = self.text_cleaner.clean_verse_text(modified_text)
   ```

## Version

- Processor version: `2.1.0`
- Text cleaner integrated

