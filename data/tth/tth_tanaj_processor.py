#!/usr/bin/env python3
"""
TTH Tanaj Processor - Structures the content of the Textual Translation of Hebrew
for Tanaj books from Markdown format to JSON.

Target format:
- Each chapter has a separate JSON file (01.json, 02.json, etc.)
- Structure compatible with the Davar app
- Includes Hebrew term detection
- Processes footnotes
- Includes section titles when applicable
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional


class TTHTanajProcessor:
    # Información de los libros del Tanaj (definida como atributo de clase)
    books_info = {
            'bereshit': {
                'tth_name': 'Bereshit',
                'hebrew_name': 'בראשית',
                'english_name': 'Genesis',
                'spanish_name': 'Génesis',
                'book_code': 'genesis',
                'expected_chapters': 50,
                'input_file': 'tanaj/bereshit.md',
                'section': 'torah',
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá'
            },
            'shemot': {
                'tth_name': 'Shemot',
                'hebrew_name': 'שמות',
                'english_name': 'Exodus',
                'spanish_name': 'Éxodo',
                'book_code': 'exodus',
                'expected_chapters': 40,
                'input_file': 'tanaj/shemot.md',
                'section': 'torah',
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá'
            },
            'vaikra': {
                'tth_name': 'Vaikra',
                'hebrew_name': 'ויקרא',
                'english_name': 'Leviticus',
                'spanish_name': 'Levítico',
                'book_code': 'leviticus',
                'expected_chapters': 27,
                'input_file': 'tanaj/vaikra.md',
                'section': 'torah',
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá'
            },
            'bamidbar': {
                'tth_name': 'Bamidbar',
                'hebrew_name': 'במדבר',
                'english_name': 'Numbers',
                'spanish_name': 'Números',
                'book_code': 'numbers',
                'expected_chapters': 36,
                'input_file': 'tanaj/bamidbar.md',
                'section': 'torah',
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá'
            },
            'devarim': {
                'tth_name': 'Devarim',
                'hebrew_name': 'דברים',
                'english_name': 'Deuteronomy',
                'spanish_name': 'Deuteronomio',
                'book_code': 'deuteronomy',
                'expected_chapters': 34,
                'input_file': 'tanaj/devarim.md',
                'section': 'torah',
                'section_hebrew': 'תורה',
                'section_english': 'Torah',
                'section_spanish': 'Torá'
            },
            'iehosua': {
                'tth_name': 'Iehoshúa',
                'hebrew_name': 'יהושע',
                'english_name': 'Joshua',
                'spanish_name': 'Josué',
                'book_code': 'joshua',
                'expected_chapters': 24,
                'input_file': 'tanaj/iehosua.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'shoftim': {
                'tth_name': 'Shoftim',
                'hebrew_name': 'שפטים',
                'english_name': 'Judges',
                'spanish_name': 'Jueces',
                'book_code': 'judges',
                'expected_chapters': 21,
                'input_file': 'tanaj/shoftim.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'shemuel_alef': {
                'tth_name': 'Shemuel Alef',
                'hebrew_name': 'א שמואל',
                'english_name': '1 Samuel',
                'spanish_name': '1 Samuel',
                'book_code': '1_samuel',
                'expected_chapters': 31,  # Actual: 30 (capítulo 27 no está en fuente)
                'input_file': 'tanaj/shemuel_alef.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'shemuel_bet': {
                'tth_name': 'Shemuel Bet',
                'hebrew_name': 'ב שמואל',
                'english_name': '2 Samuel',
                'spanish_name': '2 Samuel',
                'book_code': '2_samuel',
                'expected_chapters': 24,
                'input_file': 'tanaj/shemuel_bet.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'melajim_alef': {
                'tth_name': 'Melajim Alef',
                'hebrew_name': 'א מלכים',
                'english_name': '1 Kings',
                'spanish_name': '1 Reyes',
                'book_code': '1_kings',
                'expected_chapters': 22,
                'input_file': 'tanaj/melajim_alef.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'melajim_bet': {
                'tth_name': 'Melajim Bet',
                'hebrew_name': 'ב מלכים',
                'english_name': '2 Kings',
                'spanish_name': '2 Reyes',
                'book_code': '2_kings',
                'expected_chapters': 25,
                'input_file': 'tanaj/melajim_bet.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'ieshaiahu': {
                'tth_name': 'Ieshaiáhu',
                'hebrew_name': 'ישעיהו',
                'english_name': 'Isaiah',
                'spanish_name': 'Isaías',
                'book_code': 'isaiah',
                'expected_chapters': 66,
                'input_file': 'tanaj/ieshaiahu.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'irmeiahu': {
                'tth_name': 'Irmeiáhu',
                'hebrew_name': 'ירמיהו',
                'english_name': 'Jeremiah',
                'spanish_name': 'Jeremías',
                'book_code': 'jeremiah',
                'expected_chapters': 52,
                'input_file': 'tanaj/irmeiahu.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'iejezkel': {
                'tth_name': 'Iejezkel',
                'hebrew_name': 'יחזקאל',
                'english_name': 'Ezekiel',
                'spanish_name': 'Ezequiel',
                'book_code': 'ezekiel',
                'expected_chapters': 48,
                'input_file': 'tanaj/iejezkel.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'hoshea': {
                'tth_name': 'Hoshea',
                'hebrew_name': 'הושע',
                'english_name': 'Hosea',
                'spanish_name': 'Oseas',
                'book_code': 'hosea',
                'expected_chapters': 14,
                'input_file': 'tanaj/hoshea.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'ioel': {
                'tth_name': 'Ioel',
                'hebrew_name': 'יואל',
                'english_name': 'Joel',
                'spanish_name': 'Joel',
                'book_code': 'joel',
                'expected_chapters': 3,
                'input_file': 'tanaj/ioel.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'amos': {
                'tth_name': 'Amós',
                'hebrew_name': 'עמוס',
                'english_name': 'Amos',
                'spanish_name': 'Amós',
                'book_code': 'amos',
                'expected_chapters': 9,
                'input_file': 'tanaj/amos.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'ionah': {
                'tth_name': 'Ionah',
                'hebrew_name': 'יונה',
                'english_name': 'Jonah',
                'spanish_name': 'Jonás',
                'book_code': 'jonah',
                'expected_chapters': 4,
                'input_file': 'tanaj/ionah.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'micah': {
                'tth_name': 'Micah',
                'hebrew_name': 'מיכה',
                'english_name': 'Micah',
                'spanish_name': 'Miqueas',
                'book_code': 'micah',
                'expected_chapters': 7,
                'input_file': 'tanaj/micah.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'najum': {
                'tth_name': 'Najum',
                'hebrew_name': 'נחום',
                'english_name': 'Nahum',
                'spanish_name': 'Nahum',
                'book_code': 'nahum',
                'expected_chapters': 3,
                'input_file': 'tanaj/najum.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'jabakuk': {
                'tth_name': 'Jabakuk',
                'hebrew_name': 'חבקוק',
                'english_name': 'Habakkuk',
                'spanish_name': 'Habacuc',
                'book_code': 'habakkuk',
                'expected_chapters': 3,
                'input_file': 'tanaj/jabakuk.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'tzefaniah': {
                'tth_name': 'Tzefaniah',
                'hebrew_name': 'צפניה',
                'english_name': 'Zephaniah',
                'spanish_name': 'Sofonías',
                'book_code': 'zephaniah',
                'expected_chapters': 3,
                'input_file': 'tanaj/tzefaniah.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'jagai': {
                'tth_name': 'Jagai',
                'hebrew_name': 'חגי',
                'english_name': 'Haggai',
                'spanish_name': 'Hageo',
                'book_code': 'haggai',
                'expected_chapters': 2,
                'input_file': 'tanaj/jagai.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'zejariah': {
                'tth_name': 'Zejariah',
                'hebrew_name': 'זכריה',
                'english_name': 'Zechariah',
                'spanish_name': 'Zacarías',
                'book_code': 'zechariah',
                'expected_chapters': 14,
                'input_file': 'tanaj/zejariah.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'malaji': {
                'tth_name': 'Malaji',
                'hebrew_name': 'מלאכי',
                'english_name': 'Malachi',
                'spanish_name': 'Malaquías',
                'book_code': 'malachi',
                'expected_chapters': 4,
                'input_file': 'tanaj/malaji.md',
                'section': 'neviim',
                'section_hebrew': 'נביאים',
                'section_english': 'Prophets',
                'section_spanish': 'Profetas'
            },
            'tehilim': {
                'tth_name': 'Tehilim',
                'hebrew_name': 'תהלים',
                'english_name': 'Psalms',
                'spanish_name': 'Salmos',
                'book_code': 'psalms',
                'expected_chapters': 150,
                'input_file': 'tanaj/tehilim.md',
                'section': 'ketuvim',
                'section_hebrew': 'כתובים',
                'section_english': 'Writings',
                'section_spanish': 'Escritos'
            },
            'mishlei': {
                'tth_name': 'Mishlei',
                'hebrew_name': 'משלי',
                'english_name': 'Proverbs',
                'spanish_name': 'Proverbios',
                'book_code': 'proverbs',
                'expected_chapters': 31,
                'input_file': 'tanaj/mishlei.md',
                'section': 'ketuvim',
                'section_hebrew': 'כתובים',
                'section_english': 'Writings',
                'section_spanish': 'Escritos'
            }
    }
    
    def __init__(self, input_file: str = None, book_key: str = 'bereshit'):
        self.book_key = book_key
        self.output_dir = 'draft'
        # If input_file is not provided, use the one from book_key
        if input_file is None:
            if book_key in self.books_info:
                self.input_file = self.books_info[book_key]['input_file']
            else:
                raise ValueError(f"Book key '{book_key}' not found in books_info")
        else:
            self.input_file = input_file
        
        # Common Hebrew terms to detect
        self.hebrew_terms = {
            'YEHOVAH': 'Tetragrámaton - Nombre de Elohim',
            'Yehovah': 'Tetragrámaton - Nombre de Elohim',
            'יהוה': 'Tetragrámaton - Nombre de Elohim',
            'Yeshúa': 'Jesús en hebreo',
            'Mesías': 'El Ungido, Cristo',
            'Elohim': 'Dios, Poderoso',
            'Eloah': 'Singular de Elohim',
            'Elohah': 'Singular de Elohim',
            'EL': 'Versión corta de Elohim',
            'Adón': 'Señor, Amo',
            'Adonai': 'Señor, Amo',
            'Rúaj': 'Espíritu, viento, aliento',
            "Ha'Kódesh": 'Santo',
            "Rúaj Ha'Kódesh": 'Espíritu de Santidad',
            'emunah': 'fe, fidelidad, constancia',
            'shalom': 'paz, bienestar completo',
            "Ha'Satán": 'El adversario',
            "Ha'satán": 'El adversario',
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
            'mitzrim': 'Egipcios',
            'mitzrit': 'Egipcia',
            'Shofar': 'Cuerno de carnero',
            'shofarot': 'Cuernos de carnero (plural)',
            'Menorah': 'Candelabro de oro',
            'menorot': 'Candelabros de oro (plural)',
            'Gei Hinom': 'Valle de Hinom, Gehena',
            'Guei Hinom': 'Valle de Hinom, Gehena',
            'Iojanán': 'Juan',
            'Iaacob': 'Santiago, Jacobo',
            'Iehudáh': 'Judá',
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
            "Ben Ha'Adam": 'Hijo del Hombre',
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
            'Ieshaiáhu': 'Isaías',
            'Adam': 'Hombre, ser humano',
            'Adamáh': 'Tierra, suelo',
            'Néfesh': 'Alma, persona, garganta',
            'Neshamáh': 'Aliento de vida',
            'jai': 'Vida',
            'najash': 'Serpiente',
            'Ishmael': 'El escucha',
            'Itzjak': 'Reirá',
            'Ribkah': 'Unida',
            'Esav': 'Peludo',
            'Iosef': 'Él añadirá',
            'Káin': 'Adquirido',
            'Hével': 'Vapor',
            'Nóaj': 'El que porta descanso',
            'Shem': 'Nombre',
            'Jam': 'Caliente',
            'Iáfet': 'Ampliar',
            'Mitzráim': 'Egipto',
            'Kenáan': 'Canaán',
            'Beersheva': 'Pozo del juramento',
            'Shabat': 'Descanso, sábado',
            'Torah': 'Instrucción, ley',
            'Mishkán': 'Tabernáculo',
            'leviím': 'Levitas',
            'Mishpat': 'Juicio, proceso legal',
            'Tzedakáh': 'Justicia',
            'Jésed': 'Bondad, misericordia',
            'ketuvim': 'Escrituras',
            'kedoshim': 'Santos, apartados'
        }
        
        # Diccionario de notas al pie extraídas del documento
        self.footnote_definitions = {}

    def read_markdown(self) -> str:
        """Lee el archivo markdown"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_footnote_definitions(self, text: str):
        """Extrae las definiciones de notas al pie desde el final del documento"""
        # Buscar después de "## Footnotes" o cualquier línea que empiece con [^número]:
        footnote_section_match = re.search(r'##\s*Footnotes\s*\n', text, re.IGNORECASE)
        if footnote_section_match:
            footnote_section = text[footnote_section_match.end():]
        else:
            # Buscar el patrón [^número]: definición directamente
            footnote_section = text
        
        # Buscar el patrón [^número]: definición
        footnote_pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n\[|\n\n|$)'
        matches = re.finditer(footnote_pattern, footnote_section, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            footnote_num = match.group(1)
            footnote_def = match.group(2).strip()
            # Limpiar formato markdown de la definición
            footnote_def = re.sub(r'\*([^*]+)\*', r'\1', footnote_def)  # Remover cursiva
            footnote_def = re.sub(r'\*\*([^*]+)\*\*', r'\1', footnote_def)  # Remover negrita
            footnote_def = re.sub(r'\s+', ' ', footnote_def).strip()  # Limpiar espacios múltiples
            self.footnote_definitions[footnote_num] = footnote_def

    def extract_chapters(self, book_text: str) -> List[Dict[str, Any]]:
        """Extracts chapters from a book markdown"""
        # If it's tehilim, use special method
        if self.book_key == 'tehilim':
            return self.extract_psalms(book_text)
        
        # For other books, use regular extraction with alefato support
        chapters = []
        
        # Alefato mapping (for books like Mishlei chapter 31)
        alefato_map = {
            'alef': 'א', 'bet': 'ב', 'gimel': 'ג', 'guímel': 'ג', 'dalet': 'ד', 'dálet': 'ד', 
            'he': 'ה', 'vav': 'ו', 'zayin': 'ז', 'záin': 'ז', 'chet': 'ח', 'jet': 'ח', 
            'tet': 'ט', 'yod': 'י', 'yud': 'י',
            'kaf': 'כ', 'caf': 'כ', 'lamed': 'ל', 'mem': 'מ', 'nun': 'נ', 
            'samech': 'ס', 'ayin': 'ע', 'pe': 'פ', 'peh': 'פ', 'tzadi': 'צ', 
            'kuf': 'ק', 'resh': 'ר', 'shin': 'ש', 'tav': 'ת'
        }
        
        # Dividir el texto en líneas
        lines = book_text.split('\n')
        current_chapter = None
        current_verses = []
        current_verse_num = None
        current_verse_text = []
        current_title = None  # Título de sección actual
        current_alefato = None  # Alefato division (for chapters like Mishlei 31)
        in_chapter_section = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar inicio de capítulo - __número__ seguido de línea vacía o texto
            chapter_match = re.match(r'^__(\d+)__\s*$', line)
            if chapter_match:
                # Guardar capítulo anterior si existe
                if current_chapter is not None and current_verses:
                    chapters.append({
                        'chapter': current_chapter,
                        'verses': current_verses
                    })
                
                # Buscar título antes del marcador del capítulo (hasta 5 líneas antes)
                chapter_title = None
                lookback_start = max(0, i - 5)
                for j in range(i - 1, lookback_start - 1, -1):
                    if j < 0:
                        break
                    prev_line = lines[j].strip()
                    # Si la línea está vacía, continuar buscando
                    if not prev_line:
                        continue
                    # Si encontramos un título, guardarlo y parar
                    title_match = re.match(r'^\*(.+?)\*$', prev_line)
                    if title_match and not re.match(r'^\*\*\d+\*\*', prev_line):
                        chapter_title = title_match.group(1).strip()
                        break
                    # Si encontramos otra línea no vacía que no es título ni capítulo ni encabezado, parar
                    if prev_line and not re.match(r'^\*(.+?)\*$', prev_line) and not re.match(r'^__\d+__', prev_line) and not prev_line.startswith('#'):
                        break
                
                # Iniciar nuevo capítulo
                current_chapter = int(chapter_match.group(1))
                current_verses = []
                current_verse_num = None
                current_verse_text = []
                current_title = chapter_title  # Asignar título encontrado antes del capítulo
                current_alefato = None  # Reset alefato for new chapter
                in_chapter_section = True
                i += 1
                continue
            
            # Solo procesar versículos si estamos en una sección de capítulo
            if in_chapter_section:
                # Detect alefato division (for chapters like Mishlei 31)
                # Format: *Alef.*, *Bet.*, *Guímel.*, etc.
                # IMPORTANT: Save current verse BEFORE processing alefato marker
                # to ensure alefato is only applied to verses AFTER the marker
                alefato_match = re.match(r'^\*([A-Za-záéíóúÁÉÍÓÚ]+)\.\*\s*$', line)
                if alefato_match:
                    # Save current verse if exists (before changing alefato)
                    if current_verse_num is not None:
                        prev_verse_text = ' '.join(current_verse_text).strip()
                        if prev_verse_text:
                            prev_verse_text = self.clean_text_preserve_comments(prev_verse_text)
                            prev_verse_text, footnotes = self.extract_footnotes(prev_verse_text)
                            verse_entry = {
                                'verse': current_verse_num,
                                'text': prev_verse_text,
                                'footnotes': footnotes,
                                'hebrew_terms': self.extract_hebrew_terms(prev_verse_text)
                            }
                            if current_title:
                                verse_entry['title'] = current_title
                            # Use PREVIOUS alefato (if any) for this verse, not the new one
                            if current_alefato:
                                verse_entry['alefato'] = current_alefato
                            current_verses.append(verse_entry)
                            current_verse_num = None
                            current_verse_text = []
                    
                    # Now set new alefato for future verses
                    alefato_name = alefato_match.group(1).lower()
                    # Remove accents for matching
                    alefato_name_normalized = alefato_name.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                    if alefato_name in alefato_map:
                        current_alefato = alefato_map[alefato_name]
                    elif alefato_name_normalized in alefato_map:
                        current_alefato = alefato_map[alefato_name_normalized]
                    i += 1
                    continue
                
                # Detectar título en cursiva (línea que empieza y termina con asteriscos)
                title_match = re.match(r'^\*(.+?)\*$', line)
                if title_match and not re.match(r'^\*\*\d+\*\*', line):
                    # Check if it's an alefato marker (skip if it is)
                    alefato_check = re.match(r'^\*([A-Za-záéíóúÁÉÍÓÚ]+)\.\*\s*$', line)
                    if not alefato_check:
                        # Es un título de sección
                        current_title = title_match.group(1).strip()
                    i += 1
                    continue
                
                # Detectar si la línea contiene múltiples versículos (__número__ texto __número__ texto...)
                # Primero buscar todos los versículos en la línea
                # Patrón que captura __número__ seguido de texto hasta el siguiente __número__ o fin de línea
                verse_in_line_pattern = r'__(\d+)__\s*((?:(?!__\d+__).)*?)(?=__\d+__|$)'
                verse_matches = list(re.finditer(verse_in_line_pattern, line, re.DOTALL))
                
                if verse_matches:
                    # Procesar cada versículo encontrado en la línea
                    for match_idx, verse_match in enumerate(verse_matches):
                        verse_num = int(verse_match.group(1))
                        verse_text = verse_match.group(2).strip()
                        
                        # Guardar versículo anterior si existe
                        if current_verse_num is not None:
                            prev_verse_text = ' '.join(current_verse_text).strip()
                            if prev_verse_text:
                                prev_verse_text = self.clean_text_preserve_comments(prev_verse_text)
                                prev_verse_text, footnotes = self.extract_footnotes(prev_verse_text)
                                verse_entry = {
                                    'verse': current_verse_num,
                                    'text': prev_verse_text,
                                    'footnotes': footnotes,
                                    'hebrew_terms': self.extract_hebrew_terms(prev_verse_text)
                                }
                                # Include title if exists (doesn't reset, persists until new title)
                                if current_title:
                                    verse_entry['title'] = current_title
                                # Include alefato if exists (for chapters like Mishlei 31)
                                if current_alefato:
                                    verse_entry['alefato'] = current_alefato
                                current_verses.append(verse_entry)
                        
                        # Iniciar nuevo versículo
                        current_verse_num = verse_num
                        current_verse_text = [verse_text] if verse_text else []
                    
                    # Después de procesar todos los versículos de la línea, continuar con las siguientes líneas
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        
                        # Si es línea vacía, continuar
                        if not next_line:
                            i += 1
                            continue
                        
                        # Si es un nuevo capítulo, parar
                        if re.match(r'^__\d+__\s*$', next_line):
                            break
                        
                        # Si es un título en cursiva o alefato, parar
                        if re.match(r'^\*.+\*$', next_line) and not re.match(r'^\*\*\d+\*\*', next_line):
                            # Check if it's an alefato marker
                            alefato_check = re.match(r'^\*([A-Za-záéíóúÁÉÍÓÚ]+)\.\*\s*$', next_line)
                            if alefato_check:
                                # Don't change alefato here - it will be processed in the next iteration
                                # Just break to save current verse with its current alefato
                                break
                            break
                        
                        # Si la línea contiene marcadores de versículo, procesarla en la siguiente iteración
                        if re.search(r'__\d+__', next_line):
                            break
                        
                        # Agregar línea al versículo actual
                        if current_verse_num is not None:
                            current_verse_text.append(next_line)
                        i += 1
                    
                    continue
                
                # Si estamos en un versículo y la línea no es marcador, agregar al texto
                if current_verse_num is not None and line:
                    # Verificar que no sea un título
                    if not re.match(r'^\*.+\*$', line):
                        current_verse_text.append(line)
            
            i += 1
        
        # Guardar último versículo y capítulo
        if current_verse_num is not None:
            verse_text = ' '.join(current_verse_text).strip()
            if verse_text:
                verse_text = self.clean_text_preserve_comments(verse_text)
                verse_text, footnotes = self.extract_footnotes(verse_text)
                verse_entry = {
                    'verse': current_verse_num,
                    'text': verse_text,
                    'footnotes': footnotes,
                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                }
                # Incluir título si existe (se mantiene hasta nuevo título o capítulo)
                if current_title:
                    verse_entry['title'] = current_title
                current_verses.append(verse_entry)
        
        if current_chapter is not None and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })
        
        return chapters

    def extract_psalms(self, book_text: str) -> List[Dict[str, Any]]:
        """Extracts psalms from Tehilim, handling titles, books, and alefato divisions"""
        chapters = []
        
        # Map of book numbers to names
        book_map = {
            'PRIMERO': 1,
            'SEGUNDO': 2,
            'TERCERO': 3,
            'CUARTO': 4,
            'QUINTO': 5
        }
        
        # Alefato mapping (handling variations in names)
        alefato_map = {
            'alef': 'א', 'bet': 'ב', 'gimel': 'ג', 'dalet': 'ד', 'he': 'ה',
            'vav': 'ו', 'zayin': 'ז', 'chet': 'ח', 'jet': 'ח', 'tet': 'ט', 
            'yod': 'י', 'yud': 'י',
            'kaf': 'כ', 'caf': 'כ', 'lamed': 'ל', 'mem': 'מ', 'nun': 'נ', 
            'samech': 'ס', 'ayin': 'ע', 'pe': 'פ', 'peh': 'פ', 'tzadi': 'צ', 
            'kuf': 'ק', 'resh': 'ר', 'shin': 'ש', 'tav': 'ת'
        }
        
        lines = book_text.split('\n')
        current_psalm = None
        current_verses = []
        current_verse_num = None
        current_verse_text = []
        current_psalm_title = None
        current_book = None
        current_alefato = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect book marker: __LIBRO PRIMERO__, etc.
            book_match = re.match(r'^__LIBRO\s+([A-ZÁÉÍÓÚÑ\s]+)__', line)
            if book_match:
                book_name = book_match.group(1).strip()
                current_book = book_map.get(book_name)
                i += 1
                continue
            
            # Detect psalm number: __número__
            psalm_match = re.match(r'^__(\d+)__\s*$', line)
            if psalm_match:
                # Save previous psalm if exists
                if current_psalm is not None and current_verses:
                    chapters.append({
                        'chapter': current_psalm,
                        'verses': current_verses,
                        'book': current_book,
                        'psalm_title': current_psalm_title
                    })
                
                # Look for title before psalm (up to 5 lines before)
                psalm_title = None
                initial_alefato = None
                lookback_start = max(0, i - 5)
                for j in range(i - 1, lookback_start - 1, -1):
                    if j < 0:
                        break
                    prev_line = lines[j].strip()
                    if not prev_line:
                        continue
                    # Check for title with ** or *
                    if prev_line.startswith('**') or (prev_line.startswith('*') and 'supervisor' in prev_line.lower()):
                        psalm_title = prev_line.strip('*').strip()
                        break
                    # Check for alefato marker before psalm (for Psalm 119)
                    alefato_match_before = re.match(r'^\*([A-Za-z]+)\.\*\s*$', prev_line)
                    if alefato_match_before:
                        alefato_name = alefato_match_before.group(1).lower()
                        if alefato_name in alefato_map:
                            initial_alefato = alefato_map[alefato_name]
                        break
                    # Stop if we hit another psalm or book marker
                    if re.match(r'^__\d+__', prev_line) or re.match(r'^__LIBRO', prev_line):
                        break
                
                # Start new psalm
                current_psalm = int(psalm_match.group(1))
                current_verses = []
                current_verse_num = None
                current_verse_text = []
                current_psalm_title = psalm_title
                current_alefato = initial_alefato  # Set initial alefato if found before psalm marker
                i += 1
                continue
            
            # Detect alefato division (for Psalm 119 and others)
            # Format: *Alef.*, *Bet.*, etc.
            alefato_match = re.match(r'^\*([A-Za-z]+)\.\*\s*$', line)
            if alefato_match:
                alefato_name = alefato_match.group(1).lower()
                if alefato_name in alefato_map:
                    current_alefato = alefato_map[alefato_name]
                i += 1
                continue
            
            # Process verses (similar to extract_chapters)
            if current_psalm is not None:
                # Detect if line contains verse markers
                verse_in_line_pattern = r'__(\d+)__\s*((?:(?!__\d+__).)*?)(?=__\d+__|$)'
                verse_matches = list(re.finditer(verse_in_line_pattern, line, re.DOTALL))
                
                if verse_matches:
                    for verse_match in verse_matches:
                        verse_num = int(verse_match.group(1))
                        verse_text = verse_match.group(2).strip()
                        
                        # Save previous verse
                        if current_verse_num is not None:
                            prev_verse_text = ' '.join(current_verse_text).strip()
                            if prev_verse_text:
                                prev_verse_text = self.clean_text_preserve_comments(prev_verse_text)
                                prev_verse_text, footnotes = self.extract_footnotes(prev_verse_text)
                                verse_entry = {
                                    'verse': current_verse_num,
                                    'text': prev_verse_text,
                                    'footnotes': footnotes,
                                    'hebrew_terms': self.extract_hebrew_terms(prev_verse_text)
                                }
                                # Include psalm title, book, and alefato if they exist
                                if current_psalm_title:
                                    verse_entry['psalm_title'] = current_psalm_title
                                if current_book:
                                    verse_entry['psalm_book'] = current_book
                                if current_alefato:
                                    verse_entry['alefato'] = current_alefato
                                current_verses.append(verse_entry)
                        
                        # Start new verse
                        current_verse_num = verse_num
                        current_verse_text = [verse_text] if verse_text else []
                    
                    # Continue reading multi-line verses
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if not next_line:
                            i += 1
                            continue
                        if re.match(r'^__\d+__\s*$', next_line) or re.match(r'^__LIBRO', next_line):
                            break
                        if re.match(r'^\*[A-Za-z]+\.\*\s*$', next_line):
                            break
                        if re.search(r'__\d+__', next_line):
                            break
                        if current_verse_num is not None:
                            current_verse_text.append(next_line)
                        i += 1
                    continue
                
                # Add line to current verse
                if current_verse_num is not None and line:
                    if not re.match(r'^\*.+\*$', line) and not re.match(r'^\*[A-Za-z]+\.\*\s*$', line):
                        current_verse_text.append(line)
            
            i += 1
        
        # Save last verse and psalm
        if current_verse_num is not None:
            verse_text = ' '.join(current_verse_text).strip()
            if verse_text:
                verse_text = self.clean_text_preserve_comments(verse_text)
                verse_text, footnotes = self.extract_footnotes(verse_text)
                verse_entry = {
                    'verse': current_verse_num,
                    'text': verse_text,
                    'footnotes': footnotes,
                    'hebrew_terms': self.extract_hebrew_terms(verse_text)
                }
                if current_psalm_title:
                    verse_entry['psalm_title'] = current_psalm_title
                if current_book:
                    verse_entry['psalm_book'] = current_book
                if current_alefato:
                    verse_entry['alefato'] = current_alefato
                current_verses.append(verse_entry)
        
        if current_psalm is not None and current_verses:
            chapters.append({
                'chapter': current_psalm,
                'verses': current_verses,
                'book': current_book,
                'psalm_title': current_psalm_title
            })
        
        return chapters

    def extract_footnotes(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Extrae las notas al pie del texto y las reemplaza con superíndices"""
        footnotes = []
        
        # Buscar patrones [^número]
        footnote_pattern = r'\[\^(\d+)\]'
        matches = list(re.finditer(footnote_pattern, text))
        
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
            
            # Buscar términos compuestos hebreos comunes
            compound_terms = [
                (r"Rúaj\s+Ha['']Kódesh", "Rúaj Ha'Kódesh"),
                (r"Ben\s+Ha['']Adam", "Ben Ha'Adam"),
                (r"Bet\s+Léjem", "Bet Léjem"),
                (r"Bet\s+Aniah", "Bet Aniah"),
            ]
            
            # Verificar términos compuestos
            search_text = text_before[-50:] if len(text_before) > 50 else text_before
            for term_pattern, term_name in compound_terms:
                pattern = term_pattern + r'\s*$'
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    return term_name
            
            # Buscar la última palabra simple
            simple_word_pattern = r'([\w\'-]+)\s*$'
            match = re.search(simple_word_pattern, text_before)
            
            if match:
                word = match.group(1).strip()
                # Limpiar puntuación final
                word = re.sub(r'[.,;:!?]+$', '', word)
                return word if word else ''
            
            return ''
        
        # Extraer todas las palabras asociadas del texto original
        footnote_data = []
        for match in matches:
            footnote_num = match.group(1)
            marker = num_to_superscript(footnote_num)
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
        modified_text = text
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
        
        # Remover formato de versículos __número__ que puedan quedar
        modified_text = re.sub(r'__(\d+)__', r'\1', modified_text)
        
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
        
        # Convertir paréntesis escapados de markdown \( y \) a paréntesis normales ( y )
        # El escape en markdown es solo para evitar interpretación como formato,
        # pero en el texto final queremos paréntesis normales
        modified_text = modified_text.replace('\\(', '(').replace('\\)', ')')
        
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

    def create_json_structure(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Crea la estructura JSON final compatible con la app"""
        book_info = self.books_info[self.book_key]
        json_data = []
        
        for chapter_data in chapters:
            chapter_num = chapter_data['chapter']
            
            for verse_data in chapter_data['verses']:
                verse_entry = {
                    'book': self.book_key,
                    'book_id': book_info.get('book_code', self.book_key),  # Use book_code as book_id
                    'book_tth_name': book_info['tth_name'],
                    'book_hebrew_name': book_info['hebrew_name'],
                    'book_english_name': book_info['english_name'],
                    'book_spanish_name': book_info['spanish_name'],
                    'section': book_info.get('section', ''),
                    'section_hebrew': book_info.get('section_hebrew', ''),
                    'section_english': book_info.get('section_english', ''),
                    'section_spanish': book_info.get('section_spanish', ''),
                    'chapter': chapter_num,
                    'verse': verse_data['verse'],
                    'status': 'present',
                    'tth': verse_data['text'],
                    'footnotes': verse_data.get('footnotes', []),
                    'hebrew_terms': verse_data.get('hebrew_terms', [])
                }
                # Add title if exists (for regular books)
                if 'title' in verse_data:
                    verse_entry['title'] = verse_data['title']
                # Add psalm-specific fields (for tehilim)
                if 'psalm_title' in verse_data:
                    verse_entry['psalm_title'] = verse_data['psalm_title']
                if 'psalm_book' in verse_data:
                    verse_entry['psalm_book'] = verse_data['psalm_book']
                # Add alefato field (for tehilim and other books like mishlei)
                if 'alefato' in verse_data:
                    verse_entry['alefato'] = verse_data['alefato']
                json_data.append(verse_entry)
        
        return json_data

    def save_chapter_files(self, json_data: List[Dict[str, Any]]):
        """Saves JSON files by chapter"""
        book_info = self.books_info[self.book_key]
        
        # Create directory with book name
        book_dir = f"{self.output_dir}/{self.book_key}"
        os.makedirs(book_dir, exist_ok=True)
        
        # Group by chapters
        chapters_data = {}
        for verse in json_data:
            chapter = verse['chapter']
            if chapter not in chapters_data:
                chapters_data[chapter] = []
            chapters_data[chapter].append(verse)
        
        # Save each chapter
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

    def validate_processing(self, json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida el procesamiento y genera reporte de QA"""
        book_info = self.books_info[self.book_key]
        expected_chapters = book_info['expected_chapters']
        
        # Agrupar por capítulos
        chapters_data = {}
        for verse in json_data:
            chapter = verse['chapter']
            if chapter not in chapters_data:
                chapters_data[chapter] = []
            chapters_data[chapter].append(verse)
        
        # Estadísticas
        total_chapters = len(chapters_data)
        total_verses = len(json_data)
        chapters_with_titles = sum(1 for chapter_num, verses in chapters_data.items() 
                                 if any('title' in v for v in verses))
        verses_with_footnotes = sum(1 for v in json_data if v.get('footnotes'))
        verses_with_hebrew_terms = sum(1 for v in json_data if v.get('hebrew_terms'))
        
        # Validaciones
        validation_results = {
            'book': self.book_key,
            'expected_chapters': expected_chapters,
            'actual_chapters': total_chapters,
            'chapters_match': total_chapters == expected_chapters,
            'total_verses': total_verses,
            'chapters_with_titles': chapters_with_titles,
            'verses_with_footnotes': verses_with_footnotes,
            'verses_with_hebrew_terms': verses_with_hebrew_terms,
            'footnote_definitions_found': len(self.footnote_definitions),
            'issues': []
        }
        
        # Verificar capítulos faltantes o extra
        if total_chapters != expected_chapters:
            validation_results['issues'].append(
                f"Capítulos: esperados {expected_chapters}, encontrados {total_chapters}"
            )
        
        # Verificar que cada capítulo tenga versículos
        for chapter_num in range(1, total_chapters + 1):
            if chapter_num not in chapters_data:
                validation_results['issues'].append(f"Capítulo {chapter_num} faltante")
        
        # Verificar versículos vacíos
        empty_verses = [v for v in json_data if not v.get('tth', '').strip()]
        if empty_verses:
            validation_results['issues'].append(f"{len(empty_verses)} versículos con texto vacío")
        
        return validation_results

    def process(self):
        """Proceso principal"""
        print(f"Iniciando procesamiento de TTH {self.book_key} desde Markdown...")
        
        # Leer markdown
        markdown_text = self.read_markdown()
        print(f"Markdown leído: {len(markdown_text)} caracteres")
        
        # Extraer definiciones de notas al pie
        self.extract_footnote_definitions(markdown_text)
        print(f"Definiciones de notas al pie encontradas: {len(self.footnote_definitions)}")
        
        # Separar contenido de notas al pie
        footnote_section_match = re.search(r'##\s*Footnotes\s*\n', markdown_text, re.IGNORECASE)
        if footnote_section_match:
            book_text = markdown_text[:footnote_section_match.start()]
        else:
            # Buscar donde empiezan las notas al pie
            first_footnote_match = re.search(r'\n\[\^\d+\]:', markdown_text)
            if first_footnote_match:
                book_text = markdown_text[:first_footnote_match.start()]
            else:
                book_text = markdown_text
        
        # Extraer capítulos
        chapters = self.extract_chapters(book_text)
        print(f"Capítulos encontrados: {len(chapters)}")
        
        # Crear estructura JSON
        json_data = self.create_json_structure(chapters)
        print(f"Versículos totales: {len(json_data)}")
        
        # Validar procesamiento
        validation = self.validate_processing(json_data)
        print("\n=== REPORTE DE VALIDACIÓN ===")
        print(f"Capítulos: {validation['actual_chapters']}/{validation['expected_chapters']} {'✓' if validation['chapters_match'] else '✗'}")
        print(f"Versículos totales: {validation['total_verses']}")
        print(f"Capítulos con títulos: {validation['chapters_with_titles']}")
        print(f"Versículos con notas al pie: {validation['verses_with_footnotes']}")
        print(f"Versículos con términos hebreos: {validation['verses_with_hebrew_terms']}")
        print(f"Definiciones de notas al pie: {validation['footnote_definitions_found']}")
        
        if validation['issues']:
            print("\n⚠️  PROBLEMAS ENCONTRADOS:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        else:
            print("\n✓ Validación exitosa - No se encontraron problemas")
        
        # Guardar archivos
        self.save_chapter_files(json_data)
        
        print("\nProcesamiento completado exitosamente!")


def process_book(book_key: str, cleanup_on_error: bool = True):
    """Processes a single book safely, without affecting previously processed books"""
    import shutil
    
    book_dir = f"draft/{book_key}"
    temp_dir = f"draft/{book_key}_temp"
    
    try:
        print(f"\n{'='*60}")
        print(f"Procesando libro: {book_key}")
        print(f"{'='*60}")
        
        # If book directory exists, backup to temp before processing
        if os.path.exists(book_dir):
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            shutil.copytree(book_dir, temp_dir)
        
        processor = TTHTanajProcessor(book_key=book_key)
        processor.process()
        
        # If successful, remove temp backup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        print(f"\n❌ ERROR procesando {book_key}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # On error: restore from backup if exists, or clean up new book only
        if cleanup_on_error:
            if os.path.exists(temp_dir):
                # Restore backup
                if os.path.exists(book_dir):
                    shutil.rmtree(book_dir)
                shutil.move(temp_dir, book_dir)
                print(f"✓ Restaurado estado anterior de {book_key}")
            elif os.path.exists(book_dir):
                # Remove failed book directory (only if it's a new book)
                shutil.rmtree(book_dir)
                print(f"✓ Eliminado directorio fallido de {book_key}")
        
        return False


def process_torah_books():
    """Procesa todos los libros de la Torá hasta devarim"""
    torah_books = ['bereshit', 'shemot', 'vaikra', 'bamidbar', 'devarim']
    results = {}
    
    for book_key in torah_books:
        success = process_book(book_key)
        results[book_key] = success
        if not success:
            print(f"\n⚠️  Deteniendo procesamiento después de {book_key} debido a errores")
            break
    
    # Resumen final
    print(f"\n{'='*60}")
    print("RESUMEN FINAL")
    print(f"{'='*60}")
    successful = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    
    if successful:
        print(f"✓ Libros procesados exitosamente: {', '.join(successful)}")
    if failed:
        print(f"✗ Libros con errores: {', '.join(failed)}")
    
    return results


def main():
    import sys
    
    if len(sys.argv) > 1:
        # Si se proporciona un argumento, procesar solo ese libro
        book_key = sys.argv[1]
        process_book(book_key)
    else:
        # Por defecto, procesar todos los libros de la Torá
        process_torah_books()


if __name__ == '__main__':
    main()
