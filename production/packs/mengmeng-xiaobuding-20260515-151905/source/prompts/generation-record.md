# Image Generation Record

## Mode

- Built-in `image_gen` for raw character poses.
- Local Python/Pillow processing for chroma-key removal, cropping, exact Simplified Chinese captions, final WeChat sizing, cover, icon, banner, metadata, and validation.

## Source Images

- Master reference: `master/input/master-reference-original.png`
- Raw generated sheet 1: `generated/sheets/raw/sheet-01-raw-ai.png`
- Raw generated sheet 2: `generated/sheets/raw/sheet-02-raw-ai.png`
- Raw generated single sticker: `generated/sheets/raw/sheet-03-single-raw-ai.png`

## Key Prompt Constraints

- Preserve the toddler identity from the reference image.
- Keep the cream-and-navy star cap, front smiling star badge, glossy dark eyes, cream cardigan, striped bib collar, navy pants, and white shoes.
- Generate no final caption text in the image model output.
- Use a perfectly flat `#00ff00` chroma-key background for local alpha extraction.
- Compose exact Chinese captions locally from `spec.json`.
