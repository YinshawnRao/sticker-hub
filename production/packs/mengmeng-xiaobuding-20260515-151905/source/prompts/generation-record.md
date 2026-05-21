# Image Generation Record

## Mode

- Built-in `image_gen` for raw character poses.
- Local Python/Pillow processing for chroma-key removal, cropping, exact Simplified Chinese captions, final WeChat sizing, cover, icon, banner, metadata, and validation.

## Source Images

- Master reference: `master/input/master-reference-original.png`
- Raw generated sheet 1: `generated/sheets/raw/sheet-01-raw-ai.png`
- Raw generated sheet 2: `generated/sheets/raw/sheet-02-raw-ai.png`
- Raw generated single sticker: `generated/sheets/raw/sheet-03-single-raw-ai.png`

## Expression Refresh

- Refreshed at: 2026-05-15.
- Reason: user review found that several facial expressions, especially 1, 2, 3, 9, 14, and 15, were too similar and did not strongly express the Chinese semantic emotion.
- Built-in generated source sheet 1: `/Users/yinshawnrao/.codex/generated_images/019e2ad8-b561-7940-9d02-d0407fbfca04/ig_030e0f88d9d60521016a06dfd53ac88191abda06d0e1570de3.png`
- Built-in generated source sheet 2: `/Users/yinshawnrao/.codex/generated_images/019e2ad8-b561-7940-9d02-d0407fbfca04/ig_030e0f88d9d60521016a06e043e3f481918716d49a9b3ca55a.png`
- Built-in generated source single sticker: `/Users/yinshawnrao/.codex/generated_images/019e2ad8-b561-7940-9d02-d0407fbfca04/ig_030e0f88d9d60521016a06e0a8b13c81919624d22344a41bb5.png`
- Previous raw sheets and contact sheets were backed up under `review/stickers/expression-before-20260515/`.
- Local cleanup removes the generated yellow question mark from sticker 02 and isolated top residue from sticker 04 before final export.

## Key Prompt Constraints

- Preserve the toddler identity from the reference image.
- Keep the cream-and-navy star cap, front smiling star badge, glossy dark eyes, cream cardigan, striped bib collar, navy pants, and white shoes.
- Generate no final caption text in the image model output.
- Use a perfectly flat `#00ff00` chroma-key background for local alpha extraction.
- Compose exact Chinese captions locally from `spec.json`.
- Make the emotion differences visible in eyebrows, eyelids, eye shape, mouth shape, cheeks, tears, head angle, and pose.
- Cover fix on 2026-05-18: regenerated `exports/wechat/cover.png` from the approved master image as a clean frontal upper-body crop, excluding raised hands, caption text, and decorative action marks.
- Chat-page icon fix on 2026-05-18: regenerated `exports/wechat/icon.png` from the approved master image as a head-only frontal crop, excluding body, hands, caption text, and decorative marks, with transparent padding inside the 50x50 canvas.
- Sticker 09 crop fix on 2026-05-19: expanded the raw-sheet crop 24px upward for `09-ok-好的.png` so the hat edge uses original source pixels instead of the strict grid boundary.
