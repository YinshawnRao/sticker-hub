# Generation Record

- Reset at: 2026-05-15 Asia/Shanghai after rejecting prior local-drawing/compositing outputs.
- Current phase: approved master is present; continuing with image-model raw sticker sheet generation.
- Image generation mode: built-in `image_gen` using `master/input/cx-master-reference.png` as the visual identity reference.
- Local processing performed: copy generated candidate into `master/candidates/`, remove flat chroma-key background, create review comparison image.
- Local processing not allowed for final artwork: no local drawing of face, eyes, mouth, hair, pose, hands, props, or action marks.

## Cleared Outputs

The previous generated outputs were removed from:

- `generated/`
- `review/`
- `exports/`
- `master/approved/`

The source reference images and pack metadata remain.

## Master Candidate 01

- Chroma-key source: `master/candidates/xiazi-master-candidate-01-chromakey.png`
- Transparent candidate: `master/candidates/xiazi-master-candidate-01.png`
- Review comparison: `review/master/master-candidate-review-01.png`
- Approved continuation source: `master/approved/xiazi-approved-master.png`
- Continuation approval: user invoked `/goal` on 2026-05-15 to continue generation under the repository constraints.

## Prompt Summary

Create one clean anime/chibi WeChat sticker master candidate from the visible chibi girl reference image only. Preserve the dark shoulder-length hair, rounded bangs, large brown eyes, blush, cream sleeveless lace or knit top, warm soft rendering, and thick dark outlines. Ignore unrelated floral/banner screenshots. Use a flat `#00ff00` background for local background removal. No text, watermark, logo, flowers, scenery, or copied decorative banner content.

## Raw Sheet Gate

Final 18-sticker generation must use the approved master/reference as an actual image input and must produce real expression/action variation from the image model before any local captioning, cropping, or export processing. Local processing is limited to chroma-key removal, cropping, exact caption composition, sizing, cover/icon/banner composition, review sheets, metadata, and validation.

## Raw Sticker Sheets 2026-05-15

- Built-in generated source sheet 1: `/Users/yinshawnrao/.codex/generated_images/019e2b4a-548c-7220-a18b-728bcb52f815/ig_09204231038cdecb016a06fd63d9f48191bd4777e889e89a3e.png`
- Built-in generated source sheet 2: `/Users/yinshawnrao/.codex/generated_images/019e2b4a-548c-7220-a18b-728bcb52f815/ig_09204231038cdecb016a06fdec009081918c078fd84859ce0f.png`
- Workspace raw sheet 1: `generated/sheets/raw/sheet-01-raw-ai.png`
- Workspace raw sheet 2: `generated/sheets/raw/sheet-02-raw-ai.png`
- Identity method: the approved master `master/approved/xiazi-approved-master.png` was loaded into the conversation and used as the visual reference for both image-model raw sheets.
- Local processing method: `source/prompts/generate_assets.py` removes chroma-key background, crops model outputs, renders exact captions from `spec.json`, creates WeChat-size PNGs, cover, icon, banner, review sheets, metadata, and validation reports. It does not draw or alter character face, eyes, mouth, hair, pose, hands, props, or action marks.
