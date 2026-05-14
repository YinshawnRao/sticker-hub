# 小布丁03 Master Character Card

## Status

Approved for production by the user. The master identity is locked before final sticker production.

- Pack ID: `xiaobudou-20260514-152334`
- Workflow phase: asset generation
- Approval status: approved
- Approved master image: `source/references/xbd-small-reference.png`

## Input Mode

`image-to-master`

The provided images are treated as identity references. The character identity should be preserved first; cleanup and export normalization are allowed, but the character must not drift into a new design unless the user explicitly requests it.

## Source Material

- Reference 1: `source/references/xbd-big-reference.png`
  - Role: full-body and outfit reference
  - Source copy: `master/input/xbd-big-master-source.png`
  - Observed: `1024x1024` PNG, alpha channel present, source size about 2.17MB
- Reference 2: `source/references/xbd-small-reference.png`
  - Role: head, face, and blue-white bib reference
  - Source copy: `master/input/xbd-small-master-source.png`
  - Observed: `1024x1024` PNG, alpha channel present, source size about 1.96MB

Reference 2 drives the face, head shape, expression, and bib identity. Reference 1 supplements the full-body clothing, posture, and simple childlike outfit details.

## Character

- Character name: 小布丁
- Pack name: 小布丁03
- Copyright: 饶小虎
- Personality: 爱笑、亲近、会撒娇，偏嘴硬、犯懒和轻微戏精感。
- Visual style: 温暖手绘卡通贴纸，粗深色描边，柔和纹理，透明背景，适合微信聊天小图阅读。

## Locked Traits

These traits should stay stable across the whole pack:

1. Human baby/toddler character, not an animal, plush toy, older child, or adult.
2. Oversized round head, broad forehead, soft round face, short baby body proportions.
3. Short black hair with sparse top/front hair strokes; no long hair, dyed hair, hat, or hairstyle replacement.
4. Large black oval eyes with clear white highlights; eyebrows are simple curved strokes.
5. Tiny rounded nose and a wide open smile as a major identity marker.
6. Warm peach/orange skin tone with round rosy cheeks and subtle hand-drawn blush strokes.
7. Round ears with peach-pink inner ear detail and thick dark outline.
8. Blue-white checked bib/collar is the fixed accessory and must remain visible in most stickers.
9. Outfit may use the cream baby clothes/sleeping-bag feel from reference 1, including tiny simple patterns, but those details are secondary.
10. Line art should use thick dark brown/black hand-drawn outlines, not thin vector outlines.
11. Final single stickers should be on transparent background. No baked checkerboard, no white square, no hard rectangular frame.
12. Cover and icon must avoid a white background and avoid an overly thick white sticker border.

## Allowed Variations

- Facial expressions: big smile, shy smile, pout, teary eyes, sleepy, surprised, proud, focused, grateful,嘴硬,犯懒。
- Poses: waving, cheering, nodding, hands-together thanks, fist pump, open-arms hug, thumbs-up, heart gesture, running away, sleeping, lying down, peeking from the edge.
- Props: small bowl, milk bottle, pillow, simple heart, small star, small moon, tiny motion lines.
- Framing: head, half-body, and full-body compositions are allowed as long as the baby identity and bib are still recognizable.
- Clothing detail: light cream baby outfit and tiny naive patterns may appear in full-body stickers, but should not dominate the image.
- Scene cues: very small non-text decorative cues are allowed for emotion, but the sticker should stay clean and readable at 240x240.

## Forbidden Variations

- Do not change species, age range, face shape, dominant colors, eye style, or bib design.
- Do not convert the character into 3D, realistic portrait, pixel art, thick oil painting, cyber style, or unrelated anime style.
- Do not add unapproved logos, brand marks, IP characters, celebrities, or personally sensitive content.
- Do not generate or alter production captions inside the image model. Captions must come from `spec.json` and should be composed locally for exact text.
- Do not cover the eyes, mouth, hands, or main expression with captions.
- Do not use white or transparent backgrounds for the banner. Banner must be opaque and contain no text.
- Do not put raw sheets, rejected candidates, checkerboard previews, or review-only images into `exports/wechat/`.

## Caption Style

- Language: Simplified Chinese.
- Source of truth: `spec.json` `captions.items`.
- Rendering: local composition preferred for final captions.
- Default style: white fill, thick dark brown outline, warm yellow/brown accent shadow.
- Placement: usually lower third, centered or slightly arced; must not block eyes, mouth, hands, or core pose.
- Readability target: clear at WeChat small chat display size after resizing to `240x240`.

## Planned Sticker Set

| # | Caption | Pose |
| --- | --- | --- |
| 01 | 抱抱 | 张开双手求抱抱，表情温软 |
| 02 | 哼哼 | 撇嘴叉腰，带一点小傲娇 |
| 03 | 吃饭 | 捧小碗或奶瓶，开心张嘴 |
| 04 | 开工 | 认真坐好，举小手或拿小笔 |
| 05 | 溜啦 | 小跑回头挥手 |
| 06 | 装乖 | 乖巧坐好但眼神机灵 |
| 07 | 要哄 | 委屈等安慰，眼睛水润 |
| 08 | 先躺 | 抱枕瘫倒，先躺一会儿 |
| 09 | 不听 | 捂耳朵摇头，鼓脸拒绝 |
| 10 | 嘴硬 | 叉腰撇嘴，表情嘴硬但可爱 |
| 11 | 已读乱回 | 认真但迷糊回应，眼神飘忽 |
| 12 | 脑袋空空 | 呆住放空，头顶小圈圈 |
| 13 | 偷偷冒泡 | 从画面边缘探头出现，像刚上线但不想太高调 |
| 14 | 让我想想 | 托腮思考，眉毛微皱 |
| 15 | 偷偷开心 | 捂嘴笑，脸颊更红 |
| 16 | 有点慌 | 瞪眼手忙脚乱，旁边小汗滴 |
| 17 | 充电中 | 抱奶瓶或抱枕恢复体力 |
| 18 | 别催啦 | 小手挡住催促，表情有点慌又撒娇 |

## Approval Record

- 2026-05-14: User approved pack name `小布丁03`, copyright `饶小虎`, master strategy, locked traits, forbidden drift rules, and the 18 captions above.
