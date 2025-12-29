# Lexicon Generation Workflow

## 📁 Directory Structure

```
lexicon/
├── draft/              # WORK IN PROGRESS
│   ├── H7965.json      # ✅ Completed
│   ├── H7999.json      # ✅ Completed
│   ├── H1254.json      # ✅ Completed
│   └── H1234.json      # ⏳ In progress
│
└── final/              # FINALIZED LEXICON (when ready)
    ├── H7965.json
    ├── H7999.json
    └── ...
```

---

## 🔄 Workflow

### Step 1: Create entry in draft/

```bash
# Generate new lexicon entry
python3 scripts/generate_lexicon.py H7965
```

This creates `lexicon/draft/H7965.json` with:
- Basic Strong's data
- BDB definitions (if available)
- **Bilingual definitions (EN/ES)** in each entry
- Complete structure ready for review

### Step 2: Review and complete

1. **Verify BDB definitions**
   - Are they all included?
   - Are there duplicates?
   - Is anything missing?

2. **Verify Strong's definitions**
   - Are they parsed correctly?
   - Are there duplicates with BDB?
   - Do they all have Spanish translations?

3. **Verify root**
   - Is root identified correctly?
   - Are root definitions complete and bilingual?

4. **Verify occurrences**
   - Are references normalized to lowercase?
   - Is the total correct?

### Step 3: Move to final/

When the entry is complete and reviewed:

```bash
# Move from draft to final
mv lexicon/draft/H7965.json lexicon/final/H7965.json
```

---

## 📋 Review Checklist

Before moving from `draft/` to `final/`:

- [ ] All BDB definitions included
- [ ] All Strong's definitions included
- [ ] **Bilingual definitions (EN/ES)** in each entry
- [ ] No exact duplicates
- [ ] Root identified and complete
- [ ] Occurrences normalized (lowercase)
- [ ] Valid JSON structure
- [ ] Sources correctly marked (bdb, strongs)

---

## 🛠️ Helper Scripts

### Generate new entry

```python
# scripts/generate_lexicon.py
python3 generate_lexicon.py H7965
```

### Validate entry

```python
# scripts/validate_lexicon.py
python3 validate_lexicon.py lexicon/draft/H7965.json
```

### Compare with sources

```python
# scripts/compare_sources.py
python3 compare_sources.py H7965
```

---

## 📊 Current Status

### ✅ Completed (in draft/)
- H7965 (שָׁלוֹם) - 35 bilingual definitions (EN/ES)
- H7999 (שָׁלַם) - 31 bilingual definitions (EN/ES)
- H1254 (בָּרָא) - 9 bilingual definitions (EN/ES)

### ⏳ Pending
- Generate all remaining entries
- Review and validate
- Move to final/

---

## 🎯 Next Steps

1. Create bulk generation script
2. Validate all entries in draft/
3. Move validated entries to final/
4. Generate search index
