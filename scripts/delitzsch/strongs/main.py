#!/usr/bin/env python3
"""
Main CLI entry point for Delitzsch Strong's assignment.

Assigns Strong's numbers to Hebrew words in Delitzsch NT translation
that currently have null Strong's values, using xAI Grok API.
"""

import argparse
import logging
import sys
from pathlib import Path

from .processor import StrongsProcessor
from .config import ALL_BOOKS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Assign Strong\'s numbers to Hebrew words in Delitzsch NT translation using xAI Grok API',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--book',
        choices=ALL_BOOKS,
        help='Process specific book (e.g., matthew). If not specified, processes all books.'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Scan and count null-strong words without making API calls'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-process books even if output files already exist'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate API key
    try:
        from .config import validate_grok_api_key
        if not validate_grok_api_key():
            logger.error(
                "XAI_API_KEY not found in environment variables.\n"
                "Please create a .env file in the project root with:\n"
                "XAI_API_KEY=your_api_key_here\n"
                "Get your API key from: https://console.x.ai/team/default/api-keys"
            )
            sys.exit(1)
    except ImportError as e:
        logger.error(f"Failed to import Grok configuration: {e}")
        sys.exit(1)

    # Initialize processor
    try:
        processor = StrongsProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        sys.exit(1)

    # Determine which books to process
    books_to_process = [args.book] if args.book else ALL_BOOKS

    # Process books
    all_stats = {
        'total_books': len(books_to_process),
        'books_processed': 0,
        'total_null_words': 0,
        'total_assigned': 0,
        'total_failed': 0,
        'book_stats': []
    }

    try:
        for book_name in books_to_process:
            logger.info(f"Processing book: {book_name}")

            try:
                stats = processor.process_book(
                    book_name,
                    dry_run=args.dry_run,
                    force=args.force
                )

                if not stats.get('skipped', False):
                    all_stats['books_processed'] += 1
                    all_stats['total_null_words'] += stats.get('total_null_words', 0)
                    all_stats['total_assigned'] += stats.get('total_assigned', 0)
                    all_stats['total_failed'] += stats.get('total_failed', 0)

                all_stats['book_stats'].append(stats)

                if stats.get('total_null_words', 0) > 0:
                    logger.info(
                        f"Book {book_name}: {stats.get('total_assigned', 0)}/"
                        f"{stats.get('total_null_words', 0)} words assigned"
                    )

            except Exception as e:
                logger.error(f"Failed to process book {book_name}: {e}")
                all_stats['book_stats'].append({
                    'book': book_name,
                    'error': str(e)
                })
                continue

        # Print summary
        print("\n" + "="*60)
        print("Strong's Assignment Summary")
        print("="*60)

        print(f"Books processed: {all_stats['books_processed']}/{all_stats['total_books']}")
        print(f"Total null-strong words: {all_stats['total_null_words']}")
        print(f"Total assigned: {all_stats['total_assigned']}")
        print(f"Total failed: {all_stats['total_failed']}")

        if all_stats['total_null_words'] > 0:
            success_rate = (all_stats['total_assigned'] / all_stats['total_null_words']) * 100
            print(f"Success rate: {success_rate:.1f}%")

        # Print mismatch statistics
        mismatch_stats = processor.get_mismatch_stats()
        if mismatch_stats['total_batches'] > 0:
            print(f"\nAPI Quality Stats:")
            print(f"  Total batches processed: {mismatch_stats['total_batches']}")
            print(f"  Batches with mismatches: {mismatch_stats['mismatched_batches']}")
            if mismatch_stats['mismatched_batches'] > 0:
                print(f"  Total padding applied: {mismatch_stats['total_padding']}")
                print(f"  Total truncation applied: {mismatch_stats['total_truncation']}")
                print(f"  Mismatch patterns: {mismatch_stats['mismatch_patterns']}")

        print("="*60)

        if args.dry_run:
            print("\n⚠️  DRY RUN MODE - No API calls were made")
        elif args.force:
            print("\n🔄 Force mode - Existing files were overwritten")
        else:
            print("\n✅ Assignment completed successfully!")

    except KeyboardInterrupt:
        logger.info("\n\nAssignment interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Assignment failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    main()