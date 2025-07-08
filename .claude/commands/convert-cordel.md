# Convert Cordel

Convert raw cordel text to formatted markdown for Hugo.

## Usage

```
/convert-cordel [file_path|text]
```

## Arguments

- `file_path`: Path to a text file containing the cordel
- `text`: Raw cordel text (if no file path provided)

## Description

This command converts raw cordel text to the proper markdown format used by Hugo in this project. It:

1. Processes the text according to cordel formatting rules
2. Generates appropriate frontmatter with title and date
3. Converts the text to use proper line endings (`\`)
4. Replaces page numbers with horizontal rules (`---`)
5. Creates the directory structure in `content/cordeis/`
6. Saves the formatted markdown as `index.md`
7. Generates and outputs an AI illustration prompt for the cordel cover

## Conversion Rules

- Replace page numbers with `---` (horizontal rules), with blank lines before and after
- All lines within a stanza (except the last line) must end with `\` for proper line breaks
- The last line of each stanza should NOT have `\` - it ends the stanza
- File must end with an empty line (end with a line break)
- Title should be converted to sentence case and appear only in frontmatter
- Remove author, contact info, and other metadata from the content
- Preserve the original text content without alterations
- Create directory name using snake_case format (e.g., "museu_a_preservacao_da_cultura")

## Example

```
/convert-cordel ./raw-cordel.txt
```

or

```
/convert-cordel "O CORDEL DA VIDA
Página 1
Era uma vez um homem
Que vivia a trabalhar..."
```

## Output

Creates a new directory in `content/cordeis/` with:
- `index.md` - Formatted markdown with Hugo frontmatter
- Placeholder for `cover.png` (to be added later)

Also outputs an AI illustration prompt (in Portuguese) for creating the cordel cover image, providing:
- Inspiration elements extracted from the cordel content for xilogravura nordestina style illustration
- Visual themes, characters, objects, and scenes from the story
- Cultural and thematic context relevant to the narrative
- Technical note about 2:1 portrait ratio and grayscale aesthetic
