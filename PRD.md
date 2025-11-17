# Davar - Product Requirements Document

**Version:** 1.1  
**Hebrew:** דבר (word)  
**Tagline:** Minimalist Bible study app for meditating on the Word of Elohim

## Vision & Description

Create a kadosh, distraction-free digital altar for engaging Hebrew Scriptures with depth and authenticity. Focus on Hebrew text (Tanaj + Besorah), Qumran textual variants, custom dictionary system with expandable word definitions, and immersive yet simple UX with offline-first design.

## Localization

- **Current:** Hebrew (RTL), Spanish, English
- **Future:** Portuguese
- **Features:** Hebrew keyboard support, localized book names, system-responsive themes
- **Identification System:** Universal reference system in English (books, chapters, verses)

## Legal & Credits

### Licensing
- **Code:** GNU General Public License v3.0 (GPL-3.0)
  - All source code and dictionary data (including Klein Dictionary) distributed under GPL-3.0
  - See LICENSE file for full GPL-3.0 text
  - Note: ISR content is NOT covered by GPL-3.0 (see LICENSE-ISR)
- **ISR Content:** Restricted use per agreement dated 20 July 2025
  - One verse per screen restriction
  - Visible attribution required
  - Subject to separate license agreement (see LICENSE-ISR)
  - ISR content remains under ISR's proprietary license, not GPL-3.0
- **TTH (Traducción Textual del Hebreo):** Permission secured from Natanael Doldan
  - PDF processing required
  - Manual validation needed
- **Klein Dictionary:** GPL-3.0 (via Sefaria-Export)
  - Included in codebase under GPL-3.0
  - Independent of Sefaria API (data downloaded directly)
- **Fonts:** Project-limited use with attribution (Kriss Udd permission secured)

### Contributors
- **Adi Greenberg:** Custom DSS-inspired font design (DSS variants only)
- **Kriss Udd:** BiblePlaces.com fonts permission (REMOVED from word display)
- **Leonardo & Danezli Cancio:** UI design assets (pictographs REMOVED)
- **Partners:** ISR, Natanael Doldan (TTH - pending approval)

## Repository Structure

```
davar/
├── ruaj/              # Frontend React Native app
├── or/                # Backend FastAPI services (Railway)
├── workers/           # Cloudflare Workers proxy layer
├── besorah/           # Content management features
├── content/           # Data files (PRIVATE branch only)
├── design-system/     # Penpot integration & design tokens
│   ├── tokens/        # Design tokens (JSON/TS)
│   ├── penpot-assets/ # Penpot project files
│   ├── components/    # React Native components
│   └── documentation/ # Component usage (MDX)
├── tools/             # Development tools and utilities
│   └── transliteration/ # Hebrew transliteration system (SBL/Brill)
└── docs/              # Documentation
```

**Privacy Policy:**
- **Public:** Code (GPL-3.0) + dictionary data (GPL-3.0) + mock data
- **Private:** ISR/BTX/DSS datasets (ISR license), licensed fonts, translations
- **Gitignore:** `/content/data`, `/content/sqlite`, `*.db`, `.env`, `wrangler.toml`

**License Separation:**
- **Public Repository:** Code and dictionary data under GPL-3.0
- **Private Branch:** ISR content remains under ISR license (not GPL-3.0)
- **Documentation:** See LICENSE (GPL-3.0) and LICENSE-ISR (ISR agreement)

## Design System: "Minimalismo Kadosh con Influencia Art Deco"

### Visual System

**Glassmorphism Implementation:**
```scss
// /design-system/tokens/effects.ts
export const effects = {
  glassmorphism: {
    primary: {
      background: 'rgba(224, 222, 211, 0.25)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(181, 158, 81, 0.18)',
      borderRadius: 12
    },
    secondary: {
      background: 'rgba(89, 112, 87, 0.15)',
      backdropFilter: 'blur(8px)',
      border: '1px solid rgba(89, 112, 87, 0.25)',
      borderRadius: 8
    }
  },
  shadows: {
    soft: '0 4px 12px rgba(16, 16, 15, 0.1)',
    medium: '0 8px 24px rgba(16, 16, 15, 0.15)',
    strong: '0 12px 32px rgba(16, 16, 15, 0.2)'
  }
}
```

**Icon System:**
- **Style:** Monochromatic biblical symbols
- **Library:** Custom SVG icon set in Penpot
- **Export:** React Native compatible format
- **Themes:** Automatic color adaptation

**Accessibility Features:**
- **Dynamic Type:** iOS/Android system font scaling
- **Color Contrast:** WCAG AA compliance
- **VoiceOver/TalkBack:** Semantic markup support
- **RTL Support:** Complete Hebrew text rendering

### Penpot Workflow Integration

**Project Structure in Penpot:**
```
Dabar Design System/
├── 📁 Foundations
│   ├── Colors & Tokens
│   ├── Typography Scales
│   └── Spacing System
├── 📁 Components
│   ├── Verse Display
│   ├── Navigation
│   ├── Analysis Sheets
│   └── Form Elements
├── 📁 Patterns
│   ├── Reading Flow
│   ├── Word Study Flow
│   └── Cross-Reference Flow
└── 📁 Screens
    ├── Main Reading View
    ├── Book Selection
    └── Settings
```

**Claude Code Integration:**
1. **Design Tokens Export:** Automated JSON/TS generation from Penpot
2. **Component Specs:** Structured documentation for AI code generation
3. **Style Guide:** Machine-readable component specifications
4. **Asset Export:** Optimized SVG/PNG assets for React Native

### Design-to-Code Pipeline

**Workflow Steps:**
1. **Design in Penpot:** Create/update components with specs
2. **Export Design Tokens:** Generate JSON/TypeScript files
3. **Claude Code Generation:** AI generates React Native components
4. **Integration Testing:** Validate components in Storybook
5. **Version Control:** Commit design files with code

**Export Configuration:**
```json
{
  "exportConfig": {
    "tokens": {
      "format": "typescript",
      "path": "/design-system/tokens/"
    },
    "components": {
      "target": "react-native",
      "path": "/design-system/components/",
      "documentation": "mdx"
    },
    "assets": {
      "format": ["svg", "png@2x", "png@3x"],
      "path": "/design-system/assets/"
    }
  }
}
```

### Design Tools & Workflow

**Primary Tool:** Penpot (Open Source Design Platform)
- **Cost:** $0 (completely free)
- **Integration:** Claude Code compatible structure
- **Export Target:** React Native components
- **Collaboration:** Web-based, Git-friendly workflow

**Design-to-Code Pipeline:**
1. **Design in Penpot** → Component specifications
2. **Export Design Tokens** → JSON/TypeScript format
3. **Claude Code Generation** → React Native components
4. **Version Control** → Git integration for design files

### Design Tokens Architecture

```typescript
// /design-system/tokens/colors.ts
export const colors = {
  palette: {
    beige: '#E0DED3',        // Primary background
    dorado: '#B59E51',       // Kadosh accents
    verde_olivo: '#597057',  // Secondary
    verde_oscuro: '#2A2E17', // Deep text
    negro: '#10100F'         // Primary text
  },
  semantic: {
    background: {
      primary: 'beige',
      overlay: 'rgba(224, 222, 211, 0.95)'
    },
    text: {
      primary: 'negro',
      secondary: 'verde_oscuro',
      accent: 'dorado'
    },
    accent: {
      primary: 'dorado',
      secondary: 'verde_olivo'
    }
  }
}

// /design-system/tokens/typography.ts
export const typography = {
  fonts: {
    hebrew: 'SBL Hebrew',
    heading: 'Playfair Display',
    body: 'Inter',
    bodyAlt: 'Nunito Sans',
    dss: 'Adi DSS Custom'
  },
  scales: {
    display: { size: 32, weight: '700', lineHeight: 1.2 },
    h1: { size: 28, weight: '600', lineHeight: 1.3 },
    h2: { size: 24, weight: '600', lineHeight: 1.4 },
    h3: { size: 20, weight: '500', lineHeight: 1.4 },
    body: { size: 16, weight: '400', lineHeight: 1.6 },
    caption: { size: 14, weight: '400', lineHeight: 1.5 },
    hebrew: { size: 18, weight: '400', lineHeight: 1.8 }
  }
}

// /design-system/tokens/spacing.ts
export const spacing = {
  base: 8,
  scale: {
    xs: 4,   // 0.5 * base
    sm: 8,   // 1 * base
    md: 16,  // 2 * base
    lg: 24,  // 3 * base
    xl: 32,  // 4 * base
    xxl: 48  // 6 * base
  }
}
```

### Component Architecture

**Core Components (Claude Code Ready):**

```typescript
// /design-system/components/verse-card/
VerseCard {
  variants: ['default', 'highlighted', 'qumran']
  props: {
    text: string
    language: 'hebrew' | 'spanish' | 'english'
    hasVariants: boolean
    isSelected: boolean
  }
  glassmorphism: true
}

// /design-system/components/word-analysis-sheet/
WordAnalysisSheet {
  behavior: 'expandable-bottom-sheet'
  sections: ['root', 'definition', 'occurrences', 'variants']
  props: {
    word: HebrewWord
    customDefinition?: CustomDefinition
    strongsData?: StrongsEntry
    isExpanded: boolean
  }
}

// /design-system/components/navigation/
BookSelector {
  style: 'glassmorphism-grid'
  layout: 'responsive-masonry'
  props: {
    books: Book[]
    selectedBook?: Book
    onSelect: (book: Book) => void
  }
}
```

## Dictionary System (NEW FEATURE)

### Custom Definition System
- **Phase 1:** 72 most important Hebrew words with custom definitions (English + Spanish)
- **Future Phases:** Gradual expansion in app updates
- **Fallback:** Strong + BDB for undefined words (English + Spanish)
- **Etymology Layer:** Klein Dictionary integration (GPL-3.0)
  - Hebrew etymological dictionary via Sefaria-Export
  - Includes word evolution, semitic connections, and derivations
  - Data included directly in codebase (independent of Sefaria API)
  - Distributed under GPL-3.0 alongside code
- **User Choice:** Toggle to view Strong's alongside custom definitions
- **Future Consideration:** Hebrew native dictionary integration (v3.0+)

### Multi-Language Architecture
```json
{
  "word_definitions": {
    "hebrew_word": "שָׁלוֹם",
    "transliteration": "shalom",
    "root": "שלם",
    "custom_definition": {
      "en": {
        "primary": "Complete wholeness and peace",
        "variants": ["wellness", "harmony", "completion"],
        "theological_notes": "More than absence of conflict...",
        "usage_examples": ["greeting", "state of being", "divine attribute"]
      },
      "es": {
        "primary": "Integridad y paz completa",
        "variants": ["bienestar", "armonía", "plenitud"],
        "theological_notes": "Más que ausencia de conflicto...",
        "usage_examples": ["saludo", "estado del ser", "atributo divino"]
      }
    },
    "strong_available": true,
    "bdb_available": true,
    "priority_level": 1,
    "future_hebrew_support": true
  }
}
```

## Technical Architecture

### Stack & Hosting (Hybrid Architecture)
- **Frontend:** React Native (iOS 15+, Android API 24+)
- **Backend (Origin):** FastAPI + PostgreSQL (Railway - $5/month)
- **Edge Layer:** Cloudflare Workers proxy (FREE - caching & DDoS protection)
- **Database:** PostgreSQL (Railway managed)
- **Domain:** davarapp.org (owned)
- **Offline:** SQLite with AES-256 encryption
- **Total Cost:** $5/month (Railway) + $0 (Cloudflare free tier)

### API Endpoints (`api.davarapp.org`)
- `GET /verse/{id}` - Single verse retrieval
- `GET /word/{id}` - Detailed lexical analysis (custom + Strong/BDB)
- `GET /variants/{verse_id}` - Qumran textual variants
- `GET /crossrefs/{verse_id}` - Related verses (third-party + custom edits)
- `GET /occurrences/{word_id}` - Word occurrences across Scripture (v1.1)
- `POST /search` - Hebrew text search (v1.5)
- `GET /books` - Book hierarchy
- `GET /health` - Health check

### Database Schema (PostgreSQL)
```sql
-- Updated PostgreSQL Schema
CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  name_hebrew TEXT NOT NULL,
  name_translit TEXT,
  name_es TEXT,
  name_en TEXT NOT NULL, -- Universal reference system
  order_tanaj INTEGER,
  is_besorah BOOLEAN DEFAULT FALSE
);

CREATE TABLE verses (
  id SERIAL PRIMARY KEY,
  chapter_id INTEGER REFERENCES chapters(id),
  number INTEGER NOT NULL,
  text_hebrew TEXT NOT NULL,
  text_es TEXT, -- Natanael Doldan translation
  text_en TEXT, -- Existing English
  has_qumran_variants BOOLEAN DEFAULT FALSE
);

CREATE TABLE words (
  id SERIAL PRIMARY KEY,
  verse_id INTEGER REFERENCES verses(id),
  position INTEGER NOT NULL,
  text_hebrew TEXT NOT NULL,
  translit TEXT,
  root TEXT NOT NULL, -- Always show root
  custom_definition JSONB, -- New custom dictionary
  strong_number TEXT,
  bdb_reference TEXT,
  morphology JSONB
  -- REMOVED: pictographs JSONB
);

CREATE TABLE custom_dictionary (
  id SERIAL PRIMARY KEY,
  hebrew_word TEXT NOT NULL,
  root TEXT NOT NULL,
  transliteration TEXT,
  priority_level INTEGER, -- 1=initial 50, 2=next expansion, etc.
  custom_definition_en JSONB, -- English custom definition
  custom_definition_es JSONB, -- Spanish custom definition
  custom_definition_he JSONB, -- Future Hebrew native definition
  strong_available BOOLEAN DEFAULT TRUE,
  bdb_available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE qumran_variants (
  id SERIAL PRIMARY KEY,
  verse_id INTEGER REFERENCES verses(id),
  manuscript_source TEXT NOT NULL, -- 1QIsa, 4QSam, etc.
  variant_text TEXT NOT NULL,
  dss_font_required BOOLEAN DEFAULT TRUE,
  notes TEXT,
  significance TEXT
);

CREATE TABLE cross_references (
  id SERIAL PRIMARY KEY,
  verse_id INTEGER REFERENCES verses(id),
  related_verse_id INTEGER REFERENCES verses(id),
  relationship_type TEXT,
  source TEXT DEFAULT 'third_party', -- 'third_party' or 'custom'
  weight DECIMAL(3,2) DEFAULT 1.0
);

CREATE TABLE word_occurrences (
  id SERIAL PRIMARY KEY,
  word_id INTEGER REFERENCES words(id),
  verse_id INTEGER REFERENCES verses(id),
  context_before TEXT,
  context_after TEXT,
  occurrence_rank INTEGER -- For ordering by importance
);

-- REMOVED: strong_entries, bdb_entries (integrated into custom_dictionary)
```

## User Experience

### Core Features
- **Navigation:** Glassmorphism book/chapter selectors
- **Reading:** One verse per screen (contemplative focus)
- **Analysis:** Expandable bottom sheet with:
  - Word root (always visible)
  - Custom definition OR Strong+BDB fallback
  - BDB sense assignment: Main definitions (`sense: "0"`) vs. specific senses (`sense: "1"`, `"2"`, etc.)
  - Etymology (Klein Dictionary) - word evolution and semitic connections
  - Morphology details
  - User toggle for Strong's view (when custom exists)
- **Qumran Variants:** DSS font rendering with manuscript attribution
- **Cross References:** Parallel verse viewer with tap navigation
- **Preferences:** Theme toggle, nikud toggle, auto-save position
- **Offline:** Cache recently read verses only

### New Features (v1.1)
- **Word Occurrences:** Tap word → show all Scripture occurrences
- **Parallel References:** Cross-reference verses open side-by-side
- **Custom Dictionary:** Progressive revelation of Hebrew meanings

## Development Roadmap

### Version 1.0 (MVP - Initial Release)
- Hebrew text (Tanaj + Besorah) with SBL Hebrew font
- Custom dictionary (72 words) with Strong/BDB fallback
- Klein Dictionary etymology integration (GPL-3.0)
- Qumran variants with DSS font
- Cross-references with parallel view
- Spanish (Natanael Doldan) + English versions
- Dark/light mode + nikud toggle
- App Store + Play Store release

### Version 1.1 (First Update)
- Word occurrence finder
- Custom dictionary expansion (next 72 words)
- Enhanced cross-reference editing tools

### Version 1.5 (Search & Aramaic)
- Hebrew text search functionality
- Targum Aramaic integration
- Enhanced navigation

### Version 2.0 (Greek & Distribution)
- LXX (Septuagint) integration
- Telegram Mini App
- Enhanced analytics

### Version 3.0+ (Future Language Support)
- Hebrew native dictionary integration
- Advanced linguistics features
- Academic collaboration tools

## Text Sources & Processing

### Hebrew Text
- **Base:** ISR/BTX Hebrew text
- **Processing:** Tokenized with morphological analysis
- **Variants:** Qumran manuscripts with DSS font display

### Spanish Translation
- **Source:** Natanael Doldan translation (permission needed)
- **Processing:** If structured files unavailable, PDF extraction system needed
- **Format:** Verse-by-verse alignment with Hebrew base

### English Translation
- **Source:** Existing TS2009 + Besorah content
- **Processing:** Direct integration from current datasets

### Hebrew Transliteration System
- **Standards:** SBL General Purpose + Brill Simplified academic systems
- **Languages:** Spanish (primary), extensible to other languages
- **Features:** Phonetic adaptation, dagesh handling, sheva pronunciation
- **Tools:** `tools/transliteration/` - Python scripts for schema generation
- **Data:** Strong's concordance integration with custom phonetic mappings
- **Output:** `strong_{language}.json` files for app integration

### Cross-References
- **Initial:** Third-party cross-reference system
- **Enhancement:** Manual curation and weighting system
- **Display:** Parallel verse view with relationship indicators

## Deployment Strategy

### Multi-Platform Release Plan
1. **Mobile Apps:** iOS App Store + Google Play Store (v1.0)
2. **Telegram Mini App:** After mobile app stabilization (v2.0)
3. **Base Network:** Web3 integration for decentralized access (v3.0)

### Hosting Architecture
- **Cost:** $5/month (Railway) + $0 (Cloudflare)
- **Environments:**
  - Development: `dev.dabar.one`
  - Production: `api.dabar.one`
  - Web (future): `dabar.one`

## Success Metrics

### Spiritual Transformation Funnel
1. Install → First Sacred Session
2. First Sacred Session → Hebrew Word Understanding
3. Hebrew Understanding → Custom Dictionary Engagement
4. Dictionary Engagement → Deep Contemplative Practice

### Technical KPIs
- App Store rating > 4.5
- Zero unauthorized mass downloads
- Custom dictionary engagement rate > 40%
- Qumran variant interaction rate > 20%

## Risk Mitigation

- **Legal:** Secure Natanael Doldan permission for TTH usage (SECURED), develop PDF processing system
- **Content:** PDF processing system development for TTH extraction (REQUIRED)
- **Security:** Enhanced rate limiting for custom dictionary content
- **User Experience:** Progressive Hebrew learning curve with custom definitions

---

## Immediate Action Items

### CRITICAL - Content Licensing
1. **Contact Natanael Doldan:** Request structured files or PDF processing permission
2. **Document Permissions:** Create formal agreements for all text sources
3. **Test Content Processing:** Validate PDF extraction if needed

### Priority 1 - Design System
1. **Figma Integration:** Set up design system with component library
2. **Remove Deprecated Elements:** Clean pictogram references, ancient font systems
3. **Create Custom Dictionary UI:** Design expandable definition interface
4. **Parallel View Design:** Cross-reference verse display mockups

### Priority 2 - Data Architecture
1. **Custom Dictionary Schema:** Implement 72-word priority system
2. **Qumran Processing:** Organize DSS manuscripts by verse
3. **Cross-Reference Integration:** Set up third-party system + editing interface
4. **Occurrence Mapping:** Create word-to-verse occurrence tables

### Priority 3 - Development Setup
1. **Railway + Cloudflare:** Deploy hybrid architecture
2. **PostgreSQL Schema:** Implement updated database design
3. **Content Processing:** Build PDF extraction for Spanish translation
4. **API Endpoints:** Custom dictionary and occurrence routes

### Priority 4 - Content Creation
1. **50 Core Words:** Define initial Hebrew dictionary entries
2. **Qumran Variants:** Map manuscript variants to specific verses
3. **Spanish Integration:** Process Natanael Doldan translation
4. **Cross-Reference Curation:** Begin third-party system customization

*This updated PRD reflects the strategic pivot toward custom Hebrew scholarship, simplified typography, and comprehensive multi-platform deployment strategy.*