# Pack Brief

## Status

Production pack initialized. Current phase: `wechat-export-generated-pending-human-review`.

Master candidate 01 has been accepted for continuation as `master/approved/xiazi-approved-master.png`. Final sticker production must still use image-model raw sheets for expression, pose, hands, props, and action marks; local scripts may only process those outputs.

The current dry-run WeChat export package has been generated under `exports/wechat/`. Local mechanical validation passed; real upload is still pending human review for identity preservation, semantic variation, small-size caption readability, cover/icon quality, banner text absence, and latest official platform rules.

## Pack ID

`xiazi-daily-20260515-174410`

## Input Mode

`image-to-master`

## Source Material

- Original local path: `/Users/yinshawnrao/Pictures/表情包/000mother/cx.png`
- Pack reference copy: `source/references/cx-reference.png`
- Master input copy: `master/input/cx-master-reference.png`

Source image facts captured at initialization:

- PNG
- `1024x1024`
- RGBA / has alpha channel
- `1686861` bytes

This source image is a master/reference image only. It is not a final WeChat upload asset because final stickers, cover, and icon must be exported at the required sizes with transparent backgrounds and target file-size limits.

## Concept

“霞子的日常” is a static WeChat sticker pack about Xiazi, a young woman with a grounded, lively daily rhythm. She likes reading and traveling, works hard, and has many small emotional states from ordinary life: saying hello, receiving tasks, reading, thinking, traveling, focusing, thanking, resting, and finishing work.

The pack should feel friendly, relatable, and clean. The humor should be everyday rather than exaggerated or complaint-heavy.

## Character

- Character name: 霞子
- Role: young female chibi/anime sticker character
- Personality: warm, energetic, curious, practical, slightly workaholic but not bitter
- Core identity: big-eyed, smiling, approachable young woman with dark shoulder-length hair and a cream sleeveless top

## Visual Direction

- Preserve the identity of the provided master image as the first priority.
- Keep a cute 2D anime/chibi sticker style with thick dark brown outlines, warm skin tones, soft blush, clean shapes, and high readability at small sizes.
- Downstream stickers should use transparent canvases. Avoid keeping the source image's visible brown background in sticker, cover, or icon exports.
- Banner may use an opaque lively background, but it must not contain text.

## Planned Outputs

- 18 static sticker PNGs at `240x240`
- `cover.png` at `240x240`
- `icon.png` at `50x50`
- `banner.png` at `750x400`
- `metadata.json`
- `form.md`
- Review contact sheets and validation reports under `review/`
- Upload-ready package only under `exports/wechat/`

## Initial Compliance Notes

- Pack name candidate `霞子的日常`: passes current local rule, 5 Chinese characters, no punctuation, no spaces.
- Copyright `饶小虎`: passes current local rule, 3 Chinese characters.
- Source image is not upload-ready as-is: it is `1024x1024`, larger than the target upload dimensions, and visually includes a background. It is valid as master input only.
- Before final production export, re-check the latest official WeChat Sticker Open Platform requirements.

## Review Notes

Current human review focus:

- Identity: compare `review/wechat/master-output-identity-review.png` against the approved master.
- Semantic variation: check `review/stickers/final-stickers-contact-sheet.png` with captions mentally hidden.
- Upload detail: re-check cover/icon/banner quality and the latest WeChat platform rules before real submission.
