#!/usr/bin/env python3
"""
TTH Tanaj Cleaner - Limpia y corrige posibles errores en el archivo tanaj.md
antes del procesamiento principal.

Funciones:
- Verificar numeración correcta de libros y capítulos
- Corregir duplicaciones de marcadores
- Validar estructura de versículos
- Limpiar formato inconsistente
"""

import re
import os
from typing import Dict, List, Tuple
from collections import defaultdict


class TTHTanajCleaner:
    def __init__(self, input_file: str = 'tanaj.md', output_file: str = 'tanaj_clean.md'):
        self.input_file = input_file
        self.output_file = output_file

        # Información de libros del Tanaj (Torah, Neviim, Ketuvim)
        self.expected_books = {
            # Torah (Pentateuco)
            'bereshit': {'name': 'BERESHIT (GÉNESIS)', 'chapters': 50},
            'shemot': {'name': 'SHEMOT (ÉXODO)', 'chapters': 40},
            'vaikra': {'name': 'VAIKRÁ (LEVÍTICO)', 'chapters': 27},
            'bamidbar': {'name': 'BAMIDBAR (NÚMEROS)', 'chapters': 36},
            'devarim': {'name': 'DEVARIM (DEUTERONOMIO)', 'chapters': 34},

            # Neviim (Profetas)
            'iehosua': {'name': 'IEHOSHÚA (JOSUÉ)', 'chapters': 24},
            'shoftim': {'name': 'SHOFTIM (JUECES)', 'chapters': 21},
            'shemuel_alef': {'name': 'SHEMUEL ÁLEF (1 SAMUEL)', 'chapters': 31},
            'shemuel_bet': {'name': 'SHEMUEL BET (2 SAMUEL)', 'chapters': 24},
            'melakim_alef': {'name': 'MELAKIM ÁLEF (1 REYES)', 'chapters': 22},
            'melakim_bet': {'name': 'MELAKIM BET (2 REYES)', 'chapters': 25},
            'ieshaihu': {'name': 'IESHAIÁHU (ISAÍAS)', 'chapters': 66},
            'irmiahu': {'name': 'IRMEIÁHU (JEREMÍAS)', 'chapters': 52},
            'iejezkel': {'name': 'IEJEZKEL (EZEQUIEL)', 'chapters': 48},
            'hosea': {'name': 'HOSEA (OSEAS)', 'chapters': 14},
            'ioel': {'name': 'IOEL (JOEL)', 'chapters': 4},
            'amos': {'name': 'AMÓS', 'chapters': 9},
            'obadiah': {'name': 'OBADIÁH (ABDÍAS)', 'chapters': 1},
            'ionah': {'name': 'IONÁH (JONÁS)', 'chapters': 4},
            'micah': {'name': 'MICÁH (MIQUEAS)', 'chapters': 7},
            'nahum': {'name': 'NAJUM (NAHÚM)', 'chapters': 3},
            'habakuk': {'name': 'HABAKUK (HABACUC)', 'chapters': 3},
            'tzefaniah': {'name': 'TZEFANIAH (SOFONÍAS)', 'chapters': 3},
            'hagai': {'name': 'HAGAI (HAGEO)', 'chapters': 2},
            'zejariah': {'name': 'ZEJARIAH (ZACARÍAS)', 'chapters': 14},
            'malaji': {'name': 'MALAJÍ (MALAQUÍAS)', 'chapters': 4},

            # Ketuvim (Escritos)
            'tehilim': {'name': 'TEHILIM (SALMOS)', 'chapters': 150},
            'mishlei': {'name': 'MISHLEI (PROVERBIOS)', 'chapters': 31},
            'iob': {'name': 'IOB (JOB)', 'chapters': 42},
            'shir_hashirim': {'name': 'SHIR HASHIRIM (CANTAR DE LOS CANTARES)', 'chapters': 8},
            'rut': {'name': 'RUT', 'chapters': 4},
            'eja': {'name': 'EJA (LAMENTACIONES)', 'chapters': 5},
            'kohelet': {'name': 'KOHELET (ECLESIASTÉS)', 'chapters': 12},
            'ester': {'name': 'ESTER', 'chapters': 10},
            'daniel': {'name': 'DANIEL', 'chapters': 12},
            'ezra': {'name': 'EZRA (ESDRAS)', 'chapters': 10},
            'nehemiah': {'name': 'NEHEMIÁH (NEHEMÍAS)', 'chapters': 13},
            'dibre_hayamim_alef': {'name': 'DIBRE HAYAMIM ÁLEF (1 CRÓNICAS)', 'chapters': 29},
            'dibre_hayamim_bet': {'name': 'DIBRE HAYAMIM BET (2 CRÓNICAS)', 'chapters': 36}
        }

    def read_file(self) -> str:
        """Lee el archivo de entrada"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def analyze_book_structure(self, text: str) -> Dict[str, Dict]:
        """Analiza la estructura de libros encontrada en el texto"""
        books_found = {}

        # Buscar todas las líneas que empiecen con # __
        lines = text.split('\n')
        book_lines = [(i, line) for i, line in enumerate(lines) if line.startswith('# __')]

        current_pos = 0
        for line_num, line in book_lines:
            # Extraer el nombre completo y hebreo
            # Patrón: # __NOMBRE_LIBRO*__TEXTO_HEBREO*
            match = re.match(r'# __(.+?)\*__(.+?)\*', line.strip())
            if match:
                full_name, hebrew_name = match.groups()
                full_name = full_name.strip()
                hebrew_name = hebrew_name.strip()

                # Extraer nombre en español si existe
                spanish_match = re.search(r'\(([^)]+)\)', full_name)
                spanish_name = spanish_match.group(1) if spanish_match else full_name

                # Crear clave simplificada
                book_key = self._normalize_book_name(full_name)

                if book_key in self.expected_books:
                    # Usar la posición de la línea como start_pos
                    start_pos = sum(len(lines[i]) + 1 for i in range(line_num))  # +1 por \n
                    books_found[book_key] = {
                        'full_name': full_name,
                        'hebrew_name': hebrew_name,
                        'spanish_name': spanish_name,
                        'start_pos': start_pos,
                        'expected_chapters': self.expected_books[book_key]['chapters']
                    }

        return books_found

    def _normalize_book_name(self, name: str) -> str:
        """Normalize book names to create consistent keys"""
        # Direct mapping of exact names from the file to expected keys
        exact_mappings = {
            'TORAH - BERESHIT (GÉNESIS)': 'bereshit',
            'SHEMOT (ÉXODO)': 'shemot',
            'VAIKRÁ (LEVÍTICO)': 'vaikra',
            'BAMIDBAR (NÚMEROS)': 'bamidbar',
            'DEVARIM (DEUTERONOMIO)': 'devarim',
            'NEVIÍM - IEHOSHÚA (JOSUÉ)': 'iehosua',
            'SHOFTIM (JUECES)': 'shoftim',
            'SHEMUEL ÁLEF (1 SAMUEL)': 'shemuel_alef',
            'SHEMUEL BET (2 SAMUEL)': 'shemuel_bet',
            'MELAKIM ÁLEF (1 REYES)': 'melakim_alef',
            'MELAKIM BET (2 REYES)': 'melakim_bet',
            'IESHAIÁHU (ISAÍAS)': 'ieshaihu',
            'IRMEIÁHU (JEREMÍAS)': 'irmiahu',
            'IEJEZKEL (EZEQUIEL)': 'iejezkel',
            'HOSEA (OSEAS)': 'hosea',
            'IOEL (JOEL)': 'ioel',
            'AMÓS': 'amos',
            'OBADIÁH (ABDÍAS)': 'obadiah',
            'IONÁH (JONÁS)': 'ionah',
            'MICÁH (MIQUEAS)': 'micah',
            'NAJUM (NAHÚM)': 'nahum',
            'HABAKUK (HABACUC)': 'habakuk',
            'TZEFANIAH (SOFONÍAS)': 'tzefaniah',
            'HAGAI (HAGEO)': 'hagai',
            'ZEJARIAH (ZACARÍAS)': 'zejariah',
            'MALAJÍ (MALAQUÍAS)': 'malaji',
            'KETUVIM - TEHILIM (SALMOS)': 'tehilim',
            'MISHLEI (PROVERBIOS)': 'mishlei',
            'IOB (JOB)': 'iob',
            'SHIR HASHIRIM (CANTAR DE LOS CANTARES)': 'shir_hashirim',
            'RUT': 'rut',
            'EIJÁH (LAMENTACIONES)': 'eja',
            'KOHELET (ECLESIASTÉS)': 'kohelet',
            'ESTER': 'ester',
            'DANIEL': 'daniel',
            'EZRA (ESDRAS)': 'ezra',
            'NEHEMIÁH (NEHEMÍAS)': 'nehemiah',
            'DIBRE HAYAMIM ÁLEF (1 CRÓNICAS)': 'dibre_hayamim_alef',
            'DIBRE HAYAMIM BET (2 CRÓNICAS)': 'dibre_hayamim_bet'
        }

        # Try exact match first
        if name in exact_mappings:
            return exact_mappings[name]

        # If no exact match, try partial matching (for variations)
        name_lower = name.lower()
        for key, value in exact_mappings.items():
            if key.lower() in name_lower or value in name_lower:
                return value

        # Last resort: return lowercase version
        return name.lower().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    def validate_chapter_structure(self, text: str, book_key: str, book_info: Dict) -> List[str]:
        """Valida la estructura de capítulos de un libro"""
        issues = []

        # Extraer la sección del libro
        book_start = book_info['start_pos']
        # Encontrar el siguiente libro o el final
        next_book_keys = list(self.expected_books.keys())
        current_index = next_book_keys.index(book_key) if book_key in next_book_keys else -1

        if current_index >= 0 and current_index + 1 < len(next_book_keys):
            next_book = next_book_keys[current_index + 1]
            next_book_name = self.expected_books[next_book]['name'].split(' (')[0]
            next_book_pattern = f'# __{re.escape(next_book_name)}'
            next_match = re.search(next_book_pattern, text[book_start:])
            if next_match:
                book_end = book_start + next_match.start()
            else:
                book_end = len(text)
        else:
            book_end = len(text)

        book_content = text[book_start:book_end]

        # Buscar capítulos (patrón __número__)
        chapter_pattern = r'^__(\d+)__$'
        chapters_found = []
        lines = book_content.split('\n')

        for i, line in enumerate(lines):
            match = re.match(chapter_pattern, line.strip())
            if match:
                chapter_num = int(match.group(1))
                chapters_found.append(chapter_num)

        # Validar capítulos
        expected_chapters = book_info['expected_chapters']
        found_count = len(set(chapters_found))  # Usar set para eliminar duplicados

        if found_count != expected_chapters:
            issues.append(f"Libro {book_key}: Esperados {expected_chapters} capítulos, encontrados {found_count}")

        # Verificar duplicados
        duplicates = [x for x in chapters_found if chapters_found.count(x) > 1]
        if duplicates:
            unique_duplicates = list(set(duplicates))
            issues.append(f"Libro {book_key}: Capítulos duplicados: {unique_duplicates}")

        # Verificar secuencia
        sorted_chapters = sorted(set(chapters_found))
        expected_sequence = list(range(1, expected_chapters + 1))
        if sorted_chapters != expected_sequence:
            missing = [x for x in expected_sequence if x not in sorted_chapters]
            extra = [x for x in sorted_chapters if x not in expected_sequence]
            if missing:
                issues.append(f"Libro {book_key}: Capítulos faltantes: {missing}")
            if extra:
                issues.append(f"Libro {book_key}: Capítulos extra: {extra}")

        return issues

    def clean_duplicate_markers(self, text: str) -> str:
        """Limpia marcadores duplicados de capítulos y versículos"""
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Verificar si hay marcadores duplicados de capítulo al inicio de línea
            # Patrón: __número____número__ al inicio de línea
            duplicate_pattern = r'^(__\d+__)(\s*__)\1'
            if re.match(duplicate_pattern, line):
                # Mantener solo el primer marcador
                line = re.sub(duplicate_pattern, r'\1\2', line)

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def validate_verse_structure(self, text: str) -> List[str]:
        """Valida la estructura general de versículos"""
        issues = []

        # Buscar versículos sin número de capítulo precedente
        lines = text.split('\n')
        current_chapter = None

        for i, line in enumerate(lines):
            # Detectar capítulo
            chapter_match = re.match(r'^__(\d+)__$', line.strip())
            if chapter_match:
                current_chapter = int(chapter_match.group(1))
                continue

            # Si estamos en un capítulo, buscar versículos
            if current_chapter:
                # Buscar versículos en la línea (patrón __número__)
                verse_matches = re.findall(r'__(\d+)__', line)
                if verse_matches:
                    # Verificar que los números de versículo sean válidos
                    for verse_num in verse_matches:
                        try:
                            verse_int = int(verse_num)
                            if verse_int <= 0:
                                issues.append(f"Capítulo {current_chapter}, línea {i+1}: Versículo inválido {verse_num}")
                        except ValueError:
                            issues.append(f"Capítulo {current_chapter}, línea {i+1}: Número de versículo no válido '{verse_num}'")

        return issues

    def generate_cleaned_file(self, text: str) -> str:
        """Genera el archivo limpiado"""
        # Aplicar limpiezas
        cleaned_text = self.clean_duplicate_markers(text)

        return cleaned_text

    def process(self):
        """Proceso principal de limpieza"""
        print("Iniciando limpieza del archivo Tanaj...")

        # Leer archivo
        text = self.read_file()
        print(f"Archivo leído: {len(text)} caracteres")

        # Analizar estructura de libros
        books_found = self.analyze_book_structure(text)
        print(f"Libros encontrados: {len(books_found)}")

        # Validar cada libro
        all_issues = []
        for book_key, book_info in books_found.items():
            print(f"Validando {book_key}...")
            issues = self.validate_chapter_structure(text, book_key, book_info)
            if issues:
                all_issues.extend(issues)
                for issue in issues:
                    print(f"  ⚠️  {issue}")

        # Validar estructura general de versículos
        print("Validando estructura de versículos...")
        verse_issues = self.validate_verse_structure(text)
        if verse_issues:
            all_issues.extend(verse_issues)
            for issue in verse_issues[:10]:  # Mostrar solo los primeros 10
                print(f"  ⚠️  {issue}")
            if len(verse_issues) > 10:
                print(f"  ... y {len(verse_issues) - 10} problemas más")

        # Generar archivo limpiado
        cleaned_text = self.generate_cleaned_file(text)

        # Guardar archivo limpiado
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        print(f"\nArchivo limpiado guardado como: {self.output_file}")

        # Resumen
        total_issues = len(all_issues)
        if total_issues == 0:
            print("✅ No se encontraron problemas en la estructura")
        else:
            print(f"⚠️  Se encontraron {total_issues} problemas")
            print("Se recomienda revisar manualmente antes de procesar")

        print("\nLimpieza completada!")


def main():
    cleaner = TTHTanajCleaner()
    cleaner.process()


if __name__ == '__main__':
    main()
