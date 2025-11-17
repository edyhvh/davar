#!/usr/bin/env python3
"""
Script para convertir archivos .docx a Markdown
Convierte tanaj.docx a tanaj.md con formato similar a tesalonicenses.md
"""

import sys
import os
import re
from pathlib import Path

try:
    import mammoth
except ImportError:
    print("Error: La librería 'mammoth' no está instalada.")
    print("Instálala con: pip install mammoth")
    sys.exit(1)


def normalize_markdown(text: str) -> str:
    """
    Normaliza el markdown para que tenga formato similar a tesalonicenses.md
    
    Args:
        text: Texto markdown crudo de mammoth
        
    Returns:
        Texto markdown normalizado
    """
    # Convertir notas al pie de formato HTML a formato markdown
    # Patrón: <a id="footnote-ref-1"></a>[[1]](#footnote-1)
    # Resultado: [^1]
    text = re.sub(
        r'<a id="footnote-ref-(\d+)"[^>]*></a>\[\[\d+\]\]\(#footnote-\d+\)',
        r'[^\1]',
        text
    )
    
    # También manejar casos donde solo está el enlace sin el número visible
    text = re.sub(r'<a[^>]*id="footnote-ref-(\d+)"[^>]*></a>', r'[^\1]', text)
    
    # Limpiar enlaces markdown duplicados después de notas al pie
    # De: [^1][[1]](#footnote-1) a [^1]
    text = re.sub(r'\[\^(\d+)\]\[\[\d+\]\]\(#footnote-\d+\)', r'[^\1]', text)
    
    # Limpiar notas al pie duplicadas adicionales que pueden quedar
    # De: [^1][[1]](#footnote-1) o [^1][\[1\]](#footnote-1) a [^1]
    # Esto maneja variaciones en el formato de los enlaces
    # Manejar tanto [[número]] como \[número\] (con escapes)
    text = re.sub(r'\[\^(\d+)\]\[\\?\[.*?\\?\]\]\(#footnote-\d+\)', r'[^\1]', text)
    # También manejar casos donde puede haber espacios o caracteres adicionales
    text = re.sub(r'\[\^(\d+)\]\[\\?\[.*?\\?\]\]\s*\(#footnote-\d+\)', r'[^\1]', text)
    
    # Limpiar referencias de vuelta en las definiciones de notas al pie
    # De: [^1]: texto [↑](#footnote-ref-1) 2. a [^1]: texto
    # Capturar cualquier carácter entre corchetes (puede ser ↑, flecha, etc.)
    # También capturar números y punto final después del enlace
    text = re.sub(
        r'(\[\^\d+\]:\s[^\n]+?)\s*\[[^\]]+\]\(#footnote-ref-\d+\)\s*\d+\.\s*',
        r'\1\n',
        text
    )
    # Limpiar también sin el número final
    text = re.sub(
        r'(\[\^\d+\]:\s[^\n]+?)\s*\[[^\]]+\]\(#footnote-ref-\d+\)\s*',
        r'\1\n',
        text
    )
    
    # Convertir notas al pie al final del documento de formato HTML a markdown
    # Buscar patrones como: <a id="footnote-38"></a>texto de la nota
    # Reemplazar por: [^38]: texto de la nota
    def replace_footnote_definition(match):
        num = match.group(1)
        content = match.group(2).strip()
        # Limpiar HTML tags del contenido
        content = re.sub(r'<[^>]+>', '', content)
        # Limpiar espacios múltiples pero preservar uno
        content = re.sub(r'\s+', ' ', content).strip()
        return f'\n[^{num}]: {content}\n'
    
    # Buscar definiciones de notas al pie al final del documento
    text = re.sub(
        r'<a id="footnote-(\d+)"[^>]*></a>\s*(.+?)(?=<a id="footnote-|\Z)',
        replace_footnote_definition,
        text,
        flags=re.DOTALL
    )
    
    # Convertir versículos de formato __número__ a **número**
    # Manejar casos: __1__, __2__, etc. (puede tener espacios alrededor)
    text = re.sub(r'__\s*(\d+)\s*__', r'**\1**', text)
    
    # Convertir versículos con espacios: __ __ (versículo sin número al inicio)
    # Normalmente esto es el versículo 1 después del número de capítulo
    text = re.sub(r'__\s*__', r'**1**', text)
    
    # Convertir cualquier __número__ restante que pueda quedar
    text = re.sub(r'__(\d+)__', r'**\1**', text)
    
    # Limpiar espacios múltiples pero preservar un espacio después de versículos
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Normalizar saltos de línea múltiples (máximo 2 líneas vacías consecutivas)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    # Limpiar espacios al inicio y final de líneas
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    text = '\n'.join(lines)
    
    # Eliminar líneas completamente vacías al inicio
    text = text.lstrip('\n')
    
    # Limpiar formato de cursiva y negrita inconsistente
    # Remover asteriscos duplicados que puedan haber quedado
    text = re.sub(r'\*\*\*+', '**', text)
    
    # Limpiar caracteres de escape innecesarios pero preservar los necesarios para markdown
    # Eliminar escapes de caracteres que no necesitan escape en markdown
    # Pero mantener escapes de [, ], (, ), etc. que sí son necesarios
    # Eliminar principalmente escapes de punto, coma, punto y coma, etc.
    text = re.sub(r'\\([.;:,!?])', r'\1', text)
    
    # Limpiar espacios extras alrededor de versículos
    text = re.sub(r'\*\*(\d+)\*\*\s+', r'**\1** ', text)
    
    # Asegurar que siempre haya un espacio después de **número** si no lo hay
    # Esto corrige casos como **12**Iejaniáh a **12** Iejaniáh
    text = re.sub(r'\*\*(\d+)\*\*([A-Za-zÁÉÍÓÚáéíóúñÑ])', r'**\1** \2', text)
    
    # NUEVO: Separar versículos que están juntos en la misma línea
    # Detectar patrones como: **1** texto**2** texto**3** texto
    # Convertirlos a líneas separadas: **1** texto\n**2** texto\n**3** texto
    # Pero preservar los casos donde **número** está al inicio de línea ya
    def separate_verses_in_line(line: str) -> str:
        """
        Separa versículos que están juntos en una línea.
        Busca patrones **número** seguidos de texto y luego **número** nuevamente.
        """
        # Si la línea no tiene múltiples versículos, retornarla tal cual
        verse_count = len(re.findall(r'\*\*(\d+)\*\*', line))
        if verse_count <= 1:
            return line
        
        # Separar versículos: cada **número** seguido de su texto debe ir en su propia línea
        # Patrón: **número** texto**número** texto
        # Necesitamos separar en: **número** texto\n**número** texto
        
        # Primero, agregar un salto de línea antes de cada **número** que no esté al inicio
        # Pero solo si hay texto antes (no al inicio de línea ya)
        parts = []
        matches = list(re.finditer(r'\*\*(\d+)\*\*', line))
        
        if len(matches) <= 1:
            return line
        
        # Construir las líneas separadas
        for i, match in enumerate(matches):
            start = match.start()
            # Encontrar el final del versículo (inicio del siguiente o fin de línea)
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(line)
            
            verse_text = line[start:end].strip()
            if verse_text:
                parts.append(verse_text)
        
        return '\n'.join(parts)
    
    # Aplicar separación de versículos línea por línea
    lines = text.split('\n')
    separated_lines = []
    for line in lines:
        # Solo procesar líneas que contienen versículos
        if re.search(r'\*\*\d+\*\*', line):
            separated = separate_verses_in_line(line)
            # Si se separó, agregar las líneas resultantes
            if '\n' in separated:
                separated_lines.extend(separated.split('\n'))
            else:
                separated_lines.append(separated)
        else:
            separated_lines.append(line)
    
    text = '\n'.join(separated_lines)
    
    # Limpieza final: eliminar cualquier referencia de vuelta restante en definiciones de notas
    # Buscar líneas que empiecen con [^número]: y limpiar referencias al final
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.match(r'\[\^\d+\]:', line):
            # Limpiar referencias de vuelta al final de la línea
            line = re.sub(r'\s*\[[^\]]+\]\(#footnote-ref-\d+\)\s*\d*\.?\s*$', '', line)
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    
    return text


def convert_docx_to_markdown(input_file: str, output_file: str = None):
    """
    Convierte un archivo .docx a Markdown usando mammoth y normaliza el formato.
    
    Args:
        input_file: Ruta al archivo .docx de entrada
        output_file: Ruta al archivo .md de salida (opcional, se genera automáticamente si no se proporciona)
    """
    # Verificar que el archivo de entrada existe
    if not os.path.exists(input_file):
        print(f"Error: El archivo '{input_file}' no existe.")
        sys.exit(1)
    
    # Generar nombre de salida si no se proporciona
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.with_suffix('.md')
    
    print(f"Convirtiendo '{input_file}' a '{output_file}'...")
    
    try:
        # Convertir el documento
        with open(input_file, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown_text = result.value
            
            # Mostrar advertencias si las hay
            if result.messages:
                print("\nAdvertencias durante la conversión:")
                for message in result.messages:
                    print(f"  - {message}")
            
            # Normalizar el formato del markdown
            print("Normalizando formato...")
            markdown_text = normalize_markdown(markdown_text)
            
            # Guardar el resultado
            with open(output_file, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_text)
            
            print(f"\n✓ Conversión completada exitosamente!")
            print(f"  Archivo generado: {output_file}")
            print(f"  Tamaño: {len(markdown_text)} caracteres")
            
    except Exception as e:
        print(f"Error durante la conversión: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Función principal"""
    # Si se proporciona un argumento, usarlo como archivo de entrada
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Por defecto, convertir tanaj.docx
        script_dir = Path(__file__).parent
        input_file = script_dir / "tanaj.docx"
        output_file = script_dir / "tanaj.md"
    
    convert_docx_to_markdown(str(input_file), str(output_file) if output_file else None)


if __name__ == '__main__':
    main()

