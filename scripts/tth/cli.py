#!/usr/bin/env python3
"""
TTH Processing CLI
==================

Command-line interface for TTH (Traducción Textual del Hebreo) processing system.

Usage:
    python cli.py convert <docx_file> [output_dir]    # Convert DOCX to Markdown
    python cli.py extract <book_key> <docx_file>     # Extract single book from DOCX
    python cli.py process <book_key> <markdown_file> # Process Markdown to JSON
    python cli.py validate <output_dir>              # Validate processing results
    python cli.py full <docx_file> <output_dir>      # Full pipeline: DOCX -> Books -> JSON
    python cli.py books                              # List available books

Author: Davar Project
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# Import TTH modules
try:
    # When run as module
    from .converter import TTHDocxConverter, convert_file, MAMMOTH_AVAILABLE
    from .extractor import TTHBookExtractor, extract_book, get_available_books
    from .processor import TTHProcessor, process_book_to_json
    from .validator import TTHValidator, validate_all_books
except ImportError:
    # When run as script
    from converter import TTHDocxConverter, convert_file, MAMMOTH_AVAILABLE
    from extractor import TTHBookExtractor, extract_book, get_available_books
    from processor import TTHProcessor, process_book_to_json
    from validator import TTHValidator, validate_all_books


class TTHCLI:
    """Command-line interface for TTH processing."""

    def __init__(self):
        """Initialize CLI."""
        self.converter = TTHDocxConverter()
        self.extractor = TTHBookExtractor()
        self.validator = TTHValidator()

    def convert_command(self, args: List[str]) -> int:
        """Handle convert command."""
        if len(args) < 1:
            print("Uso: python cli.py convert <docx_file> [markdown_file]")
            return 1

        docx_file = args[0]
        markdown_file = args[1] if len(args) > 1 else None

        try:
            output_file, warnings = convert_file(docx_file, markdown_file)
            print(f"✓ Conversion completed: {output_file}")

            if warnings:
                print(f"Warnings: {len(warnings)}")
                for warning in warnings[:5]:  # Show first 5 warnings
                    print(f"  - {warning}")
                if len(warnings) > 5:
                    print(f"  ... and {len(warnings) - 5} additional warnings")

            return 0

        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return 1

    def extract_command(self, args: List[str]) -> int:
        """Handle extract command."""
        if len(args) < 2:
            print("Uso: python cli.py extract <book_key> <docx_file> [output_dir]")
            return 1

        book_key = args[0]
        docx_file = args[1]
        output_dir = args[2] if len(args) > 2 else 'extracted'

        try:
            # Convert DOCX to Markdown first
            print(f"Convirtiendo {docx_file}...")
            with open(docx_file, 'rb') as f:
                import mammoth
                result = mammoth.convert_to_markdown(f)
                markdown_text = result.value

            # Normalize the markdown
            markdown_text = self.converter.normalize_footnotes(markdown_text)
            markdown_text = self.converter.normalize_verse_markers(markdown_text)
            markdown_text = self.converter.separate_inline_verses(markdown_text)
            markdown_text = self.converter.clean_html_artifacts(markdown_text)

            # Extract book
            print(f"Extrayendo libro {book_key}...")
            book_text = self.extractor.extract_book_section(markdown_text, book_key)

            # Validate extraction
            validation = self.extractor.validate_book_extraction(book_text, book_key)

            if not validation['has_content']:
                print(f"❌ Extracción fallida: {book_key}")
                return 1

            # Save result
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{book_key}.md")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(book_text)

            print(f"✓ Book extracted: {output_file}")
            print(f"  Chapters detected: {validation['chapter_count']}")
            print(f"  Verses detected: {validation['verse_count']}")
            print(f"  Hebrew text: {'✓' if validation['has_hebrew'] else '✗'}")

            if validation['warnings']:
                print("Warnings:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")

            return 0

        except Exception as e:
            print(f"❌ Error en extracción: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def process_command(self, args: List[str]) -> int:
        """Handle process command."""
        if len(args) < 2:
            print("Uso: python cli.py process <book_key> <markdown_file> [output_dir]")
            return 1

        book_key = args[0]
        markdown_file = args[1]
        output_dir = args[2] if len(args) > 2 else 'draft'

        try:
            validation = process_book_to_json(book_key, markdown_file, output_dir)

            if validation.get('chapters_match', False):
                print(f"✓ Procesamiento exitoso: {book_key}")
                return 0
            else:
                print(f"⚠️  Procesamiento completado con problemas: {book_key}")
                return 1

        except Exception as e:
            print(f"❌ Error en procesamiento: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def validate_command(self, args: List[str]) -> int:
        """Handle validate command."""
        output_dir = args[0] if args else 'draft'

        try:
            validation = validate_all_books(output_dir)

            if validation['valid']:
                print(f"✓ Validación exitosa: {validation['books_valid']}/{validation['books_validated']} libros válidos")
                return 0
            else:
                print(f"⚠️  Issues found: {validation['books_invalid']}/{validation['books_validated']} books with problems")

                # Print summary of issues
                for report in validation['validation_reports']:
                    if not report['valid']:
                        print(f"\nProblemas en {report['book_key']}:")
                        for issue in report['issues'][:5]:  # First 5 issues
                            print(f"  - {issue}")

                return 1

        except Exception as e:
            print(f"❌ Error en validación: {e}")
            return 1

    def full_command(self, args: List[str]) -> int:
        """Handle full pipeline command."""
        if len(args) < 2:
            print("Uso: python cli.py full <docx_file> <output_dir> [book_keys...]")
            print("Ejemplos:")
            print("  python cli.py full tanaj.docx output/              # Procesar todos los libros")
            print("  python cli.py full tanaj.docx output/ bereshit shemot  # Procesar libros específicos")
            return 1

        docx_file = args[0]
        output_dir = args[1]
        book_keys = args[2:] if len(args) > 2 else None

        try:
            # Convert DOCX to Markdown
            print("=" * 60)
            print("PHASE 1: DOCX -> Markdown Conversion")
            print("=" * 60)

            with open(docx_file, 'rb') as f:
                import mammoth
                result = mammoth.convert_to_markdown(f)
                markdown_text = result.value

            # Normalize
            print("Normalizing markdown...")
            markdown_text = self.converter.normalize_footnotes(markdown_text)
            markdown_text = self.converter.normalize_verse_markers(markdown_text)
            markdown_text = self.converter.separate_inline_verses(markdown_text)
            markdown_text = self.converter.clean_html_artifacts(markdown_text)

            # Determine which books to process
            if book_keys:
                books_to_process = book_keys
            else:
                books_to_process = get_available_books()
                print(f"Processing all available books: {len(books_to_process)}")

            # Process each book
            successful_books = []
            failed_books = []

            for book_key in books_to_process:
                print("\n" + "=" * 60)
                print(f"Processing book: {book_key}")
                print("=" * 60)

                try:
                    # Extract book
                    print("Extracting book from complete document...")
                    book_text = self.extractor.extract_book_section(markdown_text, book_key)

                    # Validate extraction
                    validation = self.extractor.validate_book_extraction(book_text, book_key)
                    if not validation['has_content']:
                        print(f"⚠️  Extraction failed for {book_key}, skipping...")
                        failed_books.append(book_key)
                        continue

                    # Save temporary markdown
                    temp_dir = os.path.join(output_dir, 'temp')
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_md_file = os.path.join(temp_dir, f"{book_key}.md")

                    with open(temp_md_file, 'w', encoding='utf-8') as f:
                        f.write(book_text)

                    # Process to JSON
                    print("Converting to JSON...")
                    process_validation = process_book_to_json(book_key, temp_md_file, output_dir)

                    if process_validation.get('chapters_match', False):
                        successful_books.append(book_key)
                        print(f"✓ {book_key} processed successfully")
                    else:
                        failed_books.append(book_key)
                        print(f"⚠️  {book_key} processed with issues")

                except Exception as e:
                    print(f"❌ Error processing {book_key}: {e}")
                    failed_books.append(book_key)
                    continue

            # Final validation
            print("\n" + "=" * 60)
            print("PHASE 3: Final Validation")
            print("=" * 60)

            final_validation = validate_all_books(output_dir)

            print(f"\nFINAL SUMMARY:")
            print(f"✓ Books processed successfully: {len(successful_books)}")
            if successful_books:
                print(f"  {', '.join(successful_books)}")

            if failed_books:
                print(f"✗ Books with issues: {len(failed_books)}")
                print(f"  {', '.join(failed_books)}")

            if final_validation['valid']:
                print("✓ All books passed validation")
                return 0
            else:
                print(f"⚠️  {final_validation['books_invalid']} books have validation issues")
                return 1

        except Exception as e:
            print(f"❌ Error in complete pipeline: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def simple_run_command(self, args: List[str]) -> int:
        """Handle simplified run command for normal processing to data/tth/."""
        if not args:
            print("Uso: python cli.py run <book_key>")
            print("Ejemplo: python cli.py run amos")
            return 1

        book_key = args[0]
        output_dir = '../../data/tth/'

        # Try to use existing Markdown file first (faster, no mammoth needed)
        markdown_files = [
            f"../../data/tth/tanaj/{book_key}.md",  # Tanaj books
            f"../../data/tth/raw/{book_key}.md"     # NT books (like sodot_iaacob_iehudah.md extracts)
        ]

        for markdown_file in markdown_files:
            if os.path.exists(markdown_file):
                print(f"Procesando libro '{book_key}' desde archivo Markdown existente...")
                print(f"Archivo: {markdown_file}")
                print(f"Output will go to: {output_dir}")
                return self.process_command([book_key, markdown_file, output_dir])

        # Fall back to full pipeline with DOCX (requires mammoth)
        if not MAMMOTH_AVAILABLE:
            print("❌ Error: No se encontró archivo Markdown y mammoth no está instalado")
            print("Opciones:")
            print("1. Instala mammoth: pip install mammoth")
            print("2. Crea el archivo Markdown manualmente")
            return 1

        try:
            from extractor import TTHBookExtractor
            extractor = TTHBookExtractor()
            docx_file = extractor.get_source_document_path(book_key)

            print(f"Procesando libro '{book_key}' desde {docx_file}...")
            print(f"Output will go to: {output_dir}")

            return self.full_command([docx_file, output_dir, book_key])
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def test_command(self, args: List[str]) -> int:
        """Handle test command for testing to data/tth/temp."""
        if not args:
            print("Uso: python cli.py test <book_key>")
            print("Ejemplo: python cli.py test amos")
            return 1

        book_key = args[0]
        output_dir = '../../data/tth/temp/'

        # Try to use existing Markdown file first (faster, no mammoth needed)
        markdown_files = [
            f"../../data/tth/tanaj/{book_key}.md",  # Tanaj books
            f"../../data/tth/raw/{book_key}.md"     # NT books (like sodot_iaacob_iehudah.md extracts)
        ]

        for markdown_file in markdown_files:
            if os.path.exists(markdown_file):
                print(f"Probando libro '{book_key}' desde archivo Markdown existente...")
                print(f"Archivo: {markdown_file}")
                print(f"Resultado de prueba irá a: {output_dir}")
                return self.process_command([book_key, markdown_file, output_dir])

        # Fall back to full pipeline with DOCX (requires mammoth)
        if not MAMMOTH_AVAILABLE:
            print("❌ Error: No se encontró archivo Markdown y mammoth no está instalado")
            print("Opciones:")
            print("1. Instala mammoth: pip install mammoth")
            print("2. Crea el archivo Markdown manualmente")
            return 1

        try:
            from extractor import TTHBookExtractor
            extractor = TTHBookExtractor()
            docx_file = extractor.get_source_document_path(book_key)

            print(f"Probando libro '{book_key}' desde {docx_file}...")
            print(f"Resultado de prueba irá a: {output_dir}")

            return self.full_command([docx_file, output_dir, book_key])
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def all_command(self, args: List[str]) -> int:
        """Handle all command to process all books."""
        test_mode = '--test' in args
        output_dir = '../../data/tth/temp/' if test_mode else '../../data/tth/'

        if test_mode:
            args.remove('--test')

        print(f"Procesando TODOS los libros...")
        print(f"Resultado irá a: {output_dir}")

        # Get all available books
        from extractor import get_available_books
        all_books = get_available_books()

        # For now, process only a few books to avoid overwhelming
        # In production, this would process all books
        test_books = ['bereshit', 'shemot', 'amos', 'iehudah']  # Sample books

        print(f"Procesando {len(test_books)} libros de muestra: {', '.join(test_books)}")

        # Process each book
        successful = []
        failed = []

        for book in test_books:
            try:
                from extractor import TTHBookExtractor
                extractor = TTHBookExtractor()
                docx_file = extractor.get_source_document_path(book)

                result = self.full_command([docx_file, output_dir, book])
                if result == 0:
                    successful.append(book)
                else:
                    failed.append(book)
            except Exception as e:
                print(f"❌ Error procesando {book}: {e}")
                failed.append(book)

        print(f"\n✅ Completado: {len(successful)} libros exitosos, {len(failed)} fallidos")
        return 0 if not failed else 1

    def book_command(self, args: List[str]) -> int:
        """Handle book command for multiple specific books."""
        if not args:
            print("Uso: python cli.py book <book_key1> [book_key2] ... [--test]")
            print("Ejemplo: python cli.py book amos iehudah --test")
            return 1

        test_mode = '--test' in args
        if test_mode:
            args.remove('--test')

        book_keys = args
        output_dir = '../../data/tth/temp/' if test_mode else '../../data/tth/'

        print(f"Procesando {len(book_keys)} libros: {', '.join(book_keys)}")
        print(f"Resultado irá a: {output_dir}")

        successful = []
        failed = []

        for book_key in book_keys:
            try:
                from extractor import TTHBookExtractor
                extractor = TTHBookExtractor()
                docx_file = extractor.get_source_document_path(book_key)

                result = self.full_command([docx_file, output_dir, book_key])
                if result == 0:
                    successful.append(book_key)
                else:
                    failed.append(book_key)
            except Exception as e:
                print(f"❌ Error procesando {book_key}: {e}")
                failed.append(book_key)

        print(f"\n✅ Completado: {len(successful)} libros exitosos, {len(failed)} fallidos")
        return 0 if not failed else 1

    def books_command(self, args: List[str]) -> int:
        """Handle books command."""
        try:
            books = get_available_books()
            print(f"Libros disponibles ({len(books)}):")
            print()

            # Group by section
            torah_books = [b for b in books if b in ['bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim']]
            neviim_books = [b for b in books if b not in torah_books + ['tehilim', 'mishlei']]
            ketuvim_books = [b for b in ['tehilim', 'mishlei'] if b in books]

            print("TORAH (Pentateuco):")
            for book in torah_books:
                print(f"  {book}")
            print()

            print("NEVIIM (Profetas):")
            for book in neviim_books:
                print(f"  {book}")
            print()

            print("KETUVIM (Escritos):")
            for book in ketuvim_books:
                print(f"  {book}")

            return 0

        except Exception as e:
            print(f"❌ Error listando libros: {e}")
            return 1

    def run(self, args: List[str]) -> int:
        """Run CLI with given arguments."""
        if not args:
            self.show_help()
            return 1

        command = args[0].lower()

        # Comandos simplificados
        if command in ['run', 'process', 'go']:
            return self.simple_run_command(args[1:])
        elif command == 'test':
            return self.test_command(args[1:])
        elif command == 'all':
            return self.all_command(args[1:])
        elif command == 'book':
            return self.book_command(args[1:])

        # Comandos técnicos (mantener compatibilidad)
        elif command == 'convert':
            return self.convert_command(args[1:])
        elif command == 'extract':
            return self.extract_command(args[1:])
        elif command == 'validate':
            return self.validate_command(args[1:])
        elif command == 'full':
            return self.full_command(args[1:])
        elif command == 'books':
            return self.books_command(args[1:])
        else:
            print(f"Comando desconocido: {command}")
            self.show_help()
            return 1

    def show_help(self):
        """Show help information."""
        help_text = """
TTH Processing System - Simplified Command Line Interface

SIMPLE COMMANDS:

  run <book_key>
    Process a single book to data/tth/ (normal production)

  test <book_key>
    Test a single book to data/tth/temp (testing mode)

  all [--test]
    Process all books (use --test for testing mode)

  book <book_key1> [book_key2] ... [--test]
    Process multiple specific books

ADVANCED COMMANDS:

  convert <docx_file> [output_file]
    Convert DOCX file to normalized Markdown

  extract <book_key> <docx_file> [output_dir]
    Extract specific book from complete DOCX document

  validate [output_dir]
    Validate processing results

  full <docx_file> <output_dir> [book_keys...]
    Complete pipeline: DOCX -> Markdown -> JSON for one or more books

  books
    List all available books

EXAMPLES:

  # Process single book (production)
  python cli.py run amos

  # Test single book
  python cli.py test amos

  # Process multiple books
  python cli.py book amos iehudah bereshit

  # Test multiple books
  python cli.py book amos iehudah --test

  # Process all books (sample)
  python cli.py all

  # Test all books (sample)
  python cli.py all --test

AVAILABLE BOOKS:
  Tanaj (Hebrew Bible): bereshit, shemot, vaikra, bamidbar, devarim, etc.
  Besorah (New Testament): matityahu, markos, lukas, iojanan, iehudah, etc.

OUTPUT DIRECTORIES:
  Production: data/tth/ (one JSON file per book)
  Testing: data/tth/temp/ (one JSON file per book)
"""
        print(help_text)


def main():
    """Main entry point."""
    cli = TTHCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == '__main__':
    main()
