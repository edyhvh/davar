# Generador de Versículos Ligeros

Script para generar archivos JSON de versículos ligeros según el formato especificado en `HYBRID_SYSTEM_EXPLANATION.md`.

## Uso

```bash
cd data/dict
python3 generate_verses.py
```

## Descripción

El script procesa todos los libros disponibles en `data/oe/` y genera archivos JSON individuales para cada versículo en `data/dict/verses/`.

### Fuentes de datos

1. **Texto hebreo y morfología**: `data/oe/{book}/{chapter}.json`
2. **Texto en inglés (TS2009)**: `data/ts2009/{book}/{chapter}.json` (opcional, no incluido en el output actual)
3. **Texto en español (TTH)**: `data/tth/draft/{book}/{chapter}.json` (si está disponible)

### Formato de salida

Cada versículo se guarda como `{book}.{chapter}.{verse}.json` en `data/dict/verses/`.

Ejemplo: `gen.1.1.json`

### Estructura del archivo generado

```json
{
  "reference": "gen.1.1",
  "book": {
    "es": "Génesis",
    "en": "Genesis",
    "heb": "בְּרֵאשִׁית"
  },
  "chapter": 1,
  "verse": 1,
  "hebrew_text": "בְּרֵאשִׁית בָּרָא אֱלֹהִים...",
  "spanish_text": "Con lo primero le dio forma...",
  "words": [
    {
      "position": 1,
      "hebrew": "בְּרֵאשִׁית",
      "lexicon_ref": "H7225",
      "morphology": "HR/Ncfsa"
    }
  ],
  "metadata": {
    "has_qumran_variants": false,
    "has_cross_references": false
  }
}
```

## Notas

- Los archivos se generan en formato lowercase para normalización (ej: `gen.1.1` en lugar de `Gen.1.1`)
- Las referencias al lexicon usan números Strong's (ej: `H7965`)
- El texto español se obtiene de TTH cuando está disponible
- Los metadatos de variantes Qumran y referencias cruzadas se establecen en `false` por defecto (se pueden actualizar después)


