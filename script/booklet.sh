#!/bin/sh

set -e

# Default values
TEMPLATE=""
PAPER_SIZE="a6"
FONT_SCALE="0.95"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --template|-t)
      TEMPLATE="$2"
      shift 2
      ;;
    --paper-size|-p)
      PAPER_SIZE="$2"
      shift 2
      ;;
    --font-scale|-s)
      FONT_SCALE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Find template if not provided
if [[ -z "$TEMPLATE" ]]; then
  if [[ -f script/cordel-template.tex ]]; then
    TEMPLATE="script/cordel-template.tex"
  elif [[ -f script/booklet-template.tex ]]; then
    TEMPLATE="script/booklet-template.tex"
  else
    echo "No LaTeX template found."
    exit 1
  fi
fi

mkdir -p static/livretos

for dir in content/cordeis/*; do
  if [[ -d "$dir" && -f "$dir/index.md" ]]; then
    name=$(basename "$dir")
    md="$dir/index.md"
    tmp_md="$dir/index_processed.md"

    # Replace <!-- pagebreak --> with \clearpage and ensure stanza separation
    awk '
      BEGIN { in_yaml=0; yaml_delim=0 }
      {
        if ($0 ~ /^---[[:space:]]*$/) {
          yaml_delim++
          in_yaml = (yaml_delim % 2 == 1)
          print
          next
        }
        if (in_yaml) { print; next }
        gsub(/<!-- pagebreak -->/, "\n\n\\\\clearpage\n\n")
        if (NF) {
          if (!in_stanza) in_stanza=1
          print
        } else {
          if (in_stanza) { in_stanza=0; print "" }
          else print ""
        }
      }
    ' "$md" > "$tmp_md"

    out="static/livretos/${name}.pdf"
    echo "Generating $out ..."
    pandoc -s "$tmp_md" --template="$TEMPLATE" --pdf-engine=xelatex \
      --variable=papersize:"$PAPER_SIZE" --variable=fontscale:"$FONT_SCALE" -o "$out"
    rm "$tmp_md"
  fi
done

echo "All PDFs generated in static/livretos/"
