# Pack Brief

## Status

Production pack initialized on 2026-05-14. Current phase: `master-character`.

The master character card is approved for asset production. Every generated character image must retain the `COS` text on the blue folder.

## Pack ID

`image-master-20260514-155523`

## Input Mode

`image-to-master`

The user provided a master/reference image. The workflow must preserve that character identity as the top priority. Style cleanup is allowed only when it does not drift into a different character design.

## Production Boundary

Only this directory is in scope for the current pack:

`production/packs/image-master-20260514-155523/`

Do not write production assets into `testdata/`. Do not modify sibling production packs unless the user explicitly switches pack id.

## Source Material

Reference image captured from:

- Original local path: `/Users/yinshawnrao/Desktop/cos-ip.png`
- Pack reference copy: `source/references/cos-ip-reference.png`
- Master input copy: `master/input/cos-ip-master-reference.png`
- Approved master image: `master/approved/cos-ip-approved-master.png`
- Style reference copy: `source/references/line-art-style-reference.png`

Source image facts checked locally:

- Format: PNG
- Dimensions: `512x512`
- Color: RGBA
- File size: `320692` bytes

## Concept

Draft pack theme: a cheerful cloud-shaped office companion for everyday internet-company work.

The tone should be normal, positive, collaborative, and workday-friendly. It should show everyday product, design, engineering, operations, and team collaboration moments without leaning into overtime complaints or dense corporate jargon.

## Character

Draft name: 云朵同事

Core character direction:

- A 2D line-art white cloud mascot with a warm smiling face.
- Rounded blue arms and small rounded feet.
- Pink cheeks and closed smiling eyes.
- A bright blue folder held in front of the body.
- Small sparkle accents can appear as positive mood cues.

The source image includes visible `COS` text on the folder. The user explicitly requires this text to remain in every generated character image.

## Visual Direction

- Preserve the source character identity.
- Keep the look cute, clean, rounded, bright, and sticker-friendly.
- Match the new style reference more closely: thick dark outlines, flatter Q-version drawing, clearer expression, and less soft 3D toy rendering.
- Use simple workday props only when they reinforce the caption, such as laptop, checklist, calendar, document, coffee cup, small chart, upload arrow, or team note.
- Avoid dark overtime mood, exhaustion-first humor, real company names, unapproved logos, and unrelated characters.

## Planned Outputs

- 18 static sticker PNGs
- Cover image
- Chat page icon
- Detail page banner
- Metadata
- Form copy
- Review contact sheets
- Validation report

## Review Notes

- Master character card approval is required before sticker production.
- Final captions must come from `spec.json` or another explicit config.
- Before production export, re-check the latest official WeChat Sticker Open Platform requirements.
- All sticker, cover, icon, banner, review, and export assets containing the character must keep `COS` legible on the folder.
