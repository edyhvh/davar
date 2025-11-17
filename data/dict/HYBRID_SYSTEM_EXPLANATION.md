# Hybrid System: Base Lexicon + Lightweight Verses

## 📋 General Concept

**Problem**: If we store all definitions in each verse, there's a lot of duplication.

**Solution**: Separate into two levels:
1. **Base Lexicon** - Once per word (lemma)
2. **Lightweight Verses** - Only references to lexicon

---

## 📁 Directory Structure

```
data/dict/
├── lexicon/              # BASE LEXICON (by Strong's number)
│   ├── draft/
│   │   ├── H7965.json    # Shalom (שָׁלוֹם)
│   │   ├── H7999.json    # Shalem (שָׁלַם) - root
│   │   ├── H1254.json    # Bara (בָּרָא)
│   │   └── ...
│   └── roots/
│       └── ...
│
└── verses/               # LIGHTWEIGHT VERSES (organized by book)
    ├── genesis/
    │   ├── genesis.1.1.json
    │   ├── genesis.1.2.json
    │   ├── genesis.15.15.json
    │   └── ...
    ├── exodus/
    │   ├── exodus.1.1.json
    │   └── ...
    ├── leviticus/
    └── ...
```

---

## 📄 Example 1: Base Lexicon (H7965.json)

**Location**: `lexicon/draft/H7965.json` (named by Strong's number)

```json
{
  "strong_number": "H7965",
  "lemma": "שָׁלוֹם",
  "normalized": "שלום",
  "pronunciation": "shaw-lome'",
  "transliteration": "shâlôwm",
  
  "definitions": [
    {"en": "completeness", "es": "completitud", "source": "bdb", "order": 1, "sense": "1"},
    {"en": "soundness", "es": "solidez", "source": "bdb", "order": 2, "sense": "2"},
    {"en": "welfare", "es": "bienestar", "source": "bdb", "order": 3, "sense": "0"},
    {"en": "peace", "es": "paz", "source": "bdb", "order": 4, "sense": "3"},
    {"en": "safety", "es": "seguridad", "source": "bdb", "order": 5, "sense": "0"},
    {"en": "health", "es": "salud", "source": "bdb", "order": 6, "sense": "0"},
    {"en": "prosperity", "es": "prosperidad", "source": "bdb", "order": 7, "sense": "0"},
    {"en": "quiet", "es": "quietud", "source": "bdb", "order": 8, "sense": "0"},
    {"en": "tranquility", "es": "tranquilidad", "source": "bdb", "order": 9, "sense": "0"},
    {"en": "contentment", "es": "contentamiento", "source": "bdb", "order": 10, "sense": "0"},
    {"en": "friendship", "es": "amistad", "source": "bdb", "order": 11, "sense": "0"},
    {"en": "safe", "es": "seguro", "source": "strongs", "order": 12},
    {"en": "well", "es": "bien", "source": "strongs", "order": 13},
    {"en": "happy", "es": "feliz", "source": "strongs", "order": 14},
    {"en": "friendly", "es": "amigable", "source": "strongs", "order": 15}
    // ... ALL available definitions (no limit)
  ],
  
  "root": {
    "strong_number": "H7999",
    "lemma": "שָׁלַם",
    "pronunciation": "shaw-lam'",
    "definitions": [
      {"en": "be complete", "es": "ser completo", "source": "bdb", "order": 1},
      {"en": "finish", "es": "terminar", "source": "bdb", "order": 2},
      {"en": "make safe", "es": "hacer seguro", "source": "bdb", "order": 3},
      {"en": "make whole", "es": "hacer completo", "source": "bdb", "order": 4},
      {"en": "restore", "es": "restaurar", "source": "bdb", "order": 5},
      {"en": "pay", "es": "pagar", "source": "bdb", "order": 6},
      {"en": "requite", "es": "recompensar", "source": "bdb", "order": 7}
      // ... ALL available definitions
    ]
  },
  
  "occurrences": {
    "total": 209,
    "references": ["gen.15.15", "gen.26.29", "gen.43.27", ...]  // ALL occurrences, lowercase, sorted by book/chapter/verse
  },
  
  "sources": {
    "strongs": true,
    "bdb": true
  }
}
```

**Size**: ~20-30 KB (with all definitions)  
**Loaded**: Only when user taps the word  
**Name**: By Strong's number (H7965.json) to avoid issues with Hebrew characters in filenames

---

## 📄 Example 2: Lightweight Verse (genesis.15.15.json)

**Location**: `verses/genesis/genesis.15.15.json` (organized by book directory)

```json
{
  "reference": "genesis.15.15",
  "book_id": "genesis",
  "chapter": 15,
  "verse": 15,
  "hebrew_text": "וְאַתָּה תָּבוֹא אֶל־אֲבֹתֶיךָ בְּשָׁלוֹם",
  "words": [
    {
      "position": 1,
      "hebrew": "וְאַתָּה",
      "strong_number": "H859",
      "sense": "1"
    },
    {
      "position": 2,
      "hebrew": "תָּבוֹא",
      "strong_number": "H935",
      "sense": null
    },
    {
      "position": 3,
      "hebrew": "אֶל",
      "strong_number": "H413",
      "sense": null
    },
    {
      "position": 4,
      "hebrew": "אֲבֹתֶיךָ",
      "strong_number": "H1",
      "sense": "0"
    },
    {
      "position": 5,
      "hebrew": "בְּשָׁלוֹם",
      "strong_number": "H7965",
      "sense": "3"
    }
  ]
}
```

**Size**: ~1-2 KB  
**Loaded**: Immediately when opening verse  
**Reference**: Full book name in English lowercase (`genesis.15.15`)

### Key Fields:
- **`reference`**: Full reference with book name (`genesis.15.15`)
- **`book_id`**: Book name in English lowercase (`genesis`, `exodus`, `leviticus`, etc.)
- **`hebrew_text`**: Complete Hebrew text of the verse
- **`words`**: Array of word references with:
  - **`position`**: Word position in verse (1-indexed)
  - **`hebrew`**: Hebrew text of the word (for tap detection)
  - **`strong_number`**: Reference to lexicon file (`H7965` → `lexicon/draft/H7965.json`)
  - **`sense`**: BDB sense number as string (simple format: `"0"`, `"1"`, `"2"`, etc., or `null`)

---

## 🔄 App Flow

```
1. User opens Genesis 15:15
   ↓
2. App loads: verses/genesis/genesis.15.15.json (1-2 KB, fast)
   ↓
3. User taps "בְּשָׁלוֹם" (position 5)
   ↓
4. App reads: strong_number = "H7965", sense = "3"
   ↓
5. App loads: lexicon/draft/H7965.json (20-30 KB, only when needed)
   ↓
6. App filters definitions by sense "3" and shows relevant definition
   ↓
7. App displays definition with priority: BDB > Strong's
```

---

## ✅ Hybrid System Advantages

### 1. No Duplication
- **Without system**: Each verse with shalom = 25 KB × 209 = 5.2 MB
- **With system**: 25 KB (lexicon) + 2 KB × 209 = 443 KB
- **Savings**: ~92% less data

### 2. Fast Loading
- Verses load quickly (only references)
- Definitions load only when needed

### 3. Easy to Update
- Update shalom definition = only one file (`lexicon/draft/H7965.json`)
- All verses automatically have the new definition

### 4. Flexible
- Add more definitions later = only update lexicon
- No need to touch verses

---

## 📊 Definition Priority

**Priority order** (as shown in app):

1. **BDB** (more detailed and academic) - PRIORITY
2. **Strong's** (complements BDB)

**Rule**: Store **ALL available definitions**, no quantity limit. Prioritize BDB over Strong's, avoiding duplicates.

**Bilingual structure**: Each definition includes English (`en`) and Spanish (`es`) in the same object:
```json
{
  "en": "completeness",
  "es": "completitud",
  "source": "bdb",
  "order": 1,
  "sense": "1"  // "0" = main definition, "1"+" = specific sense
}
```

**Sense field**: All BDB definitions include a `sense` field:
- `"sense": "0"` = Main definition (not in a specific sense)
- `"sense": "1"`, `"sense": "2"`, etc. = Specific sense numbers from BDB
- Format: Simple string without decimals (e.g., `"1"` not `"1.0"` or `"1.1.1"`)
- In verses: The `sense` field indicates which BDB sense applies to that specific word occurrence
- This allows the app to identify and prioritize main definitions vs. sense-specific definitions

---

## 🔍 Word Search

### Identification by Strong's
- Lexicon files are named by Strong's number
- `שָׁלוֹם` (H7965) → `lexicon/draft/H7965.json`
- `שָׁלַם` (H7999) → `lexicon/draft/H7999.json`
- `בָּרָא` (H1254) → `lexicon/draft/H1254.json`

**Advantages**:
- ✅ Avoids issues with Hebrew characters in filenames
- ✅ Direct search by Strong's number
- ✅ Compatible with all operating systems

### Quick Index
```json
{
  "H7965": "lexicon/draft/H7965.json",
  "H7999": "lexicon/draft/H7999.json",
  "H1254": "lexicon/draft/H1254.json"
}
```

### Reference Normalization
- All references use full book name in English lowercase
- `Gen.15.15` → `genesis.15.15`
- `1SAM.1.17` → `1samuel.1.17`
- Book names match `book_id` format (e.g., `genesis`, `exodus`, `leviticus`, `1samuel`, `2samuel`, etc.)
- Facilitates search and comparison

### Occurrences Storage
- **Complete list**: ALL occurrences are stored (no limit)
- **Total count**: `occurrences.total` reflects the actual number of occurrences in Scripture
- **References array**: Contains ALL references, sorted by book/chapter/verse
- **Format**: Full book name in English lowercase (e.g., `genesis.15.15`, `1samuel.1.17`, `zephaniah.3.13`)
- **Sorting**: Alphabetical by book name, then numerical by chapter, then numerical by verse

**Example**:
```json
{
  "occurrences": {
    "total": 209,
    "references": [
      "genesis.15.15",
      "genesis.26.29",
      "genesis.43.27",
      // ... all 209 occurrences
      "zephaniah.3.13"
    ]
  }
}
```

This ensures:
- ✅ Complete data for word occurrence searches
- ✅ Accurate total counts
- ✅ All references available for cross-referencing
- ✅ Consistent sorting for easy lookup

---

## 📝 Example Files

- `example_lexicon_h7965.json` - Complete lexicon of shalom (H7965)
- `example_lexicon_h7999.json` - Complete lexicon of shalem (H7999) - root
- `example_verse_genesis_15_15.json` - Lightweight verse with reference

## 📋 Book Format

Book identification uses `book_id` (full English name in lowercase):

```json
{
  "book_id": "genesis"
}
```

**Book ID Format**:
- Full English book name in lowercase
- Examples: `genesis`, `exodus`, `leviticus`, `numbers`, `deuteronomy`
- For numbered books: `1samuel`, `2samuel`, `1kings`, `2kings`, `1chronicles`, `2chronicles`
- Matches the directory structure: `verses/genesis/`, `verses/exodus/`, etc.

**File Naming**:
- Format: `{book_id}.{chapter}.{verse}.json`
- Examples: `genesis.1.1.json`, `genesis.15.15.json`, `1samuel.1.17.json`

---

## ✅ Current Status

- ✅ Structure defined
- ✅ Examples created
- ✅ Priority BDB > Strong's established
- ✅ Lexicon files named by Strong's number (`H7965.json`)
- ✅ Verse files organized by book directories (`verses/genesis/`, `verses/exodus/`, etc.)
- ✅ References use full book name (`genesis.15.15` instead of `gen.15.15`)
- ✅ Book identification via `book_id` (English lowercase)
- ✅ Sense format: Simple strings without decimals (`"0"`, `"1"`, `"2"`, etc.)
- ✅ Verse generation script implemented
- ⏳ Bulk lexicon generation pending
- ⏳ Bulk verse generation pending

## 📌 Summary of Applied Changes

1. **Lexicon files**: Named by Strong's number (`lexicon/draft/H7965.json`)
2. **Verse directory structure**: Organized by book (`verses/genesis/`, `verses/exodus/`, etc.)
3. **Verse file naming**: Full book name (`genesis.1.1.json` instead of `gen.1.1.json`)
4. **Book identification**: `book_id` field with full English name in lowercase (`genesis`, `exodus`, etc.)
5. **Verse references**: Use Strong's number (`strong_number: "H7965"`)
6. **Sense format**: Simple strings without decimals (`"0"`, `"1"`, `"2"`, etc.) - matches lexicon format
7. **Word fields**: `position`, `hebrew`, `strong_number`, `sense`
8. **Verse fields**: `reference`, `book_id`, `chapter`, `verse`, `hebrew_text`, `words`
9. **Definitions**: ALL available, no quantity limit
10. **Bilingual structure**: Each definition includes `en` and `es` fields

