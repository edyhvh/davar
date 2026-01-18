# Davar FastAPI Backend - Manual API Testing Guide

## 🚀 Getting Started

### 1. Start the Server

First, make sure you're in the backend directory and start the server:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 2220
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:2220 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 2. API Base URL
```
http://localhost:2220
```

### 3. Authentication

All `/api/v1/*` endpoints require an API key in the `X-API-Key` header. Set your API key as an environment variable before running the examples:

```bash
# Method 1: Set directly (simplest)
export API_KEY="your-api-key-here"
```

Or load it from your `.env` file (if it exists):
```bash
# Method 2: Load from .env file in backend directory
# If you're in the project root:
if [ -f backend/.env ]; then
  export API_KEY=$(grep DAVAR_API_KEY backend/.env | cut -d '=' -f2)
fi

# If you're already in the backend directory:
if [ -f .env ]; then
  export API_KEY=$(grep DAVAR_API_KEY .env | cut -d '=' -f2)
fi
```

**Note:** The `.env` file must exist in the `backend/` directory. If it doesn't exist, use Method 1 above or create it first (see "Generating Secure API Keys" below).

All examples below use `$API_KEY` environment variable instead of hardcoding the key.

#### 🔐 Generating Secure API Keys

**For Development:**
```bash
# Create or update .env file in backend directory
cd backend
echo "DAVAR_API_KEY=your-dev-key" > .env  # Creates new file (overwrites if exists)
# OR append if file already exists:
# echo "DAVAR_API_KEY=your-dev-key" >> .env

# Then export it for immediate use
export API_KEY="your-dev-key"
```

**For Production (secure method):**
```bash
# Generate a cryptographically secure random key
python -c "import secrets; print('DAVAR_API_KEY=' + secrets.token_urlsafe(32))"
# Output: DAVAR_API_KEY=lhg-nRFu6G9tBnXJM3Sxi-1ASkcZ1hPUaTYHCQ8YaO4

# Or using openssl
openssl rand -hex 32
```

**Security Best Practices:**
- Use `secrets.token_urlsafe()` or `secrets.token_hex()` for cryptographically secure keys
- Never use predictable or hardcoded keys in production
- Store keys in environment variables (`.env` files) - never commit them to version control
- Use different keys for development, staging, and production
- Rotate keys regularly (every 90 days)
- Never commit real API keys to version control
- Use HTTPS in production to encrypt API key transmission
- Always use environment variables (`$API_KEY`) instead of hardcoding keys in scripts or documentation

---

## 🧪 Manual Testing Commands

### 1. Health Check

Test that the server is running:
    
```bash
curl -X GET "http://localhost:2220/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Root Endpoint

```bash
curl -X GET "http://localhost:2220/"
```

**Expected Response:**
```json
{
  "message": "Davar API - Hebrew Scripture Study",
  "docs": "/docs",
  "health": "/health"
}
```

### 3. API Documentation

Visit in browser: `http://localhost:2220/docs`

---

## 📚 Books Endpoints

### 3.1 List All Books

```bash
curl -X GET "http://localhost:2220/api/v1/books" \
  -H "X-API-Key: $API_KEY"
```

**Expected Response:** Array of books with id, name, section, chapters

### 3.2 List Books by Section

```bash
# Torah books only
curl -X GET "http://localhost:2220/api/v1/books?section=torah" \
  -H "X-API-Key: $API_KEY"

# Neviim books only
curl -X GET "http://localhost:2220/api/v1/books?section=neviim" \
  -H "X-API-Key: $API_KEY"

# Ketuvim books only
curl -X GET "http://localhost:2220/api/v1/books?section=ketuvim" \
  -H "X-API-Key: $API_KEY"

# Besorah books only
curl -X GET "http://localhost:2220/api/v1/books?section=besorah" \
  -H "X-API-Key: $API_KEY"
```

### 3.3 Get Chapters for a Book

```bash
curl -X GET "http://localhost:2220/api/v1/books/Genesis/chapters" \
  -H "X-API-Key: $API_KEY"
```

**Expected Response:**
```json
{
  "book": "Genesis",
  "chapters": [1, 2, 3, ..., 50]
}
```

### 3.4 Get Verse Count for a Chapter

```bash
curl -X GET "http://localhost:2220/api/v1/books/Genesis/chapters/1/verses" \
  -H "X-API-Key: $API_KEY"
```

**Expected Response:**
```json
{
  "book": "Genesis",
  "chapter": 1,
  "verse_count": 31
}
```

---

## 📖 Verses Endpoints

### 4.1 Get Verses (Hebrew Only)

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/1" \
  -H "X-API-Key: $API_KEY"
```

### 4.2 Get Verses with Spanish Translation

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/1?language=es" \
  -H "X-API-Key: $API_KEY"
```

### 4.3 Get Verses with English Translation

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/1?language=en" \
  -H "X-API-Key: $API_KEY"
```

### 4.4 Get Verses with DSS Variants

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/1?show_dss=true" \
  -H "X-API-Key: $API_KEY"
```

### 4.5 Get Verses with All Options

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/1?language=en&show_dss=true" \
  -H "X-API-Key: $API_KEY"
```

### 4.6 Test Different Books

```bash
# Tanaj (Hebrew Bible)
curl -X GET "http://localhost:2220/api/v1/verses/Psalms/1" \
  -H "X-API-Key: $API_KEY"

# Besorah (New Testament)
curl -X GET "http://localhost:2220/api/v1/verses/Matthew/1" \
  -H "X-API-Key: $API_KEY"
```

---

## 🔍 Lexicon Endpoints

### 5.1 Get Word Definition (Hebrew)

```bash
curl -X GET "http://localhost:2220/api/v1/lexicon/H430" \
  -H "X-API-Key: $API_KEY"
```

### 5.2 Get Word Definition (Greek)

```bash
curl -X GET "http://localhost:2220/api/v1/lexicon/G3056" \
  -H "X-API-Key: $API_KEY"
```

---

## 🔤 Prefixes Endpoints

### 6.1 Get Prefix Definition

```bash
curl -X GET "http://localhost:2220/api/v1/prefixes/Hb" \
  -H "X-API-Key: $API_KEY"
```

---

## ❌ Error Testing

### 7.1 Missing API Key

```bash
curl -X GET "http://localhost:2220/api/v1/books"
```

**Expected:** 401 Unauthorized

### 7.2 Invalid API Key

```bash
curl -X GET "http://localhost:2220/api/v1/books" \
  -H "X-API-Key: wrong-key"
```

**Expected:** 401 Unauthorized

### 7.3 Invalid Book Name

```bash
curl -X GET "http://localhost:2220/api/v1/verses/InvalidBook/1" \
  -H "X-API-Key: $API_KEY"
```

**Expected:** 404 Not Found

### 7.4 Invalid Chapter Number

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/999" \
  -H "X-API-Key: $API_KEY"
```

**Expected:** 404 Not Found

### 7.5 Invalid Language

```bash
curl -X GET "http://localhost:2220/api/v1/verses/Genesis/1?language=fr" \
  -H "X-API-Key: $API_KEY"
```

**Expected:** 400 Bad Request

### 7.6 Invalid Section

```bash
curl -X GET "http://localhost:2220/api/v1/books?section=invalid" \
  -H "X-API-Key: $API_KEY"
```

**Expected:** Empty array or filtered results

---

## 📊 Expected Response Formats

### Books Response
```json
[
  {
    "id": "Genesis",
    "name": "Genesis",
    "section": "torah",
    "chapters": 50,
    "testament": "tanaj"
  }
]
```

### Verses Response
```json
[
  {
    "chapter": 1,
    "verse": 1,
    "hebrew": "בְּ/רֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַ/שָּׁמַ֖יִם וְ/אֵ֥ת הָ/אָֽרֶץ׃",
    "hebrew_no_nikud": "ב/ראשית ברא אלהים את ה/שמים ו/את ה/ארץ",
    "words": [
      {
        "position": 1,
        "text": "בְּ/רֵאשִׁ֖ית",
        "text_no_nikud": "ב/ראשית",
        "strong": "Hb/H7225",
        "morph": "HR/Ncfsa",
        "prefixes": ["Hb"],
        "has_dss_variant": false
      }
    ],
    "translation": "En el principio creó Dios los cielos y la tierra.",
    "translation_language": "es",
    "translation_footnotes": [
      {
        "marker": "¹",
        "number": "1",
        "word": "Con",
        "explanation": "O, Por medio de."
      }
    ],
    "dss": null
  }
]
```

### Lexicon Response
```json
{
  "strong_number": "H430",
  "hebrew": "אֱלֹהִים",
  "transliteration": "ʼĕlōhîm",
  "definitions": [
    {
      "text": "gods, God",
      "source": "custom",
      "language": "en"
    }
  ],
  "root": "אלה",
  "root_strong": "H433",
  "occurrences_count": 2601
}
```

### Prefix Response
```json
{
  "id": "Hb",
  "hebrew": "בְּ",
  "meanings_en": ["in", "with", "by"],
  "meanings_es": ["en", "con", "por"],
  "examples": ["בְּ/רֵאשִׁ֖ית (in the beginning)"]
}
```

---

## 🐛 Debugging Tips

### 1. Check Server Logs
The server logs will show request IDs and any errors:

```
INFO: Request 12345678-1234-1234-1234-123456789abc: GET /api/v1/books
```

### 2. Request ID in Response Headers
Every API response includes an `X-Request-ID` header for tracing.

### 3. Common Issues

- **401 Unauthorized**: Check your API key header
- **404 Not Found**: Verify book names and chapter numbers exist
- **500 Internal Server Error**: Check server logs for details
- **Empty responses**: Data files might not be loading correctly

### 4. Test Data Availability

Check if data files exist:
```bash
ls -la data/oe/genesis/
ls -la data/delitzsch_parsed/matthew/
ls -la data/tth/draft/
ls -la data/ts2009/
```

---

## ✅ Success Checklist

After testing, verify these work:

- [ ] `/health` returns healthy status
- [ ] `/api/v1/books` returns book list with authentication
- [ ] `/api/v1/books?section=torah` filters correctly
- [ ] `/api/v1/books/Genesis/chapters` returns chapter list
- [ ] `/api/v1/verses/Genesis/1` returns Hebrew text
- [ ] `/api/v1/verses/Genesis/1?language=es` includes Spanish translation
- [ ] `/api/v1/verses/Matthew/1` works for New Testament
- [ ] `/api/v1/lexicon/H430` returns word definition
- [ ] `/api/v1/prefixes/Hb` returns prefix info
- [ ] All endpoints properly reject invalid API keys
- [ ] Error responses have consistent format

---

## 🔄 Quick Test Script

Run this to test all endpoints quickly:

```bash
#!/bin/bash
# Make sure API_KEY is set before running
if [ -z "$API_KEY" ]; then
  echo "Error: API_KEY environment variable is not set"
  echo "Set it with: export API_KEY='your-api-key'"
  exit 1
fi

BASE_URL="http://localhost:2220"

echo "Testing Davar API..."

# Health check
curl -s "$BASE_URL/health" | jq '.status'

# Books
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/books" | jq 'length'

# Verses
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/verses/Genesis/1" | jq 'length'

# Lexicon
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/lexicon/H430" | jq '.strong_number'

echo "Tests complete!"
```