# Davar Backend & Offline Architecture Plan

> Complete plan for FastAPI backend optimization and offline-first mobile integration for the Davar Hebrew Scriptures study app.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend Improvements](#backend-improvements)
3. [Data Loading Strategy](#data-loading-strategy)
4. [API Endpoints](#api-endpoints)
5. [Mobile Offline Strategy](#mobile-offline-strategy)
6. [Frontend Integration](#frontend-integration)
7. [Implementation Steps](#implementation-steps)
8. [Deployment (Supabase)](#deployment-supabase)

---

## Architecture Overview

### Philosophy

Davar is a **minimalist, contemplative app** for deep study of the Hebrew Scriptures (Tanaj and Besorah). The architecture prioritizes:

- **Offline-first**: Core Hebrew texts available without network
- **Speed**: Instant load times for scripture navigation
- **Simplicity**: No unnecessary complexity or bloat
- **Reverence**: Clean, precise code honoring the sacred texts

### Decision: Hybrid JSON-first + Supabase

| Data Type | Storage | Rationale |
|-----------|---------|-----------|
| Scripture (Masoretic, Delitzsch) | Static JSON files | Read-only, fast, cacheable |
| Dictionary/Lexicon | Static JSON + SQLite (mobile) | Large dataset, queryable |
| Translations (TTH, TS2009) | Static JSON + SQLite (mobile) | Optional downloads |
| DSS/Qumran Variants | Static JSON | Small dataset (~20KB) |
| User Data (future) | Supabase PostgreSQL | Annotations, highlights, sync |

### Server Configuration

- **Single Uvicorn worker** (no `--workers N`)
- In-memory metadata cache (~2MB) in one process
- No Redis needed for current read-heavy workload
- Future scaling: Gunicorn + Uvicorn workers with `--preload`, Redis for shared caches

---

## Backend Improvements

### 1. Lifespan Metadata Preloading

Preload lightweight metadata at startup via FastAPI's `lifespan` context manager:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload on startup (~2MB)
    app.state.books = await load_books_metadata()
    app.state.chapter_counts = await load_chapter_counts()
    app.state.verse_counts = await load_verse_counts()
    yield
    # Cleanup on shutdown (if needed)

app = FastAPI(lifespan=lifespan)
```

**Preloaded data:**
- Book lists (39 Tanaj + 27 Besorah)
- Chapter counts per book
- Verse counts per chapter

### 2. Performance Middleware

```python
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Dependencies to add:**
```
orjson
aiofiles
```

### 3. Streaming Responses

For large payloads (full chapters, search results):

```python
from fastapi.responses import StreamingResponse
import orjson

async def stream_verses(verses):
    yield b"["
    for i, verse in enumerate(verses):
        if i > 0:
            yield b","
        yield orjson.dumps(verse)
    yield b"]"

@router.get("/verses/{book}/{chapter}")
async def get_chapter(book: str, chapter: int):
    verses = load_chapter(book, chapter)
    return StreamingResponse(
        stream_verses(verses),
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "ETag": f'"{book}-{chapter}-v1"'
        }
    )
```

### 4. Fix Data Loading Mismatches

**book_mapper.py** - Add OE folder aliases:
```python
# OE folders use different naming
"isamuel": "samuel1",
"iisamuel": "samuel2",
"ikings": "kings1",
"iikings": "kings2",
"ichronicles": "chronicles1",
"iichronicles": "chronicles2",
```

**prefix.py** schema - Align with service:
```python
class PrefixResponse(BaseModel):
    id: str
    main_form: str
    type: str
    meanings: dict[str, list[str]]  # {"en": [...], "es": [...]}
    forms: list[str]
```

---

## Data Loading Strategy

### Caching Pattern

```python
from functools import lru_cache

class DataLoader:
    def __init__(self):
        self._cache: dict[str, Any] = {}
    
    @lru_cache(maxsize=100)
    def load_json(self, filepath: str) -> dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            return orjson.loads(f.read())
    
    def get_chapter(self, book: str, chapter: int):
        cache_key = f"{book}:{chapter}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load_chapter(book, chapter)
        return self._cache[cache_key]
```

### Data Size Estimates

| Dataset | Raw Size | Compressed |
|---------|----------|------------|
| Tanaj Hebrew (OE) | ~15-20 MB | ~4 MB |
| NT Hebrew (Delitzsch) | ~3-5 MB | ~1 MB |
| Spanish Translation (TTH) | ~8-12 MB | ~2-3 MB |
| English Translation (TS2009) | ~10-15 MB | ~3-4 MB |
| Dictionary/Lexicon | ~18-25 MB | ~5-6 MB |
| DSS Variants | ~20 KB | ~5 KB |
| **Total** | **~55-80 MB** | **~15-20 MB** |

---

## API Endpoints

### Existing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/books` | List all books |
| GET | `/api/v1/books/{book}/chapters` | Get chapter count |
| GET | `/api/v1/books/{book}/chapters/{chapter}/verses` | Get verse count |
| GET | `/api/v1/verses/{book}/{chapter}` | Get verses for chapter |
| GET | `/api/v1/dictionary` | Get lexicon entry |
| GET | `/health` | Health check |

### New Endpoints to Add

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/verses/{book}/{chapter}/{verse}` | Single verse retrieval |
| GET | `/api/v1/search` | Lexicon search |
| GET | `/api/v1/metadata/preload` | All preloaded metadata |
| GET | `/api/v1/export/bundle/{dataset}` | Download minified JSON bundle |

### Export Bundle Endpoint

Serves minified JSON for mobile offline downloads:

```python
@router.get("/export/bundle/{dataset}")
async def export_bundle(dataset: str):
    """
    Download minified JSON bundle.
    
    Datasets:
    - tanaj: OE Hebrew (Masoretic)
    - besorah: Delitzsch Hebrew (NT)
    - dss: Qumran variants
    - dictionary: Full lexicon
    - tth: Spanish translation
    - ts2009: English translation
    """
    data = await load_dataset(dataset)
    return ORJSONResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Content-Disposition": f'attachment; filename="{dataset}.json"'
        }
    )
```

### Query Parameters

```
# Verses endpoint
/verses/{book}/{chapter}?language=es&show_dss=true&hebrew_only=false

# Dictionary endpoint with pagination
/dictionary?strong=H7225&limit=50&offset=0

# Search endpoint
/search?q=בְּרֵאשִׁית&type=hebrew|strong|transliteration
```

### Caching Headers

For all scripture endpoints (immutable data):

```python
headers = {
    "Cache-Control": "public, max-age=31536000, immutable",
    "ETag": f'"{content_hash}"'
}
```

---

## Mobile Offline Strategy

### Hybrid Approach

| Tier | Data | Storage | When |
|------|------|---------|------|
| **Tier 1** | Core Hebrew (Tanaj + Besorah + DSS) | Bundled in app assets | Instant on install |
| **Tier 2** | Dictionary/Lexicon | SQLite (downloaded) | User taps "Download" on home screen |
| **Tier 3** | Translations (Spanish/English) | SQLite (downloaded) | User taps "Download" on home screen |

### Data Format

**Minified JSON** (no gzip compression):
- Instant parsing on modern devices
- No decompression step required
- Stored in `mobile/assets/data/`

### SQLite Schema

```sql
-- Verses table (for downloaded translations)
CREATE TABLE verses (
    id TEXT PRIMARY KEY,           -- "genesis-1-1"
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text TEXT NOT NULL,
    language TEXT NOT NULL,        -- "es" or "en"
    footnotes TEXT                 -- JSON array
);

CREATE INDEX idx_verses_book_chapter ON verses(book, chapter);

-- Lexicon table
CREATE TABLE lexicon (
    strong TEXT PRIMARY KEY,       -- "H7225"
    hebrew TEXT,
    transliteration TEXT,
    definitions TEXT NOT NULL,     -- JSON array
    root TEXT,
    root_strong TEXT,
    occurrences TEXT               -- JSON array
);

CREATE INDEX idx_lexicon_hebrew ON lexicon(hebrew);
```

### Download Flow

1. User taps "Download Dictionary" button on home screen
2. Show progress indicator with percentage
3. Fetch `/api/v1/export/bundle/dictionary`
4. Parse JSON and insert into SQLite
5. Update download status in AsyncStorage
6. Show completion notification

### Mobile Dependencies

```json
{
  "expo-sqlite": "latest",
  "expo-file-system": "latest"
}
```

---

## Frontend Integration

### Web API Client

**`web/src/app/services/apiClient.ts`:**

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:2220';
const API_KEY = import.meta.env.VITE_API_KEY;

export async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    });
    
    if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
    }
    
    return res.json();
}
```

**Environment variables (`web/.env`):**
```
VITE_API_BASE_URL=http://localhost:2220
VITE_API_KEY=your-api-key
```

### Mobile API Client

**`mobile/src/services/api.ts`:**

```typescript
const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:2220';
const API_KEY = process.env.EXPO_PUBLIC_API_KEY;

export async function apiRequest<T>(endpoint: string): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            'X-API-Key': API_KEY,
        },
    });
    
    if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
    }
    
    return res.json();
}

// Offline fallback
export async function getVerses(book: string, chapter: number): Promise<VerseResponse[]> {
    // Try bundled data first
    const bundled = await loadBundledData(book, chapter);
    if (bundled) return bundled;
    
    // Fall back to API
    return apiRequest(`/api/v1/verses/${book}/${chapter}`);
}
```

### TypeScript Types

Manually maintained in both frontends to match backend Pydantic schemas:

```typescript
// Shared interface structure
interface WordResponse {
    position: number;
    text: string;
    strong?: string;
    morph?: string;
    prefixes: string[];
    has_dss_variant: boolean;
}

interface VerseResponse {
    chapter: number;
    verse: number;
    hebrew: string;
    words: WordResponse[];
    translation?: string;
    translation_language?: string;
    translation_footnotes?: TranslationFootnote[];
    dss?: DssVariant[];
}

interface BookResponse {
    id: string;
    name: string;
    section: 'torah' | 'neviim' | 'ketuvim' | 'besorah';
    chapters: number;
    order: string;
    hebrew_name: string;
    hebrew_transliteration: string;
    spanish_name: string;
}

interface LexiconResponse {
    strong_number: string;
    hebrew?: string;
    transliteration?: string;
    definitions: DefinitionItem[];
    root?: string;
    root_strong?: string;
    root_definitions?: DefinitionItem[];
    occurrences_count: number;
}
```

### Error Boundaries & Loading States

Both web and mobile include:

- `ErrorBoundary` component wrapping data-fetching sections
- `VerseSkeleton` / `LexiconSkeleton` loading placeholders
- Retry logic for failed API calls
- Offline indicator in navigation

---

## Implementation Steps

### Phase 1: Backend Optimization

1. [ ] Add `orjson`, `aiofiles` to `requirements.txt`
2. [ ] Implement lifespan metadata preloading in `main.py`
3. [ ] Add `GZipMiddleware` and `ORJSONResponse`
4. [ ] Fix book mapper aliases (`isamuel` → `samuel1`, etc.)
5. [ ] Fix prefix schema to match service
6. [ ] Add streaming responses for chapter endpoints
7. [ ] Add caching headers (`ETag`, `Cache-Control`)

### Phase 2: New Endpoints

8. [ ] Add `/verses/{book}/{chapter}/{verse}` single-verse endpoint
9. [ ] Add `/search` endpoint exposing lexicon search
10. [ ] Add `/metadata/preload` endpoint
11. [ ] Add `/export/bundle/{dataset}` endpoint for offline downloads
12. [ ] Add pagination to dictionary endpoint

### Phase 3: Mobile Offline

13. [ ] Add `expo-sqlite`, `expo-file-system` dependencies
14. [ ] Create `mobile/assets/data/` with minified Hebrew JSON bundles
15. [ ] Create SQLite database service (`database.ts`)
16. [ ] Create offline sync service (`offlineSync.ts`)
17. [ ] Add download buttons to home screen
18. [ ] Add download progress indicator
19. [ ] Add download status in settings

### Phase 4: Frontend Integration

20. [ ] Create web API client (`apiClient.ts`)
21. [ ] Create mobile API client (`api.ts`)
22. [ ] Add TypeScript types matching backend schemas
23. [ ] Refactor `verseService.ts` to async API calls
24. [ ] Refactor `lexiconService.ts` to async API calls
25. [ ] Replace mobile mock data with API/offline data
26. [ ] Add error boundaries and loading skeletons

### Phase 5: Supabase Preparation

27. [ ] Add `supabase-py` to `requirements.txt`
28. [ ] Create `backend/app/db/supabase.py` with client setup
29. [ ] Add `DAVAR_SUPABASE_URL`, `DAVAR_SUPABASE_KEY` to config
30. [ ] Document future user data tables (annotations, highlights, sync)

---

## Deployment (Supabase)

### Backend Hosting

Deploy FastAPI to **Supabase Edge Functions** or **external hosting** (Railway, Render, Fly.io):

- Static JSON data bundled with deployment
- Environment variables for API key and Supabase credentials
- Single worker for cost efficiency

### Supabase PostgreSQL (Future)

Reserved for dynamic user data:

```sql
-- Future tables
CREATE TABLE user_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    verse_id TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_highlights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    verse_id TEXT NOT NULL,
    word_position INTEGER,
    color TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_progress (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    last_book TEXT,
    last_chapter INTEGER,
    last_verse INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Environment Variables

```bash
# Backend
DAVAR_API_KEY=your-secure-api-key
DAVAR_SUPABASE_URL=https://your-project.supabase.co
DAVAR_SUPABASE_KEY=your-supabase-anon-key

# Web
VITE_API_BASE_URL=https://api.davar.app
VITE_API_KEY=your-api-key

# Mobile
EXPO_PUBLIC_API_BASE_URL=https://api.davar.app
EXPO_PUBLIC_API_KEY=your-api-key
```

---

## Summary

| Component | Decision |
|-----------|----------|
| **Data storage** | Hybrid JSON-first + Supabase for user data |
| **Server config** | Single Uvicorn worker, in-memory cache |
| **Metadata loading** | Lifespan preload (~2MB) |
| **Response format** | `orjson` + GZip middleware + streaming |
| **Mobile offline** | Bundle Hebrew (~5MB), download dictionary/translations on user tap |
| **Download format** | Minified JSON (no compression) |
| **Types sync** | Manually maintained in web + mobile |
| **Future scaling** | Gunicorn + workers + Redis when needed |

---

*Document created: January 2026*  
*Project: Davar - Minimalist Hebrew Bible Study App*
