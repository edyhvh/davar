# Hebrew Text Transcription

Transcribe Hebrew Bible images using Claude Vision API.

## Installation

```bash
pip install anthropic jsonschema Pillow PyYAML python-dotenv tqdm
```

## Setup

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Usage

```bash
# List books
python -m scripts.text --list

# Dry run (5 images)
python -m scripts.text --book matthew --dry-run

# Process book
python -m scripts.text --book matthew

# Multiple books
python -m scripts.text matthew mark luke

# All books
python -m scripts.text --all

# Resume
python -m scripts.text --book matthew --resume

# Reprocess failed
python -m scripts.text --book acts --reprocess-failed

# Different model
python -m scripts.text --book acts --model opus-4.5
```

## Package Structure

```
scripts/text/
├── __init__.py      # Package exports
├── __main__.py      # Entry point
├── cli.py           # CLI argument parsing
├── api.py           # Claude API client
├── processor.py     # Core processing logic
├── books.py         # Book structure data
├── checkpoint.py    # Checkpoint management
├── consolidate.py   # Verse consolidation
├── prompt.py        # Prompt building
├── validate.py      # Validation functions
└── config.py        # Constants
```

## Models

| Alias | Description |
|-------|-------------|
| `sonnet-4.5` (default) | Best balance |
| `opus-4.5` | Most capable |
| `opus-4` | Very capable |
| `sonnet-4` | Fallback |

## CLI Options

| Option | Description |
|--------|-------------|
| `--book`, `-b` | Single book |
| `--all` | All books |
| `--list` | List books |
| `--dry-run` | Test mode (5 images) |
| `--resume` | Continue from checkpoint |
| `--reprocess-failed` | Retry failed images |
| `--reprocess-images` | Specific images |
| `--model`, `-m` | Claude model |
| `--parallel` | Concurrent requests |
| `--verbose`, `-v` | Debug logging |

## Output

```
output/
├── <book>.json           # Final transcription
└── .checkpoints/
    └── <book>_state.json # Processing state
```

## Cost

~$0.01 per image (Claude Sonnet 4.5)

## Features

- Automatic image compression
- Sequential chapter inference
- Checkpoint recovery
- Parallel processing
- Progress tracking
- Error diagnostics

## API Usage

```python
from scripts.text import ClaudeClient, CheckpointManager

# Transcribe image
client = ClaudeClient()
result = client.transcribe_image(image_path, prompt)

# Manage checkpoints
checkpoint = CheckpointManager(checkpoint_path)
checkpoint.load()
checkpoint.save()
```

