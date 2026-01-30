# DSS Commentary Enhancement

Claude-powered tool to enhance Dead Sea Scrolls variant commentaries with Strong's numbers and trilingual meditative explanations.

## Overview

This module processes 966 textual differences from the DSSI (Dead Sea Insights) dataset, using Claude Haiku 4.5 to:

1. **Assign Strong's numbers** to Hebrew words (both Masoretic and DSS variants)
2. **Generate reverent commentaries** in 3 languages (English, Spanish, Hebrew)
3. **Preserve original scholarship** while making it accessible

## Features

- **Batch processing**: Handles 966 differences in 1-2 API calls (~$1.15)
- **Robust JSON parsing**: Multiple fallback strategies for API response handling
- **Progress tracking**: Real-time statistics and cost estimation
- **Dry-run mode**: Preview changes before committing
- **Sample testing**: Test with small batches (5-10 entries)
- **Automatic retries**: Handles rate limits and transient failures

## Requirements

```bash
pip install anthropic python-dotenv tqdm
```

Set your Anthropic API key in `.env`:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Test with samples (recommended first)
```bash
# Test with 5 differences (dry run)
python -m scripts.dss.commentary.main --sample 5 --dry-run

# Test with 5 differences and save output
python -m scripts.dss.commentary.main --sample 5 --output-sample sample_output.json
```

### Process all 966 differences
```bash
# Preview changes
python -m scripts.dss.commentary.main --dry-run

# Full production run
python -m scripts.dss.commentary.main
```

### Advanced options
```bash
# Custom batch size
python -m scripts.dss.commentary.main --batch-size 250

# Verbose logging
python -m scripts.dss.commentary.main --verbose --sample 10
```

## Output Format

Each difference is enhanced with:

```json
{
  "position": 3,
  "masoretic_word": "יִקָּו֨וּ",
  "dss_word": "יקוו",
  "masoretic_strong": "H6960",
  "dss_strong": "H6960",
  "original_commentary": "4QGenb, Mas, LXX: be gathered...",
  "commentary_en": "The traditional Hebrew Tanaj text and several Qumran scrolls...",
  "commentary_es": "El texto hebreo tradicional de la Tanaj y varios rollos de Qumrán...",
  "commentary_he": "הטקסט העברי המסורתי של התנ\"ך וכמה מגילות מקומראן...",
  "commentary_version": "v2_claude_2026"
}
```

## Model Details

- **Model**: `claude-haiku-4-5-20251001`
- **Purpose**: Fast, near-frontier intelligence with extended thinking for Strong's assignment
- **Cost**: ~$1.15 for all 966 differences ($1/1M input, $5/1M output)
- **Time**: ~10-15 minutes for full processing (2x faster than Sonnet 4)

## Architecture

```
commentary/
├── __init__.py       # Module exports
├── config.py         # XAI configuration
├── loader.py         # Load DSSI differences
├── rewriter.py       # XAI Grok integration
├── writer.py         # Update JSON files
└── main.py           # CLI orchestrator
```

## Quality Standards

- **Strong's accuracy**: Target 99%+ (leveraging reasoning model)
- **Commentary tone**: Meditative, reverent, accessible
- **Language quality**: Natural expression in all 3 languages
- **Preservation**: Original commentaries maintained in `original_commentary` field

## Workflow

1. Load all DSSI book files from `data/dss/dssi/books/`
2. Flatten differences into processable list (966 entries)
3. Split into batches of ~500 for API calls
4. Send to Grok with system prompt + structured request
5. Parse JSON responses with robust extraction
6. Write enhanced data back to source files
7. Update metadata with processing stats

## Error Handling

- **Rate limits**: Automatic retry with exponential backoff
- **JSON parsing**: Multiple fallback strategies (direct, markdown, bracket-matching, regex)
- **API failures**: Up to 3 retries per batch
- **Partial success**: Continue processing remaining batches

## Example Session

```bash
$ python -m scripts.dss.commentary.main --sample 5

Checking Anthropic API key...
Using model: claude-haiku-4-5-20251001
Loading DSSI differences...
Loaded 5 sample differences

============================================================
COST ESTIMATE
============================================================
Total differences: 5
Batch size: 500
Number of batches: 1
Estimated tokens: ~2,500 (1,500 in, 1,000 out)
Estimated cost: ~$0.01 ($0.0015 in, $0.0050 out)
============================================================

Initializing Claude rewriter...
Processing 1 batch(es)...

============================================================
BATCH 1/1 (5 differences)
============================================================
Making API call to claude-haiku-4-5-20251001 with 5 differences
API call completed
Successfully processed 5 differences
✓ Batch 1 completed successfully

============================================================
PROCESSING STATISTICS
============================================================
Total batches: 1
Total differences: 5
Successful: 5
Failed: 0
Success rate: 100.0%
============================================================

Writing enhanced differences to DSSI files...
Updated 1 books
Updated 5 differences

Updating metadata...

✓ Processing completed successfully!
```

## Notes

- First run should be with `--sample 5 --dry-run` to validate output
- Review sample output for Strong's accuracy and commentary quality
- Full run requires user confirmation (unless `--sample` or `--dry-run`)
- Enhanced files maintain pretty formatting (indent=2)
- Metadata updated with timestamp, model, and token stats

## License

Part of the Davar (דבר) project - Minimalist Hebrew Bible Study App
