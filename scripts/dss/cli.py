#!/usr/bin/env python3
"""
DSS Command Line Interface

Professional command-line interface for DSS variant processing operations.
Provides standardized commands for extraction, validation, and processing tasks.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from .processor import DSSProcessor
from .markdown_extractor import DSSMarkdownExtractor
from .validator import DSSValidator
from .dss_config import config, BOOKS_WITH_VARIANTS, BOOK_MAPPINGS, get_available_books


class DSSCLI:
    """Command Line Interface for DSS operations."""

    def __init__(self):
        self.processor = DSSProcessor()
        self.validator = DSSValidator()
        self.markdown_extractor = DSSMarkdownExtractor()

    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description="DSS Variants Processing System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m dss.cli extract-markdown data/dss/raw/variants.md
  python -m dss.cli validate-all
  python -m dss.cli process-book isaiah
  python -m dss.cli demo
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Extract Markdown command
        extract_parser = subparsers.add_parser(
            'extract-markdown',
            help='Extract DSS variants from Markdown document'
        )
        extract_parser.add_argument(
            'markdown_path',
            help='Path to Markdown document containing DSS variants'
        )
        extract_parser.add_argument(
            '--output-dir',
            help='Output directory for extracted data',
            default=str(config.paths.output_dir)
        )

        # Validate command
        validate_parser = subparsers.add_parser(
            'validate-all',
            help='Validate all DSS variant data'
        )
        validate_parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix validation issues automatically'
        )

        # Process book command
        process_parser = subparsers.add_parser(
            'process-book',
            help='Process DSS variants for a specific book'
        )
        process_parser.add_argument(
            'book',
            choices=BOOKS_WITH_VARIANTS,
            help='Book to process'
        )
        process_parser.add_argument(
            '--cross-reference',
            action='store_true',
            help='Enable cross-referencing with MT'
        )

        # Demo command
        subparsers.add_parser(
            'demo',
            help='Run complete system demonstration'
        )

        # List books command
        subparsers.add_parser(
            'list-books',
            help='List available books with DSS variants'
        )

        # Status command
        subparsers.add_parser(
            'status',
            help='Show system status and statistics'
        )

        return parser

    def run_extract_markdown(self, markdown_path: str, output_dir: str) -> int:
        """Run Markdown extraction command."""
        try:
            markdown_file = Path(markdown_path)
            if not markdown_file.exists():
                print(f"Error: Markdown file not found: {markdown_path}")
                return 1

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            print(f"Extracting DSS variants from: {markdown_path}")
            stats = self.markdown_extractor.extract_and_save(str(markdown_file), output_path)

            print(f"Successfully extracted variants from {stats['total_books']} books")
            print(f"Total variants: {stats['total_variants']}")

            for book, count in stats.items():
                if book not in ['total_books', 'total_variants']:
                    print(f"  - {book}: {count} variants")

            return 0

        except Exception as e:
            print(f"Error during Markdown extraction: {e}")
            return 1

    def run_validate_all(self, fix: bool = False) -> int:
        """Run validation command."""
        try:
            print("Validating DSS variant data...")

            results = self.validator.validate_all_data()
            total_variants = results['total_variants']
            errors = results['errors']
            warnings = results['warnings']

            print(f"Validated {total_variants} variants")
            print(f"Found {len(errors)} errors and {len(warnings)} warnings")

            if errors:
                print("\nErrors:")
                for error in errors:
                    print(f"  - {error}")

            if warnings:
                print("\nWarnings:")
                for warning in warnings:
                    print(f"  - {warning}")

            if fix and errors:
                print("\nAttempting to fix issues...")
                fixed_count = self.validator.fix_issues(errors)
                print(f"Fixed {fixed_count} issues automatically")

            return 0 if not errors else 1

        except Exception as e:
            print(f"Error during validation: {e}")
            return 1

    def run_process_book(self, book: str, cross_reference: bool = False) -> int:
        """Run book processing command."""
        try:
            print(f"Processing DSS variants for {book}...")

            if cross_reference:
                print("Cross-referencing with Masoretic Text...")
                results = self.processor.cross_validate_with_mt()
                print(f"Cross-validation: {results['matches_found']} matches found")
            else:
                # Basic processing
                variants = self.processor.load_variants_for_book(book)
                print(f"Loaded {len(variants)} variants for {book}")

            print("Processing completed successfully")
            return 0

        except Exception as e:
            print(f"Error during book processing: {e}")
            return 1

    def run_demo(self) -> int:
        """Run demonstration command."""
        try:
            from .demo import run_demo
            return run_demo()
        except Exception as e:
            print(f"Error running demo: {e}")
            return 1

    def run_list_books(self) -> int:
        """Run list books command."""
        try:
            books = get_available_books()
            if not books:
                print("No DSS variant books found")
                return 1

            print("Available books with DSS variants:")
            for book in sorted(books):
                print(f"  - {book}")

            return 0

        except Exception as e:
            print(f"Error listing books: {e}")
            return 1

    def run_status(self) -> int:
        """Run status command."""
        try:
            print("DSS Processing System Status")
            print("=" * 40)

            # Check available books
            books = config.get_available_books()
            print(f"Books with variants: {len(books)}")

            total_variants = 0
            for book in books:
                variants = self.processor.load_variants_for_book(book)
                total_variants += len(variants)
                print(f"  - {book}: {len(variants)} variants")

            print(f"Total variants: {total_variants}")

            # Check ETCBC integration
            try:
                from .etcbc_integrator import ETCBCIntegrator
                integrator = ETCBCIntegrator()
                etcbc_status = "Available" if integrator.check_availability() else "Not available"
            except:
                etcbc_status = "Not configured"

            print(f"ETCBC DSS integration: {etcbc_status}")

            # Check directories
            dirs_ok = all([
                config.paths.output_dir.exists(),
                config.paths.dss_data_dir.exists()
            ])
            print(f"Directory structure: {'OK' if dirs_ok else 'Issues found'}")

            return 0

        except Exception as e:
            print(f"Error getting status: {e}")
            return 1

    def run(self, args: Optional[list] = None) -> int:
        """Main entry point for CLI."""
        parser = self.setup_parser()

        if args is None:
            args = sys.argv[1:]

        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return 1

        # Configure logging based on verbosity
        log_level = logging.WARNING
        if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
            log_level = logging.INFO
        if hasattr(parsed_args, 'debug') and parsed_args.debug:
            log_level = logging.DEBUG

        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s'
        )

        # Execute command
        command_map = {
            'extract-markdown': lambda: self.run_extract_markdown(
                parsed_args.markdown_path, parsed_args.output_dir
            ),
            'validate-all': lambda: self.run_validate_all(
                getattr(parsed_args, 'fix', False)
            ),
            'process-book': lambda: self.run_process_book(
                parsed_args.book, getattr(parsed_args, 'cross_reference', False)
            ),
            'demo': self.run_demo,
            'list-books': self.run_list_books,
            'status': self.run_status,
        }

        if parsed_args.command in command_map:
            return command_map[parsed_args.command]()
        else:
            print(f"Unknown command: {parsed_args.command}")
            parser.print_help()
            return 1


def main() -> int:
    """Main entry point for the DSS CLI."""
    cli = DSSCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
