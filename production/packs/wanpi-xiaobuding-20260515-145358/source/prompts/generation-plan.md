# Generation Plan

## Source

- Pack: `wanpi-xiaobuding-20260515-145358`
- Approved master: `master/approved/xiaobuding-approved-master.png`
- Primary reference: `source/references/master-reference-ip-option-a-transparent.png`
- Input mode: `image-to-master`

## Confirmed Identity

Keep the same toddler as the reference image: one-year-old child, big round forehead, short dark slightly spiky hair, large glossy eyes, warm peach skin, cream oversized shirt, yellow snail chest graphic, olive cuffed pants, and white toddler shoes.

## Image Generation Inputs

Two raw 3x3 sheets were generated with the built-in image generation tool, using the approved master image as identity reference:

- `generated/sheets/raw/sheet-01-raw-ai.png`: home set, stickers 01-09.
- `generated/sheets/raw/sheet-02-raw-ai.png`: park set, stickers 10-18.

Both prompts requested:

- No in-image text.
- One child per cell.
- Compact props only.
- Flat solid `#ff00ff` chroma-key background for local alpha extraction.
- No watermark, no border lines, no full background.

## Deterministic Local Processing

`source/prompts/generate_assets.py` reads `spec.json` and the raw sheets, then writes only inside this pack directory:

- Removes chroma-key background from raw sheets.
- Crops each 3x3 cell into an intermediate transparent source crop.
- Locally renders exact Simplified Chinese captions from `spec.json`.
- Exports `240x240` WeChat draft stickers and copies them to `exports/wechat/stickers/`.
- Creates `cover.png`, `icon.png`, and an opaque no-text `banner.png`.
- Creates contact sheets and validation reports under `review/`.
- Writes `exports/wechat/metadata.json` and `exports/wechat/form.md`.

Targeted replacement sources:

- `generated/stickers/replacements/raw/02-oops-raw-ai.png`
- `generated/stickers/replacements/raw/03-good-boy-raw-ai.png`
- `generated/stickers/replacements/raw/08-little-chaos-raw-ai.png`
- `generated/stickers/replacements/raw/09-sleepy-raw-ai.png`
- `generated/stickers/replacements/raw/17-more-play-raw-ai.png`
- `generated/stickers/replacements/raw/18-hehe-raw-ai.png`

These are used instead of the original sheet cells for stickers 02, 03, and 18 after user feedback that the first version did not match the captions closely enough. Stickers 08, 09, and 17 were later replaced because the first versions put the hair too close to the top edge; their local composition uses extra top safety padding.

Run command:

```bash
/Users/yinshawnrao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 production/packs/wanpi-xiaobuding-20260515-145358/source/prompts/generate_assets.py
```

## Export Rules

- Final sticker captions must come from `spec.json`; the image model must not invent or rewrite captions.
- Final sticker PNGs must be `240x240`, RGBA, transparent at the corners, and `<=500KB`.
- `cover.png` must be `240x240`, RGBA, transparent, and `<=500KB`.
- `icon.png` must be `50x50`, RGBA, transparent, and `<=100KB`.
- `banner.png` must be `750x400`, opaque, no text, and `<=500KB`.
