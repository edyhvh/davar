#!/usr/bin/env python3
"""
Ejemplo: Generación de Versículos Ligeros

Este script muestra cómo transformar los datos de data/oe/ 
en versículos ligeros que referencian al lexicon.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Directorios
DICT_DIR = Path(__file__).parent
OE_DIR = Path(__file__).parent.parent / 'oe'  # data/oe/
VERSES_DIR = DICT_DIR / 'verses'
VERSES_DIR.mkdir(exist_ok=True)


# Mapeo de nombres de libros (ejemplo parcial)
BOOK_NAMES = {
    'genesis': {
        'es': 'Génesis',
        'en': 'Genesis',
        'heb': 'בְּרֵאשִׁית'
    },
    'exodus': {
        'es': 'Éxodo',
        'en': 'Exodus',
        'heb': 'שְׁמוֹת'
    },
    # ... más libros
}


def normalize_book_name(book_name: str) -> str:
    """
    Normaliza nombre de libro a formato estándar
    
    Ejemplos:
        Genesis → genesis
        1Samuel → 1samuel
        IChr → 1chronicles
    """
    book_name = book_name.lower()
    
    # Mapeo de variaciones comunes
    variations = {
        '1samuel': '1samuel',
        '1sam': '1samuel',
        '2samuel': '2samuel',
        '2sam': '2samuel',
        '1kings': '1kings',
        '1kgs': '1kings',
        '2kings': '2kings',
        '2kgs': '2kings',
        '1chronicles': '1chronicles',
        '1chr': '1chronicles',
        '2chronicles': '2chronicles',
        '2chr': '2chronicles',
    }
    
    return variations.get(book_name, book_name)


def extract_strong_number(lemma: str) -> str:
    """
    Extrae el Strong's number de un lemma
    
    Ejemplos:
        H1254 → H1254
        Hb/H7225 → H7225
        Hc/H1961 → H1961
    """
    # Remover prefijos comunes
    lemma = lemma.replace('Hb/', '').replace('Hc/', '').replace('Hd/', '')
    
    # Extraer número Strong's
    match = re.search(r'H\d+', lemma)
    if match:
        return match.group(0)
    
    return lemma


def process_word(word_data: Dict, position: int) -> Dict:
    """
    Procesa una palabra del archivo oe/ y la convierte al formato del versículo
    
    Args:
        word_data: Datos de la palabra desde oe/
        position: Posición de la palabra en el versículo
    
    Returns:
        Dict con formato del versículo ligero
    """
    # Extraer Strong's number
    strong = word_data.get('strong') or word_data.get('lemma', '')
    lexicon_ref = extract_strong_number(strong)
    
    return {
        "position": position,
        "hebrew": word_data.get('text', '').replace('/', ''),  # Limpiar separadores
        "hebrew_no_nikud": word_data.get('text_no_nikud', '').replace('/', ''),
        "lexicon_ref": lexicon_ref,
        "morphology": word_data.get('morph', ''),
        "bdb_sense": None  # Se agregará después con el índice de BDB
    }


def generate_verse(book_name: str, chapter: int, verse: int, verse_data: Dict) -> Dict:
    """
    Genera un versículo ligero desde los datos de oe/
    
    Args:
        book_name: Nombre del libro (ej: 'genesis')
        chapter: Número de capítulo
        verse: Número de versículo
        verse_data: Datos del versículo desde oe/
    
    Returns:
        Dict con formato del versículo ligero
    """
    # Normalizar referencia
    normalized_book = normalize_book_name(book_name)
    reference = f"{normalized_book}.{chapter}.{verse}"
    
    # Obtener nombres del libro
    book_info = BOOK_NAMES.get(normalized_book, {
        'es': book_name.title(),
        'en': book_name.title(),
        'heb': ''
    })
    
    # Procesar palabras
    words_data = verse_data.get('words', [])
    words = []
    for i, word_data in enumerate(words_data, start=1):
        word = process_word(word_data, i)
        words.append(word)
    
    # Construir versículo
    verse_obj = {
        "reference": reference,
        "book": book_info,
        "chapter": chapter,
        "verse": verse,
        "hebrew_text": verse_data.get('hebrew', '').replace('/', ' '),
        "spanish_text": None,  # Se agregará cuando tengamos TTH
        "words": words,
        "metadata": {
            "has_qumran_variants": False,  # Se determinará después
            "has_cross_references": False,  # Se determinará después
            "source": "oe"
        }
    }
    
    return verse_obj


def process_oe_file(book_name: str, chapter_file: Path) -> List[Dict]:
    """
    Procesa un archivo de capítulo desde oe/ y genera versículos
    
    Args:
        book_name: Nombre del libro
        chapter_file: Path al archivo JSON del capítulo
    
    Returns:
        Lista de versículos generados
    """
    with open(chapter_file, 'r', encoding='utf-8') as f:
        verses_data = json.load(f)
    
    # Extraer número de capítulo del nombre del archivo
    chapter_num = int(chapter_file.stem)
    
    verses = []
    for verse_data in verses_data:
        verse_num = verse_data.get('verse', 0)
        verse_obj = generate_verse(book_name, chapter_num, verse_num, verse_data)
        verses.append(verse_obj)
    
    return verses


def example_generate_genesis_1():
    """
    Ejemplo: Generar versículos de Génesis 1
    """
    print("=" * 60)
    print("EJEMPLO: Generación de Versículos Ligeros")
    print("=" * 60)
    
    # Leer archivo de ejemplo
    genesis_1_file = OE_DIR / 'genesis' / '1.json'
    
    if not genesis_1_file.exists():
        print(f"❌ Archivo no encontrado: {genesis_1_file}")
        return
    
    print(f"📖 Procesando: {genesis_1_file}")
    
    verses = process_oe_file('genesis', genesis_1_file)
    
    print(f"✅ Generados {len(verses)} versículos")
    
    # Guardar cada versículo
    for verse in verses:
        reference = verse['reference']
        output_file = VERSES_DIR / f"{reference}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(verse, f, ensure_ascii=False, indent=2)
        
        print(f"   💾 {reference} → {output_file}")
    
    # Mostrar ejemplo
    if verses:
        print(f"\n📄 Ejemplo - {verses[0]['reference']}:")
        print(json.dumps(verses[0], ensure_ascii=False, indent=2)[:500] + "...")


if __name__ == "__main__":
    example_generate_genesis_1()

