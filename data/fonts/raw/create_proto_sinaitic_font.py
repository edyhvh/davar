#!/usr/bin/env python3
"""
Script para crear una fuente TrueType (.ttf) a partir de los glifos proto-sinaíticos en SVG
Los glifos están ordenados del 1 al 22, donde 1 = Alef (א), siguiendo el orden del alfabeto hebreo
"""

import os
import sys
from pathlib import Path

def create_fontforge_script(svg_dir, output_font):
    """Crea un script de FontForge para generar la fuente"""

    script_content = '''#!/usr/bin/fontforge
# Script de FontForge para crear fuente Proto-Sinaítica

# Crear nueva fuente
New();

# Configurar unidades por em
SetFontHasVerticalMetrics(0);
ScaleToEm(1000);

'''

    # Crear glifos e importar SVGs en orden correcto (1-22 donde 1=Alef)
    base_unicode = 0xE000  # Empezar en el rango de uso privado

    for i in range(1, 23):  # 1 al 22
        svg_file = f"{svg_dir}/{i}.svg"
        unicode_value = base_unicode + (i - 1)
        glyph_index = i - 1  # Índices empiezan en 0

        hebrew_names = [
            "Alef (א)", "Bet (ב)", "Gimel (ג)", "Dalet (ד)", "He (ה)", "Vav (ו)",
            "Zayin (ז)", "Chet (ח)", "Tet (ט)", "Yod (י)", "Kaf (כ)", "Lamed (ל)",
            "Mem (מ)", "Nun (נ)", "Samekh (ס)", "Ayin (ע)", "Pe (פ)", "Tsade (צ)",
            "Qof (ק)", "Resh (ר)", "Shin (ש)", "Tav (ת)"
        ]
        letter_name = hebrew_names[i-1] if i-1 < len(hebrew_names) else f"Letra {i}"

        script_content += f'''
# Crear glifo {i} (U+{unicode_value:04X}) - {letter_name}
Select({glyph_index});
SetUnicodeValue({unicode_value});
Import("{svg_file}");
Simplify();
AddExtrema();
RoundToInt();
CorrectDirection();
'''

    # Configurar metadatos
    script_content += '''
# Configurar metadatos
SetTTFName(0x409, 1, "Proto Sinaitic Leo");
SetTTFName(0x409, 2, "Regular");
SetTTFName(0x409, 4, "Proto Sinaitic Leo Regular");
SetTTFName(0x409, 6, "ProtoSinaiticLeo-Regular");

# Configurar métricas OS/2
SetOS2Value("Weight", 400);
SetOS2Value("Width", 5);
SetOS2Value("FSType", 0);

'''

    # Generar la fuente
    script_content += f'''
# Generar la fuente
Generate("{output_font}");

# Cerrar FontForge
Quit(0);
'''

    return script_content

def main():
    # Directorios
    project_root = Path(__file__).parent.parent.parent  # Subir 3 niveles: fonts -> data -> davar
    svg_dir = project_root / "data/fonts/proto_sinaitic_leo"
    output_font = project_root / "data/fonts/ProtoSinaiticLeo-Regular.ttf"
    script_file = project_root / "proto_sinaitic_fontforge_script.pe"

    # Verificar que el directorio de SVGs existe
    if not svg_dir.exists():
        print(f"❌ Error: Directorio {svg_dir} no encontrado")
        sys.exit(1)

    # Verificar que existen los archivos SVG
    svg_files = list(svg_dir.glob("*.svg"))
    if len(svg_files) != 22:
        print(f"⚠️  Advertencia: Se encontraron {len(svg_files)} archivos SVG, se esperaban 22")
        print("Archivos encontrados:", [f.name for f in svg_files])

    # Crear el script de FontForge
    script_content = create_fontforge_script(svg_dir, output_font)
    script_file.write_text(script_content, encoding='utf-8')

    print(f"✅ Script de FontForge creado: {script_file}")
    print(f"📁 Directorio SVG: {svg_dir}")
    print(f"🎨 Fuente de salida: {output_font}")
    print("📋 Orden de glifos: 1=Alef (א), 2=Bet (ב), ..., 22=Tav (ת)")

    # Ejecutar el script con FontForge
    print("🔧 Ejecutando FontForge...")
    result = os.system(f"fontforge -script {script_file}")

    # Verificar que se creó la fuente
    if output_font.exists() and result == 0:
        size_kb = output_font.stat().st_size / 1024
        print(f"✅ Fuente creada: {size_kb:.1f} KB")
        print("✅ ¡Fuente Proto-Sinaítica creada exitosamente!")
        print("📝 Mapeo: U+E000 (1) = Alef, U+E001 (2) = Bet, ..., U+E015 (22) = Tav")

        # Crear un archivo de muestra actualizado
        update_sample_file(output_font, project_root)
    else:
        print("❌ Error: No se pudo crear la fuente")
        print(f"Código de salida: {result}")

    # Limpiar archivo temporal
    if script_file.exists():
        script_file.unlink()

def update_sample_file(font_path, project_root):
    """Actualiza el archivo HTML de muestra con la nueva fuente"""

    sample_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Proto Sinaitic Leo - Sample</title>
    <style>
        @font-face {{
            font-family: 'ProtoSinaiticLeo';
            src: url('{font_path.name}') format('truetype');
        }}
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .glyph {{ font-family: 'ProtoSinaiticLeo'; font-size: 48px; margin: 10px; }}
        .unicode {{ font-family: monospace; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <h1>Proto Sinaitic Leo Font</h1>
    <p>Glifos proto-sinaíticos mapeados a Unicode U+E000-U+E015</p>

    <div style="display: grid; grid-template-columns: repeat(11, 1fr); gap: 10px; margin: 20px 0;">
'''

    # Agregar cada glifo con su información
    hebrew_letters = [
        "א Alef", "ב Bet", "ג Gimel", "ד Dalet", "ה He", "ו Vav", "ז Zayin", "ח Chet", "ט Tet", "י Yod", "כ Kaf",
        "ל Lamed", "מ Mem", "נ Nun", "ס Samekh", "ע Ayin", "פ Pe", "צ Tsade", "ק Qof", "ר Resh", "ש Shin", "ת Tav"
    ]

    for i in range(22):
        unicode_val = 0xE000 + i
        letter_name = hebrew_letters[i] if i < len(hebrew_letters) else f"Letra {i+1}"
        sample_content += f'''
        <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
            <div class="glyph">&#{unicode_val};</div>
            <div class="unicode">U+{unicode_val:04X}</div>
            <div style="font-size: 10px; color: #666;">{letter_name}</div>
        </div>'''

    sample_content += '''
    </div>

    <h2>Información Técnica</h2>
    <ul>
        <li><strong>Archivo:</strong> ProtoSinaiticLeo-Regular.ttf</li>
        <li><strong>Rango Unicode:</strong> U+E000 - U+E015 (Uso privado)</li>
        <li><strong>Glifos:</strong> 22 caracteres proto-sinaíticos</li>
        <li><strong>Orden:</strong> 1=Alef (א), 2=Bet (ב), ..., 22=Tav (ת)</li>
    </ul>
</body>
</html>'''

    sample_file = project_root / "data/fonts/proto_sinaitic_sample.html"
    sample_file.write_text(sample_content, encoding='utf-8')
    print(f"📄 Archivo de muestra actualizado: {sample_file}")

if __name__ == "__main__":
    main()