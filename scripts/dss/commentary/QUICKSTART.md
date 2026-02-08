# Quick Start Guide

## Prerequisites

1. Ensure you have the Anthropic API key in your `.env` file:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

2. Install required dependencies (if not already installed):
```bash
pip install anthropic python-dotenv tqdm
```

## Test Commands

### 1. Test with 5 samples (dry-run)
```bash
python -m scripts.dss.commentary.main --sample 5 --dry-run
```

This will:
- Load 5 sample differences from Genesis
- Send to Grok-4-1-fast-reasoning
- Show what would be generated
- **Not modify any files**

### 2. Test with 5 samples and save output
```bash
python -m scripts.dss.commentary.main --sample 5 --output-sample /tmp/dss_sample.json
```

This will:
- Process 5 differences
- Write enhanced data to DSSI files
- Save first 10 results to `/tmp/dss_sample.json` for review

### 3. Full production run (all 966 differences)
```bash
python -m scripts.dss.commentary.main
```

This will:
- Show cost estimate (~$1.15)
- Ask for confirmation
- Process all 966 differences in ~2 batches
- Update all DSSI book files
- Update metadata.json

## What to Check After Testing

1. **Review the sample output** at `/tmp/dss_sample.json`:
   - Check if `masoretic_strong` and `dss_strong` are assigned (format: "H####" or "H####,H####")
   - Verify `commentary_en`, `commentary_es`, `commentary_he` match the meditative tone
   - Confirm `original_commentary` is preserved

2. **Check DSSI book files** (e.g., `data/dss/dssi/books/genesis.json`):
   - Differences should have new fields added
   - Original structure should be maintained
   - Pretty formatting (indent=2) should be preserved

3. **Verify metadata** at `data/dss/dssi/metadata.json`:
   - `schema_version` should be "2.0"
   - `commentary_generation` section should be added with timestamp and stats

## Expected Output Structure

```json
{
  "position": 3,
  "masoretic_word": "יִקָּו֨וּ",
  "dss_word": "יקוו",
  "masoretic_strong": "H6960",
  "dss_strong": "H6960",
  "original_commentary": "4QGenb, Mas, LXX: be gathered. 4QGeng has the variant spelling יקאו...",
  "commentary_en": "The traditional Hebrew Tanaj text and several Qumran scrolls read this word the same way...",
  "commentary_es": "El texto hebreo tradicional de la Tanaj y varios rollos de Qumrán...",
  "commentary_he": "הטקסט העברי המסורתי של התנ\"ך...",
  "commentary_version": "v2_claude_2026"
}
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check `.env` file exists at project root
- Verify key is set: `ANTHROPIC_API_KEY=sk-ant-...`

### "ImportError: No module named 'anthropic'"
```bash
pip install anthropic
```

### Rate limit errors
- The script automatically retries with exponential backoff
- Grok-4 has high rate limits, should not be an issue

### JSON parsing errors
- The rewriter has 4 fallback strategies for parsing
- Check verbose logs: `--verbose` flag
- May indicate API response format change

## Cost Estimates

- **5 samples**: ~$0.01 (testing)
- **50 samples**: ~$0.10 (validation)
- **966 differences**: ~$1.15 (full run)

Pricing: claude-haiku-4-5 @ $1/1M input, $5/1M output
