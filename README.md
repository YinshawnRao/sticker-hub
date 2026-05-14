# Sticker Hub

Sticker Hub is a local workflow for producing WeChat Sticker Open Platform submission packages.

The project is designed around a strict production pipeline:

1. Start a pack under `production/packs/<pack-id>/`.
2. Choose an input mode:
   - `text-to-master`: generate a master character from a text brief.
   - `image-to-master`: derive the master character from a user-provided reference image.
3. Confirm the master character card before producing final stickers.
4. Generate two `3x3` sticker sheets for 18 static stickers.
5. Add exact Simplified Chinese captions locally.
6. Crop and normalize stickers to WeChat upload dimensions.
7. Export a complete `exports/wechat/` package.

## Output Target

The current production target is a static WeChat sticker pack:

- 18 sticker images: `240x240` PNG, transparent background
- Cover: `240x240` PNG, transparent background
- Chat icon: `50x50` PNG, transparent background
- Detail banner: `750x400` PNG/JPG, opaque background, no text
- Form metadata: name, introduction, copyright, and asset manifest

## Directory Layout

```text
production/
  packs/
    _template/
    <pack-id>/
      brief.md
      spec.json
      master/character-card.md
      generated/
      review/
      exports/wechat/

testdata/
  packs/
    sample-pack/
```

`testdata/packs/sample-pack/` is the trial pack used to validate the workflow. Real packs should be created under `production/packs/<pack-id>/`.

Generated images, review images, exported upload packages, and user reference images are ignored by git by default. The repository commits the reusable workflow, templates, specs, and documentation.

## Starting A New Pack

Open a new Codex window and paste the prompt in:

[docs/start-new-pack-prompt.md](docs/start-new-pack-prompt.md)

The important rule is: do not generate the final 18 stickers until the master character card has been confirmed.

## Core Files

- [AGENTS.md](AGENTS.md): authoritative workflow rules for agents.
- [docs/start-new-pack-prompt.md](docs/start-new-pack-prompt.md): reusable startup prompt for new windows.
- [production/packs/_template](production/packs/_template): production pack template.
