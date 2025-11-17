#!/usr/bin/env python3
"""
TTH Besorah 2 Processor - Estructura el contenido de la Traducción Textual del Hebreo
para los libros de la Besorah (Evangelios y Hechos) desde formato Markdown a JSON.

Formato objetivo:
- Cada capítulo tiene un archivo JSON separado (01.json, 02.json, etc.)
- Estructura compatible con la app Davar
- Incluye detección de términos hebreos
- Procesa notas al pie de página
- Mantiene comentarios y referencias en el texto
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple


class TTHBesorah2Processor:
    def __init__(self, input_file: str = 'besorah.md'):
        self.input_file = input_file
        self.output_dir = 'draft'
        self.books_info = {
            'matityahu': {
                'tth_name': 'Matityáhu',
                'hebrew_name': 'מתתיהו',
                'english_name': 'Matthew',
                'spanish_name': 'Mateo',
                'book_code': 'matthew',
                'expected_chapters': 28
            },
            'markos': {
                'tth_name': 'Markos',
                'hebrew_name': 'מרקוס',
                'english_name': 'Mark',
                'spanish_name': 'Marcos',
                'book_code': 'mark',
                'expected_chapters': 16
            },
            'lukah': {
                'tth_name': 'Lukah',
                'hebrew_name': 'לוקס',
                'english_name': 'Luke',
                'spanish_name': 'Lucas',
                'book_code': 'luke',
                'expected_chapters': 24
            },
            'iojanan': {
                'tth_name': 'Iojanán',
                'hebrew_name': 'יוחנן',
                'english_name': 'John',
                'spanish_name': 'Juan',
                'book_code': 'john',
                'expected_chapters': 21
            },
            'maasei': {
                'tth_name': 'Maasei Hash\'lijim',
                'hebrew_name': 'מעשי השליחים',
                'english_name': 'Acts',
                'spanish_name': 'Hechos',
                'book_code': 'acts',
                'expected_chapters': 28
            }
        }

        # Términos hebreos comunes para detectar
        self.hebrew_terms = {
            'YEHOVAH': 'Tetragrámaton - Nombre de Dios',
            'Yehovah': 'Tetragrámaton - Nombre de Dios',
            'Yeshúa': 'Jesús en hebreo',
            'Mesías': 'El Ungido, Cristo',
            'Elohim': 'Dios, Poderoso',
            'Eloah': 'Singular de Elohim',
            'Elohah': 'Singular de Elohim',
            'EL': 'Versión corta de Elohim',
            'Adón': 'Señor, Amo',
            'Adonai': 'Señor, Amo',
            'Rúaj': 'Espíritu, viento, aliento',
            'Ha\'Kódesh': 'Santo',
            'Rúaj Ha\'Kódesh': 'Espíritu de Santidad',
            'emunah': 'fe, fidelidad, constancia',
            'shalom': 'paz, bienestar completo',
            'Ha\'satán': 'El adversario',
            'Ha\'Satán': 'El adversario',
            'Kadosh': 'Apartado, Santo',
            'Teshuváh': 'Retorno, arrepentimiento',
            'Malajim': 'Mensajeros, ángeles',
            'malaj': 'mensajero, ángel',
            'Tzebaot': 'Ejércitos',
            'Hejal': 'Santuario, Templo',
            'Ierushaláim': 'Jerusalén',
            'Ierushalem': 'Jerusalén',
            'Iehudáh': 'Judá',
            'Iehudí': 'Judío',
            'Iehudim': 'Judíos',
            'iehudim': 'Judíos',
            'Mitzráim': 'Egipto',
            'Shofar': 'Cuerno de carnero',
            'shofarot': 'Cuernos de carnero (plural)',
            'Menorah': 'Candelabro de oro',
            'menorot': 'Candelabros de oro (plural)',
            'Gei Hinom': 'Valle de Hinom, Gehena',
            'Guei Hinom': 'Valle de Hinom, Gehena',
            'Iojanán': 'Juan',
            'Iaacob': 'Santiago, Jacobo',
            'Iehudáh': 'Judas',
            'Moshéh': 'Moisés',
            'Rajab': 'Rahab',
            'Rujot': 'Espíritus, Vientos (plural)',
            'Galil': 'Galilea',
            'Iardén': 'Jordán',
            'Bet Léjem': 'Belén',
            'Natzrat': 'Nazaret',
            'Notzrí': 'Nazareno',
            'Pésaj': 'Pascua',
            'tefilah': 'oración',
            'Ben Ha\'Adam': 'Hijo del Hombre',
            'av': 'Padre',
            'olam': 'mundo, era, tiempo',
            'man': 'Maná',
            'Rabí': 'Rabino, Maestro',
            'perushim': 'Fariseos',
            'tzadikim': 'Saduceos',
            'shomroní': 'Samaritano',
            'guelilí': 'Galileo',
            'Ieshaiáhu': 'Isaías',
            'Irmiáh': 'Jeremías',
            'Ionah': 'Jonás',
            'Eliyáhu': 'Elías',
            'Shelomóh': 'Salomón',
            'Migdalit': 'Magdalena',
            'kirení': 'Cireneo',
            'Gólgota': 'Gólgota',
            'Gulgolet': 'Calavera',
            'goral': 'suerte, suertes',
            'Matzot': 'Pan sin levadura',
            'Ish-Kariot': 'Iscariote',
            'Bet Aniah': 'Betania',
            'Eleazar': 'Lázaro',
            'Martah': 'Marta',
            'Miriam': 'María',
            'Filipos': 'Felipe',
            'Andreas': 'Andrés',
            'Shimón': 'Simón',
            'Kefa': 'Pedro',
            'Tomáh': 'Tomás',
            'Zekariáhu': 'Zacarías',
            'Ieshaiáhu': 'Isaías'
        }

        # Diccionario de notas al pie extraídas del documento
        self.footnote_definitions = {}

    def read_markdown(self) -> str:
        """Lee el archivo markdown"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_footnote_definitions(self, text: str):
        """Extrae las definiciones de notas al pie desde el final del documento"""
        # Buscar el patrón [^número]: definición
        footnote_pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n|$)'
        matches = re.finditer(footnote_pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            footnote_num = match.group(1)
            footnote_def = match.group(2).strip()
            self.footnote_definitions[footnote_num] = footnote_def

    def split_into_books(self, text: str) -> Dict[str, str]:
        """Divide el texto en los diferentes libros"""
        books = {}
        
        # Encontrar los límites de cada libro
        matityahu_match = re.search(r'\*\*MATITYÁHU \(MATEO\)\*\*', text, re.IGNORECASE)
        markos_match = re.search(r'\*\*MARKO \(MARCOS\)\*\*', text, re.IGNORECASE)
        lukah_match = re.search(r'\*\*LUKAH \(LUCAS\)\*\*', text, re.IGNORECASE)
        iojanan_match = re.search(r'\*\*IOJANÁN \(JUAN\)\*\*', text, re.IGNORECASE)
        maasei_match = re.search(r'\*\*HECHOS DE LOS ENVIADOS\*\*|\(MAASEI HASH\'LIJIM\)', text, re.IGNORECASE)
        
        matches = []
        if matityahu_match:
            matches.append(('matityahu', matityahu_match.start()))
        if markos_match:
            matches.append(('markos', markos_match.start()))
        if lukah_match:
            matches.append(('lukah', lukah_match.start()))
        if iojanan_match:
            matches.append(('iojanan', iojanan_match.start()))
        if maasei_match:
            matches.append(('maasei', maasei_match.start()))
        
        # Ordenar por posición
        matches.sort(key=lambda x: x[1])
        
        # Extraer cada libro
        for i, (book_key, start_pos) in enumerate(matches):
            if i + 1 < len(matches):
                # El libro va desde start_pos hasta el inicio del siguiente
                end_pos = matches[i + 1][1]
                books[book_key] = text[start_pos:end_pos]
            else:
                # El último libro va hasta el final (antes de las notas al pie)
                # Buscar el inicio de las notas al pie (líneas que empiezan con [^)
                footnote_start_match = re.search(r'\n\[\^\d+\]:', text[start_pos:])
                if footnote_start_match:
                    books[book_key] = text[start_pos:start_pos + footnote_start_match.start()]
                else:
                    books[book_key] = text[start_pos:]
        
        return books

    def extract_chapters(self, book_text: str, book_key: str) -> List[Dict[str, Any]]:
        """Extrae los capítulos de un libro desde el markdown"""
        chapters = []
        
        # Dividir el texto en líneas
        lines = book_text.split('\n')
        current_chapter = None
        current_verses = []
        current_verse_num = None
        current_verse_text = []
        in_chapter_section = False
        skip_empty_lines = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Saltar línea vacía si acabamos de procesar un capítulo/versículo
            if not line and skip_empty_lines:
                i += 1
                continue
            
            skip_empty_lines = False
            
            # Detectar inicio de capítulo - **número** seguido de línea vacía o texto
            chapter_match = re.match(r'^\*\*(\d+)\*\*\s*$', line)
            if chapter_match:
                # Guardar capítulo anterior si existe
                if current_chapter is not None and current_verses:
                    chapters.append({
                        'chapter': current_chapter,
                        'verses': current_verses
                    })
                
                # Iniciar nuevo capítulo
                current_chapter = int(chapter_match.group(1))
                current_verses = []
                current_verse_num = None
                current_verse_text = []
                in_chapter_section = True
                skip_empty_lines = True
                i += 1
                continue
            
            # Solo procesar versículos si estamos en una sección de capítulo
            if in_chapter_section:
                # Detectar versículo - patrón **número** seguido de texto en la misma línea
                verse_match = re.match(r'^\*\*(\d+)\*\*\s+(.+)$', line)
                if verse_match:
                    # Guardar versículo anterior si existe
                    if current_verse_num is not None:
                        verse_text = ' '.join(current_verse_text).strip()
                        if verse_text:
                            verse_text = self.clean_text_preserve_comments(verse_text)
                            # Procesar notas al pie
                            verse_text, footnotes = self.extract_footnotes(verse_text)
                            current_verses.append({
                                'verse': current_verse_num,
                                'text': verse_text,
                                'footnotes': footnotes,
                                'hebrew_terms': self.extract_hebrew_terms(verse_text)
                            })
                    
                    # Iniciar nuevo versículo
                    current_verse_num = int(verse_match.group(1))
                    current_verse_text = [verse_match.group(2)]
                    i += 1
                    
                    # Continuar leyendo líneas siguientes que no sean nuevos versículos/capítulos
                    while i < len(lines):
                        next_line = lines[i].strip()
                        
                        # Si es línea vacía, continuar
                        if not next_line:
                            i += 1
                            continue
                        
                        # Si es un nuevo versículo o capítulo, parar
                        if re.match(r'^\*\*\d+\*\*', next_line):
                            break
                        
                        # Si es solo un título en cursiva sin texto adicional, saltarlo
                        if next_line.startswith('*') and next_line.endswith('*') and len(next_line) < 100:
                            i += 1
                            continue
                        
                        # Agregar línea al versículo actual
                        current_verse_text.append(next_line)
                        i += 1
                    
                    skip_empty_lines = True
                    continue
            
            i += 1
        
        # Guardar último versículo y capítulo
        if current_verse_num is not None:
            verse_text = ' '.join(current_verse_text).strip()
            if verse_text:
                verse_text = self.clean_text_preserve_comments(verse_text)
                verse_text, footnotes = self.extract_footnotes(verse_text)
                current_verses.append({
                    'verse': current_verse_num,
                    'text': verse_text,
                    'footnotes': footnotes,
                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                })
        
        if current_chapter is not None and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })
        
        return chapters

    def extract_footnotes(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Extrae las notas al pie del texto y las reemplaza con superíndices"""
        footnotes = []
        
        # Buscar patrones [^número]
        footnote_pattern = r'\[\^(\d+)\]'
        matches = list(re.finditer(footnote_pattern, text))
        
        # Procesar de atrás hacia adelante para no afectar las posiciones
        modified_text = text
        footnote_markers = {
            '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
            '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '10': '¹⁰',
            '11': '¹¹', '12': '¹²', '13': '¹³', '14': '¹⁴', '15': '¹⁵'
        }
        
        # Función para convertir número a superíndice
        def num_to_superscript(num_str):
            superscript_map = {
                '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
                '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
            }
            return ''.join(superscript_map.get(digit, digit) for digit in num_str)
        
        # Función para extraer la palabra asociada a la nota al pie
        def extract_associated_word(text_before_marker: str) -> str:
            """Extrae la palabra más cercana antes del marcador de nota al pie"""
            text_before = text_before_marker.rstrip()
            
            # Buscar la última palabra directamente antes del marcador
            # Primero intentar con términos compuestos hebreos comunes
            # Términos compuestos conocidos que pueden tener espacios
            compound_terms = [
                (r"Rúaj\s+Ha['']Kódesh", "Rúaj Ha'Kódesh"),
                (r"Ben\s+Ha['']Adam", "Ben Ha'Adam"),
                (r"Bet\s+Léjem", "Bet Léjem"),
                (r"Bet\s+Aniah", "Bet Aniah"),
                (r"Kefar\s+Najum", "Kefar Najum"),
                (r"Gue\s+Shemanim", "Gue Shemanim"),
            ]
            
            # Verificar si termina con algún término compuesto (buscar desde el final)
            # Buscar en los últimos 50 caracteres para mejorar rendimiento
            # Pero también verificar que el término esté justo antes del marcador
            search_text = text_before[-50:] if len(text_before) > 50 else text_before
            for term_pattern, term_name in compound_terms:
                # Buscar el término compuesto que termine justo antes del final
                pattern = term_pattern + r'\s*$'
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    # Verificar que realmente termina ahí (no hay más texto después)
                    # El match ya asegura que está al final del search_text
                    return term_name  # Retornar el nombre normalizado del término
            
            # También intentar buscar términos compuestos más largos en todo el texto final
            # si el texto es corto (menos de 100 caracteres), buscar en todo
            if len(text_before) < 100:
                for term_pattern, term_name in compound_terms:
                    pattern = term_pattern + r'(?:\s|\.|,|;|:|!|\?|$)'  # Término seguido de espacio o puntuación
                    # Buscar todas las ocurrencias y tomar la última
                    matches = list(re.finditer(pattern, text_before, re.IGNORECASE))
                    if matches:
                        last_match = matches[-1]
                        # Verificar que está cerca del final (últimos 20 caracteres)
                        if len(text_before) - last_match.end() < 5:
                            return term_name
            
            # Si no es un término compuesto, buscar solo la última palabra
            # Buscar secuencia alfanumérica (incluyendo hebreo) con apostrofes/guiones
            # que termine justo antes del marcador
            simple_word_pattern = r'([\w\'-]+)\s*$'
            match = re.search(simple_word_pattern, text_before)
            
            if match:
                word = match.group(1).strip()
                # Limpiar puntuación final
                word = re.sub(r'[.,;:!?]+$', '', word)
                return word if word else ''
            
            return ''
        
        # Primero, extraer todas las palabras asociadas del texto original (antes de modificarlo)
        footnote_data = []
        for match in matches:
            footnote_num = match.group(1)
            marker = footnote_markers.get(footnote_num, num_to_superscript(footnote_num))
            definition = self.footnote_definitions.get(footnote_num, f'Nota al pie {footnote_num}')
            
            # Extraer la palabra asociada del texto original
            text_before = text[:match.start()]
            associated_word = extract_associated_word(text_before)
            
            footnote_data.append({
                'match': match,
                'footnote_num': footnote_num,
                'marker': marker,
                'definition': definition,
                'word': associated_word
            })
        
        # Procesar en orden inverso para reemplazar en el texto
        for data in reversed(footnote_data):
            match = data['match']
            
            # Reemplazar [^número] con superíndice
            modified_text = modified_text[:match.start()] + data['marker'] + modified_text[match.end():]
            
            # Agregar a la lista de notas (evitar duplicados)
            if not any(fn['number'] == data['footnote_num'] for fn in footnotes):
                footnotes.append({
                    'marker': data['marker'],
                    'number': data['footnote_num'],
                    'word': data['word'],
                    'explanation': data['definition']
                })
        
        # Ordenar notas por número
        footnotes.sort(key=lambda x: int(x['number']))
        
        return modified_text.strip(), footnotes

    def clean_text_preserve_comments(self, text: str) -> str:
        """Limpia el texto preservando todos los comentarios entre paréntesis y referencias"""
        modified_text = text
        
        # Remover negrita **texto** -> texto
        modified_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', modified_text)
        
        # Proteger comentarios entre paréntesis que pueden contener asteriscos
        protected_parts = []
        protected_pattern = r'\([^)]*\)'
        
        def protect_replace(match):
            protected_id = f"__PROTECTED_{len(protected_parts)}__"
            protected_parts.append(match.group(0))
            return protected_id
        
        # Proteger comentarios entre paréntesis
        modified_text = re.sub(protected_pattern, protect_replace, modified_text)
        
        # Remover cursiva *texto* -> texto (solo si no está en contexto de término hebreo)
        modified_text = re.sub(r'\*([^*\s]+)\*', r'\1', modified_text)
        modified_text = re.sub(r'\*(\s+)', r'\1', modified_text)
        modified_text = re.sub(r'(\s+)\*', r'\1', modified_text)
        
        # Restaurar partes protegidas
        for i, protected in enumerate(protected_parts):
            modified_text = modified_text.replace(f"__PROTECTED_{i}__", protected)
        
        # Limpiar espacios múltiples pero preservar espacios simples
        modified_text = re.sub(r'\s+', ' ', modified_text).strip()
        
        return modified_text

    def extract_hebrew_terms(self, text: str) -> List[Dict[str, str]]:
        """Extrae términos hebreos del texto"""
        terms_found = []
        
        # Normalizar términos para evitar duplicados
        term_normalization = {}
        for term, explanation in self.hebrew_terms.items():
            normalized = term.upper()
            if normalized not in term_normalization:
                term_normalization[normalized] = (term, explanation)
        
        # Buscar términos en orden de longitud (más largos primero)
        sorted_terms = sorted(term_normalization.items(), key=lambda x: len(x[1][0]), reverse=True)
        
        found_normalized = set()
        
        for normalized, (term, explanation) in sorted_terms:
            # Caso especial: "EL" solo debe detectarse si es realmente el término hebreo
            if term.upper() == 'EL':
                pattern = re.compile(r'\bEL\b', re.MULTILINE)
                matches = pattern.finditer(text)
                found_el = False
                for match in matches:
                    start_pos = match.start()
                    end_pos = match.end()
                    char_before = text[max(0, start_pos - 1)] if start_pos > 0 else ' '
                    char_after = text[end_pos] if end_pos < len(text) else ' '
                    
                    if char_before.lower() in 'da' and not char_before.isupper() and char_after in ' \n\t':
                        continue
                    
                    context_start = max(0, start_pos - 10)
                    context_end = min(len(text), end_pos + 30)
                    context = text[context_start:context_end]
                    context_lower = context.lower()
                    
                    if ('un el' in context_lower or 'del el' in context_lower or 'el (' in context or 
                        'elohim' in context_lower or 'contracción' in context_lower):
                        found_el = True
                        break
                
                if found_el:
                    terms_found.append({
                        'term': term,
                        'explanation': explanation
                    })
                    found_normalized.add(normalized)
            else:
                # Buscar el término considerando variaciones de capitalización
                pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                
                if pattern.search(text) and normalized not in found_normalized:
                    terms_found.append({
                        'term': term,
                        'explanation': explanation
                    })
                    found_normalized.add(normalized)
        
        return terms_found

    def create_json_structure(self, book_key: str, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Crea la estructura JSON final compatible con la app"""
        book_info = self.books_info[book_key]
        json_data = []
        
        for chapter_data in chapters:
            chapter_num = chapter_data['chapter']
            
            for verse_data in chapter_data['verses']:
                verse_entry = {
                    'book': book_key,
                    'book_tth_name': book_info['tth_name'],
                    'book_hebrew_name': book_info['hebrew_name'],
                    'book_english_name': book_info['english_name'],
                    'book_spanish_name': book_info['spanish_name'],
                    'chapter': chapter_num,
                    'verse': verse_data['verse'],
                    'status': 'present',
                    'tth': verse_data['text'],
                    'footnotes': verse_data.get('footnotes', []),
                    'hebrew_terms': verse_data.get('hebrew_terms', [])
                }
                json_data.append(verse_entry)
        
        return json_data

    def save_chapter_files(self, book_key: str, json_data: List[Dict[str, Any]]):
        """Guarda los archivos JSON por capítulo"""
        book_info = self.books_info[book_key]
        
        # Crear directorio con nombre del libro
        book_dir = f"{self.output_dir}/{book_key}"
        os.makedirs(book_dir, exist_ok=True)
        
        # Agrupar por capítulos
        chapters_data = {}
        for verse in json_data:
            chapter = verse['chapter']
            if chapter not in chapters_data:
                chapters_data[chapter] = []
            chapters_data[chapter].append(verse)
        
        # Guardar cada capítulo
        for chapter_num, verses in sorted(chapters_data.items()):
            filename = f"{chapter_num:02d}.json"
            filepath = f"{book_dir}/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(verses, f, ensure_ascii=False, indent=2)
            
            print(f"Guardado: {filepath} ({len(verses)} versículos)")
        
        # Guardar información del libro
        book_info_data = {
            **book_info,
            'total_chapters': len(chapters_data),
            'total_verses': len(json_data),
            'source_file': self.input_file,
            'processed_date': datetime.now().isoformat(),
            'processor_version': '1.0'
        }
        
        with open(f"{book_dir}/book_info.json", 'w', encoding='utf-8') as f:
            json.dump(book_info_data, f, ensure_ascii=False, indent=2)
        
        print(f"Guardado: {book_dir}/book_info.json")

    def process(self):
        """Proceso principal"""
        print("Iniciando procesamiento de TTH Besorah 2 desde Markdown...")
        
        # Leer markdown
        markdown_text = self.read_markdown()
        print(f"Markdown leído: {len(markdown_text)} caracteres")
        
        # Extraer definiciones de notas al pie
        self.extract_footnote_definitions(markdown_text)
        print(f"Definiciones de notas al pie encontradas: {len(self.footnote_definitions)}")
        
        # Dividir en libros
        books = self.split_into_books(markdown_text)
        print(f"Libros encontrados: {list(books.keys())}")
        
        # Procesar cada libro
        for book_key, book_text in books.items():
            print(f"\nProcesando {book_key}...")
            
            # Extraer capítulos
            chapters = self.extract_chapters(book_text, book_key)
            print(f"Capítulos encontrados: {len(chapters)}")
            
            # Crear estructura JSON
            json_data = self.create_json_structure(book_key, chapters)
            print(f"Versículos totales: {len(json_data)}")
            
            # Guardar archivos
            self.save_chapter_files(book_key, json_data)
        
        print("\nProcesamiento completado exitosamente!")


def main():
    processor = TTHBesorah2Processor()
    processor.process()


if __name__ == '__main__':
    main()

