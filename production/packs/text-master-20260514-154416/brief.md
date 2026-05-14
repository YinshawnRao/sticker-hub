# Pack Brief

## Pack Identity

- Pack ID: `text-master-20260514-154416`
- Environment: production
- Working directory: `production/packs/text-master-20260514-154416/`
- Input mode: `text-to-master`
- Status: initialized, awaiting master character card confirmation

## Current Stage

This pack is stopped at the `master-character` stage. No master candidates, sticker sheets, cropped stickers, WeChat-size draft stickers, cover, icon, banner, or upload-ready assets have been generated.

## Source Text Brief

Generate an anime-style character image of a programmer who has been working overtime for a long time. The 18-sticker set should express common Chinese internet big-tech workplace jargon and engineering-office moments.

- Character species or type: human anime programmer
- Character name: 卷卷码农
- Personality: tired, sharp, self-deprecating, resilient, quietly funny
- Visual style: clean anime sticker style, cute but recognizably overworked, expressive face, thick readable outline, transparent-background friendly
- Main colors: dark hoodie, muted tech-blue accents, warm skin tone, black messy hair, mild under-eye shadows
- Recurring accessories or props: laptop, keyboard, coffee cup, ID badge without real company logo, dark hoodie, small code symbols when useful
- Caption tone: short Simplified Chinese captions using generic Chinese internet-company jargon, dry humor, no specific company names
- Must avoid: real company logos, trademarked mascots, specific employer references, copyrighted IP, realistic personal likeness, unreadable long captions

## Provisional Pack Direction

- Working title: 加班码农
- Pack type: static WeChat sticker pack
- Target sticker count: 18
- Caption language: Simplified Chinese
- Theme: long-overtime programmer life and generic Chinese internet big-tech jargon
- Final export target: WeChat Sticker Open Platform package under `exports/wechat/` after master approval

## Workflow Gates

1. Confirm the source text brief and master character card.
2. Generate master character candidates under `master/candidates/`.
3. Move only the user-approved master image to `master/approved/`.
4. Generate final sticker sheets only after the master character card and approved master image are locked.

## Review Notes

- 2026-05-14: Production pack initialized from template with `text-to-master` mode. Work intentionally stopped before master image generation and before the final 18-sticker stage.
- 2026-05-14: User requirement added: anime character of a long-overtime programmer, with 18 captions reflecting generic Chinese internet big-tech jargon. Still waiting for master character card confirmation.
