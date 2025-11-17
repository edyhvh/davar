#!/usr/bin/env python3
"""
TTH Tanaj QA - Quality Assurance for Tanaj processing results
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path


class TTHTanajQA:
    def __init__(self, draft_dir: str = 'draft'):
        self.draft_dir = Path(draft_dir)
        self.tanaj_books = {
            'bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim',
            'iehosua', 'shoftim', 'shemuel_alef', 'shemuel_bet',
            'melakim_alef', 'melakim_bet', 'ieshaihu', 'irmiahu', 'iejezkel',
            'hosea', 'ioel', 'amos', 'obadiah', 'ionah', 'micah',
            'nahum', 'habakuk', 'tzefaniah', 'hagai', 'zejariah', 'malaji',
            'tehilim', 'mishlei', 'iob', 'shir_hashirim', 'rut',
            'eja', 'kohelet', 'ester', 'daniel', 'ezra', 'nehemiah',
            'dibre_hayamim_alef', 'dibre_hayamim_bet'
        }

    def get_tanaj_book_dirs(self) -> List[Path]:
        """Get only Tanaj book directories"""
        all_dirs = [d for d in self.draft_dir.iterdir() if d.is_dir()]
        return [d for d in all_dirs if d.name in self.tanaj_books]

    def analyze_book_structure(self, book_dir: Path) -> Dict[str, Any]:
        """Analyze a single book's structure"""
        book_name = book_dir.name
        book_info_file = book_dir / 'book_info.json'

        if not book_info_file.exists():
            return {'error': f'Missing book_info.json for {book_name}'}

        with open(book_info_file, 'r', encoding='utf-8') as f:
            book_info = json.load(f)

        # Get chapter files
        chapter_files = sorted([f for f in book_dir.glob('*.json') if f.name != 'book_info.json'])
        actual_chapters = len(chapter_files)

        total_verses = 0
        chapter_details = []

        for chapter_file in chapter_files:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                verses = json.load(f)
                verse_count = len(verses)
                total_verses += verse_count

                # Get first and last verse numbers
                if verses:
                    first_verse = verses[0]['verse']
                    last_verse = verses[-1]['verse']
                else:
                    first_verse = last_verse = 0

                chapter_num = int(chapter_file.stem)
                chapter_details.append({
                    'chapter': chapter_num,
                    'verses': verse_count,
                    'first_verse': first_verse,
                    'last_verse': last_verse
                })

        return {
            'book_name': book_name,
            'expected_chapters': book_info.get('expected_chapters', 0),
            'actual_chapters': actual_chapters,
            'expected_verses': book_info.get('total_verses', 0),  # This is from book_info
            'actual_verses': total_verses,
            'chapters': chapter_details,
            'chapter_coverage': actual_chapters / book_info.get('expected_chapters', 1) * 100,
            'book_info': book_info
        }

    def check_content_quality(self, book_dir: Path) -> Dict[str, Any]:
        """Check content quality of a book"""
        issues = []
        samples = []

        # Check a few chapter files
        chapter_files = list(book_dir.glob('*.json'))[:3]  # Check first 3 chapters

        for chapter_file in chapter_files:
            if chapter_file.name == 'book_info.json':
                continue

            with open(chapter_file, 'r', encoding='utf-8') as f:
                verses = json.load(f)

            for verse in verses[:2]:  # Check first 2 verses of each chapter
                text = verse.get('tth', '')
                samples.append({
                    'book': book_dir.name,
                    'chapter': verse.get('chapter'),
                    'verse': verse.get('verse'),
                    'text_length': len(text),
                    'has_footnotes': len(verse.get('footnotes', [])) > 0,
                    'has_hebrew_terms': len(verse.get('hebrew_terms', [])) > 0,
                    'text_preview': text[:100] + '...' if len(text) > 100 else text
                })

                # Check for common issues
                if not text.strip():
                    issues.append(f"Empty text in {book_dir.name} {verse.get('chapter')}:{verse.get('verse')}")

                if '__' in text:
                    issues.append(f"Unprocessed markers in {book_dir.name} {verse.get('chapter')}:{verse.get('verse')}")

                if '[^' in text:
                    issues.append(f"Unprocessed footnotes in {book_dir.name} {verse.get('chapter')}:{verse.get('verse')}")

        return {
            'issues': issues,
            'samples': samples
        }

    def run_qa(self):
        """Run complete QA analysis"""
        print("🔍 Iniciando QA del procesamiento del Tanaj...")
        print("=" * 60)

        tanaj_dirs = self.get_tanaj_book_dirs()
        print(f"📚 Analizando {len(tanaj_dirs)} libros del Tanaj")

        results = []
        total_expected_chapters = 0
        total_actual_chapters = 0
        total_expected_verses = 0
        total_actual_verses = 0

        # Analyze each book
        for book_dir in sorted(tanaj_dirs):
            print(f"\n📖 Analizando: {book_dir.name}")

            # Structure analysis
            structure = self.analyze_book_structure(book_dir)
            if 'error' in structure:
                print(f"  ❌ {structure['error']}")
                continue

            results.append(structure)

            # Print summary
            expected_ch = structure['expected_chapters']
            actual_ch = structure['actual_chapters']
            coverage = structure['chapter_coverage']

            total_expected_chapters += expected_ch
            total_actual_chapters += actual_ch
            total_expected_verses += structure['expected_verses']
            total_actual_verses += structure['actual_verses']

            status = "✅" if coverage >= 90 else "⚠️" if coverage >= 50 else "❌"
            print(f"  {status} Capítulos: {actual_ch}/{expected_ch} ({coverage:.1f}%)")
            print(f"     Versículos: {structure['actual_verses']}")

            # Content quality check
            quality = self.check_content_quality(book_dir)
            if quality['issues']:
                print(f"  🔧 Problemas encontrados: {len(quality['issues'])}")
                for issue in quality['issues'][:3]:  # Show first 3 issues
                    print(f"     - {issue}")
            else:
                print("  ✅ Sin problemas de contenido detectados")

        # Overall summary
        print("\n" + "=" * 60)
        print("📊 RESUMEN GENERAL:")
        print(f"  📚 Libros procesados: {len(results)}/{len(self.tanaj_books)}")
        print(f"  📄 Capítulos totales: {total_actual_chapters}/{total_expected_chapters} ({total_actual_chapters/total_expected_chapters*100:.1f}%)")
        print(f"  📝 Versículos totales: {total_actual_verses}")

        # Coverage analysis
        full_coverage = [r for r in results if r['chapter_coverage'] >= 95]
        partial_coverage = [r for r in results if 50 <= r['chapter_coverage'] < 95]
        poor_coverage = [r for r in results if r['chapter_coverage'] < 50]

        print("\n🎯 COBERTURA:")
        print(f"  ✅ Cobertura completa (≥95%): {len(full_coverage)} libros")
        print(f"  ⚠️ Cobertura parcial (50-95%): {len(partial_coverage)} libros")
        print(f"  ❌ Cobertura pobre (<50%): {len(poor_coverage)} libros")

        if poor_coverage:
            print("\n❌ Libros con problemas:")
            for book in poor_coverage:
                print(f"  - {book['book_name']}: {book['actual_chapters']}/{book['expected_chapters']} capítulos")

        # Sample content check
        print("\n📝 MUESTRAS DE CONTENIDO:")
        for result in results[:3]:  # Show first 3 books
            quality = self.check_content_quality(self.draft_dir / result['book_name'])
            if quality['samples']:
                sample = quality['samples'][0]
                print(f"  📖 {result['book_name']} {sample['chapter']}:{sample['verse']}")
                print(f"     \"{sample['text_preview']}\"")
                print(f"     📎 Notas: {sample['has_footnotes']} | 🌿 Términos hebreos: {sample['has_hebrew_terms']}")

        print("\n✅ QA completado!")


def main():
    qa = TTHTanajQA()
    qa.run_qa()


if __name__ == '__main__':
    main()
