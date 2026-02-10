# Kilo Configs

Centralized configuration files for Kilo Code AI-assisted development.

## Usage

Copy `~/.kilo/` to any repository:

```bash
cd ~/my-repo
~/.kilo/scripts/copy-kilo.sh

# Commit the changes
git add .kilo/ .kilocodemodes
git commit -m 'Add Kilo Code configs'
git push
```

## Directory Structure

```
.kilo/
├── instructions/    # Project rules and guidelines
├── skills/         # AI skill definitions
└── scripts/
    └── copy-kilo.sh  # Copy script
```

## Kilo Code Modes

Custom modes are configured in `.kilocodemodes`:
- `github-expert` - GitHub repository setup
- `issue-creator` - Create GitHub issues
- `pr-creator` - Generate pull request commands

## Updating

To update configs in a repository:

1. Edit files in `~/.kilo/`
2. Run the copy script:
   ```bash
   cd ~/my-repo
   ~/.kilo/scripts/copy-kilo.sh
   ```
3. Commit changes

## Dry Run

Preview what would be copied without actually copying:

```bash
~/.kilo/scripts/copy-kilo.sh --dry-run
```

## Important

The `.kilocodemodes` file is also copied to `~/.kilocodemodes` for global mode availability.
