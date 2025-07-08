# Generate Illustration Prompt

Generate an AI prompt for creating cordel illustrations.

## Usage

```
/generate-illustration-prompt [cordel_identifier]
```

## Arguments

- `cordel_identifier`: Can be:
  - Cordel name (e.g., "a_danca_do_carimbo")
  - Directory path (e.g., "content/cordeis/a_danca_do_carimbo")
  - File path (e.g., "content/cordeis/a_danca_do_carimbo/index.md")

## Description

This command reads a cordel from the content directory and generates a specialized prompt (in Portuguese) for AI image generation tools. The prompt provides inspiration elements for creating illustrations in the traditional xilogravura nordestina (northeastern woodcut) style that's characteristic of cordel literature.

## Generated Prompt Format

The command creates a prompt that provides:
- Inspiration elements extracted from the cordel content for xilogravura nordestina style illustration
- Visual themes, characters, objects, and scenes from the story that can be represented
- Cultural and thematic context relevant to the narrative
- Technical note about 2:1 portrait ratio and traditional black on white aesthetic
- The cordel title for inclusion in the composition

## Example

```
/generate-illustration-prompt a_danca_do_carimbo
```

## Output

Generates a complete prompt in Portuguese with inspiration elements ready to use with AI image generation tools like DALL-E, Midjourney, or Stable Diffusion, providing creative guidance for authentic-looking cordel cover illustrations.