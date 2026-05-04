import json
import os
from pathlib import Path

def calculate_pages_with_line_spacing_1_4():
    """Calculate total characters and estimate pages needed for A4 printing with 1.4 line spacing"""

    # Get the script directory and navigate to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    output_dir = project_root / "output"

    if not output_dir.exists():
        print(f"Error: No se encontró el directorio {output_dir}")
        return

    total_chars = 0
    total_verses = 0
    total_words = 0

    # Count all characters in text_nikud fields
    json_files = list(output_dir.glob("*.json"))
    if not json_files:
        print(f"Error: No se encontraron archivos JSON en {output_dir}")
        return

    for json_file in sorted(json_files):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for chapter in data.get('chapters', []):
            for verse in chapter.get('verses', []):
                text = verse.get('text_nikud', '')
                total_chars += len(text)
                total_words += len(text.split())
                total_verses += 1

    print(f"=== Estadísticas del Texto ===")
    print(f"Total de versos: {total_verses:,}")
    print(f"Total de caracteres: {total_chars:,}")
    print(f"Total de palabras: {total_words:,}")
    if total_verses > 0:
        print(f"Promedio de caracteres por verso: {total_chars/total_verses:.1f}")
    else:
        print("Error: No se encontraron versos")
        return

    # Calculate for different configurations
    formats = {
        "A4": {
            "page_width": 210,  # mm
            "page_height": 297,  # mm
            "margin": 25,  # mm (2.5cm each side)
        },
        "A5": {
            "page_width": 148,  # mm (half of A4 width)
            "page_height": 210,  # mm (half of A4 height)
            "margin": 25,  # mm (2.5cm each side)
        }
    }

    # Different font and spacing configurations to test
    configurations = [
        {"format": "A4", "font_size": 10, "line_spacing": 1.4, "chars_per_line": 75, "chars_options": [70, 75, 80, 85]},
        {"format": "A5", "font_size": 10, "line_spacing": 1.4, "chars_per_line": 50, "chars_options": [45, 50, 55, 60]},
        {"format": "A5", "font_size": 9, "line_spacing": 1.3, "chars_per_line": 55, "chars_options": [50, 55, 60, 65]},
    ]

    for config in configurations:
        format_name = config["format"]
        specs = formats[format_name]
        font_size_pt = config["font_size"]
        line_spacing = config["line_spacing"]
        default_chars = config["chars_per_line"]
        chars_options = config["chars_options"]

        font_size_mm = font_size_pt * 0.352778  # Convert pt to mm
        line_height_mm = font_size_mm * line_spacing

        usable_width = specs["page_width"] - (specs["margin"] * 2)
        usable_height = specs["page_height"] - (specs["margin"] * 2)

        # Calculate lines per page
        lines_per_page = int(usable_height / line_height_mm)

        chars_per_page_one_side = lines_per_page * default_chars
        pages_needed = (total_chars / chars_per_page_one_side) / 2

        print(f"\n{'='*60}")
        print(f"=== Formato {format_name} - Fuente {font_size_pt}pt, Interlineado {line_spacing} ===")
        print(f"{'='*60}")
        print(f"Tamaño de página: {specs['page_width']}mm x {specs['page_height']}mm")
        print(f"Márgenes: {specs['margin']}mm cada lado")
        print(f"Área utilizable: {usable_width}mm x {usable_height}mm")
        print(f"Tamaño de fuente: {font_size_pt}pt")
        print(f"Interlineado: {line_spacing}")
        print(f"Altura de línea: {line_height_mm:.2f}mm")
        print(f"Líneas por página: {lines_per_page}")
        print(f"\n=== Resultado con {default_chars} caracteres/línea ===")
        print(f"Caracteres por página (una cara): {chars_per_page_one_side:,}")
        print(f"Páginas necesarias (impresión a doble cara): {pages_needed:.1f}")
        print(f"Páginas necesarias (redondeado): {int(pages_needed) + (1 if pages_needed % 1 > 0 else 0)}")

        # Additional calculations with different chars_per_line for comparison
        print(f"\n=== Variaciones según caracteres por línea ===")
        for chars in chars_options:
            chars_per_page = lines_per_page * chars
            pages = (total_chars / chars_per_page) / 2
            print(f"Con {chars} caracteres/línea: {pages:.1f} páginas")

if __name__ == "__main__":
    calculate_pages_with_line_spacing_1_4()