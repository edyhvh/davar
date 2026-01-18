# Davar FastAPI Backend

A secure FastAPI backend for serving Hebrew Scripture text, translations, lexicon data, and DSS variants from JSON files.

## Features

- **API Key Authentication**: Secure access with configurable API keys
- **Hebrew Scripture Data**: Tanaj (OE) and Besorah (Delitzsch) texts
- **Translations**: TTH (Spanish) and TS2009 (English)
- **DSS Variants**: DSS manuscript variants
- **Lexicon**: Custom definitions with Strong's/BDB fallback
- **Caching**: In-memory caching with memory safeguards
- **Rate Limiting**: Configurable request limits
- **CORS Support**: Configurable cross-origin access

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API key and settings
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- `GET /api/v1/books` - List all books with metadata
- `GET /api/v1/verses/{book}/{chapter}` - Get verses with translations
- `GET /api/v1/lexicon/{strong}` - Get word definitions
- `GET /api/v1/prefixes/{id}` - Get prefix meanings

## Development

The backend serves data from the `../data` directory containing:
- OE Hebrew texts (Tanaj)
- Delitzsch Hebrew texts (Besorah)
- TTH Spanish translations (tth_2 format: one JSON file per book with hierarchical structure)
- TS2009 English translations
- DSS variants
- Custom lexicon and prefixes

### TTH Data Structure (tth_2)

The TTH Spanish translations now use an optimized format with one JSON file per book:

```json
{
  "book_info": {
    "book_id": "amos",
    "tth_name": "Amós",
    "hebrew_name": "עמוס",
    "english_name": "Amos",
    "spanish_name": "Amós",
    "section": "neviim",
    "total_chapters": 10,
    "total_verses": 166
  },
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        {
          "verse": 1,
          "tth": "Palabras de Amós...",
          "footnotes": [
            {"marker": "¹", "number": "1", "word": "palabra", "explanation": "..."}
          ],
          "hebrew_terms": []
        }
      ]
    }
  ]
}
```

**Benefits of tth_2 format:**
- 67% smaller file sizes
- Single file per book (38 total) vs multiple chapter files
- Hierarchical structure for better organization
- Faster loading with improved caching efficiency