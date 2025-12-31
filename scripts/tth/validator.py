#!/usr/bin/env python3
"""
Validation Module
=================

Quality assurance and validation for TTH processing results.

Features:
- Validates JSON structure against expected format
- Checks data integrity and completeness
- Generates QA reports
- Compares with expected book statistics
- Validates Hebrew text presence and formatting

Author: Davar Project
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class TTHValidator:
    """
    Validates TTH processing results and generates QA reports.
    """

    # Expected structure for JSON entries
    REQUIRED_FIELDS = [
        'book', 'book_id', 'book_tth_name', 'book_hebrew_name',
        'book_english_name', 'book_spanish_name', 'section',
        'chapter', 'verse', 'status', 'tth'
    ]

    OPTIONAL_FIELDS = [
        'title', 'psalm_title', 'psalm_book', 'alefato',
        'footnotes', 'hebrew_terms',
        'section_hebrew', 'section_english', 'section_spanish'
    ]

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_book_directory(self, book_dir: str) -> Dict[str, Any]:
        """
        Validate a complete book directory.

        Args:
            book_dir: Path to book directory (e.g., 'draft/bereshit')

        Returns:
            Validation report
        """
        book_key = os.path.basename(book_dir)
        report = {
            'book_key': book_key,
            'directory': book_dir,
            'valid': True,
            'issues': [],
            'statistics': {},
            'chapter_files': [],
            'book_info_valid': False
        }

        # Check if directory exists
        if not os.path.exists(book_dir):
            report['issues'].append(f"Directory does not exist: {book_dir}")
            report['valid'] = False
            return report

        # Validate book_info.json
        book_info_path = os.path.join(book_dir, 'book_info.json')
        if not os.path.exists(book_info_path):
            report['issues'].append("book_info.json not found")
            report['valid'] = False
        else:
            book_info_valid, book_info_issues = self.validate_book_info(book_info_path)
            report['book_info_valid'] = book_info_valid
            if book_info_issues:
                report['issues'].extend(book_info_issues)
                report['valid'] = False

        # Find chapter files
        chapter_files = []
        for filename in os.listdir(book_dir):
            if filename.endswith('.json') and filename != 'book_info.json':
                match = re.match(r'(\d+)\.json', filename)
                if match:
                    chapter_num = int(match.group(1))
                    chapter_files.append((chapter_num, filename))

        chapter_files.sort()
        report['chapter_files'] = [f[1] for f in chapter_files]

        # Validate each chapter file
        total_verses = 0
        chapter_validations = []

        for chapter_num, filename in chapter_files:
            filepath = os.path.join(book_dir, filename)
            chapter_validation = self.validate_chapter_file(filepath, chapter_num)
            chapter_validations.append(chapter_validation)

            if not chapter_validation['valid']:
                report['issues'].extend([f"Capítulo {chapter_num}: {issue}" for issue in chapter_validation['issues']])
                report['valid'] = False

            total_verses += chapter_validation['verse_count']

        # Overall statistics
        report['statistics'] = {
            'total_chapters': len(chapter_files),
            'total_verses': total_verses,
            'chapter_validations': chapter_validations
        }

        return report

    def validate_book_info(self, book_info_path: str) -> Tuple[bool, List[str]]:
        """
        Validate book_info.json file.

        Args:
            book_info_path: Path to book_info.json

        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []

        try:
            with open(book_info_path, 'r', encoding='utf-8') as f:
                book_info = json.load(f)

            required_fields = [
                'tth_name', 'hebrew_name', 'english_name', 'spanish_name',
                'book_code', 'expected_chapters', 'section'
            ]

            for field in required_fields:
                if field not in book_info:
                    issues.append(f"Campo requerido faltante: {field}")
                elif not book_info[field]:
                    issues.append(f"Campo vacío: {field}")

            # Validate expected_chapters is a number
            if 'expected_chapters' in book_info:
                if not isinstance(book_info['expected_chapters'], int) or book_info['expected_chapters'] <= 0:
                    issues.append("expected_chapters debe ser un número entero positivo")

            # Validate Hebrew text presence
            if 'hebrew_name' in book_info:
                hebrew_text = book_info['hebrew_name']
                if not re.search(r'[\u0590-\u05FF]', hebrew_text):
                    issues.append("hebrew_name no contiene texto hebreo")

        except json.JSONDecodeError as e:
            issues.append(f"Error de JSON: {e}")
        except Exception as e:
            issues.append(f"Error al leer archivo: {e}")

        return len(issues) == 0, issues

    def validate_chapter_file(self, chapter_path: str, expected_chapter: int) -> Dict[str, Any]:
        """
        Validate a single chapter JSON file.

        Args:
            chapter_path: Path to chapter JSON file
            expected_chapter: Expected chapter number

        Returns:
            Validation report for the chapter
        """
        report = {
            'chapter': expected_chapter,
            'filepath': chapter_path,
            'valid': True,
            'issues': [],
            'verse_count': 0,
            'verses_with_footnotes': 0,
            'verses_with_hebrew_terms': 0,
            'verses_with_titles': 0
        }

        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                verses = json.load(f)

            if not isinstance(verses, list):
                report['issues'].append("File must contain a list of verses")
                report['valid'] = False
                return report

            if len(verses) == 0:
                report['issues'].append("Chapter contains no verses")
                report['valid'] = False
                return report

            report['verse_count'] = len(verses)

            # Validate each verse
            for i, verse in enumerate(verses):
                verse_issues = self.validate_verse_structure(verse, i + 1, expected_chapter)
                if verse_issues:
                    report['issues'].extend([f"Versículo {i+1}: {issue}" for issue in verse_issues])
                    report['valid'] = False

                # Statistics
                if verse.get('footnotes'):
                    report['verses_with_footnotes'] += 1
                if verse.get('hebrew_terms'):
                    report['verses_with_hebrew_terms'] += 1
                if verse.get('title') or verse.get('psalm_title'):
                    report['verses_with_titles'] += 1

        except json.JSONDecodeError as e:
            report['issues'].append(f"Error de JSON: {e}")
            report['valid'] = False
        except Exception as e:
            report['issues'].append(f"Error al leer archivo: {e}")
            report['valid'] = False

        return report

    def validate_verse_structure(self, verse: Dict[str, Any], verse_num: int, chapter_num: int) -> List[str]:
        """
        Validate the structure of a single verse entry.

        Args:
            verse: Verse dictionary
            verse_num: Verse number (for error messages)
            chapter_num: Chapter number (for validation)

        Returns:
            List of validation issues
        """
        issues = []

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in verse:
                issues.append(f"Campo requerido faltante: {field}")
            elif field == 'chapter' and verse.get('chapter') != chapter_num:
                issues.append(f"Número de capítulo incorrecto: esperado {chapter_num}, encontrado {verse.get('chapter')}")
            elif field == 'verse' and verse.get('verse') != verse_num:
                issues.append(f"Número de versículo incorrecto: esperado {verse_num}, encontrado {verse.get('verse')}")
            elif field == 'status' and verse.get('status') != 'present':
                issues.append(f"Status incorrecto: esperado 'present', encontrado '{verse.get('status')}'")

        # Validate text content
        if 'tth' in verse:
            tth_text = verse['tth']
            if not isinstance(tth_text, str):
                issues.append("Campo 'tth' debe ser una cadena de texto")
            elif not tth_text.strip():
                issues.append("Campo 'tth' está vacío")
            else:
                # Check for Hebrew text presence in some verses (not all books have it)
                has_hebrew = bool(re.search(r'[\u0590-\u05FF]', tth_text))
                if not has_hebrew and verse.get('book') in ['bereshit', 'shemot', 'vaikra']:  # Torah books should have Hebrew
                    issues.append("TTH text does not contain Hebrew characters (expected in Torah books)")

        # Validate footnotes structure
        if 'footnotes' in verse:
            footnotes = verse['footnotes']
            if not isinstance(footnotes, list):
                issues.append("Campo 'footnotes' debe ser una lista")
            else:
                for j, footnote in enumerate(footnotes):
                    if not isinstance(footnote, dict):
                        issues.append(f"Nota al pie {j+1} debe ser un diccionario")
                        continue

                    required_footnote_fields = ['marker', 'number', 'word', 'explanation']
                    for field in required_footnote_fields:
                        if field not in footnote:
                            issues.append(f"Nota al pie {j+1}: campo requerido faltante '{field}'")

        # Validate Hebrew terms structure
        if 'hebrew_terms' in verse:
            hebrew_terms = verse['hebrew_terms']
            if not isinstance(hebrew_terms, list):
                issues.append("Campo 'hebrew_terms' debe ser una lista")
            else:
                for j, term in enumerate(hebrew_terms):
                    if not isinstance(term, dict):
                        issues.append(f"Término hebreo {j+1} debe ser un diccionario")
                        continue

                    if 'term' not in term or 'explanation' not in term:
                        issues.append(f"Término hebreo {j+1}: campos 'term' y 'explanation' requeridos")

        # Validate optional fields
        for field in self.OPTIONAL_FIELDS:
            if field in verse and verse[field] is not None:
                if field in ['title', 'psalm_title'] and not isinstance(verse[field], str):
                    issues.append(f"Campo '{field}' debe ser una cadena de texto")
                elif field == 'alefato' and not isinstance(verse[field], str):
                    issues.append("Campo 'alefato' debe ser una cadena de texto")
                elif field == 'psalm_book' and not isinstance(verse[field], int):
                    issues.append("Campo 'psalm_book' debe ser un número entero")

        return issues

    def generate_qa_report(self, validation_reports: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive QA report from validation results.

        Args:
            validation_reports: List of validation reports

        Returns:
            Formatted QA report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("REPORTE DE CONTROL DE CALIDAD - TTH Processing")
        report_lines.append("=" * 80)
        report_lines.append("")

        total_books = len(validation_reports)
        valid_books = sum(1 for r in validation_reports if r['valid'])
        invalid_books = total_books - valid_books

        report_lines.append("RESUMEN GENERAL:")
        report_lines.append(f"  Libros procesados: {total_books}")
        report_lines.append(f"  Libros válidos: {valid_books}")
        report_lines.append(f"  Libros con problemas: {invalid_books}")
        report_lines.append("")

        total_verses = sum(r['statistics'].get('total_verses', 0) for r in validation_reports)
        total_chapters = sum(r['statistics'].get('total_chapters', 0) for r in validation_reports)

        report_lines.append("ESTADÍSTICAS TOTALES:")
        report_lines.append(f"  Total chapters: {total_chapters}")
        report_lines.append(f"  Total verses: {total_verses}")
        report_lines.append("")

        # Individual book reports
        for report in validation_reports:
            book_key = report['book_key']
            valid = report['valid']
            status = "✓ VÁLIDO" if valid else "✗ PROBLEMAS"

            report_lines.append(f"LIBRO: {book_key} - {status}")
            report_lines.append("-" * 40)

            stats = report['statistics']
            report_lines.append(f"  Chapters: {stats.get('total_chapters', 0)}")
            report_lines.append(f"  Verses: {stats.get('total_verses', 0)}")
            report_lines.append(f"  book_info.json: {'✓' if report.get('book_info_valid', False) else '✗'}")

            if report['issues']:
                report_lines.append("  PROBLEMAS:")
                for issue in report['issues'][:10]:  # Limit to first 10 issues
                    report_lines.append(f"    - {issue}")
                if len(report['issues']) > 10:
                    report_lines.append(f"    ... y {len(report['issues']) - 10} problemas adicionales")
            else:
                report_lines.append("  Sin problemas detectados")

            report_lines.append("")

        # Overall assessment
        report_lines.append("=" * 80)
        if invalid_books == 0:
            report_lines.append("✓ TODOS LOS LIBROS PASARON LA VALIDACIÓN")
        else:
            report_lines.append(f"⚠️  {invalid_books} LIBROS TIENEN PROBLEMAS QUE REQUIEREN ATENCIÓN")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def validate_processing_results(self, output_dir: str = 'draft') -> Dict[str, Any]:
        """
        Validate all processing results in a directory.

        Args:
            output_dir: Directory containing processed books

        Returns:
            Comprehensive validation report
        """
        if not os.path.exists(output_dir):
            return {
                'valid': False,
                'error': f"Directorio de salida no existe: {output_dir}",
                'books_validated': 0
            }

        # Find all book directories
        book_dirs = []
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                book_dirs.append(item_path)

        if not book_dirs:
            return {
                'valid': False,
                'error': f"No se encontraron directorios de libros en: {output_dir}",
                'books_validated': 0
            }

        # Validate each book
        validation_reports = []
        for book_dir in sorted(book_dirs):
            print(f"Validando: {os.path.basename(book_dir)}")
            report = self.validate_book_directory(book_dir)
            validation_reports.append(report)

        # Generate summary
        valid_books = sum(1 for r in validation_reports if r['valid'])
        total_books = len(validation_reports)

        summary = {
            'valid': valid_books == total_books,
            'books_validated': total_books,
            'books_valid': valid_books,
            'books_invalid': total_books - valid_books,
            'validation_reports': validation_reports,
            'qa_report': self.generate_qa_report(validation_reports)
        }

        return summary


def validate_book(book_key: str, output_dir: str = 'draft') -> Dict[str, Any]:
    """
    Validate a single book.

    Args:
        book_key: Book identifier
        output_dir: Output directory

    Returns:
        Validation report for the book
    """
    validator = TTHValidator()
    book_dir = os.path.join(output_dir, book_key)
    return validator.validate_book_directory(book_dir)


def validate_all_books(output_dir: str = 'draft') -> Dict[str, Any]:
    """
    Validate all books in output directory.

    Args:
        output_dir: Output directory

    Returns:
        Comprehensive validation report
    """
    validator = TTHValidator()
    return validator.validate_processing_results(output_dir)
