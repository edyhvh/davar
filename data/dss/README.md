# Dead Sea Scrolls (DSS) Data

This directory contains Dead Sea Scrolls data and research materials for the Davar Hebrew Scripture study app. The DSS provide valuable textual variants and insights into ancient Hebrew textual traditions.

## 📁 Directory Structure

```
data/dss/
├── README.md                    # This documentation
├── isaiah_dss_variants.json     # Isaiah DSS variants (4 variants)
├── samuel_1_dss_variants.json   # 1 Samuel DSS variants (6 variants)
├── samuel_2_dss_variants.json   # 2 Samuel DSS variants (1 variant)
└── raw/                        # 📚 RAW DSS DATA - Read-only
    ├── VARIANTES - TEXTO MASORÉTICO Y QUMRÁN.pdf  # Research document
    └── dss_corpus/             # DSS Text Corpus
        ├── biblical/           # Biblical DSS manuscripts
        └── nonbiblical/        # Non-biblical DSS texts
```

## 📚 Data Sources

### Primary Data
- **DSS Corpus**: Collection of Dead Sea Scrolls manuscripts
- **Research Document**: Comparative analysis of Masoretic Text vs Qumran variants
- **Biblical Texts**: Hebrew Scripture manuscripts from Qumran caves
- **Non-Biblical Texts**: Other ancient texts found at Qumran

### Content Categories
- **Biblical DSS**: Manuscripts of Tanakh books with textual variants
- **Non-Biblical**: Psalms, apocryphal texts, sectarian documents
- **Research Materials**: Scholarly analysis and comparative studies

## 🔬 Research Applications

### Textual Criticism
- **Masoretic vs Qumran**: Comparison of textual traditions
- **Variant Analysis**: Understanding textual development
- **Historical Context**: Insights into Second Temple Judaism

### Biblical Studies
- **Manuscript Dating**: Understanding textual history
- **Orthographic Variants**: Spelling and grammatical differences
- **Theological Implications**: Impact on biblical interpretation

## 📋 File Descriptions

| File/Directory | Description | Purpose |
|----------------|-------------|---------|
| `isaiah_dss_variants.json` | Processed Isaiah variants | App-ready variant data |
| `samuel_1_dss_variants.json` | Processed 1 Samuel variants | App-ready variant data |
| `samuel_2_dss_variants.json` | Processed 2 Samuel variants | App-ready variant data |
| `VARIANTES....pdf` | Scholarly research document | Comparative textual analysis |
| `dss_corpus/biblical/` | Biblical manuscript texts | Primary source materials |
| `dss_corpus/nonbiblical/` | Non-biblical texts | Supplementary materials |

## 📄 Processed JSON Files

The DSS variants have been extracted from the research PDF and processed into structured JSON files for app integration.

### JSON File Structure

Each book-specific JSON file contains DSS variants organized by chapter and verse with detailed word-by-word comparison:

```json
{
  "book": "isaiah",
  "total_variants": 4,
  "manuscripts": ["1QIsa-a", "1QIsa-b"],
  "manuscript_details": {
    "1QIsa-a": {
      "source": "DSS",
      "description": "Dead Sea Scrolls manuscript for isaiah"
    }
  },
  "chapters": {
    "14": {
      "4": [{
        "book": "isaiah",
        "chapter": 14,
        "verse": 4,
        "masoretic_text": "מַדְהֵבָה",
        "dss_text": "מַרְהֵבָה",
        "variant_words": [
          {
            "verse_position": 11,
            "masoretic_word": "מַדְהֵבָֽה",
            "dss_word": "מַרְהֵבָה"
            // Note: Morphological analysis not available for DSS variants
            // (only available for Masoretic Text in data/oe/)
          }
        ],
        "variant_type": "spelling",
        "significance": "high",
        "dss_source": "PDF_VARIANTS",
        "variant_translation_en": "",
        "variant_translation_es": "Variante ortográfica: MT מַדְהֵבָה vs DSS מַרְהֵבָה",
        "comments_en": "",
        "comments_es": ""
      }]
    }
  }
}
```

### Available JSON Files

- **`isaiah_dss.json`**: 4 variants from Isaiah 14:4, 21:8, 36:5, 38:13
- **`samuel_1_dss.json`**: 6 variants from 1 Samuel 1:22-23, 1:24, 2:17, 11:8, 17:4, 2:20
- **`samuel_2_dss.json`**: 1 variant from 2 Samuel 12:14

### Morphological Analysis Notes

- **Masoretic Text**: Full morphological analysis available (`lemma`, `strong`, `morph`) from `data/oe/`
- **DSS Variants**: No morphological analysis available since DSS texts lack standardized morphological tagging
- **Position Info**: Only verse position provided for DSS variants

### Processing Pipeline

1. **PDF Extraction**: `scripts/dss/pdf_analyzer.py` parses the research document
2. **Data Processing**: Variants extracted and structured using DSS types
3. **Text Correction**: `scripts/dss/fix_dss_variants_structure.py` corrects Hebrew text placement
4. **Hebrew Integration**: Masoretic Hebrew from `data/oe/`, DSS Hebrew from ETCBC DSS corpus
5. **Word Analysis**: `scripts/dss/generate_book_jsons.py` performs word-by-word comparison
6. **JSON Export**: Creates book-specific files with detailed word-level analysis

### Statistics

- **Total variants**: 11 across 3 books
- **Books covered**: Isaiah, 1 Samuel, 2 Samuel
- **Manuscript sources**: 1QIsa-a, 1QIsa-b, 4QSama, 4QSamb
- **Variant significance**: High (orthographic), Medium (lexical), Low (spelling)
- **Structure**: Hebrew texts properly separated, Spanish translations consolidated
- **DSS Texts**: Real Hebrew text from ETCBC DSS corpus integration
- **Word Analysis**: Only variant words shown with position and morphological data
- **File Naming**: Simplified to `book_dss.json` format
- **File Size**: Optimized (282 lines total vs 1084+ lines before)

## ⚠️ Important Notes

### Data Integrity
- **Read-only**: Raw DSS data should never be modified
- **Source Attribution**: Always credit original scholarly sources
- **Academic Use**: Materials for research and educational purposes

### Scholarly Context
- **Historical Value**: DSS date from ~250 BCE to 68 CE
- **Discovery**: Found in Qumran caves 1947-1956
- **Significance**: Oldest known Hebrew biblical manuscripts

---

*Last updated: December 30, 2025 (DSS variants without morphological analysis)*

*Dead Sea Scrolls research materials for the Davar Hebrew Scripture study app.*
