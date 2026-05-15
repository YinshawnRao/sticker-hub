# 萌萌小布丁 Pack Brief

## Status

Production pack initialized on 2026-05-15.

- Pack ID: `mengmeng-xiaobuding-20260515-151905`
- Workflow phase: `master-character`
- Input mode: `image-to-master`
- Final sticker generation: blocked until the user approves the master character card and master image

## Source Material

User-provided master/reference image has been archived in this pack:

- `source/references/master-reference-original.png`
- `master/input/master-reference-original.png`

Source image facts captured during intake:

- Format: PNG
- Dimensions: 1449 x 1086
- Color/alpha: RGB, no alpha channel
- Size: about 1.3 MB

This image is suitable as identity reference material, but it is not directly upload-ready for WeChat sticker, cover, or icon assets. Final upload assets must be regenerated or processed into transparent RGBA PNGs at the required platform sizes and byte limits.

## Concept

Candidate sticker pack name: 萌萌小布丁

Theme: a cute toddler character expressing a broad range of everyday chat emotions, including greetings, joy, grievance, anger, surprise, crying, affection, agreement, refusal, shyness, sleepiness, encouragement, thanks, pleading, apology, eating, and farewell.

## Character

Character name: 小布丁

小布丁 is a soft, expressive toddler with a round face, glossy dark eyes, rosy cheeks, and a signature cream-and-navy star cap. The pack should preserve the original master image identity while allowing richer facial expressions, gestures, and small props for classic chat-sticker emotional scenarios.

## Visual Direction

- Static WeChat sticker pack.
- Soft high-quality illustrated baby style, not photorealistic.
- Cute, clean, warm, and emotionally readable at small chat size.
- Preserve the star cap, cream cardigan, striped collar, navy pants, and white shoes as the recurring identity system.
- Use transparent backgrounds for stickers, cover, and icon.
- Use an opaque, lively, no-text banner later in the export stage.
- Final captions should be deterministic local composition rather than model-generated text.

## Planned Outputs

- 19 static `240x240` PNG sticker images
- `cover.png` at `240x240`, transparent PNG
- `icon.png` at `50x50`, transparent PNG
- `banner.png` at `750x400`, opaque JPG/PNG-compatible image with no text
- `metadata.json`
- `form.md`
- Review contact sheets and WeChat validation report under `review/`

## Compliance Notes

- Name candidate `萌萌小布丁` is 5 Chinese characters, with no punctuation or spaces.
- Copyright `饶小虎` is 3 Chinese characters.
- Intro copy must stay within 80 Chinese characters.
- Source image currently has no alpha channel and is larger than the final per-asset target; it must not be copied directly into `exports/wechat/`.
- Before real production submission, re-check the latest official WeChat Sticker Open Platform requirements.

## Review Notes

Awaiting user confirmation of:

1. Master character card.
2. Whether the provided image should be treated as the approved master identity.
3. Planned 19 captions and emotional cases.
