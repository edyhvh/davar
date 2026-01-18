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
- TTH Spanish translations
- TS2009 English translations
- DSS variants
- Custom lexicon and prefixes