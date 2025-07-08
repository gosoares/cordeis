# Convert to Gray

Convert cordel cover images to grayscale.

## Usage

```
/convert-to-gray [image_path]
```

## Arguments

- `image_path`: Path to the image file to convert (defaults to current directory's `cover.png`)

## Description

This command converts cordel cover images to grayscale using ImageMagick. This is particularly useful for:
- Creating traditional black and white cordel covers
- Ensuring consistent styling across all cordel illustrations
- Preparing images for print in the traditional cordel booklet format

## Requirements

- ImageMagick must be installed (`convert` command)
- Image file must be accessible

## Example

```
/convert-to-gray content/cordeis/a_danca_do_carimbo/cover.png
```

or (from within a cordel directory):

```
/convert-to-gray
```

## Output

The command modifies the image file in place, converting it to grayscale while preserving the original dimensions and format.