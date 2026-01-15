# Lexicon Translation

Translate English definitions in `roots.json` and `words.json` to target languages using xAI's Grok API.

## Quick Start

1. **Install**: `pip install openai`

2. **Configure**: Add `XAI_API_KEY=your_key` to `.env` file ([get key here](https://console.x.ai/team/default/api-keys))

3. **Translate**:
   ```bash
   # Translate all to Spanish (default)
   python -m scripts.dict.translation.main

   # Translate to Portuguese
   python -m scripts.dict.translation.main --language pt

   # Fix missing translations
   python -m scripts.dict.translation.fix_mismatches
   ```

## Usage

### Main Translation Script
```bash
# Full translation to Spanish
python -m scripts.dict.translation.main --language es --batch-size 500

# Single file only
python -m scripts.dict.translation.main --file roots --language es

# Single entry by Strong's number
python -m scripts.dict.translation.main --strong-number H1 --language es

# Dry run (no changes saved)
python -m scripts.dict.translation.main --dry-run --strong-number H10
```

### Fix Missing Translations
```bash
# Scan and fix all missing translations
python -m scripts.dict.translation.fix_mismatches --language es

# Fix specific file only
python -m scripts.dict.translation.fix_mismatches --file words --language es
```

## Supported Languages

- `es` - Spanish
- `pt` - Portuguese
- `fr` - French
- `de` - German
- `it` - Italian
- `ar` - Arabic
- `fa` - Farsi

## Architecture

- **`main.py`** - CLI interface
- **`fix_mismatches.py`** - Batch fix utility for missing translations
- **`processor.py`** - File processing and orchestration
- **`translator.py`** - Grok API communication with robust JSON parsing
- **`config.py`** - Configuration and language support

## API Details

- **Model**: `grok-4` (fastest xAI model)
- **Cost**: ~$0.38 for full translation (27,930 definitions)
- **Pricing**: $0.10/1M input, $0.30/1M output tokens
- **Endpoint**: `https://api.x.ai/v1/responses`

## Error Handling

- Robust JSON extraction with bracket-matching algorithm
- Automatic retry with exponential backoff
- Detailed mismatch logging and statistics
- Batch processing for efficient error recovery
