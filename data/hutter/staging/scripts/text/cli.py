"""Command-line interface for Hebrew text transcription."""

import argparse
import logging
import sys
from pathlib import Path

from .config import AVAILABLE_BOOKS, DEFAULT_IMAGES_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_YAML_PATH, DEFAULT_CHECKPOINT_DIR
from .processor import process_books

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    for pkg, name in [('yaml', 'PyYAML'), ('jsonschema', 'jsonschema'), ('anthropic', 'anthropic')]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(name)

    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.info(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)


def list_books():
    """List all available books."""
    print("Available books:")
    print("=" * 50)
    for i, book in enumerate(AVAILABLE_BOOKS, 1):
        print(f"{i:2d}. {book}")
    print("\nUsage:")
    print("  python -m scripts.text --book matthew --dry-run")
    print("  python -m scripts.text matthew mark luke")
    print("  python -m scripts.text --all")


def validate_books(book_names: list) -> list:
    """Validate book names."""
    invalid = []
    valid = []

    for book in book_names:
        if book.lower() == 'all':
            return AVAILABLE_BOOKS
        elif book.lower() in AVAILABLE_BOOKS:
            valid.append(book.lower())
        else:
            invalid.append(book)

    if invalid:
        print(f"Error: Unknown books: {', '.join(invalid)}")
        print("Use --list to see available books")
        sys.exit(1)

    return valid


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Transcribe Hebrew Bible images using Claude Vision API.",
        epilog="""
Examples:
  python -m scripts.text --list                    # List books
  python -m scripts.text --book matthew --dry-run  # Process 5 images
  python -m scripts.text --book matthew            # Process one book
  python -m scripts.text matthew mark luke         # Multiple books
  python -m scripts.text --all                     # All books
  python -m scripts.text --book acts --resume      # Resume from checkpoint
  python -m scripts.text --book acts --reprocess-failed  # Reprocess failed

Models:
  sonnet-4.5, sonnet  (default) - Best balance of speed/quality
  opus-4.5, opus                - Most capable for difficult cases
  opus-4                        - Claude Opus 4
  sonnet-4                      - Claude Sonnet 4
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('books', nargs='*', help='Book names to process')
    parser.add_argument('--book', '-b', type=str, help='Single book name')
    parser.add_argument('--all', action='store_true', help='Process all books')
    parser.add_argument('--list', action='store_true', help='List available books')
    parser.add_argument('--dry-run', action='store_true', help='Process only 5 images')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--reprocess-failed', action='store_true', help='Reprocess failed images')
    parser.add_argument('--reprocess-images', type=str, help='Comma-separated images to reprocess')
    parser.add_argument('--images-dir', type=str, default=str(DEFAULT_IMAGES_DIR), help='Images directory')
    parser.add_argument('--output-dir', type=str, default=str(DEFAULT_OUTPUT_DIR), help='Output directory')
    parser.add_argument('--yaml-path', type=str, default=str(DEFAULT_YAML_PATH), help='YAML config path')
    parser.add_argument('--checkpoint-dir', type=str, default=str(DEFAULT_CHECKPOINT_DIR), help='Checkpoint directory')
    parser.add_argument('--parallel', type=int, default=1, help='Parallel requests')
    parser.add_argument('--model', '-m', type=str, help='Claude model (default: sonnet-4.5)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    if args.list:
        list_books()
        return

    check_dependencies()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Determine books to process
    if args.all:
        book_names = AVAILABLE_BOOKS
    elif args.book:
        book_names = validate_books([args.book])
    elif args.books:
        book_names = validate_books(args.books)
    else:
        print("Error: No books specified. Use --list to see available books.")
        print("Example: python -m scripts.text --book matthew --dry-run")
        sys.exit(1)

    # Validate paths
    images_dir = Path(args.images_dir)
    output_dir = Path(args.output_dir)
    yaml_path = Path(args.yaml_path)
    checkpoint_dir = Path(args.checkpoint_dir)

    if not images_dir.exists():
        logger.error(f"Images directory not found: {images_dir}")
        sys.exit(1)

    if not yaml_path.exists():
        logger.error(f"YAML file not found: {yaml_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Parse reprocess images
    reprocess_images = None
    if args.reprocess_images:
        reprocess_images = [img.strip() for img in args.reprocess_images.split(',')]

    # Process books
    success = process_books(
        book_names=book_names,
        images_dir=images_dir,
        output_dir=output_dir,
        yaml_path=yaml_path,
        checkpoint_dir=checkpoint_dir,
        dry_run=args.dry_run,
        resume=args.resume,
        reprocess_failed=args.reprocess_failed,
        reprocess_images=reprocess_images,
        parallel=args.parallel,
        model_name=args.model
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

