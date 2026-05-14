# Generation Plan

## Source

- Pack: `image-master-20260514-155523`
- Master input: `master/input/cos-ip-master-reference.png`
- Approved master: `master/approved/cos-ip-approved-master.png`
- Style reference: `source/references/line-art-style-reference.png`

## Production Constraint

Every generated character asset must retain a legible `COS` label on the blue folder. The label is rendered locally instead of delegated to an image model so the text remains exact.

## Visual Direction

- White cloud-shaped mascot body.
- Bright blue folder with exact `COS` text.
- Clean 2D chibi line-art sticker style, thick dark outline, expressive face, rounded positive office-friendly character.
- Internet-company daily work mood, but normal and upbeat rather than overtime or complaint driven.

## Deterministic Output

The current pack uses `source/prompts/generate_assets.py` for first-pass production. It reads `spec.json` captions and writes only inside this pack directory.

Generated assets:

- `generated/sheets/raw/`
- `generated/sheets/captioned/`
- `generated/stickers/source-crops/`
- `generated/stickers/wechat-draft/`
- `review/master/`
- `review/sheets/`
- `review/stickers/`
- `review/wechat/`
- `exports/wechat/`

Run command:

```bash
/Users/yinshawnrao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 production/packs/image-master-20260514-155523/source/prompts/generate_assets.py
```
