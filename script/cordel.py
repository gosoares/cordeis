#!/usr/bin/env python3
"""
Cordel PDF Converter

This script converts cordel literature from Markdown to PDF booklets
with proper A6 dimensions and typical cordel styling.
"""

import os
import sys
import subprocess
import argparse
import re
from pathlib import Path


def process_markdown(markdown_file):
    """
    Process the markdown file to properly handle pagebreak comments and stanza formatting.

    Args:
        markdown_file: Path to the markdown file

    Returns:
        Path to the processed markdown file
    """
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace HTML pagebreak comments with LaTeX pagebreaks
    # Using \clearpage for a hard page break that forces all content before it to be typeset
    processed_content = re.sub(r"<!-- pagebreak -->", r"\n\n\\clearpage\n\n", content)

    # Ensure stanzas are properly separated as paragraphs
    # In cordel format, empty lines separate stanzas
    # This helps pandoc process them correctly as distinct paragraphs
    lines = processed_content.split("\n")
    in_stanza = False
    in_yaml = False
    yaml_delimiters = 0
    result = []

    for i, line in enumerate(lines):
        # Handle YAML frontmatter
        if line.strip() == "---":
            yaml_delimiters += 1
            in_yaml = yaml_delimiters % 2 != 0
            result.append(line)
            continue

        if in_yaml:
            result.append(line)
            continue

        if line.strip():  # Non-empty line
            if not in_stanza:
                in_stanza = True
            result.append(line)
        else:  # Empty line
            if in_stanza:
                # End of stanza
                in_stanza = False
                result.append("")  # Ensure empty line between stanzas
            else:
                # Additional empty line or space between sections
                result.append("")

    processed_content = "\n".join(result)

    # Write the processed content to a temporary file
    temp_file = markdown_file.parent / f"{markdown_file.stem}_processed.md"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(processed_content)

    return temp_file


import yaml


def extract_cover_image_from_frontmatter(markdown_file):
    """
    Extrai o caminho da capa do frontmatter YAML do arquivo markdown.
    Se cover.image começar com "/images", retorna "static/images/..."
    """
    with open(markdown_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or not lines[0].strip() == "---":
        return None

    yaml_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        yaml_lines.append(line)
    try:
        meta = yaml.safe_load("".join(yaml_lines))
        cover_image = meta.get("cover", {}).get("image")
        if cover_image and cover_image.startswith("/images"):
            return f"static{cover_image}"
        return cover_image
    except Exception:
        return None


def convert_cordel_to_pdf(
    markdown_path, output_path=None, template_path=None, paper_size="a6", font_scale=1.0
):
    """
    Converte um cordel de markdown para PDF usando pandoc com template customizado.

    Args:
        markdown_path: Caminho do arquivo markdown
        output_path: Caminho de saída do PDF (opcional)
        template_path: Caminho do template LaTeX (opcional)
        paper_size: Tamanho do papel (default: a6)
        font_scale: Escala da fonte (default: 1.0)
    """
    markdown_file = Path(markdown_path)
    if not markdown_file.exists() or not markdown_file.is_file():
        print(f"Erro: Arquivo '{markdown_file}' não existe ou não é um arquivo")
        return False

    # Processa o markdown para pagebreaks/estrofes
    processed_markdown = process_markdown(markdown_file)

    # Extrai a capa do frontmatter
    cover_image = extract_cover_image_from_frontmatter(markdown_file)
    if cover_image and not Path(cover_image).exists():
        print(f"Aviso: Capa '{cover_image}' não encontrada. Continuando sem capa.")
        cover_image = None

    # Define o caminho de saída
    if output_path:
        output_pdf = Path(output_path)
    else:
        output_pdf = markdown_file.parent / f"{markdown_file.stem}.pdf"

    # Define o template
    if template_path:
        template_path = Path(template_path)
    else:
        script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
        template_path = script_dir / "cordel-template.tex"

    if not template_path.exists():
        print(f"Erro: Template '{template_path}' não encontrado")
        return False

    # Monta comando pandoc
    cmd = [
        "pandoc",
        "-s",
        str(processed_markdown),
        "--template",
        str(template_path),
        "--pdf-engine=xelatex",
    ]
    if cover_image:
        cmd.append(f"--variable=cover_image:{cover_image}")
    cmd.append(f"--variable=papersize:{paper_size}")
    cmd.append(f"--variable=fontscale:{font_scale}")
    cmd.extend(["-o", str(output_pdf)])

    print(f"Convertendo '{markdown_file}' para '{output_pdf}'...")
    print(f"Comando: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Conversão concluída com sucesso!")
        print(f"PDF gerado em: {output_pdf}")
        if processed_markdown.exists():
            processed_markdown.unlink()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro na conversão: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        if processed_markdown.exists():
            processed_markdown.unlink()
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    # Check for pandoc
    try:
        subprocess.run(
            ["pandoc", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("pandoc")

    # Check for xelatex
    try:
        subprocess.run(
            ["xelatex", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("xelatex")

    if missing:
        print("The following dependencies are missing:")
        for dep in missing:
            print(f"- {dep}")
        print("\nPlease install them and try again.")
        return False

    return True


def main():
    """Ponto de entrada principal do script"""
    parser = argparse.ArgumentParser(
        description="Converte um cordel em markdown para PDF (usando frontmatter para capa)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    check_only_parser = parser.add_argument_group("apenas checar dependências")
    check_only_parser.add_argument(
        "--check",
        action="store_true",
        help="Checa dependências e sai sem converter",
    )

    parser.add_argument(
        "markdown_file",
        nargs="?",
        help="Caminho do arquivo markdown do cordel",
    )
    parser.add_argument("-o", "--output", help="Caminho de saída do PDF")
    parser.add_argument(
        "-t", "--template", help="Caminho para template LaTeX customizado"
    )
    parser.add_argument(
        "-p",
        "--paper-size",
        default="a6",
        choices=["a6", "a5", "a4", "letter"],
        help="Tamanho do papel para o cordel",
    )
    parser.add_argument(
        "-s",
        "--font-scale",
        type=float,
        default=0.95,
        help="Fator de escala da fonte (ex: 0.9 para texto menor)",
    )

    args = parser.parse_args()

    if args.check:
        return 0 if check_dependencies() else 1

    if not args.markdown_file:
        parser.error(
            "É necessário informar o caminho do arquivo markdown para conversão."
        )

    if not check_dependencies():
        return 1

    success = convert_cordel_to_pdf(
        args.markdown_file,
        output_path=args.output,
        template_path=args.template,
        paper_size=args.paper_size,
        font_scale=args.font_scale,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
