#!/usr/bin/env python3
"""
TTH Sodot, Iaacob, Iehudah Processor - Estructura el contenido de la Traducción Textual del Hebreo
para Santiago (Iaacob), Judas (Iehudáh) y Apocalipsis (Sodot) desde formato Markdown a JSON similar a TS2009.

Formato objetivo:
- Cada capítulo tiene un archivo JSON separado (01.json, 02.json, etc.)
- Estructura compatible con la app Davar
- Incluye detección de términos hebreos
- Mantiene los comentarios en el texto tal cual
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any


class TTHSodotIaacobIehudahProcessor:
    def __init__(self, input_file: str = 'sodot_iaacob_iehudah.md'):
        self.input_file = input_file
        self.output_dir = 'draft'
        self.books_info = {
            'iaacob': {
                'tth_name': 'Iaacob',
                'hebrew_name': 'יעקב',
                'english_name': 'James',
                'spanish_name': 'Santiago',
                'book_code': 'james',
                'expected_chapters': 5
            },
            'iehudah': {
                'tth_name': 'Iehudáh',
                'hebrew_name': 'יהודה',
                'english_name': 'Jude',
                'spanish_name': 'Judas',
                'book_code': 'jude',
                'expected_chapters': 1
            },
            'sodot': {
                'tth_name': 'Sodot',
                'hebrew_name': 'סודות',
                'english_name': 'Revelation',
                'spanish_name': 'Apocalipsis',
                'book_code': 'revelation',
                'expected_chapters': 22
            }
        }

        # Términos hebreos comunes para detectar (del glosario del archivo y términos comunes)
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
            'Ha\'Satán': 'El adversario',
            'Kadosh': 'Apartado, Santo',
            'Teshuváh': 'Retorno, arrepentimiento',
            'Malajim': 'Mensajeros, ángeles',
            'malaj': 'mensajero, ángel',
            'Tzebaot': 'Ejércitos',
            'Hejal': 'Santuario, Templo',
            'Ierushaláim': 'Jerusalén',
            'Iehudáh': 'Judá',
            'Iehudí': 'Judío',
            'Iehudim': 'Judíos',
            'Mitzráim': 'Egipto',
            'Shofar': 'Cuerno de carnero',
            'shofarot': 'Cuernos de carnero (plural)',
            'Menorah': 'Candelabro de oro',
            'menorot': 'Candelabros de oro (plural)',
            'Gei Hinom': 'Valle de Hinom, Gehena',
            'Iaacob': 'Santiago, Jacobo',
            'Iehudáh': 'Judas',
            'Iojanán': 'Juan',
            'Mijael': 'Miguel',
            'Moshéh': 'Moisés',
            'Rajab': 'Rahab',
            'Rujot': 'Espíritus, Vientos (plural)',
            'satanim': 'adversarios, demonios',
            'kedoshim': 'apartados, santos',
            'Ketuvim': 'Escrituras',
            'jésed': 'bondad',
            'rajamim': 'compasión',
            'tikváh': 'esperanza',
            'dat': 'decreto, ley',
            'Torah': 'instrucción, ley',
            'neshamáh': 'persona que respira',
            'neshamot': 'personas que respiran (plural)',
            'néfesh': 'alma, persona',
            'sodot': 'secretos, misterios',
            'tanín': 'serpiente, reptil',
            'simán': 'marca',
            'Mashíaj': 'Ungido, Mesías',
            'Mishkán': 'Tabernáculo',
            'ajlamáh': 'amatista, jaspe rojo',
            'bat kol': 'voz de los cielos, eco',
            'Har Meguidón': 'Monte de Meguidón',
            'Har Meguidón': 'Monte de Meguidón',
            'Harmagedón': 'Armagedón',
            'Oy ve\' Aháh': 'Ay y Ah',
            'Mélej ha\'mlajim ve\'Adón ha\'adonim': 'Rey de los reyes y Amo de los amos',
            'Haleluyah': '¡Alaben a Yah!'
        }

    def read_markdown(self) -> str:
        """Lee el archivo markdown"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def split_into_books(self, text: str) -> Dict[str, str]:
        """Divide el texto en los tres libros"""
        books = {}
        
        # Encontrar los límites de cada libro
        iaacob_match = re.search(r'\*\*IAACOB \(SANTIAGO\)\*\*', text, re.IGNORECASE)
        iehudah_match = re.search(r'\*\*IEHUDÁH \(JUDAS\)\*\*', text, re.IGNORECASE)
        sodot_match = re.search(r'\*\*SODOT \(APOCALIPSIS\)\*\*', text, re.IGNORECASE)
        
        if iaacob_match and iehudah_match and sodot_match:
            # Extraer Iaacob (Santiago) - desde el inicio hasta Iehudáh
            books['iaacob'] = text[iaacob_match.start():iehudah_match.start()]
            
            # Extraer Iehudáh (Judas) - desde Iehudáh hasta Sodot
            books['iehudah'] = text[iehudah_match.start():sodot_match.start()]
            
            # Extraer Sodot (Apocalipsis) - desde Sodot hasta el final (excluyendo fotografías)
            # Buscar el final del contenido (antes de "FOTOGRAFÍAS DE")
            fotografias_match = re.search(r'FOTOGRAFÍAS DE', text)
            if fotografias_match:
                books['sodot'] = text[sodot_match.start():fotografias_match.start()]
            else:
                books['sodot'] = text[sodot_match.start():]
        elif iaacob_match and iehudah_match:
            # Si no hay Sodot, solo procesar los dos primeros
            books['iaacob'] = text[iaacob_match.start():iehudah_match.start()]
            books['iehudah'] = text[iehudah_match.start():]
        
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
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar inicio de capítulo - **número** seguido de línea vacía o texto
            # Puede aparecer como **1** o **1** seguido de texto
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
                i += 1
                
                # Saltar líneas vacías y títulos en cursiva después del número de capítulo
                while i < len(lines) and (not lines[i].strip() or 
                                          lines[i].strip().startswith('*') and 
                                          not re.match(r'^\*\*\d+\*\*', lines[i].strip())):
                    i += 1
                
                # Verificar si la siguiente línea es el versículo 1 sin marcador
                if i < len(lines):
                    next_line = lines[i].strip()
                    # Si la línea siguiente no es un versículo marcado con **número**, es el versículo 1
                    if not re.match(r'^\*\*\d+\*\*', next_line) and next_line:
                        current_verse_num = 1
                        current_verse_text = [next_line]
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
                            # Limpiar texto pero mantener comentarios
                            verse_text = self.clean_text_preserve_comments(verse_text)
                            current_verses.append({
                                'verse': current_verse_num,
                                'text': verse_text,
                                'hebrew_terms': self.extract_hebrew_terms(verse_text)
                            })
                    
                    # Iniciar nuevo versículo
                    current_verse_num = int(verse_match.group(1))
                    current_verse_text = [verse_match.group(2)]
                    i += 1
                    
                    # Caso especial: si el versículo es solo un comentario corto, continuar leyendo
                    # las siguientes líneas que no tengan marcador de versículo como parte del mismo versículo
                    if i < len(lines):
                        # Verificar si la siguiente línea es vacía y luego hay texto sin marcador
                        next_line_idx = i
                        # Saltar líneas vacías
                        while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                            next_line_idx += 1
                        
                        # Si después de líneas vacías hay texto sin marcador de versículo, incluirlo
                        if next_line_idx < len(lines):
                            next_line = lines[next_line_idx].strip()
                            # Si no es un versículo nuevo ni un título en cursiva solo, incluirlo
                            if not re.match(r'^\*\*\d+\*\*', next_line) and next_line:
                                # Verificar que no sea solo un título en cursiva
                                if not (next_line.startswith('*') and len(next_line) < 100 and not '(' in next_line):
                                    current_verse_text.append(next_line)
                                    i = next_line_idx + 1
                                    continue
                    
                    continue
                
                # Si estamos en un versículo, agregar línea al texto (continuación del versículo)
                if current_verse_num is not None:
                    # Si la línea siguiente es otro versículo o capítulo, terminar este versículo
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        # Verificar si la siguiente línea es un nuevo versículo o capítulo
                        if re.match(r'^\*\*\d+\*\*', next_line):
                            # Guardar versículo actual
                            verse_text = ' '.join(current_verse_text).strip()
                            if verse_text:
                                verse_text = self.clean_text_preserve_comments(verse_text)
                                current_verses.append({
                                    'verse': current_verse_num,
                                    'text': verse_text,
                                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                                })
                            current_verse_num = None
                            current_verse_text = []
                        elif line and not (line.startswith('*') and not re.match(r'^\*\*\d+\*\*', line)):
                            # Continuar agregando al versículo actual (ignorar títulos en cursiva solos)
                            current_verse_text.append(line)
                    elif line and not (line.startswith('*') and not re.match(r'^\*\*\d+\*\*', line)):
                        current_verse_text.append(line)
            
            i += 1
        
        # Guardar último versículo y capítulo
        if current_verse_num is not None:
            verse_text = ' '.join(current_verse_text).strip()
            if verse_text:
                verse_text = self.clean_text_preserve_comments(verse_text)
                current_verses.append({
                    'verse': current_verse_num,
                    'text': verse_text,
                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                })
        
        if current_chapter is not None and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })
        
        return chapters

    def clean_text_preserve_comments(self, text: str) -> str:
        """Limpia el texto preservando todos los comentarios entre paréntesis"""
        # Remover solo el formato markdown básico (negrita, cursiva) pero preservar todo el contenido
        modified_text = text
        
        # Remover negrita **texto** -> texto
        modified_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', modified_text)
        
        # Remover cursiva *texto* -> texto, pero proteger los términos dentro de paréntesis
        # Primero, proteger los comentarios entre paréntesis que pueden contener asteriscos
        protected_parts = []
        protected_pattern = r'\([^)]*\)'
        
        def protect_replace(match):
            protected_id = f"__PROTECTED_{len(protected_parts)}__"
            protected_parts.append(match.group(0))
            return protected_id
        
        # Proteger comentarios entre paréntesis
        modified_text = re.sub(protected_pattern, protect_replace, modified_text)
        
        # Remover cursiva *texto* -> texto (solo si no está en contexto de término hebreo)
        # Remover asteriscos simples que están solos o con espacios
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
        
        # Normalizar términos para evitar duplicados (ej: Yehovah/YEHOVAH)
        term_normalization = {}
        for term, explanation in self.hebrew_terms.items():
            normalized = term.upper()
            if normalized not in term_normalization:
                term_normalization[normalized] = (term, explanation)
        
        # Buscar términos en orden de longitud (más largos primero)
        sorted_terms = sorted(term_normalization.items(), key=lambda x: len(x[1][0]), reverse=True)
        
        found_normalized = set()  # Para evitar duplicados por normalización
        
        for normalized, (term, explanation) in sorted_terms:
            # Caso especial: "EL" solo debe detectarse si es realmente el término hebreo
            # No el pronombre "él" o palabras como "del", "al", etc.
            if term.upper() == 'EL':
                # Buscar "EL" como palabra completa en mayúsculas
                # Contextos válidos: "un EL", "del EL", "EL (Contracción de Elohim)", etc.
                # No debe ser: "él", "del", "al"
                pattern = re.compile(r'\bEL\b', re.MULTILINE)
                matches = pattern.finditer(text)
                found_el = False
                for match in matches:
                    start_pos = match.start()
                    end_pos = match.end()
                    # Obtener contexto alrededor de la coincidencia
                    context_start = max(0, start_pos - 10)
                    context_end = min(len(text), end_pos + 30)
                    context = text[context_start:context_end]
                    
                    # Verificar que:
                    # 1. Sea "EL" en mayúsculas (no "él" o "El")
                    matched_word = match.group(0)
                    if matched_word != 'EL':
                        continue
                    
                    # 2. No sea parte de palabras como "del", "al"
                    # Verificar los caracteres antes y después
                    char_before = text[max(0, start_pos - 1)] if start_pos > 0 else ' '
                    char_after = text[end_pos] if end_pos < len(text) else ' '
                    
                    # Si está precedido por 'd' o 'a' y seguido de espacio, probablemente es "del" o "al"
                    if char_before.lower() in 'da' and not char_before.isupper() and char_after in ' \n\t':
                        continue
                    
                    # 3. Preferir contexto que indique término hebreo (aparece con "un", "del", o paréntesis con "Elohim")
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
                # Usar límites de palabra para evitar coincidencias parciales
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
        print("Iniciando procesamiento de TTH Sodot, Iaacob, Iehudah desde Markdown...")
        
        # Leer markdown
        markdown_text = self.read_markdown()
        print(f"Markdown leído: {len(markdown_text)} caracteres")
        
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
    processor = TTHSodotIaacobIehudahProcessor()
    processor.process()


if __name__ == '__main__':
    main()

