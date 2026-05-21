# Generation Record

- Pack: `sweet-couple-20260518-150422`
- Input mode: `image-to-master`
- Local processing not allowed for final artwork: no local drawing of face, eyes, mouth, hair, pose, hands, props, or action marks.

## Master Candidate 01

- Built-in generated source: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0abf4a33148195855297f231ba3bbe.png`
- Chroma-key source: `master/candidates/sweet-couple-master-candidate-01-chromakey.png`
- Transparent candidate: `master/candidates/sweet-couple-master-candidate-01.png`
- Review comparison: `review/master/master-candidate-review-01.png`
- Approved continuation source: `master/approved/sweet-couple-approved-master.png`
- Continuation approval: user invoked `/goal` on 2026-05-18 to generate the full pack under the current repository constraints.

## Prompt Summary

Create a clean anime/chibi master candidate from the visible young married couple reference image. Preserve the girl's long dark-brown hair, large brown eyes, navy outer layer and light top, and preserve the boy's short black hair, black rectangular glasses, gray hoodie and teal shirt. Use a flat green chroma-key background for local background removal. No text, watermark, logo, extra people, specific museum branding, or copied decorative background.

## Raw Sticker Sheets 2026-05-18

- Built-in generated source sheet 1: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0ac0ad6d508195a9ccf057fe30762a.png`
- Built-in generated source sheet 2: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0ac12523508195b70f285395119b1f.png`
- Workspace raw sheet 1: `generated/sheets/raw/sheet-01-raw-ai.png`
- Workspace raw sheet 2: `generated/sheets/raw/sheet-02-raw-ai.png`
- Identity method: the approved master `master/approved/sweet-couple-approved-master.png` was loaded into the conversation and used as the visual reference for both image-model raw sheets.
- Local processing method: `source/prompts/generate_assets.py` removes chroma-key background, crops model outputs, renders exact captions from `spec.json`, creates WeChat-size PNGs, cover, icon, banner, review sheets, metadata, and validation reports. It does not draw or alter character face, eyes, mouth, hair, pose, hands, props, or action marks.

## Icon Revision 2026-05-18

- Reason: first icon crop showed an awkward partial-body/partial-head result at `50x50`.
- Built-in generated source: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0ac78a73308195b80c05026af02cfa.png`
- Chroma-key source: `master/approved/sweet-couple-approved-icon-source-chromakey.png`
- Transparent icon source: `master/approved/sweet-couple-approved-icon-source.png`
- Identity method: generated with the approved master visible as the visual reference, constrained to a two-head-only front-facing icon source with complete chins and no bodies, props, captions, or scene elements.
