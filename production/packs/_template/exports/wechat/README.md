# WeChat Export Package

This directory is reserved for the final upload-ready package for the WeChat Sticker Open Platform.

Expected final contents:

- `stickers/`: 18 independent `240x240` PNG static sticker images.
- `cover.png`: `240x240` PNG, transparent background.
- `icon.png`: `50x50` PNG, transparent background.
  Must be a clean front-facing head-only crop. The complete chin/lower face must be visible, with clear transparent padding below it. Do not use body, hands, gestures, captions, action marks, props, or decorative elements in the chat page icon.
- `banner.png`: `750x400` PNG/JPG, opaque background, no text.
- `metadata.json`: machine-readable submission data and asset manifest.
- `form.md`: human-readable values to paste into the platform form.

Do not put intermediate sheets, failed variants, or review images here.

Before upload, review `icon.png` enlarged on a checkerboard background. Reject it if the chin looks clipped or too close to the bottom edge, even when the PNG dimensions and file size are valid.
