# Master Character Card

## Status

Approved for local asset production.

The user invoked `/goal` on 2026-05-18 to generate the full pack under the current repository constraints. Final upload still requires human review and latest platform rule re-check.

## Input Mode

`image-to-master`

## Source Material

- Original local path: `/Users/yinshawnrao/.codex/generated_images/019e392d-c7f3-7b31-85ce-da8ed8d490f6/ig_0413eed2c8144a41016a0ab8991878819085927c2789a12445.png`
- Pack reference copy: `source/references/sweet-couple-reference.png`
- Master input copy: `master/input/sweet-couple-master-reference.png`
- Approved master image: `master/approved/sweet-couple-approved-master.png`

Source image facts:

- PNG
- `1254x1254`
- RGB
- `1697792` bytes
- Baked white background and white sticker border; not suitable as a final transparent upload asset.

## Character

- Pack name: 小两口旅行记
- Character name: 小两口
- Personality: warm, affectionate, travel-loving, curious, playful, supportive.
- Visual style: soft anime/chibi couple sticker, thick clean outline, warm tones, glossy brown eyes, gentle blush, rounded face proportions.

## Theme Direction

夫妻两人在欧洲旅行和参观博物馆时的日常聊天：出发、看展、拍照、惊叹、看不懂但震撼、找路、喝咖啡、逛累、买纪念品、一起走、等一下、晚安和去下一站。

The pack should focus on travel and museum scenarios first. A little sweetness is allowed, but romance should not overpower the travel and museum theme. It should not be overly dramatic, photorealistic, or built around celebrity, fan-art, or third-party IP resemblance.

## Identity Preservation Rule

The provided master/reference image is the source of truth. Downstream generation must preserve the two-character identity before optimizing style, expression, pose, or sticker readability.

For every master-derivative generation step:

- Supply `master/input/sweet-couple-master-reference.png` as an actual image input.
- Preserve both characters' core identity traits from the reference image.
- Keep most stickers as two-person compositions. A small number of single-character close-ups are allowed only if the pack still clearly reads as a two-person couple travel pack.
- Record the source image path, prompt, model settings, and whether the output was model-edited from the image or manually approved.
- Do not use a text-only prompt to generate production sticker character artwork.
- Do not replace the couple with a local deterministic drawing, simplified placeholder, unrelated mascot, or newly invented character.

## Locked Traits

Two-person identity:

- Young anime/chibi married couple, referred to as `小两口`.
- Close side-by-side warmth and affectionate travel-companion relationship impression.
- Rounded chibi proportions with large heads, soft cheeks, and simplified bodies.
- Clean dark sticker outline and warm soft rendering.
- Travel and museum theme should remain visible across the pack.

Girl:

- Long dark-brown hair with side bangs and soft layered strands.
- Large glossy brown eyes with bright catchlights.
- Warm skin tone, soft pink cheek blush, small nose, and open friendly smile.
- Navy outer layer over a light cream or white inner top.
- Cute, bright, approachable expression.

Boy:

- Short black hair with neat fringe and slightly tousled top shape.
- Large glossy brown eyes with bright catchlights.
- Black rectangular glasses with a small warm metal hinge detail.
- Warm skin tone, soft pink cheek blush, small nose, and calm friendly smile.
- Gray hoodie over teal-green shirt.
- A black diagonal strap may appear as a graphic clothing detail; do not invent or emphasize legible brand text unless separately approved.

## Allowed Variations

- Facial expressions within the same two-character identity.
- Pose, body angle, and hand gesture.
- Most stickers should show both characters together.
- Single-character close-ups only if the selected character remains clearly traceable to the approved master image and the pack still reads as a two-person couple travel pack.
- Travel and museum props: phone, camera, generic museum ticket, map, guidebook, coffee cup, suitcase, train ticket, umbrella, postcard, souvenir bag, message bubble, or tiny gift.
- Generic European museum and travel cues: exhibition hall shapes, sculpture silhouettes, framed art shapes, street cafe hints, station signs without real brand text, cobblestone street mood, and route cards.
- Simple scene cues for going out, taking photos, entering a museum, looking at exhibitions, walking, resting, waiting, getting lost, buying souvenirs, drinking coffee, and goodbye.
- Small hearts, sparkles, sweat drops, motion marks, moon, stars, or soft blush effects when kept inside the sticker safe area and not overpowering the travel theme.

## Forbidden Variations

- Changing either character into an animal, mascot object, robot, or unrelated person.
- Changing the girl hair length, dark-brown hair identity, face shape, large brown eyes, blush style, or navy-light outfit impression without approval.
- Changing the boy short black hair, black glasses, face shape, large brown eyes, gray hoodie, or teal shirt impression without approval.
- Adding extra people or unrelated characters.
- Replacing the two-character pair with a single new mascot as the pack identity.
- Dropping the two-person couple identity from most stickers.
- Using photorealistic rendering or realistic portrait editing.
- Making the set resemble a celebrity, public figure, copyrighted character, or third-party IP.
- Adding unapproved logos, trademarks, readable brand names, recognizable museum logos, exact copyrighted artwork reproductions, or personally sensitive content.
- Making specific real landmarks or artworks so recognizable that they create review or rights risk.
- Letting image generation invent, rewrite, or misspell production captions.
- Using a baked white, checkerboard, rectangular, or square background in final transparent sticker assets.

## Caption Style

- Language: Simplified Chinese.
- Exact captions must come from `spec.json` or another explicit config.
- Prefer local text composition for final captions.
- Default style: white fill, thick dark brown outline, warm peach or soft yellow accent shadow.
- Placement should avoid covering eyes, mouth, glasses, hands, and the main expression.

## Planned Sticker Set

Draft captions and expression/action plan for confirmation:

1. 出发啦: both characters stand together with small suitcase and camera, excited travel sparkle.
2. 看展去: both characters hold generic museum tickets and walk toward a simple exhibition-hall cue.
3. 拍一张: girl raises a phone for a selfie while boy leans in, both faces clearly visible.
4. 好好看: both characters look up with sparkling eyes at a generic framed-art or sculpture silhouette.
5. 看不懂: both characters tilt heads with confused cute faces in front of a generic abstract frame.
6. 太震撼了: both characters open eyes wide with awe, small sparkle and generic sculpture silhouette.
7. 走哪边: both characters hold a generic map together with small question marks.
8. 喝咖啡: both characters hold small coffee cups and relaxed smiles.
9. 逛累了: both characters slump cutely beside a suitcase or bench, tired but cheerful.
10. 买这个: girl points to a small souvenir while boy looks amused, no real brand or artwork.
11. 安排上: boy carefully holds generic tickets while girl nods, small checkmark cue.
12. 一起走: both characters walk side by side with subtle hand-holding or close shoulder-to-shoulder pose.
13. 迷路了: both characters look at a map with cute sweat drops and turned-around arrows.
14. 帮我拍: one character adjusts camera or bag while the other waits with a patient smile.
15. 贴贴: both characters lean close with gentle blush and tiny hearts, travel cue still present.
16. 带回家: both characters hold a small postcard or souvenir bag with generic non-branded design.
17. 晚安啦: both characters sleepy beside a suitcase and small moon, still clearly the same couple.
18. 下站见: both characters wave together with train-ticket or route-card cue, no real station brand.

## Chat Page Icon Direction

Generate a dedicated front-facing two-head close crop from approved character artwork. It must not be a shrunken sticker or cover.

Icon constraints:

- Both heads should be complete and recognizable at `50x50`.
- No bodies, hands, captions, action marks, props, decorative scene elements, logos, or text.
- Full lower face and chin contours must be visible for both characters.
- Keep clear transparent padding on every side, especially below the chins.
- If a two-head crop is not readable or fails safe-area review at `50x50`, pause for user review instead of silently switching to a single-character icon.

## Approval Gate

- [x] Source/reference image is stored in the pack directory.
- [x] Character identity traits are drafted in this card.
- [x] Allowed and forbidden variations are drafted.
- [x] Planned captions and expression/action plan are drafted.
- [x] User confirms pack display name: `小两口旅行记`.
- [x] User confirms copyright text: `饶小虎`.
- [x] User confirms relationship: married couple / `小两口`.
- [x] User confirms composition rule: most stickers must be two-person; a small number of single-character stickers are allowed only when identity remains traceable.
- [x] User confirms theme: tourism and museum first, moderate sweetness second.
- [x] User confirms copyright-safe generic travel and museum cues.
- [x] User confirms chat page icon direction: dedicated two-head front-facing close crop.
- [x] User approves this card for master image generation or master cleanup via `/goal`.
- [x] Approved master image is stored in `master/approved/sweet-couple-approved-master.png`.
- [x] Final sticker production is allowed for local generation and review.
- [ ] Human review accepts identity preservation across final assets.
- [ ] Human review accepts semantic variation with captions ignored.
- [ ] Human review accepts the dedicated two-head icon at `50x50`.
- [ ] Human review accepts copyright-safe generic museum/travel cues.
