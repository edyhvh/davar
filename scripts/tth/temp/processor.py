#!/usr/bin/env python3
"""
TTH Markdown to JSON Processor (Modified)
==========================================

Modified version of the TTH processor that includes text cleaning.
This version integrates the text_cleaner module to fix common issues:
- Soft hyphens (word breaks)
- Missing spaces after punctuation
- Stuck connectors

Changes from original:
- Added text_cleaner integration
- Modified clean_text_preserve_comments to use text_cleaner

Author: Davar Project
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union
from pathlib import Path

# Import the text cleaner module
try:
    from .text_cleaner import TTHTextCleaner
except ImportError:
    from text_cleaner import TTHTextCleaner


class TTHProcessor:
    """
    Processes TTH Markdown to structured JSON format.
    
    This modified version includes text cleaning to fix common conversion issues.
    """

    # Book information database
    BOOKS_INFO = {
        # Torah (Pentateuco)
        'bereshit': {
            'tth_name': 'Bereshit',
            'hebrew_name': 'בראשית',
            'english_name': 'Genesis',
            'spanish_name': 'Génesis',
            'book_code': 'genesis',
            'expected_chapters': 50,
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
            'section': 'torah',
            'section_hebrew': 'תורה',
            'section_english': 'Torah',
            'section_spanish': 'Torá'
        },

        # Neviim (Profetas)
        'iehosua': {
            'tth_name': 'Iehoshúa',
            'hebrew_name': 'יהושע',
            'english_name': 'Joshua',
            'spanish_name': 'Josué',
            'book_code': 'joshua',
            'expected_chapters': 24,
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
            'expected_chapters': 31,
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
            'section': 'neviim',
            'section_hebrew': 'נביאים',
            'section_english': 'Prophets',
            'section_spanish': 'Profetas'
        },
        'najum': {
            'tth_name': 'Najum',
            'hebrew_name': 'נחום',
            'english_name': 'Nahum',
            'spanish_name': 'Nahúm',
            'book_code': 'nahum',
            'expected_chapters': 3,
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
            'section': 'neviim',
            'section_hebrew': 'נביאים',
            'section_english': 'Prophets',
            'section_spanish': 'Profetas'
        },

        # Ketuvim (Escritos)
        'tehilim': {
            'tth_name': 'Tehilim',
            'hebrew_name': 'תהלים',
            'english_name': 'Psalms',
            'spanish_name': 'Salmos',
            'book_code': 'psalms',
            'expected_chapters': 150,
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
                'section': 'ketuvim',
                'section_hebrew': 'כתובים',
                'section_english': 'Writings',
                'section_spanish': 'Escritos'
            },

            # Besorah (Nuevo Testamento)
            'matityahu': {
                'tth_name': 'Matityáhu',
                'hebrew_name': 'מתתיהו',
                'english_name': 'Matthew',
                'spanish_name': 'Mateo',
                'book_code': 'matthew',
                'expected_chapters': 28,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'markos': {
                'tth_name': 'Markos',
                'hebrew_name': 'מרקוס',
                'english_name': 'Mark',
                'spanish_name': 'Marcos',
                'book_code': 'mark',
                'expected_chapters': 16,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'lukas': {
                'tth_name': 'Lukas',
                'hebrew_name': 'לוקס',
                'english_name': 'Luke',
                'spanish_name': 'Lucas',
                'book_code': 'luke',
                'expected_chapters': 24,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'iojanan': {
                'tth_name': 'Iojanán',
                'hebrew_name': 'יוחנן',
                'english_name': 'John',
                'spanish_name': 'Juan',
                'book_code': 'john',
                'expected_chapters': 21,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'maasei_hashlijim': {
                'tth_name': "Maasei Hash'lijim",
                'hebrew_name': 'מעשי השליחים',
                'english_name': 'Acts',
                'spanish_name': 'Hechos',
                'book_code': 'acts',
                'expected_chapters': 28,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'romaim': {
                'tth_name': 'Romaim',
                'hebrew_name': 'רומאים',
                'english_name': 'Romans',
                'spanish_name': 'Romanos',
                'book_code': 'romans',
                'expected_chapters': 16,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'iaacob': {
                'tth_name': 'Iaacob',
                'hebrew_name': 'יעקב',
                'english_name': 'James',
                'spanish_name': 'Santiago',
                'book_code': 'james',
                'expected_chapters': 5,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'iehudah': {
                'tth_name': 'Iehudáh',
                'hebrew_name': 'יהודה',
                'english_name': 'Jude',
                'spanish_name': 'Judas',
                'book_code': 'jude',
                'expected_chapters': 1,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'sodot': {
                'tth_name': 'Sodot',
                'hebrew_name': 'סודות',
                'english_name': 'Revelation',
                'spanish_name': 'Apocalipsis',
                'book_code': 'revelation',
                'expected_chapters': 22,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'tesaloniquim_alef': {
                'tth_name': 'Tesaloniquim Alef',
                'hebrew_name': 'תסלוניקים א',
                'english_name': '1 Thessalonians',
                'spanish_name': '1 Tesalonicenses',
                'book_code': '1_thessalonians',
                'expected_chapters': 5,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            },
            'tesaloniquim_bet': {
                'tth_name': 'Tesaloniquim Bet',
                'hebrew_name': 'תסלוניקים ב',
                'english_name': '2 Thessalonians',
                'spanish_name': '2 Tesalonicenses',
                'book_code': '2_thessalonians',
                'expected_chapters': 3,
                'section': 'besorah',
                'section_hebrew': 'בשורה',
                'section_english': 'Gospel',
                'section_spanish': 'Evangelio'
            }
    }

    # Hebrew terms dictionary
    HEBREW_TERMS = {
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

    def __init__(self, book_key: str = 'bereshit', output_dir: str = 'draft'):
        """
        Initialize the TTH processor.

        Args:
            book_key: Book identifier (e.g., 'bereshit', 'shemot')
            output_dir: Output directory for JSON files
        """
        self.book_key = book_key
        self.output_dir = output_dir
        self.footnote_definitions = {}
        
        # NEW: Initialize text cleaner
        self.text_cleaner = TTHTextCleaner()

        # Validate book key
        if book_key not in self.BOOKS_INFO:
            raise ValueError(f"Book key '{book_key}' not found in books database")

    def read_markdown(self, file_path: str) -> str:
        """Read markdown file content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_footnote_definitions(self, text: str):
        """Extract footnote definitions from document."""
        footnote_section_match = re.search(r'##\s*Footnotes\s*\n', text, re.IGNORECASE)
        if footnote_section_match:
            footnote_section = text[footnote_section_match.end():]
        else:
            footnote_section = text

        footnote_pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n\[|\n\n|$)'
        matches = re.finditer(footnote_pattern, footnote_section, re.MULTILINE | re.DOTALL)

        for match in matches:
            footnote_num = match.group(1)
            footnote_def = match.group(2).strip()
            footnote_def = re.sub(r'\*([^*]+)\*', r'\1', footnote_def)
            footnote_def = re.sub(r'\*\*([^*]+)\*\*', r'\1', footnote_def)
            footnote_def = re.sub(r'\s+', ' ', footnote_def).strip()
            self.footnote_definitions[footnote_num] = footnote_def

    def extract_chapters(self, book_text: str) -> List[Dict[str, Any]]:
        """Extract chapters from book markdown."""
        if self.book_key == 'tehilim':
            return self.extract_psalms(book_text)

        # Special handling for single-chapter books like Judas
        if self.BOOKS_INFO[self.book_key]['expected_chapters'] == 1:
            return self.extract_single_chapter_book(book_text)

        return self.extract_standard_chapters(book_text)

    def extract_standard_chapters(self, book_text: str) -> List[Dict[str, Any]]:
        """Extract chapters from standard books."""
        chapters = []
        lines = book_text.split('\n')

        # Alefato mapping for special divisions
        alefato_map = {
            'alef': 'א', 'bet': 'ב', 'gimel': 'ג', 'guímel': 'ג', 'dalet': 'ד', 'dálet': 'ד',
            'he': 'ה', 'vav': 'ו', 'zayin': 'ז', 'záin': 'ז', 'chet': 'ח', 'jet': 'ח',
            'tet': 'ט', 'yod': 'י', 'yud': 'י',
            'kaf': 'כ', 'caf': 'כ', 'lamed': 'ל', 'mem': 'מ', 'nun': 'נ',
            'samech': 'ס', 'ayin': 'ע', 'pe': 'פ', 'peh': 'פ', 'tzadi': 'צ',
            'kuf': 'ק', 'resh': 'ר', 'shin': 'ש', 'tav': 'ת'
        }

        current_chapter = None
        current_verses = []
        current_verse_num = None
        current_verse_text = []
        current_title = None
        current_alefato = None
        in_chapter_section = False

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Detect chapter start - support both __número__ and **número** formats
            chapter_match = re.match(r'^(?:__(\d+)__|^\*\*(\d+)\*\*)\s*$', line)
            if chapter_match:
                if current_chapter is not None and current_verses:
                    chapters.append({
                        'chapter': current_chapter,
                        'verses': current_verses
                    })

                current_chapter = int(chapter_match.group(1) if chapter_match.group(1) else chapter_match.group(2))
                current_verses = []
                current_verse_num = None
                current_verse_text = []
                current_title = None
                current_alefato = None
                in_chapter_section = True
                i += 1
                continue

            if in_chapter_section:
                # Handle alefato divisions
                alefato_match = re.match(r'^\*([A-Za-záéíóúÁÉÍÓÚ]+)\.\*\s*$', line)
                if alefato_match:
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
                            if current_alefato:
                                verse_entry['alefato'] = current_alefato
                            current_verses.append(verse_entry)
                            current_verse_num = None
                            current_verse_text = []

                    alefato_name = alefato_match.group(1).lower()
                    alefato_name_normalized = alefato_name.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                    if alefato_name in alefato_map:
                        current_alefato = alefato_map[alefato_name]
                    elif alefato_name_normalized in alefato_map:
                        current_alefato = alefato_map[alefato_name_normalized]
                    i += 1
                    continue

                # Handle titles
                title_match = re.match(r'^\*(.+?)\*$', line)
                if title_match and not re.match(r'^\*\*\d+\*\*', line):
                    alefato_check = re.match(r'^\*([A-Za-záéíóúÁÉÍÓÚ]+)\.\*\s*$', line)
                    if not alefato_check:
                        current_title = title_match.group(1).strip()
                    i += 1
                    continue

                # Process verses (support both **número** and __número__ formats)
                verse_in_line_pattern = r'(?:\*\*(\d+)\*\*|__(\d+)__)\s*((?:(?!(?:\*\*\d+\*\*|__\d+__)).)*?)(?=(?:\*\*\d+\*\*|__\d+__)|$)'

                verse_matches = []
                for match in re.finditer(verse_in_line_pattern, line, re.DOTALL):
                    verse_num = int(match.group(1) if match.group(1) else match.group(2))
                    verse_text = match.group(3).strip()
                    verse_matches.append((verse_num, verse_text))

                if verse_matches:
                    for match_idx, (verse_num, verse_text) in enumerate(verse_matches):

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
                                if current_alefato:
                                    verse_entry['alefato'] = current_alefato
                                current_verses.append(verse_entry)

                        current_verse_num = verse_num
                        current_verse_text = [verse_text] if verse_text else []

                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if not next_line:
                            i += 1
                            continue
                        if re.match(r'^(?:__|\*\*)\d+(?:__|\*\*)\s*$', next_line):
                            break
                        if re.match(r'^\*.+\*$', next_line) and not re.match(r'^\*\*\d+\*\*', next_line):
                            alefato_check = re.match(r'^\*([A-Za-záéíóúÁÉÍÓÚ]+)\.\*\s*$', next_line)
                            if alefato_check:
                                break
                            break
                        if re.search(r'(?:\*\*\d+\*\*|__\d+__)', next_line):
                            break
                        if current_verse_num is not None:
                            current_verse_text.append(next_line)
                        i += 1
                    continue

                if current_verse_num is not None and line:
                    if not re.match(r'^\*.+\*$', line):
                        current_verse_text.append(line)

            i += 1

        # Save last verse and chapter
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
                if current_title:
                    verse_entry['title'] = current_title
                if current_alefato:
                    verse_entry['alefato'] = current_alefato
                current_verses.append(verse_entry)

        if current_chapter is not None and current_verses:
            chapters.append({
                'chapter': current_chapter,
                'verses': current_verses
            })

        return chapters

    def extract_single_chapter_book(self, book_text: str) -> List[Dict[str, Any]]:
        """Extract content from single-chapter books like Judas."""
        lines = book_text.split('\n')
        verses = []
        current_verse_num = None
        current_verse_text = []
        current_title = None

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Handle titles
            title_match = re.match(r'^\*([^*]+)\*$', line)
            if title_match and not re.match(r'^\*\*\d+\*\*', line):
                current_title = title_match.group(1).strip()
                i += 1
                continue

            # Process verses - look for **número** patterns in single chapter books
            verse_match = re.match(r'^\*\*(\d+)\*\*\s*(.*)$', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()

                # Save previous verse if exists
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
                        verses.append(verse_entry)

                current_verse_num = verse_num
                current_verse_text = [verse_text] if verse_text else []

                # Continue reading multi-line verses
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        i += 1
                        continue
                    if re.match(r'^\*\*\d+\*\*$', next_line):  # Next verse marker
                        break
                    if re.match(r'^\*([^*]+)\*$', next_line) and not next_line.startswith('**'):  # Title
                        break
                    if current_verse_num is not None:
                        current_verse_text.append(next_line)
                    i += 1
                continue


            # Add line to current verse if we're in one
            if current_verse_num is not None and line:
                if not re.match(r'^\*([^*]+)\*$', line):
                    current_verse_text.append(line)

            i += 1

        # Save last verse
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
                if current_title:
                    verse_entry['title'] = current_title
                verses.append(verse_entry)

        # Return as single chapter
        return [{'chapter': 1, 'verses': verses}] if verses else []

    def extract_psalms(self, book_text: str) -> List[Dict[str, Any]]:
        """Extract psalms with special handling for titles, books, and alefato."""
        chapters = []

        book_map = {
            'PRIMERO': 1, 'SEGUNDO': 2, 'TERCERO': 3,
            'CUARTO': 4, 'QUINTO': 5
        }

        alefato_map = {
            'alef': 'א', 'bet': 'ב', 'gimel': 'ג', 'dalet': 'ד', 'he': 'ה',
            'vav': 'ו', 'zayin': 'ז', 'chet': 'ח', 'jet': 'ח', 'tet': 'ט',
            'yod': 'י', 'yud': 'י', 'kaf': 'כ', 'caf': 'כ', 'lamed': 'ל',
            'mem': 'מ', 'nun': 'נ', 'samech': 'ס', 'ayin': 'ע', 'pe': 'פ',
            'peh': 'פ', 'tzadi': 'צ', 'kuf': 'ק', 'resh': 'ר', 'shin': 'ש', 'tav': 'ת'
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

            # Detect book marker
            book_match = re.match(r'^__LIBRO\s+([A-ZÁÉÍÓÚÑ\s]+)__', line)
            if book_match:
                book_name = book_match.group(1).strip()
                current_book = book_map.get(book_name)
                i += 1
                continue

            # Detect psalm number
            psalm_match = re.match(r'^__(\d+)__\s*$', line)
            if psalm_match:
                if current_psalm is not None and current_verses:
                    chapters.append({
                        'chapter': current_psalm,
                        'verses': current_verses,
                        'book': current_book,
                        'psalm_title': current_psalm_title
                    })

                current_psalm = int(psalm_match.group(1))
                current_verses = []
                current_verse_num = None
                current_verse_text = []
                current_psalm_title = None
                current_alefato = None
                i += 1
                continue

            # Detect alefato division
            alefato_match = re.match(r'^\*([A-Za-z]+)\.\*\s*$', line)
            if alefato_match:
                alefato_name = alefato_match.group(1).lower()
                if alefato_name in alefato_map:
                    current_alefato = alefato_map[alefato_name]
                i += 1
                continue

            if current_psalm is not None:
                # Find title before psalm
                if not current_psalm_title:
                    lookback_start = max(0, i - 5)
                    for j in range(i - 1, lookback_start - 1, -1):
                        if j < 0:
                            break
                        prev_line = lines[j].strip()
                        if not prev_line:
                            continue
                        if prev_line.startswith('**') or (prev_line.startswith('*') and 'supervisor' in prev_line.lower()):
                            current_psalm_title = prev_line.strip('*').strip()
                            break
                        if re.match(r'^__\d+__', prev_line) or re.match(r'^__LIBRO', prev_line):
                            break

                # Process verses (support both **número** and __número__ formats)
                verse_in_line_pattern = r'(?:\*\*(\d+)\*\*|__(\d+)__)\s*((?:(?!(?:\*\*\d+\*\*|__\d+__)).)*?)(?=(?:\*\*\d+\*\*|__\d+__)|$)'

                verse_matches = []
                for match in re.finditer(verse_in_line_pattern, line, re.DOTALL):
                    verse_num = int(match.group(1) if match.group(1) else match.group(2))
                    verse_text = match.group(3).strip()
                    verse_matches.append((verse_num, verse_text))

                if verse_matches:
                    for verse_num, verse_text in verse_matches:

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
                                if current_psalm_title:
                                    verse_entry['psalm_title'] = current_psalm_title
                                if current_book:
                                    verse_entry['psalm_book'] = current_book
                                if current_alefato:
                                    verse_entry['alefato'] = current_alefato
                                current_verses.append(verse_entry)

                        current_verse_num = verse_num
                        current_verse_text = [verse_text] if verse_text else []

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
                        if re.search(r'(?:\*\*\d+\*\*|__\d+__)', next_line):
                            break
                        if current_verse_num is not None:
                            current_verse_text.append(next_line)
                        i += 1
                    continue

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
        """Extract footnotes from text and convert to superscript."""
        footnotes = []

        footnote_pattern = r'\[\^(\d+)\]'
        matches = list(re.finditer(footnote_pattern, text))

        def num_to_superscript(num_str):
            superscript_map = {
                '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
                '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
            }
            return ''.join(superscript_map.get(digit, digit) for digit in num_str)

        def extract_associated_word(text_before_marker: str) -> str:
            """Extract word associated with footnote."""
            text_before = text_before_marker.rstrip()

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

            simple_word_pattern = r'([\w\'-]+)\s*$'
            match = re.search(simple_word_pattern, text_before)

            if match:
                word = match.group(1).strip()
                word = re.sub(r'[.,;:!?]+$', '', word)
                return word if word else ''

            return ''

        footnote_data = []
        for match in matches:
            footnote_num = match.group(1)
            marker = num_to_superscript(footnote_num)
            definition = self.footnote_definitions.get(footnote_num, f'Nota al pie {footnote_num}')

            text_before = text[:match.start()]
            associated_word = extract_associated_word(text_before)

            footnote_data.append({
                'match': match,
                'footnote_num': footnote_num,
                'marker': marker,
                'definition': definition,
                'word': associated_word
            })

        modified_text = text
        for data in reversed(footnote_data):
            match = data['match']
            modified_text = modified_text[:match.start()] + data['marker'] + modified_text[match.end()]

            if not any(fn['number'] == data['footnote_num'] for fn in footnotes):
                footnotes.append({
                    'marker': data['marker'],
                    'number': data['footnote_num'],
                    'word': data['word'],
                    'explanation': data['definition']
                })

        footnotes.sort(key=lambda x: int(x['number']))
        return modified_text.strip(), footnotes

    def clean_text_preserve_comments(self, text: str) -> str:
        """
        Clean text while preserving comments and formatting.
        
        MODIFIED: Now uses TTHTextCleaner to fix:
        - Soft hyphens (word breaks)
        - Missing spaces after punctuation  
        - Stuck connectors
        """
        modified_text = text

        # Remove verse markers that may remain
        modified_text = re.sub(r'\*\*(\d+)\*\*', r'\1', modified_text)

        # Protect comments in parentheses
        protected_parts = []
        protected_pattern = r'\([^)]*\)'

        def protect_replace(match):
            protected_id = f"__PROTECTED_{len(protected_parts)}__"
            protected_parts.append(match.group(0))
            return protected_id

        modified_text = re.sub(protected_pattern, protect_replace, modified_text)

        # Remove italic formatting
        modified_text = re.sub(r'\*([^*\s]+)\*', r'\1', modified_text)
        modified_text = re.sub(r'\*(\s+)', r'\1', modified_text)
        modified_text = re.sub(r'(\s+)\*', r'\1', modified_text)

        # Restore protected parts
        for i, protected in enumerate(protected_parts):
            modified_text = modified_text.replace(f"__PROTECTED_{i}__", protected)

        # Clean whitespace
        modified_text = re.sub(r'\s+', ' ', modified_text).strip()

        # Convert escaped parentheses
        modified_text = modified_text.replace('\\(', '(').replace('\\)', ')')
        
        # ========================================
        # NEW: Apply text cleaner fixes
        # ========================================
        modified_text = self.text_cleaner.clean_verse_text(modified_text)

        return modified_text

    def extract_hebrew_terms(self, text: str) -> List[Dict[str, str]]:
        """Extract Hebrew terms from text."""
        terms_found = []

        # Create normalized term mapping
        term_normalization = {}
        for term, explanation in self.HEBREW_TERMS.items():
            normalized = term.upper()
            if normalized not in term_normalization:
                term_normalization[normalized] = (term, explanation)

        # Sort by length (longest first)
        sorted_terms = sorted(term_normalization.items(), key=lambda x: len(x[1][0]), reverse=True)

        found_normalized = set()

        for normalized, (term, explanation) in sorted_terms:
            # Special handling for "EL"
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
                # Standard term detection
                pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)

                if pattern.search(text) and normalized not in found_normalized:
                    terms_found.append({
                        'term': term,
                        'explanation': explanation
                    })
                    found_normalized.add(normalized)

        return terms_found

    def create_json_structure(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create final JSON structure compatible with Davar app."""
        book_info = self.BOOKS_INFO[self.book_key]
        json_data = []

        for chapter_data in chapters:
            chapter_num = chapter_data['chapter']

            for verse_data in chapter_data['verses']:
                verse_entry = {
                    'book': self.book_key,
                    'book_id': book_info.get('book_code', self.book_key),
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

                # Add title if exists
                if 'title' in verse_data:
                    verse_entry['title'] = verse_data['title']

                # Add psalm-specific fields
                if 'psalm_title' in verse_data:
                    verse_entry['psalm_title'] = verse_data['psalm_title']
                if 'psalm_book' in verse_data:
                    verse_entry['psalm_book'] = verse_data['psalm_book']

                # Add alefato field
                if 'alefato' in verse_data:
                    verse_entry['alefato'] = verse_data['alefato']

                json_data.append(verse_entry)

        return json_data

    def save_book_file(self, json_data: List[Dict[str, Any]]):
        """Save a single JSON file for the entire book."""
        book_info = self.BOOKS_INFO[self.book_key]

        # Create temp directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Save complete book as single JSON file
        filename = f"{self.book_key}.json"
        filepath = os.path.join(self.output_dir, filename)

        # Calculate statistics
        total_chapters = len(set(v['chapter'] for v in json_data))
        total_verses = len(json_data)

        # Add book metadata
        book_data = {
            'book_info': {
                **book_info,
                'total_chapters': total_chapters,
                'total_verses': total_verses,
                'processed_date': datetime.now().isoformat(),
                'processor_version': '2.1.0'  # Updated version
            },
            'verses': json_data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

        print(f"Saved: {filepath} ({total_verses} verses in {total_chapters} chapters)")

    def validate_processing(self, json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate processing results."""
        book_info = self.BOOKS_INFO[self.book_key]
        expected_chapters = book_info['expected_chapters']

        # Group by chapters
        chapters_data = {}
        for verse in json_data:
            chapter = verse['chapter']
            if chapter not in chapters_data:
                chapters_data[chapter] = []
            chapters_data[chapter].append(verse)

        # Statistics
        total_chapters = len(chapters_data)
        total_verses = len(json_data)
        chapters_with_titles = sum(1 for chapter_num, verses in chapters_data.items()
                                 if any('title' in v for v in verses))
        verses_with_footnotes = sum(1 for v in json_data if v.get('footnotes'))
        verses_with_hebrew_terms = sum(1 for v in json_data if v.get('hebrew_terms'))

        # Validation
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

        # Check for issues
        if total_chapters != expected_chapters:
            validation_results['issues'].append(
                f"Chapters: expected {expected_chapters}, found {total_chapters}"
            )

        for chapter_num in range(1, total_chapters + 1):
            if chapter_num not in chapters_data:
                validation_results['issues'].append(f"Capítulo {chapter_num} faltante")

        empty_verses = [v for v in json_data if not v.get('tth', '').strip()]
        if empty_verses:
            validation_results['issues'].append(f"{len(empty_verses)} verses with empty text")

        return validation_results

    def process_markdown_file(self, markdown_file: str) -> Dict[str, Any]:
        """
        Process a markdown file to JSON.

        Args:
            markdown_file: Path to markdown file

        Returns:
            Validation results
        """
        print(f"Procesando {self.book_key} desde {markdown_file}...")
        print("Using modified processor with text cleaner v2.1.0")

        # Read markdown
        markdown_text = self.read_markdown(markdown_file)
        print(f"Markdown read: {len(markdown_text)} characters")

        # Extract footnote definitions
        self.extract_footnote_definitions(markdown_text)
        print(f"Definiciones de notas al pie encontradas: {len(self.footnote_definitions)}")

        # Extract chapters
        chapters = self.extract_chapters(markdown_text)
        print(f"Chapters found: {len(chapters)}")

        # Create JSON structure
        json_data = self.create_json_structure(chapters)
        print(f"Total verses: {len(json_data)}")

        # Validate
        validation = self.validate_processing(json_data)

        print("\n=== VALIDATION REPORT ===")
        print(f"Chapters: {validation['actual_chapters']}/{validation['expected_chapters']} {'✓' if validation['chapters_match'] else '✗'}")
        print(f"Total verses: {validation['total_verses']}")
        print(f"Chapters with titles: {validation['chapters_with_titles']}")
        print(f"Verses with footnotes: {validation['verses_with_footnotes']}")
        print(f"Verses with Hebrew terms: {validation['verses_with_hebrew_terms']}")
        print(f"Footnote definitions found: {validation['footnote_definitions_found']}")

        if validation['issues']:
            print("\n⚠️  ISSUES FOUND:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        else:
            print("\n✓ Validation successful - No issues found")

        # Save files
        self.save_book_file(json_data)

        print("\nProcessing completed successfully!")
        return validation


def process_book_to_json(book_key: str, markdown_file: str, output_dir: str = 'draft') -> Dict[str, Any]:
    """
    Convenience function to process a book from markdown to JSON.

    Args:
        book_key: Book identifier
        markdown_file: Path to markdown file
        output_dir: Output directory

    Returns:
        Validation results
    """
    processor = TTHProcessor(book_key=book_key, output_dir=output_dir)
    return processor.process_markdown_file(markdown_file)

