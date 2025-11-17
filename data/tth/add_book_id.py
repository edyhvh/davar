#!/usr/bin/env python3
"""
Script para agregar book_id y book_english_name_lower a todos los archivos JSON
en tth/draft/ basándose en el book_info.json de cada libro.
"""

import json
import os
from pathlib import Path
from collections import OrderedDict

def reorder_verse_fields(verse: dict, book_id: str) -> dict:
    """Reordena los campos del versículo para que book_id esté después de book"""
    if not isinstance(verse, dict):
        return verse
    
    # Crear un nuevo diccionario ordenado
    ordered_verse = OrderedDict()
    
    # Campos que deben ir al inicio en orden específico
    priority_fields = ['book', 'book_id']
    
    # Agregar book_id si no existe
    if 'book_id' not in verse:
        verse['book_id'] = book_id
    
    # Agregar book_english_name_lower si no existe
    if 'book_english_name_lower' not in verse:
        verse['book_english_name_lower'] = book_id
    
    # Primero agregar los campos prioritarios en orden
    for field in priority_fields:
        if field in verse:
            ordered_verse[field] = verse[field]
    
    # Luego agregar el resto de los campos en el orden que aparecen
    for key, value in verse.items():
        if key not in priority_fields:
            ordered_verse[key] = value
    
    return ordered_verse

def process_book_directory(book_dir: Path):
    """Procesa todos los archivos JSON de un libro"""
    book_info_path = book_dir / "book_info.json"
    
    if not book_info_path.exists():
        print(f"⚠️  No se encontró book_info.json en {book_dir.name}")
        return
    
    # Leer book_info.json
    with open(book_info_path, 'r', encoding='utf-8') as f:
        book_info = json.load(f)
    
    english_name = book_info.get('english_name', '')
    if not english_name:
        print(f"⚠️  No se encontró english_name en {book_dir.name}/book_info.json")
        return
    
    # book_id será el nombre en inglés en minúsculas
    book_id = english_name.lower()
    
    print(f"📖 Procesando {book_dir.name}: book_id = '{book_id}'")
    
    # Procesar todos los archivos JSON de capítulos (excluyendo book_info.json)
    json_files = sorted([f for f in book_dir.glob("*.json") if f.name != "book_info.json"])
    
    if not json_files:
        print(f"   No se encontraron archivos JSON de capítulos")
        return
    
    total_verses = 0
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"   ⚠️  {json_file.name} no es una lista, saltando...")
            continue
        
        reordered_data = []
        needs_save = False
        
        for verse in data:
            if not isinstance(verse, dict):
                reordered_data.append(verse)
                continue
            
            # Verificar si necesita actualización de valores
            original_book_id = verse.get('book_id')
            if 'book_id' not in verse or original_book_id != book_id:
                needs_save = True
            
            # Reordenar campos y agregar/actualizar book_id
            reordered_verse = reorder_verse_fields(verse, book_id)
            reordered_data.append(reordered_verse)
            
            # Verificar si el orden cambió comparando las claves
            if list(verse.keys())[:2] != ['book', 'book_id']:
                needs_save = True
        
        if needs_save:
            # Guardar el archivo actualizado
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(reordered_data, f, ensure_ascii=False, indent=2)
            total_verses += len(data)
            print(f"   ✓ Actualizado {json_file.name} ({len(data)} versículos)")
    
    print(f"   ✅ Completado: {len(json_files)} archivos, {total_verses} versículos totales\n")

def main():
    """Función principal"""
    script_dir = Path(__file__).parent
    draft_dir = script_dir / "draft"
    
    if not draft_dir.exists():
        print(f"❌ No se encontró el directorio {draft_dir}")
        return
    
    print(f"🚀 Iniciando procesamiento de libros en {draft_dir}\n")
    
    # Obtener todos los directorios de libros
    book_dirs = [d for d in draft_dir.iterdir() if d.is_dir()]
    
    if not book_dirs:
        print("❌ No se encontraron directorios de libros")
        return
    
    print(f"📚 Encontrados {len(book_dirs)} libros\n")
    
    # Procesar cada libro
    for book_dir in sorted(book_dirs):
        process_book_directory(book_dir)
    
    print("✨ Procesamiento completado!")

if __name__ == "__main__":
    main()

