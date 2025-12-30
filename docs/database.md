# Esquema de Base de Datos - Davar

Diagrama ER del esquema de base de datos PostgreSQL con UUIDs, enums y campos JSONB.

```mermaid
erDiagram
    BOOKS ||--o{ CHAPTERS : contains
    CHAPTERS ||--o{ VERSES : contains
    VERSES ||--o{ WORDS : contains
    VERSES ||--o{ TRANSLATIONS : has
    VERSES ||--o{ VARIANTS : has
    LEXICON ||--o{ DEFINITIONS : has
    WORDS }o--|| LEXICON : references

    BOOKS {
        uuid id PK
        string name
        string hebrew_name
        string english_name
        string spanish_name
        enum section
        string author
        string publication_year
    }

    CHAPTERS {
        uuid id PK
        uuid book_id FK
        int number
        string hebrew_letter
    }

    VERSES {
        uuid id PK
        uuid chapter_id FK
        int number
        text hebrew_text
        text hebrew_no_nikud
        jsonb source_files
        jsonb visual_uncertainty
    }

    WORDS {
        uuid id PK
        uuid verse_id FK
        int position
        text hebrew
        text hebrew_no_nikud
        string lemma
        string strong_number
        string morph
    }

    LEXICON {
        string strong_number PK
        text lemma
        text normalized
        text pronunciation
        text transliteration
        boolean is_root
        string root_ref FK
        jsonb sources
        jsonb occurrences
    }

    DEFINITIONS {
        uuid id PK
        string lexicon_strong_number FK
        text text
        string source
        int order
        string sense
    }

    TRANSLATIONS {
        uuid id PK
        uuid verse_id FK
        enum language
        string version
        text text
        enum status
        jsonb footnotes
    }

    VARIANTS {
        uuid id PK
        uuid verse_id FK
        enum source
        text variant_text
        text explanation
    }
```

## Enums

- `book_section`: `torah`, `neviim`, `ketuvim`, `besorah`
- `translation_language`: `en`, `es`
- `translation_status`: `present`, `absent`
- `variant_source`: `qumran`, `masoretic`, `septuagint`

## Extensiones PostgreSQL

- `uuid-ossp`: Para generar UUIDs automáticamente

## Notas

- Todas las tablas usan UUID como primary key (excepto LEXICON que usa `strong_number`)
- Los campos JSONB permiten almacenar estructuras flexibles (source_files, visual_uncertainty, sources, occurrences, footnotes)
- Las relaciones FK mantienen integridad referencial entre entidades




