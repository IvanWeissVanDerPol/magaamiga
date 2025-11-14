#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir archivos Markdown de ideas a PDF
"""

import os
import sys
import glob
from pathlib import Path

# Configurar salida UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import markdown2

def setup_fonts():
    """Configurar fuentes para soportar caracteres especiales"""
    styles = getSampleStyleSheet()

    # Estilos personalizados
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=18,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor='#34495e',
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor='#333333',
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='CustomBullet',
        parent=styles['BodyText'],
        fontSize=11,
        textColor='#333333',
        leftIndent=20,
        spaceAfter=6,
        fontName='Helvetica'
    ))

    return styles

def markdown_to_pdf_elements(md_text, styles):
    """Convertir texto markdown a elementos PDF"""
    elements = []
    lines = md_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            elements.append(Spacer(1, 0.2*inch))
            i += 1
            continue

        # Título principal (# )
        if line.startswith('# '):
            text = line[2:].strip()
            elements.append(Paragraph(text, styles['CustomTitle']))
            elements.append(Spacer(1, 0.3*inch))

        # Subtítulo nivel 2 (## )
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, styles['CustomHeading2']))

        # Subtítulo nivel 3 (### )
        elif line.startswith('### '):
            text = line[4:].strip()
            elements.append(Paragraph(text, styles['CustomHeading3']))

        # Lista con viñetas
        elif line.startswith('- ') or line.startswith('* '):
            text = '• ' + line[2:].strip()
            elements.append(Paragraph(text, styles['CustomBullet']))

        # Lista con checkmarks
        elif line.startswith('✅'):
            text = line
            elements.append(Paragraph(text, styles['CustomBullet']))

        # Texto con formato bold (**texto**)
        elif '**' in line:
            # Convertir markdown bold a HTML bold
            text = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
            # Si hay más bolds
            while '**' in text:
                text = text.replace('**', '<b>', 1).replace('**', '</b>', 1)
            elements.append(Paragraph(text, styles['CustomBody']))

        # Texto normal
        else:
            elements.append(Paragraph(line, styles['CustomBody']))

        i += 1

    return elements

def convert_md_to_pdf(md_file_path, output_pdf_path):
    """Convertir un archivo markdown a PDF"""
    print(f"Convirtiendo: {md_file_path}")

    # Leer archivo markdown
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Crear PDF
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Configurar estilos
    styles = setup_fonts()

    # Convertir markdown a elementos PDF
    elements = markdown_to_pdf_elements(md_content, styles)

    # Generar PDF
    doc.build(elements)
    print(f"✓ PDF creado: {output_pdf_path}")

def convert_all_ideas_to_pdf(ideas_folder, output_folder):
    """Convertir todas las ideas a PDFs individuales"""
    # Crear carpeta de salida si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Buscar todos los archivos .md en la carpeta ideas
    md_files = sorted(glob.glob(os.path.join(ideas_folder, '*.md')))

    print(f"\nEncontrados {len(md_files)} archivos markdown")
    print("="*60)

    converted = []
    for md_file in md_files:
        filename = os.path.basename(md_file)

        # Crear nombre del PDF
        pdf_filename = filename.replace('.md', '.pdf')
        output_pdf = os.path.join(output_folder, pdf_filename)

        try:
            convert_md_to_pdf(md_file, output_pdf)
            converted.append(output_pdf)
        except Exception as e:
            print(f"✗ Error convirtiendo {filename}: {e}")

    print("="*60)
    print(f"\n✓ Conversión completada: {len(converted)}/{len(md_files)} archivos")
    return converted

def create_combined_pdf(ideas_folder, output_pdf_path):
    """Crear un PDF consolidado con todas las ideas"""
    print(f"\nCreando PDF consolidado...")

    # Buscar todos los archivos .md
    md_files = sorted(glob.glob(os.path.join(ideas_folder, '*.md')))

    # Crear PDF
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = setup_fonts()
    elements = []

    # Portada
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("Campaña Pilsen 2025", styles['CustomTitle']))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Ideas Creativas", styles['CustomHeading2']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Total de ideas: {len(md_files)}", styles['CustomBody']))
    elements.append(PageBreak())

    # Agregar cada idea
    for idx, md_file in enumerate(md_files, 1):
        filename = os.path.basename(md_file)
        print(f"  Agregando: {filename}")

        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Agregar contenido
        idea_elements = markdown_to_pdf_elements(md_content, styles)
        elements.extend(idea_elements)

        # Page break entre ideas (excepto la última)
        if idx < len(md_files):
            elements.append(PageBreak())

    # Generar PDF
    doc.build(elements)
    print(f"✓ PDF consolidado creado: {output_pdf_path}")

if __name__ == "__main__":
    # Rutas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ideas_folder = os.path.join(script_dir, 'ideas')
    output_folder = os.path.join(script_dir, 'ideas-pdf')

    print("="*60)
    print("CONVERSIÓN DE IDEAS A PDF")
    print("="*60)

    # Convertir cada idea a PDF individual
    print("\n[1/2] Convirtiendo ideas individuales...")
    converted_pdfs = convert_all_ideas_to_pdf(ideas_folder, output_folder)

    # Crear PDF consolidado
    print("\n[2/2] Creando PDF consolidado...")
    combined_pdf = os.path.join(output_folder, 'TODAS-LAS-IDEAS-PILSEN-2025.pdf')
    create_combined_pdf(ideas_folder, combined_pdf)

    print("\n" + "="*60)
    print("✓ PROCESO COMPLETADO")
    print("="*60)
    print(f"PDFs individuales: {output_folder}")
    print(f"PDF consolidado: {combined_pdf}")
    print("="*60)
