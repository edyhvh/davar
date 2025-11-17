#!/usr/bin/env python3
"""
Ejemplo: Extracción de BDB Senses para determinar definición contextual

Este script muestra cómo extraer los "senses" del BDB XML y crear
un índice que mapea versículos → Strong's → sense number.
"""

import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path
from collections import defaultdict

# Namespaces del BDB XML
NS = {
    'bdb': 'http://openscriptures.github.com/morphhb/namespace'
}

BDB_XML = Path(__file__).parent / 'BrownDriverBriggs.xml'


def normalize_reference(bdb_ref: str) -> str:
    """
    Normaliza referencia del BDB a formato lowercase
    
    Ejemplos:
        Gen.15.15 → gen.15.15
        1Sam.9.3 → 1sam.9.3
        Ps.119.92 → ps.119.92
    """
    # Mapeo de abreviaciones del BDB a formato estándar
    book_map = {
        'Gen': 'gen', 'Exod': 'exod', 'Lev': 'lev', 'Num': 'num',
        'Deut': 'deut', 'Josh': 'josh', 'Judg': 'judg', 'Ruth': 'ruth',
        '1Sam': '1sam', '2Sam': '2sam', '1Kgs': '1kgs', '2Kgs': '2kgs',
        '1Chr': '1chr', '2Chr': '2chr', 'Ezra': 'ezra', 'Neh': 'neh',
        'Esth': 'esth', 'Job': 'job', 'Ps': 'ps', 'Prov': 'prov',
        'Eccl': 'eccl', 'Song': 'song', 'Isa': 'isa', 'Jer': 'jer',
        'Lam': 'lam', 'Ezek': 'ezek', 'Dan': 'dan', 'Hos': 'hos',
        'Joel': 'joel', 'Amos': 'amos', 'Obad': 'obad', 'Jonah': 'jonah',
        'Mic': 'mic', 'Nah': 'nah', 'Hab': 'hab', 'Zeph': 'zeph',
        'Hag': 'hag', 'Zech': 'zech', 'Mal': 'mal'
    }
    
    # Parsear referencia: Book.Chapter.Verse
    parts = bdb_ref.split('.')
    if len(parts) < 3:
        return bdb_ref.lower()
    
    book = parts[0]
    chapter = parts[1]
    verse = parts[2]
    
    # Normalizar libro
    normalized_book = book_map.get(book, book.lower())
    
    return f"{normalized_book}.{chapter}.{verse}"


def extract_strong_from_entry(entry) -> str:
    """
    Intenta extraer el Strong's number de un entry del BDB
    
    Nota: El BDB no siempre tiene Strong's explícito, pero podemos
    buscarlo en el LexicalIndex o usar el hebrew word para buscarlo.
    """
    # Por ahora retornamos None, se completará con mapeo externo
    return None


def extract_bdb_senses():
    """
    Extrae todos los senses del BDB con sus referencias a versículos
    
    Returns:
        dict: {
            "H7965": {
                "1": ["gen.15.15", "gen.26.29", ...],
                "2": ["gen.37.4", ...]
            },
            ...
        }
    """
    print("Parsing BDB XML...")
    tree = ET.parse(BDB_XML)
    root = tree.getroot()
    
    # Estructura para almacenar: strong → sense → verses
    senses_by_strong = defaultdict(lambda: defaultdict(list))
    
    # Estructura alternativa: verse → strong → sense
    verse_sense_index = defaultdict(dict)
    
    entries = root.findall('.//bdb:entry', NS)
    print(f"Found {len(entries)} entries")
    
    # Por ahora, vamos a buscar un ejemplo específico: shalom (שָׁלוֹם)
    # En producción, necesitaríamos mapear hebrew word → Strong's
    
    for entry in entries[:100]:  # Limitar para ejemplo
        # Buscar palabra hebrea
        w_elements = entry.findall('.//bdb:w', NS)
        if not w_elements:
            continue
        
        hebrew_word = w_elements[0].text
        if not hebrew_word:
            continue
        
        # Buscar senses
        senses = entry.findall('.//bdb:sense', NS)
        
        for sense in senses:
            sense_num = sense.get('n', '')
            if not sense_num:
                continue
            
            # Buscar referencias en este sense
            refs = sense.findall('.//bdb:ref', NS)
            
            for ref in refs:
                verse_ref = ref.get('r', '')
                if verse_ref:
                    normalized_ref = normalize_reference(verse_ref)
                    
                    # Por ahora usamos el hebrew word como clave
                    # En producción necesitaríamos Strong's number
                    word_key = f"hebrew:{hebrew_word}"
                    
                    senses_by_strong[word_key][sense_num].append(normalized_ref)
                    verse_sense_index[normalized_ref][word_key] = sense_num
    
    return senses_by_strong, verse_sense_index


def example_usage():
    """
    Ejemplo de cómo usar la extracción de senses
    """
    print("=" * 60)
    print("EJEMPLO: Extracción de BDB Senses")
    print("=" * 60)
    
    senses_by_strong, verse_sense_index = extract_bdb_senses()
    
    print(f"\n✅ Extraídos {len(senses_by_strong)} palabras con senses")
    print(f"✅ Indexados {len(verse_sense_index)} versículos")
    
    # Ejemplo: Buscar senses para un versículo específico
    example_verse = "gen.15.15"
    if example_verse in verse_sense_index:
        print(f"\n📖 Senses para {example_verse}:")
        for word_key, sense_num in verse_sense_index[example_verse].items():
            print(f"   {word_key}: sense {sense_num}")
    
    # Ejemplo: Buscar versículos para un sense específico
    example_word = "hebrew:שָׁלוֹם"
    if example_word in senses_by_strong:
        print(f"\n📚 Versículos para {example_word}:")
        for sense_num, verses in senses_by_strong[example_word].items():
            print(f"   Sense {sense_num}: {len(verses)} versículos")
            print(f"      Ejemplos: {verses[:5]}")
    
    # Guardar índice (ejemplo)
    output_file = Path(__file__).parent / 'bdb_verse_sense_index_example.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dict(verse_sense_index), f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Índice guardado en: {output_file}")


if __name__ == "__main__":
    example_usage()

