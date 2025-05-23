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


def convert_cordel_to_pdf(
    cordel_dir, output_path=None, template_path=None, paper_size="a6", font_scale=1.0
):
    """
    Convert a cordel from markdown to PDF using pandoc with a custom template.

    Args:
        cordel_dir: Directory containing the cordel.md and capa.png files
        output_path: Custom output path for the PDF (optional)
        template_path: Custom template path (optional)
        paper_size: Paper size for the cordel (default: a6)
        font_scale: Scale factor for the font size (default: 1.0)
    """
    cordel_dir = Path(cordel_dir)

    # Check if the directory exists
    if not cordel_dir.exists() or not cordel_dir.is_dir():
        print(f"Error: Directory '{cordel_dir}' does not exist or is not a directory")
        return False

    # Find the markdown file
    markdown_files = list(cordel_dir.glob("*.md"))
    markdown_files = [f for f in markdown_files if not f.name.endswith("_processed.md")]
    if not markdown_files:
        print(f"Error: No markdown file found in '{cordel_dir}'")
        return False

    markdown_file = markdown_files[0]  # Use the first markdown file found

    # Process the markdown file to handle pagebreaks
    processed_markdown = process_markdown(markdown_file)

    # Find the cover image
    cover_images = (
        list(cordel_dir.glob("*.png"))
        + list(cordel_dir.glob("*.jpg"))
        + list(cordel_dir.glob("*.jpeg"))
    )
    if not cover_images:
        print(
            f"Warning: No cover image found in '{cordel_dir}'. Proceeding without a cover."
        )
        cover_image = None
    else:
        cover_image = cover_images[0]  # Use the first image found

    # Set output file path
    if output_path:
        output_pdf = Path(output_path)
    else:
        output_filename = cordel_dir.name
        output_pdf = cordel_dir.parent / f"{output_filename}.pdf"

    # Get the template path
    if template_path:
        template_path = Path(template_path)
    else:
        script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
        template_path = script_dir / "cordel-template.tex"

    if not template_path.exists():
        print(f"Error: Template file '{template_path}' not found")
        return False

    # Build the pandoc command
    cmd = [
        "pandoc",
        "-s",
        str(processed_markdown),
        "--template",
        str(template_path),
        "--pdf-engine=xelatex",
    ]
    
    # Add cover image if available
    if cover_image:
        cmd.append(f"--variable=cover:{cover_image}")
    
    # Add paper size
    cmd.append(f"--variable=papersize:{paper_size}")
    
    # Add font scale
    cmd.append(f"--variable=fontscale:{font_scale}")
    
    # Add output file
    cmd.extend(["-o", str(output_pdf)])

    print(f"Converting '{markdown_file}' to '{output_pdf}'...")
    print(f"Command: {' '.join(cmd)}")

    # Run pandoc
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Conversion completed successfully!")
        print(f"Output saved to: {output_pdf}")

        # Clean up the temporary processed file
        if processed_markdown.exists():
            processed_markdown.unlink()

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

        # Clean up the temporary processed file even on error
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
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Convert a cordel from markdown to PDF",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add a check-only argument that doesn't require cordel_dir
    check_only_parser = parser.add_argument_group("check dependencies only")
    check_only_parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and exit without conversion",
    )

    # Main arguments
    parser.add_argument(
        "cordel_dir",
        nargs="?",
        help="Directory containing cordel.md and cover image files",
    )
    parser.add_argument("-o", "--output", help="Output PDF file path")
    parser.add_argument("-t", "--template", help="Path to custom LaTeX template")
    parser.add_argument(
        "-p",
        "--paper-size",
        default="a6",
        choices=["a6", "a5", "a4", "letter"],
        help="Paper size for the cordel",
    )
    parser.add_argument(
        "-s",
        "--font-scale",
        type=float,
        default=0.95,
        help="Scale factor for font size (e.g., 0.9 for smaller text)",
    )

    args = parser.parse_args()

    # Check dependencies only
    if args.check:
        return 0 if check_dependencies() else 1

    # Make sure we have a cordel_dir for conversion
    if not args.cordel_dir:
        parser.error("cordel_dir is required for conversion")

    # Check dependencies before conversion
    if not check_dependencies():
        return 1

    # Convert the cordel
    success = convert_cordel_to_pdf(
        args.cordel_dir,
        output_path=args.output,
        template_path=args.template,
        paper_size=args.paper_size,
        font_scale=args.font_scale
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
