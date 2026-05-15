# AGENTS.md

## Project Intent

This project is planned as a WeChat sticker pack generation workflow.

The goal is to turn a sticker pack idea into a complete submission-ready package for the WeChat Sticker Open Platform, including:

- Sticker images and animated assets where applicable
- Cover image
- Banner image
- Introductory copy
- Sticker names, descriptions, tags, and metadata
- Exported files arranged for platform review and upload

The workflow should first run in a test mode with disposable sample data. After the visual style, asset quality, validation checks, and export format are proven, the same workflow can be promoted to production assets.

## Working Principles

- Keep test data and production data separate.
- Prefer reproducible generation over manual one-off edits.
- Treat the official WeChat Sticker Open Platform requirements as the source of truth.
- Before production export, re-check the latest official platform requirements instead of relying on memory or stale notes.
- Generated assets should be traceable back to their prompt, source image, model settings, and manual edits.
- Do not mix failed experiments into final export directories.
- Any validator should fail loudly when required files, sizes, dimensions, copy fields, or metadata are missing.

## Environment Layout

Use `testdata/` only for disposable experiments and workflow validation. Use `production/` for real sticker packs intended for platform submission.

```text
testdata/
  packs/
    sample-pack/

production/
  packs/
    _template/
    <pack-id>/
```

Production rules:

- One sticker pack must live under exactly one `production/packs/<pack-id>/` directory.
- One conversation/window should work on one pack id at a time.
- Never write production assets into `testdata/`.
- Never write upload-ready assets outside `production/packs/<pack-id>/exports/wechat/`.
- Do not modify another pack's directory unless the user explicitly switches pack id.
- Do not overwrite an existing production pack; create a new unique `<pack-id>` or ask the user to confirm replacement.
- Use `production/packs/_template/` as the starting structure for new packs.

## Pack Directory Plan

Each test or production pack uses the same internal structure.

```text
<env>/
  packs/
    <pack-id>/
      brief.md
      spec.json
      source/
        references/
        prompts/
      master/
        input/
        candidates/
        approved/
        character-card.md
      generated/
        sheets/
          raw/
          captioned/
        stickers/
          source-crops/
          wechat-draft/
      review/
        master/
        sheets/
        stickers/
        wechat/
      exports/
        wechat/
          stickers/
          metadata.json
          form.md
```

Suggested meaning:

- `brief.md`: Human-readable pack concept, character setting, visual style, copy direction, and test goals.
- `spec.json`: Machine-readable pack metadata and expected asset list for test generation.
- `source/references/`: User-provided reference images, screenshots, or visual materials.
- `source/prompts/`: Prompt drafts and reusable generation instructions.
- `master/input/`: The original text brief or source image used to create the master character.
- `master/candidates/`: Candidate master images before approval.
- `master/approved/`: User-approved master image(s) only.
- `master/character-card.md`: The locked master character card used by every downstream generation task.
- `generated/sheets/raw/`: Raw generated `3x3` sticker sheets before deterministic captioning.
- `generated/sheets/captioned/`: Captioned sticker sheets used for review and cropping.
- `generated/stickers/source-crops/`: Cropped intermediate sticker PNGs before final WeChat sizing.
- `generated/stickers/wechat-draft/`: Draft `240x240` WeChat-size PNGs before final export.
- `review/`: Assets selected for human review, comparison screenshots, QA notes, and validation reports.
- `review/master/`: Master-character review images and notes.
- `review/sheets/`: Full-sheet review contact sheets.
- `review/stickers/`: Individual-sticker review contact sheets.
- `review/wechat/`: Final package review screenshots and validation reports.
- `exports/`: Platform-shaped export output for dry runs. Test exports must not be treated as production submissions.
- `exports/wechat/`: Final WeChat Sticker Open Platform upload package for the current pack.

Production data can be introduced later under a separate directory such as:

```text
production/
  packs/
    <pack-id>/
      brief.md
      spec.json
      source/
      generated/
      review/
      exports/
```

Do not create `production/` until the test workflow is stable.

Production is now enabled after the `sample-pack` trial upload succeeded. Keep `testdata/packs/sample-pack/` as a reference and start real packs under `production/packs/<pack-id>/`.

## New Window Startup

When starting a new conversation/window for a pack, the user should paste the startup prompt from `docs/start-new-pack-prompt.md`.

Agent rules for new windows:

- Read `AGENTS.md` first.
- Confirm or create exactly one `production/packs/<pack-id>/` directory.
- Identify the input mode: `text-to-master` or `image-to-master`.
- Initialize or update only that pack's `brief.md`, `spec.json`, and `master/character-card.md`.
- Do not generate the final 18 stickers until the master character card is approved.
- Keep intermediate, review, and final upload assets in their assigned task directories.
- Final deliverable must be a complete `exports/wechat/` package plus review images and validation report.

## Input Modes

The project supports two production entry modes:

- `text-to-master`: the user provides a text description, and the workflow first generates one or more master character candidates.
- `image-to-master`: the user provides a master/reference image, and the workflow derives the master character card from that image.

Both modes must converge into the same `master-character` stage before sticker production begins. Do not generate the final 18-sticker pack directly from an unconstrained text prompt or an unreviewed reference image.

## Master Character Stage

Before producing the 18 final stickers, every pack must have a user-approved master character card.

The master character card should define:

- Input mode and source material.
- Approved master image path, if available.
- Character name and short personality.
- Locked visual traits: species, body shape, face, eyes, ears, colors, markings, recurring accessories, and outline style.
- Allowed variations: facial expression, pose, hand gesture, simple props, and small scene cues.
- Forbidden variations: changing species, changing dominant colors, changing face shape, adding unrelated characters, changing the rendering style, or adding unapproved logos/IP.
- Caption style and placement rules.
- The planned 18 sticker captions and poses.

Production rule: if the user provides a master image, preserve the character identity from that image as the top priority. Style cleanup is allowed, but the character should not drift into a new design unless the user explicitly requests it.

## Task Directory Boundaries

Different tasks must write to different directories:

- Source/reference intake writes only to `source/` and `master/input/`.
- Master image generation writes to `master/candidates/`; only user-approved assets move to `master/approved/`.
- Sticker sheet generation writes to `generated/sheets/raw/`.
- Deterministic caption composition writes to `generated/sheets/captioned/`.
- Intermediate sticker crops write to `generated/stickers/source-crops/`.
- WeChat-size draft stickers write to `generated/stickers/wechat-draft/`.
- Human review images and validation reports write to `review/`.
- Upload-ready assets write only to `exports/wechat/`.

Do not mix task outputs. In particular, never place raw sheets, rejected candidates, review contact sheets, checkerboard-background images, or failed variants inside `exports/wechat/`.

## Expected Workflow

1. Define a sticker pack concept in `brief.md`.
2. Choose `text-to-master` or `image-to-master` in `spec.json`.
3. Put user-provided reference images or prompt notes into `source/` and `master/input/`.
4. Create or derive the master character card in `master/character-card.md`.
5. Get user approval for the master character card and approved master image.
6. Generate two raw `3x3` sticker-sheet previews under `generated/sheets/raw/`.
7. Add deterministic Simplified Chinese captions, preferably by local image composition, under `generated/sheets/captioned/`.
8. Crop accepted sheets into intermediate transparent PNGs under `generated/stickers/source-crops/`.
9. Normalize drafts to WeChat size under `generated/stickers/wechat-draft/`.
10. Produce contact sheets and validation reports under `review/`.
11. Run validation against the captured WeChat Sticker Open Platform requirements.
12. Export an upload-ready dry-run package into `exports/wechat/`.
13. Iterate in test mode until visual quality and validation are acceptable.
14. Only then mirror the workflow into production.

## WeChat Upload Contract

These rules are derived from the user's captured WeChat Sticker Open Platform upload form and tooltip screenshots. Treat them as the active local target, and verify against the live official platform again before a real production submission.

### Pack Type

- Choose one type for the whole pack: static stickers or animated stickers.
- Do not mix static and animated stickers in one pack.
- Current project default: static sticker pack.

### Sticker Images

- Supported by the form: JPG, PNG, or GIF.
- Current project default for static stickers: PNG with transparent background.
- Static stickers must be `240x240` pixels.
- Animated stickers must be GIF, `240x240` pixels, looped, smooth, and not choppy.
- Images larger than `500KB` may be compressed by the platform; local export should target `<=500KB`.
- A sticker pack must contain `8-24` sticker images.
- Current production default: `18` stickers, generated as two `3x3` review sheets and exported as 18 independent files.
- All sticker images in one pack must have a unified style.
- Sticker images should have enough semantic and visual difference from each other.
- Layout should be reasonable; each image should avoid excessive blank space.
- Layout must also avoid edge-touching content. Hair tips, ears, raised hands, shoes, props, caption strokes, and shadows must not touch or be clipped by the `240x240` canvas edge.

### Basic Form Fields

- Name: no more than `8` Chinese characters; `5` or fewer displays best.
- Name must not contain punctuation.
- Chinese names should not contain spaces.
- Name should avoid duplicating an existing sticker pack name.
- Introduction: no more than `80` Chinese characters; describe the character traits or story.
- Copyright: no more than `10` Chinese characters.
- If registered copyright exists, use the registered copyright information.
- If no registered copyright exists, use the designer or studio name.
- Keep copyright text short; abbreviations are acceptable.

### Detail Page Banner

- Upload exactly one detail-page banner.
- Format: JPG or PNG.
- Size: `750x400` pixels.
- Images larger than `500KB` may be compressed by the platform; local export should target `<=500KB`.
- Do not include text information in the banner.
- Banner colors should be lively and distinguishable from the WeChat background; avoid white backgrounds.
- Banner content must relate to the sticker pack, with a rich image and some story.
- Do not stretch or squash elements.
- Avoid transparent backgrounds.

### Cover Image

- Format: PNG.
- Size: `240x240` pixels.
- Images larger than `500KB` may be compressed by the platform; local export should target `<=500KB`.
- Must use transparent background.
- Choose the most recognizable character image; use a frontal half-body or full-body image when possible.
- Avoid white backgrounds.
- Avoid white outlines, jagged edges, square frames, and hard rectangular borders.
- Avoid excessive blank space.
- Keep the image clean and avoid decorative elements.
- Except for pure-text sticker packs, avoid text in the cover.
- Different sticker packs should use different cover images.

### Chat Page Icon

- Format: PNG.
- Size: `50x50` pixels.
- Images larger than `100KB` may be compressed by the platform; local export should target `<=100KB`.
- Must use transparent background.
- Use the clearest and most recognizable image; a frontal head image of the character is recommended.
- Avoid white backgrounds.
- Avoid white outlines, jagged edges, square frames, and hard rectangular borders.
- Avoid excessive blank space.
- Keep the image clean and avoid decorative elements.
- Different sticker packs should use different icon images.

### WeChat Export Package

The final export under `exports/wechat/` should contain:

- `stickers/`: 18 independent `240x240` PNG sticker images.
- `cover.png`: `240x240` PNG with transparent background.
- `icon.png`: `50x50` PNG with transparent background.
- `banner.png` or `banner.jpg`: `750x400` JPG/PNG without transparent background and without text.
- `metadata.json`: machine-readable form data, asset paths, and validation targets.
- `form.md`: human-readable values to paste into the platform form.

Do not place intermediate sheets, failed variants, checkerboard-background images, or review-only files in `exports/wechat/`.

## Test-Mode Output Contract

Until the official WeChat platform constraints are encoded, every test pack should still produce these artifacts:

- One full-sheet preview PNG for overall style review.
- One captioned full-sheet PNG when captions are part of the pack.
- One folder of cropped individual sticker PNGs.
- One contact sheet in `review/` showing all cropped stickers.

Individual sticker PNGs must be:

- PNG files.
- RGBA images with a real alpha channel.
- Transparent in the corners; checkerboard backgrounds are not valid transparency.
- Placed on a consistent transparent canvas size for the current test run.
- Named with a stable sequence number and semantic label, for example `01-hi-嗨呀.png`.

## Caption Rules

Chinese internet sticker packs usually rely on short Simplified Chinese captions. Treat caption rendering as a first-class part of the workflow:

- Captions must come from `spec.json` or another explicit config.
- Do not let the image model invent or rewrite production captions.
- Use Simplified Chinese unless the pack brief explicitly says otherwise.
- Caption accuracy is more important than artistic variation.
- Prefer local text composition for final captions because it preserves exact text and alpha transparency.
- Text should be readable at small sizes.
- Text should not cover the character's eyes, mouth, hands, or main expression.
- A good default style is white fill, thick dark outline, and a warm accent shadow.

## Cropping Rules

Do not rely only on mechanical grid slicing for final individual stickers. Grid slicing is acceptable for a first pass, but final crops should be checked for:

- No clipped character parts.
- No clipped or edge-touching hair. For character stickers, the complete head silhouette and every visible hair tip/spike must remain inside the canvas with clear transparent padding above it.
- No clipped caption strokes or shadows.
- No residue from adjacent stickers.
- Reasonable transparent padding around the visual content.
- Consistent canvas size across the pack.

If a full sheet has captions or decorative marks close to row boundaries, crop by each sticker's actual visual region and then center the result on a fixed transparent canvas.

## Safe-Area And Anti-Crop Rules

This is a hard upload-readiness rule. Several packs have failed review risk because the top of the character's hair was cut off or placed too close to the sticker edge. Do not treat this as a minor visual issue.

For generated raw sheets or single-sticker source images:

- Prompt for the full character and all props to be completely inside frame.
- Prompt for generous blank background above the highest hair tip; a good source-generation target is at least `15%` of the source image height above the highest hair or raised hand.
- If the image model returns clipped hair, clipped hands, clipped shoes, clipped props, or edge-touching content, reject that source and regenerate it instead of trying to hide the problem during final resize.

For final `240x240` sticker exports:

- The alpha bounding box of visible content must not touch any canvas edge.
- Use at least `8px` transparent padding on every side as a minimum mechanical check.
- Use at least `12px` transparent padding above the character's highest hair/head point; use more when hair is spiky, hands are raised, or props sit near the top.
- Captions, stroke outlines, shadows, action marks, moons, stars, leaves, and props must also stay inside the canvas; none may be clipped by the edge.
- If a sticker fails the safe-area check, it is not upload-ready even if dimensions, alpha channel, and file size are otherwise valid.

Validators should fail loudly when any final sticker has an alpha bounding box touching the edge or below the configured safe-area threshold. Review contact sheets are not enough; the validator should also report per-file bounding boxes or margins for suspect assets.

## Quality Bar

For every candidate pack, check:

- Asset completeness
- Test-mode output contract completeness
- Real transparency, not a baked checkerboard background
- Caption text accuracy and readability
- Clean individual crops with no adjacent-sticker residue
- Safe-area compliance: no cropped or edge-touching hair, hands, shoes, props, caption strokes, or shadows.
- Visual consistency across all stickers
- Readability at small display sizes
- No accidental copyrighted, trademarked, or personally sensitive content
- Clear pack title, description, and usage context
- Cover and banner matching the sticker style
- Export folder contains only files intended for upload

Before a package is considered upload-ready, enforce the WeChat Upload Contract above in addition to the test-mode quality checks.

## Notes For Future Agents

- This repo is in an early planning and testing stage.
- Keep changes small and easy to inspect until the workflow has been proven.
- If adding code, prefer explicit validation scripts and deterministic output paths.
- If adding generated images or large binaries, confirm whether they should be committed.
- When exact platform constraints are needed, verify them from the official WeChat Sticker Open Platform documentation before encoding them.
