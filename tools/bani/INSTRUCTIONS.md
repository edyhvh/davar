# LLM Instructions for Bani Schema Generation (v2.0)

You are an expert linguist specializing in **academic Hebrew and Aramaic transliteration systems** for **[TARGET LANGUAGE]** speakers. Your task is to create a complete transliteration schema based on established academic standards (SBL General Purpose and Brill simplified) that allows **[TARGET LANGUAGE]** speakers to accurately read and pronounce Biblical Hebrew and Aramaic words.

## ACADEMIC FOUNDATION

This schema generation is based on two major academic transliteration systems:

### SBL General Purpose
- **Source**: Society of Biblical Literature Handbook of Style (2nd edition)
- **Style**: Simplified academic transliteration
- **Features**: Vocal sheva as "e", simple characters, no qamats qatan distinction
- **Use case**: General academic work, easier for beginners

### Brill Simplified
- **Source**: Brill's Encyclopaedia of Hebrew Language and Linguistics
- **Style**: More academic with additional distinctions
- **Features**: Vocal sheva as "ᵉ" (superscript), special characters (ḥ), qamats qatan distinction
- **Use case**: Advanced academic work, scholarly publications

## CRITICAL: Output Format Requirements

You must output **ONLY** a valid JSON object with **NO** additional text, comments, markdown, or explanations. The JSON must contain only the fields listed below.

## REQUIRED FIELDS TO FILL

Fill **ALL** of these fields with appropriate values for **[TARGET LANGUAGE]**:

### 1. Style Section (Enhanced v2.0)
```json
{
  "style": {
    "name_native": "Transliteración Académica del Hebreo",  // Natural academic name in target language
    "description": "Sistema de transliteración académica basado en estándares SBL y Brill para pronunciar palabras hebreas y arameas bíblicas. Sílaba tónica en MAYÚSCULAS.",  // 1-2 sentences describing academic nature
    "system": "sbl_general_purpose",  // Choose: "sbl_general_purpose" or "brill_simplified"
    "strict": false,  // true|false - strict academic compliance
    "dagesh": true,   // true|false - distinguish spirantized/plosive
    "qamatz_qatan": false,  // true|false - distinguish qamats qatan (usually false for simplicity)
    "sheva": "vocal"  // vocal|simple - sheva pronunciation
  }
}
```

**System Selection Guidelines:**
- **`"sbl_general_purpose"`**: Recommended for general users, informal systems, educational contexts
- **`"brill_simplified"`**: Recommended for academic work, scholarly publications, advanced learners
- **`"qamatz_qatan": true`**: Only enable if target language needs to distinguish this vowel (rare)
- **`"strict": true`**: Enable for academic compliance, disable for user-friendly systems

### 2. Rules Section - Consonants (MANDATORY - ALL 27 required)
```json
{
  "rules": {
    "consonants": {
      // BASE MAPPINGS (without dagesh) - CRITICAL for proper spirantization
      "א": "",     // Silent aleph
      "ב": "v",    // Vet (base) - becomes "b" with dagesh
      "ג": "g",    // Gimel (no dagesh change in standard Hebrew)
      "ד": "d",    // Dalet (no dagesh change in standard Hebrew)
      "ה": "h",    // He
      "ו": "v",    // Vav (consonantal)
      "ז": "z",    // Zayin
      "ח": "kh",   // Het (SBL) or "ḥ" (Brill)
      "ט": "t",    // Tet
      "י": "y",    // Yod (consonantal)
      "כ": "kh",   // Kaf (base) - becomes "k" with dagesh
      "ל": "l",    // Lamed
      "מ": "m",    // Mem
      "נ": "n",    // Nun
      "ס": "s",    // Samekh
      "ע": "",     // Ayin (SBL: silent) or "'" (Brill: glottal stop)
      "פ": "f",    // Pe (base) - becomes "p" with dagesh
      "צ": "ts",   // Tzadi (or "tz" in Brill)
      "ק": "q",    // Qof
      "ר": "r",    // Resh
      "ש": "sh",   // Shin (both שׁ and שׂ in simplified systems)
      "ת": "t",    // Tav

      // Final forms (same as regular except dagesh-affected)
      "ך": "kh",   // Kaf sofit
      "ם": "m",    // Mem sofit
      "ן": "n",    // Nun sofit
      "ף": "f",    // Pe sofit
      "ץ": "ts"    // Tzadi sofit
    }
  }
}
```

### 3. Rules Section - Vowels (MANDATORY - ALL 9 required + system variants)
```json
{
  "rules": {
    "vowels_nikud": {
      // STANDARD MAPPINGS (SBL General Purpose)
      "ָ": "a",    // Qamats
      "ַ": "a",    // Patah
      "ֵ": "e",    // Tsere
      "ֶ": "e",    // Segol
      "ִ": "i",    // Hiriq
      "ֹ": "o",    // Holam
      "ֻ": "u",    // Qubuts
      "וּ": "u",    // Shuruq
      "ְ": "e"     // Vocal sheva (SBL) or "ᵉ" (Brill superscript)
    },
    "composite": {
      // DIPHTHONGS (optional but recommended)
      "וֹ": "o",   // Vav + holam
      "וּ": "u",   // Vav + shuruq
      "יִ": "i",   // Yod + hiriq
      "ֵי": "e",   // Tsere + yod
      "ֶי": "e",   // Segol + yod
      "ָי": "a",   // Qamats + yod
      "ַי": "a",   // Patah + yod
      "ִי": "i",   // Hiriq + yod
      "ֹי": "o",   // Holam + yod
      "ֻי": "u"    // Qubuts + yod
    }
  }
}
```

**System-Specific Adaptations:**
- **SBL General Purpose**: Use simple characters, vocal sheva as `"e"`
- **Brill Simplified**: Use `"ᵉ"` for vocal sheva, `"ḥ"` for het, `"tz"` for tzadi, `"'` for ayin

### 4. Rules Section - Composite (OPTIONAL - only if needed)
```json
{
  "rules": {
    "composite": {
      "וֹ": "", "וּ": "", "יִ": "", "ֵי": ""
    }
  }
}
```

### 5. Examples Section (MANDATORY - ALL 27 examples required)
```json
{
  "examples": {
    "H1": {
      "translit": "av",           // Complete transliteration
      "guide": "AV",              // With CAPITALS on stressed syllable
      "guide_full": {
        "reference": "padre",     // Common everyday word
        "stress_note": "stress on AV",
        "phonetic_notes": ["Simple transliteration"]
      }
    }
    // ... ALL 27 examples must be filled (H1 through H24)
  }
}
```

**IMPORTANT**: When generating transliterations for examples, prefer Hebrew words with **two or more syllables** whenever possible. This better demonstrates the stress marking system with CAPITALS. Single-syllable words are acceptable only when necessary (e.g., for certain Hebrew letters that primarily appear in monosyllabic words).

## LANGUAGE-SPECIFIC RULES FOR [TARGET LANGUAGE]

### Spanish (es) - SBL General Purpose Recommended:
- **System**: `"sbl_general_purpose"` (user-friendly, educational)
- **ח (chet)** → `"j"` (like Spanish "jamón")
- **ע (ayin)** → `""` (silent, SBL style)
- **ש (shin)** → `"sh"` (like English "show")
- **ג (gimel)** → `"g"` (always hard, like "gato")
- **ז (zayin)** → `"s"` (like "rosa")
- **צ (tzadi)** → `"ts"` (like "pizza")
- **ץ (tzadi sofit)** → `"ts"` (same as regular tzadi)
- **ך (kaf sofit)** → `"j"` (Spanish adaptation, matches base כ)
- **כ (kaf base)** → `"j"` (Spanish-friendly, becomes "k" with dagesh)
- **פ (pe base)** → `"f"` (becomes "p" with dagesh)

### Spanish Vowels (SBL style):
- **ָ (qamats)** → `"a"` (like "padre")
- **ַ (patah)** → `"a"` (like "cama")
- **ֵ (tsere)** → `"e"` (like "mesa")
- **ֶ (segol)** → `"e"` (like "perro")
- **ִ (hiriq)** → `"i"` (like "mira")
- **ֹ (holam)** → `"o"` (like "lobo")
- **ֻ (qubuts)** → `"u"` (like "luna")
- **וּ (shuruq)** → `"u"` (like "luna")
- **ְ (sheva)** → `"e"` (vocal, informal style)

### English (en) - Brill Simplified Recommended:
- **System**: `"brill_simplified"` (academic standard)
- **ח (chet)** → `"ḥ"` (dot under, academic)
- **ע (ayin)** → `"'"` (apostrophe, glottal stop)
- **צ (tzadi)** → `"tz"` (Brill style)
- **ְ (sheva)** → `"ᵉ"` (superscript, academic)

### Other Languages:
- **Portuguese (pt)**: Similar to Spanish, use `"sbl_general_purpose"`
- **French (fr)**: Use `"brill_simplified"` for academic contexts
- **German (de)**: Use `"brill_simplified"` with careful vowel adaptations
- **Italian (it)**: Use `"sbl_general_purpose"` with Italian phonetics

## STRESS AND GUIDE RULES

1. **Never change** the `stress_syllable` values provided in the template
2. **guide** = transliteration with **UPPERCASE** letters on the stressed syllable, **separated by hyphens (-)** between syllables. Example: "sha-LOM" for שָׁלוֹם
3. **reference** words must be extremely common, everyday words in the target language
4. **phonetic_notes** should be 1-2 very brief, helpful notes about pronunciation
5. **Word length preference**: When selecting Hebrew words for examples, prioritize words with **two or more syllables** to better demonstrate the stress marking system. Single-syllable words should only be used when necessary (e.g., for Hebrew letters that primarily appear in monosyllabic words).

## WORKFLOW: STRONG'S REFERENCE DATA INTEGRATION

The schema includes a `workflow` section that defines how to leverage Strong's reference data (`pron` and `xlit` fields from `strongs.json`) to improve transliteration accuracy:

### Workflow Configuration

```json
{
  "workflow": {
    "use_strongs_reference": true,
    "pron_parsing": {
      "enabled": true,
      "syllable_separator": "-",
      "stress_marker": "'",
      "description": "Parse 'pron' field to extract syllable boundaries and stress position."
    },
    "xlit_reference": {
      "enabled": true,
      "description": "Use 'xlit' field as reference for pronunciation patterns."
    },
    "validation_mode": "strict",
    "fallback_behavior": "use_generated"
  }
}
```

### How It Works

1. **`pron` Field Parsing** (when `pron_parsing.enabled: true`):
   - The `pron` field from `strongs.json` contains syllable boundaries separated by hyphens (`-`) and stress marked with an apostrophe (`'`)
   - Example: `"pron": "ter-oo-aw'"` indicates 3 syllables with stress on the last syllable
   - The transliteration script should parse this to extract:
     - Number of syllables
     - Position of stressed syllable
     - Approximate syllable boundaries

2. **`xlit` Field Reference** (when `xlit_reference.enabled: true`):
   - The `xlit` field contains academic transliteration (often using standard conventions)
   - Use this as a reference for pronunciation patterns, but adapt to target language phonetics according to schema rules
   - Example: `"xlit": "tᵉrûʿâ"` can inform the transliteration but should be adapted to Spanish phonetics

3. **Fallback Behavior**:
   - When `pron` or `xlit` are unavailable or invalid, fall back to rule-based generation using schema defaults
   - The `fallback_behavior` setting determines what happens: `"use_generated"` (default), `"skip"`, or `"error"`

### Implementation Notes

- Scripts generating transliterations should **always check** for `pron` and `xlit` fields in `strongs.json`
- When `pron` is available, use it to determine syllable boundaries and stress position instead of rule-based splitting
- When `xlit` is available, use it as a reference but adapt to target language phonetics
- This workflow prevents common errors like incorrect stress placement or syllable division

## ACADEMIC TRANSLITERATION FEATURES (v2.0)

### DAGHESH HANDLING (CRITICAL FOR ACCURACY)

Hebrew consonants undergo spirantization based on dagesh (ּ). The script automatically handles this transformation, but schemas must define BASE mappings correctly:

#### Dagesh Forte (Strong) Rules - Spirantization/Plosivization:
- **ב (bet)**: `"ב": "v"` (base, spirantized) → with dagesh: `"b"` (plosive)
- **כ (kaf)**: `"כ": "kh"` (base, spirantized) → with dagesh: `"k"` (plosive)
- **פ (pe)**: `"פ": "f"` (base, spirantized) → with dagesh: `"p"` (plosive)
- **ג (gimel)**: `"ג": "g"` (no change, always plosive in standard Hebrew)
- **ד (dalet)**: `"ד": "d"` (no change, always plosive in standard Hebrew)
- **ת (tav)**: `"ת": "t"` (no change, always plosive in standard Hebrew)

#### Base Mappings (Without Dagesh - Academic Standard):
```json
"consonants": {
  "ב": "v", "כ": "kh", "פ": "f",  // Spirantized forms (SBL/Brill standard)
  "ג": "g", "ד": "d", "ת": "t",    // Always plosive
  // ... other consonants
}
```

#### Why This Matters:
- **Incorrect**: `"פ": "p"` always → wrong pronunciation for 80% of cases
- **Correct**: `"פ": "f"` base → script applies dagesh rules automatically
- Affects ~15-20% of Biblical Hebrew words with major impact on accuracy

### QAMATS QATAN DISTINCTION (Advanced Feature)

Some systems distinguish qamats (ָ) from qamats qatan (narrow o sound):

#### When to Enable (`"qamatz_qatan": true`):
- **Brill Simplified**: Requires distinction
- **Academic contexts**: When precision matters
- **Languages needing /o/ vs /a/ distinction**: German, some Arabic-influenced systems

#### When to Disable (`"qamatz_qatan": false`):
- **SBL General Purpose**: Simplified, merges to `"a"`
- **User-friendly systems**: Easier for beginners
- **Most Romance languages**: Spanish, Portuguese, French, Italian

#### Implementation:
```json
"rules": {
  "vowels_nikud": {
    "ָ": "a",      // Regular qamats
    "QAMATS_QATAN": "o"  // Only when qamatz_qatan enabled
  }
}
```

## SHEVA CONFIGURATION (System-Dependent)

The sheva (ְ) pronunciation varies by transliteration system:

#### SBL General Purpose:
- **`"sheva": "vocal"`**: Sheva becomes `"e"` (recommended for user-friendly systems)
- **`"sheva": "simple"`**: Sheva becomes `""` (silent, more academic)

#### Brill Simplified:
- **Always use `"ᵉ"`** (superscript) for vocal sheva (system requirement)
- This provides the academic distinction preferred in scholarly work

**System Recommendations:**
- **SBL General Purpose**: `"vocal"` for informal, `"simple"` for academic
- **Brill Simplified**: Always use superscript `"ᵉ"` for vocal sheva

## SCHEMA VALIDATION REQUIREMENTS (v2.0 Enhanced)

### Mandatory Validations:
1. **All 27 consonants present**: א,ב,ג,ד,ה,ו,ז,ח,ט,י,כ,ל,מ,נ,ס,ע,פ,צ,ק,ר,ש,ת,ך,ם,ן,ף,ץ
2. **All 9 vowels present**: ָ,ַ,ֵ,ֶ,ִ,ֹ,ֻ,וּ,ְ
3. **Silent consonants**: א and ע must map to `""` (SBL) or `"'"` (Brill)
4. **Dagesh-affected letters**: Base mappings must use spirantized forms (v, kh, f)
5. **System selection**: Must specify `"system": "sbl_general_purpose"` or `"brill_simplified"`
6. **Sheva configuration**: Must match selected system (SBL: "e"/"", Brill: "ᵉ")
7. **At least 22 examples**: Covering all consonants with diverse words
8. **Workflow section**: Must include complete workflow configuration
9. **Style section**: Must include system selection and configuration flags

### System-Specific Validations:

#### SBL General Purpose:
- ✅ `"system": "sbl_general_purpose"`
- ✅ `"qamatz_qatan": false` (recommended)
- ✅ Simple characters: `"kh"`, `"ts"`, `""` for ayin
- ✅ Sheva: `"e"` or `""`

#### Brill Simplified:
- ✅ `"system": "brill_simplified"`
- ✅ Can use `"qamatz_qatan": true`
- ✅ Special characters: `"ḥ"`, `"tz"`, `"'"` for ayin
- ✅ Sheva: `"ᵉ"` (superscript required)

### Example Validation Errors (v2.0):
- ❌ Missing `"system"` field
- ❌ `"פ": "p"` (should be `"f"` for base mapping)
- ❌ `"א": "a"` (should be `""` for silent aleph)
- ❌ `"ḥ"` used with SBL system (should be `"kh"`)
- ❌ `"e"` sheva with Brill system (should be `"ᵉ"`)
- ❌ Missing workflow configuration

## DIGRAPH PROTECTION (CRITICAL FOR SYLLABLE ACCURACY)

Hebrew transliteration uses compound sounds (digraphs) that must stay together during syllable division:

### Protected Digraphs:
- **`"sh"`**: shin (שׁ) - never split as `"s"` + `"h"`
- **`"ts"`**: tzadi (צ) - never split as `"t"` + `"s"`
- **`"ch"`**: chet (ח) - never split as `"c"` + `"h"`
- **`"kh"`**: kaf (כ) with dagesh - never split as `"k"` + `"h"`
- **`"ph"`**: pe (פ) with dagesh - never split as `"p"` + `"h"`
- **`"th"`**: tav (ת) with dagesh - never split as `"t"` + `"h"`

### Example Corrections:
- **Before**: `"ashur"` → `"as-hur"` ❌ (incorrectly splits "sh")
- **After**: `"ashur"` → `"a-shur"` ✅ (preserves "sh" as unit)

### Implementation:
The script automatically protects digraphs during syllable splitting to prevent phonetic errors.

## PRON ALIGNMENT (ADVANCED SYLLABLE DIVISION)

When Strong's `pron` field is available, the script attempts intelligent alignment between phonetic pronunciation and transliteration:

### Alignment Logic:
1. **Normalize pron syllables**: `"aw"` → `"a"`, `"oo"` → `"u"`, `"maw"` → `"mah"`, etc.
2. **Exact substring matching**: Try to match pron syllables directly in transliteration
3. **Fuzzy phonetic matching**: Handle common Hebrew patterns (final ה becomes silent, etc.)
4. **Text continuation**: Add remaining text to final syllable when alignment is partial
5. **Fallback to basic splitting**: If alignment fails, uses rule-based syllable division

### Examples:

**Example 1 - Direct alignment:**
- **Word**: אָשֻׁר (ashur)
- **Pron**: `"aw-shoor'"`
- **Normalized**: `["a", "shur"]`
- **Result**: `"a-SHUR"` (2 syllables, stress on second)

**Example 2 - Text continuation:**
- **Word**: אַשְׁמָה (ashmah)
- **Pron**: `"ash-maw'"`
- **Normalized**: `["ash", "mah"]`
- **Result**: `"ash-MAH"` (2 syllables, stress on second)
- **Logic**: Matches `"ash"` exactly, adds remaining `"h"` to `"ma"` → `"mah"`

**Example 3 - Fuzzy matching:**
- **Word**: אֶשְׁכּוֹל (eshkol)
- **Pron**: `"esh-kole'"`
- **Normalized**: `["esh", "kol"]`
- **Result**: `"esh-KOL"` (2 syllables, stress on second)

**Example 4 - Digraph-aware fallback:**
- **Word**: אֵשֶׁל (eshel)
- **Pron**: `"ay'-shel"` (alignment fails)
- **Digraph-aware**: Detects `"sh"` digraph → splits as `["e", "shel"]`
- **Result**: `"E-shel"` (2 syllables, stress on first per pron)

## POST-PROCESSING RULES

The `post_processing` array defines cleanup operations applied in order:

```json
"post_processing": [
  "remove_duplicate_consonants",
  "apply_stress_uppercase",  // Handled by guide generation
  "lowercase_rest"
]
```

### Available Operations:
- `"remove_duplicate_consonants"`: Converts `"bb"`, `"kk"`, `"pp"` to single letters
- `"lowercase_rest"`: Ensures transliteration is lowercase except for stress guides
- `"apply_stress_uppercase"`: Automatically handled in guide generation (do not include in array)

## STRONG'S INTEGRATION BEST PRACTICES

### Pron Field Parsing:
- **Format**: `"syl-la-ble'` where `'` marks stressed syllable
- **Example**: `"pron": "tef-il-law'"` → 3 syllables, stress on 3rd
- **Fallback**: When pron unavailable, use rule-based syllable splitting

### Xlit Field Usage:
- **Purpose**: Academic transliteration reference
- **Example**: `"xlit": "tᵉphillâh"` informs but doesn't override schema rules
- **Adaptation**: Always adapt to target language phonetics

### Validation Modes:
- `"strict"`: Fail on any data inconsistency
- `"lenient"`: Warn but continue processing

## QUALITY ASSURANCE

- Every consonant and vowel mapping must have a non-empty string value (except silent consonants)
- Every example must have translit, guide, and guide_full completed
- Use only the target language for all text content
- Ensure phonetic accuracy for native speakers
- Test with diverse Hebrew words including those with/without dagesh
- Verify sheva configuration produces natural pronunciation
- Validate that Strong's integration improves rather than confuses results

## EXAMPLE OUTPUT STRUCTURE (v2.0)

```json
{
  "schema_version": "2.0.0",
  "language": {
    "code": "es",
    "name": "Spanish",
    "variant": "neutral"
  },
  "style": {
    "name": "Academic Spanish Transliteration",
    "name_native": "Transliteración Académica del Hebreo",
    "description": "Sistema de transliteración académica basado en estándares SBL y Brill para pronunciar palabras hebreas y arameas bíblicas. Sílaba tónica en MAYÚSCULAS.",
    "system": "sbl_general_purpose",
    "strict": false,
    "dagesh": true,
    "qamatz_qatan": false,
    "sheva": "vocal",
    "stress_mark": "uppercase"
  },
  "rules": {
    "consonants": {
      "א": "", "ב": "v", "ג": "g", "ד": "d", "ה": "h", "ו": "v", "ז": "s",
      "ח": "j", "ט": "t", "י": "y", "כ": "j", "ל": "l", "מ": "m", "נ": "n",
      "ס": "s", "ע": "", "פ": "f", "צ": "ts", "ק": "k", "ר": "r", "ש": "sh", "ת": "t",
      "ך": "j", "ם": "m", "ן": "n", "ף": "f", "ץ": "ts"
    },
    "vowels_nikud": {
      "ָ": "a", "ַ": "a", "ֵ": "e", "ֶ": "e", "ִ": "i", "ֹ": "o", "ֻ": "u", "וּ": "u", "ְ": "e"
    },
    "composite": {
      "וֹ": "o", "וּ": "u", "יִ": "i", "ֵי": "e", "ֶי": "e", "ָי": "a", "ַי": "a"
    },
    "post_processing": [
      "apply_dagesh_rules",
      "normalize_composites",
      "remove_duplicate_consonants",
      "lowercase_rest"
    ]
  },
  "stress": {
    "default": "penultimate",
    "exceptions": {
      "H7965": 2,
      "H1697": 2,
      "H3444": 3,
      "H2617": 1
    }
  },
  "workflow": {
    "use_strongs_reference": true,
    "pron_parsing": {
      "enabled": true,
      "syllable_separator": "-",
      "stress_marker": "'",
      "description": "Parse 'pron' field to extract syllable boundaries and stress position. Format: 'syl1-syl2-syl3' where ' marks stressed syllable."
    },
    "xlit_reference": {
      "enabled": true,
      "description": "Use 'xlit' field as reference for pronunciation patterns, but adapt to target language phonetics according to schema rules."
    },
    "validation_mode": "strict",
    "fallback_behavior": "use_generated",
    "description": "When 'pron' is available, intelligent alignment attempts to match pron syllables with transliteration. Handles normalization (aw→a, maw→mah) and text continuation. Falls back to rule-based generation if alignment fails."
  },
  "examples": {
    "H1": {
      "hebrew": "אָבִיב",
      "translit": "aviv",
      "stress_syllable": 2,
      "guide": "a-VIV",
      "guide_full": {
        "reference": "primavera",
        "stress_note": "acento en VIV",
        "phonetic_notes": ["א omitida (aleph muda)"]
      }
    },
    "H8": {
      "hebrew": "חַיִּים",
      "translit": "jaiyim",
      "stress_syllable": 2,
      "guide": "jai-YIM",
      "guide_full": {
        "reference": "vida",
        "stress_note": "acento en YIM",
        "phonetic_notes": ["ח suena como 'j' (jamón)", "יִ diptongo conservado"]
      }
    },
    "H21": {
      "hebrew": "שָׁלוֹם",
      "translit": "shalom",
      "stress_syllable": 2,
      "guide": "sha-LOM",
      "guide_full": {
        "reference": "paz",
        "stress_note": "acento en LOM",
        "phonetic_notes": ["שׁ suena como 'sh'", "ֹו diptongo holam-vav"]
      }
    }
  },
  "llm_data": {
    "prompt_template": "Guide with stress in CAPITALS: {translit} → {guide}",
    "guturals_note": "ח = [j/gutural sound], ע = omit or glottal pause",
    "shva_note": "ְ = very light 'e' sound (vocal sheva)",
    "digraph_note": "IMPORTANT: sh, ts, j must stay together during syllable splitting",
    "sbl_brill_note": "Based on SBL General Purpose and Brill simplified transliteration systems"
  },
  "validation": {
    "status": "approved",
    "reviewer": "system",
    "reviewed_at": "2025-11-14",
    "based_on": "SBL General Purpose and Brill simplified from hebrew-transliteration library"
  }
}
```

Remember: Output **ONLY** the JSON object. No introductions, no explanations, no markdown formatting.