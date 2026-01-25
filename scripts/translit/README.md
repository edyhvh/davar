# Transliteration Pipeline (Per-Word)

This module generates per-word transliterations for Tanakh and Besorah source texts using local transliteration rules. It reads word-level verse data and writes per-book JSON outputs.

## Goals

- Transliterate actual verse words (not Strong's entries)
- Output simple, readable English and Spanish transliterations
- Preserve alignment to book, chapter, verse, and word index
- Keep output aligned to the source data

## Output

Each book produces a `book.json` file in [data/translit](data/translit):

- `book_id`, `source`, `language_targets`, `generated_at`
- `verses[]` with `chapter`, `verse`, and `words[]`
- each word includes `id`, original fields, and `translit_en`/`translit_es`

## Input Sources

- Tanakh: [data/oe](data/oe)
- Besorah: [data/delitzsch_parsed](data/delitzsch_parsed)

## Files

- `config.py` - paths, model, pricing, batching defaults
- `models.py` - data structures
- `batcher.py` - mixed batching by verse + token budget
- `local_processor.py` - local per-book orchestration
- `qa.py` - output validation
- `main.py` - CLI entry point

## Notes

- Uses local transliteration rules only (no external API calls).

## How to Run

Run commands from the project root: `/Users/jhonny/davar`

### List available books

```bash
python -m scripts.translit.main --corpus tanakh --list-books
python -m scripts.translit.main --corpus besorah --list-books
```

### Transliterate a single book

```bash
# Dry-run (no file written)
python -m scripts.translit.main --corpus tanakh --book genesis --dry-run

# Write output
python -m scripts.translit.main --corpus besorah --book john
```

### Local mode (default)

```bash
# Local dry-run
python -m scripts.translit.main --corpus besorah --book john --dry-run
```

### Transliterate all books in a corpus

```bash
# Dry-run entire Tanakh
python -m scripts.translit.main --corpus tanakh --book all --dry-run

# Process entire Besorah
python -m scripts.translit.main --corpus besorah --book all
```

### Control batch size

```bash
python -m scripts.translit.main --corpus tanakh --book genesis --token-budget 8000
```

### Verbose logging

```bash
python -m scripts.translit.main --corpus tanakh --book genesis --verbose
```
