#!/bin/bash
# Copy ~/.kilo/ to current directory's .kilo/
# Usage: ~/.kilo/scripts/copy-kilo.sh [--dry-run]

SOURCE_DIR="$HOME/.kilo"
TARGET_DIR="$(pwd)/.kilo"
GLOBAL_MODES="$HOME/.kilocodemodes"

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: ~/.kilo/ does not exist"
    exit 1
fi

# Create target directory if needed
if [ ! -d "$TARGET_DIR" ]; then
    echo "📁 Creating $TARGET_DIR/"
    mkdir -p "$TARGET_DIR"
fi

# Dry run mode
if [ "$1" = "--dry-run" ]; then
    echo "🔍 Dry run - showing what would be copied:"
    rsync -avn --delete "$SOURCE_DIR/" "$TARGET_DIR/"
    echo ""
    echo "Run without --dry-run to actually copy."
    exit 0
fi

# Warning about --delete flag
echo "⚠️  Warning: This will delete files in $TARGET_DIR that don't exist in $SOURCE_DIR"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Copy .kilo/ directory
rsync -av --delete "$SOURCE_DIR/" "$TARGET_DIR/"

# Copy .kilocodemodes to global location if it exists
if [ -f "$TARGET_DIR/.kilocodemodes" ]; then
    cp "$TARGET_DIR/.kilocodemodes" "$GLOBAL_MODES"
    echo "✅ Copied .kilocodemodes to global settings"
fi

echo "✅ Copied ~/.kilo/ to $TARGET_DIR/"
echo ""
echo "Next steps:"
echo "  git add .kilo/ .kilocodemodes"
echo "  git commit -m 'Add .kilo configs'"
echo "  git push"
