# Lexicon Translation Module

Translation system for adding multilingual definitions to the Davar lexicon dictionary using xAI's Grok API (grok-4 model).

## Overview

This module translates English definitions in `roots.json` and `words.json` to target languages, updating the JSON structure from `text` to `text_en` and adding language-specific fields like `text_es` (Spanish), `text_pt` (Portuguese), etc.

## Features

- **Grok-4 Model**: Uses xAI's most advanced and fastest model
- **Language-agnostic**: Supports multiple languages via CLI option
- **Batch processing**: Efficiently translates multiple definitions per API call
- **Single entry processing**: Test or translate individual words/roots by Strong's number
- **Error handling**: Retry logic with exponential backoff
- **Progress tracking**: Detailed logging and statistics
- **Dry run mode**: Preview changes without saving

## Setup

### 1. Install Dependencies

```bash
pip install openai
```

The module requires:
- `openai>=1.0.0` - OpenAI-compatible SDK for Grok API
- `python-dotenv` - Environment variable management (already in requirements.txt)

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
XAI_API_KEY=your_api_key_here
```

Get your API key from [xAI Console](https://console.x.ai/team/default/api-keys).

## Usage

### Basic Usage

```bash
# Translate all entries to Spanish (default)
python -m scripts.dict.translation.main

# Translate to Portuguese
python -m scripts.dict.translation.main --language pt

# Process only roots.json
python -m scripts.dict.translation.main --file roots --language es

# Process only words.json
python -m scripts.dict.translation.main --file words --language es
```

### Single Entry Processing

```bash
# Translate single entry by Strong's number
python -m scripts.dict.translation.main --strong-number H1 --language es
```

### Dry Run Mode

```bash
# Preview changes without saving
python -m scripts.dict.translation.main --dry-run --strong-number H10
```

## API Details

### Endpoint
- **Base URL**: `https://api.x.ai/v1`
- **Endpoint**: `/v1/responses`
- **Model**: `grok-4`

### Cost Comparison

| Dataset | grok-4 Cost | Notes |
|---------|-------------|-------|
| **27,930 definitions** | ~$0.38 | Full translation |
| **H1 (14 definitions)** | ~$0.0001 | Test entry |

### Pricing (as of 2026-01-06)
- **grok-4**: $0.10/1M input tokens, $0.30/1M output tokens

## Supported Languages

- **es**: Spanish
- **pt**: Portuguese
- **fr**: French
- **de**: German
- **it**: Italian
- **ar**: Arabic
- **fa**: Farsi

## Architecture

The translation system consists of:

- **`config.py`**: Configuration and API key management
- **`translator.py`**: GrokTranslator class for API communication
- **`processor.py`**: LexiconProcessor for file processing and orchestration
- **`main.py`**: CLI interface and argument parsing

## Error Handling

The system handles:
- **API Key Missing**: Clear error message with setup instructions
- **Rate Limiting**: Automatic retry with exponential backoff
- **JSON Parsing**: Robust extraction from Grok's reasoning responses
- **Network Issues**: Retry logic with configurable attempts

## Notes

- Grok API uses OpenAI-compatible SDK but with custom base URL
- All translations are synchronous (Grok doesn't support batch API)
- Timeout set to 3600s (1 hour) as recommended by xAI docs
- Cost is approximately $0.38 for full translation of 27,930 definitions
