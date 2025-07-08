# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo static site that showcases "Cordéis" (traditional Brazilian folk literature) by Poet Manoel Ribeiro. The site includes:
- A collection of cordel poems in markdown format
- Automated PDF booklet generation using LaTeX
- Docker-based deployment with nginx
- NetlifyCMS for content management

## Core Architecture

### Content Structure
- **Content Source**: `content/cordeis/` - Each cordel has its own directory with:
  - `index.md` - Markdown content with Hugo frontmatter
  - `cover.png` - Cover image in 2:1 portrait ratio
- **Static Assets**: `static/livretos/` - Generated PDF booklets
- **Theme**: Uses PaperMod Hugo theme in `themes/PaperMod/`

### Content Format
Cordel markdown files follow this structure:
```markdown
---
title: "Title in sentence case"
date: "2023-01-15"
cover:
  image: "cover.png"
---

Cordel text with lines ending in `\`  
For proper line breaks in Hugo  

---

Use `---` (horizontal rules) to separate pages  
These become `\clearpage` in PDF generation  
```

### Build Pipeline
The project uses a multi-stage Docker build:
1. **Booklet Stage**: Uses `pandoc/latex` to generate PDFs via `script/booklet.sh`
2. **Hugo Stage**: Builds static site with `hugo --minify`
3. **Nginx Stage**: Serves static files

## Common Development Commands

### Local Development
```bash
# Start development server
hugo server

# Build static site
hugo --minify

# Generate PDF booklets
bash script/booklet.sh

# Run with Docker
docker-compose up --build
```

### Content Management
```bash
# Convert images to grayscale (for covers)
convert cover.png -colorspace Gray cover.png

# Access NetlifyCMS admin
# Navigate to /admin/ on the running site
```

## PDF Generation System

The `script/booklet.sh` script converts markdown cordels to PDF booklets:
- Uses `script/booklet-template.tex` as LaTeX template
- Processes markdown to replace `---` with `\clearpage`
- Generates A6 booklets optimized for print
- Supports custom paper sizes and font scaling

Template parameters:
- `--paper-size` (default: a6)
- `--font-scale` (default: 0.95)
- `--template` (auto-detected)

## File Organization

### Key Directories
- `content/cordeis/` - Source cordel content
- `static/livretos/` - Generated PDF files
- `script/` - Build and processing scripts
- `layouts/` - Hugo template overrides
- `public/` - Generated static site (build output)

### Configuration Files
- `hugo.toml` - Hugo site configuration
- `docker-compose.yml` - Local development setup
- `Dockerfile` - Multi-stage build definition
- `nginx.conf` - Production web server config
- `static/admin/config.yml` - NetlifyCMS configuration

## Content Conversion Workflow

When adding new cordels (reference `prompts.md`):
1. Convert source text to markdown format
2. Replace page numbers with `---` (horizontal rules)
3. Ensure lines end with `\` for proper formatting
4. Add frontmatter with title, date, and cover image
5. Generate or add cover image (2:1 portrait ratio)
6. Run PDF generation script

## Custom Claude Code Commands

This project includes three custom commands in `.claude/commands/` to streamline cordel workflow:

### `/convert-cordel`
Converts raw cordel text to formatted Hugo markdown:
- Accepts file path or raw text input
- Processes text according to cordel formatting rules
- Generates frontmatter with title and date
- Creates directory structure in `content/cordeis/`
- Saves as properly formatted `index.md`

### `/generate-illustration-prompt`
Generates AI prompts for cordel cover illustrations:
- Accepts cordel name, directory, or file path
- Creates prompts for xilogravura nordestina style
- Specifies 2:1 portrait ratio and black/white colors
- Includes cordel title and visual elements

### `/convert-to-gray`
Converts cover images to grayscale:
- Uses ImageMagick's `convert` command
- Accepts image path or defaults to `cover.png`
- Modifies images in place
- Ensures traditional cordel styling

## Development Notes

- The site uses Portuguese (`pt-br`) as primary language
- Cover images should be 2:1 portrait ratio for consistency
- PDF booklets are optimized for A6 paper size
- The build process automatically generates PDFs during Docker build
- NetlifyCMS provides a web interface for content management at `/admin/`

## Commit Guidelines
- Commit messages should be single line only
- Do not include English translations of Portuguese titles