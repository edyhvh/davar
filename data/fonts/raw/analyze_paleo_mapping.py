#!/usr/bin/env python3
"""
Script para analizar el mapeo de la fuente PaleoHebrew.ttf
Creado para el proyecto Davar - Fuentes Hebreas
"""

import os

# Mapeo estándar esperado para fuentes paleo-hebreas
expected_mapping = {
    'A': 'א',  # Alef
    'B': 'ב',  # Bet
    'G': 'ג',  # Gimel
    'D': 'ד',  # Dalet
    'H': 'ה',  # He
    'V': 'ו',  # Vav
    'W': 'ו',  # Vav (alternativo)
    'Z': 'ז',  # Zayin
    'CH': 'ח', # Chet (usualmente CH o H con modificador)
    'T': 'ת',  # Tav
    'TH': 'ת', # Tav (alternativo)
    'I': 'י',  # Yod
    'Y': 'י',  # Yod (alternativo)
    'K': 'כ',  # Kaf
    'L': 'ל',  # Lamed
    'M': 'מ',  # Mem
    'N': 'נ',  # Nun
    'S': 'ש',  # Shin (o Samekh)
    'SH': 'ש', # Shin
    'O': 'ע',  # Ayin
    'P': 'פ',  # Pe
    'TS': 'צ', # Tsade
    'Q': 'ק',  # Qof
    'R': 'ר',  # Resh
}

# Texto hebreo: בראשית ברא אלהים את השמים ואת הארץ׃
hebrew_text = "בראשית ברא אלהים את השמים ואת הארץ׃"

# Descomposición fonética
phonetic_breakdown = [
    ("ב", "B", "Bet"),
    ("ר", "R", "Resh"),
    ("א", "A", "Alef"),
    ("ש", "SH", "Shin"),
    ("י", "Y", "Yod"),
    ("ת", "T", "Tav"),
    (" ", " ", "space"),
    ("ב", "B", "Bet"),
    ("ר", "R", "Resh"),
    ("א", "A", "Alef"),
    (" ", " ", "space"),
    ("א", "A", "Alef"),
    ("ל", "L", "Lamed"),
    ("ה", "H", "He"),
    ("י", "Y", "Yod"),
    ("ם", "M", "Mem"),
    (" ", " ", "space"),
    ("א", "A", "Alef"),
    ("ת", "T", "Tav"),
    (" ", " ", "space"),
    ("ה", "H", "He"),
    ("ש", "SH", "Shin"),
    ("מ", "M", "Mem"),
    ("י", "Y", "Yod"),
    ("ם", "M", "Mem"),
    (" ", " ", "space"),
    ("ו", "V", "Vav"),
    ("א", "A", "Alef"),
    ("ת", "T", "Tav"),
    (" ", " ", "space"),
    ("ה", "H", "He"),
    ("א", "A", "Alef"),
    ("ר", "R", "Resh"),
    ("ץ", "TS", "Tsade"),
]

print("ANÁLISIS DEL MAPEO PALEO-HEBREO - PROYECTO DAVAR")
print("=" * 60)
print()
print("Texto hebreo original:")
print(hebrew_text)
print()
print("Descomposición fonética:")
print("Hebreo | Latino | Nombre | Descripción")
print("-" * 45)
for heb, lat, name in phonetic_breakdown:
    if heb == " ":
        print(f"   {heb}   |   {lat}   | {name}")
    else:
        print(f"   {heb}   |   {lat}   | {name}")

print()
print("Mapeo usado en font_preview.html:")
current_mapping = "BRASYT BRA ALHYM AT HASMYM VAT HARTS"
print(current_mapping)
print()
print("Nota: La fuente PaleoHebrew.ttf mapea letras latinas a glifos paleo-hebreos.")
print("El mapeo específico depende de cómo esté configurada la fuente.")
print()
print("Posibles problemas:")
print("1. La fuente podría no manejar correctamente combinaciones como 'SH' o 'TS'")
print("2. El mapeo podría ser diferente al estándar esperado")
print("3. Podría requerir letras individuales en lugar de combinaciones")
print()
print("Solución aplicada:")
print("- Cambiar 'SH' por 'S' para compatibilidad con fuentes que mapean individualmente")
print("- Mantener 'TS' como combinación aceptada")
print("- Resultado: BRASYT BRA ALHYM AT HASMYM VAT HARTS")
