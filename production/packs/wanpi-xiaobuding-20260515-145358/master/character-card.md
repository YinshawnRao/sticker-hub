# 顽皮小布丁 Master Character Card

## Status

Approved for production. The pack name, fixed visual traits, home/park scene boundary, and 18-sticker caption and visual plan are confirmed. The user requested production generation on 2026-05-15.

- Pack ID: `wanpi-xiaobuding-20260515-145358`
- Workflow phase: asset generation
- Approval status: approved for production
- Approved master image: `master/approved/xiaobuding-approved-master.png`
- Primary reference image: `source/references/master-reference-ip-option-a-transparent.png`

All generated assets must still pass `review/wechat` validation before being treated as upload-ready.

## Input Mode

`image-to-master`

The provided image is treated as the master identity reference. Character cleanup, pose variation, and export normalization are allowed later, but the face, age, outfit identity, and hand-drawn sticker style should not drift.

## Source Material

- Reference 1: `source/references/master-reference-ip-option-a-transparent.png`
  - Role: primary master reference
  - Source copy: `master/input/master-source-ip-option-a-transparent.png`
  - Observed: `1024x1536` PNG, alpha channel present, source size `824664` bytes

The source image has a transparent background and enough resolution for master-character derivation. It is taller than the final sticker format and must not be used directly as a `240x240` production asset without composition, resizing, padding, and validation.

## Character

- Character name: 小布丁
- Pack name: 顽皮小布丁
- Copyright: 饶小虎
- Personality: 顽皮、好奇、机灵，喜欢把家里和公园变成自己的小游乐场；闯祸后会装无辜、撒娇、卖萌。
- Visual style: 温暖手绘卡通贴纸，柔和纹理，细致头发笔触，圆润体块，干净透明背景。

## Locked Traits

These traits should stay stable across the whole pack:

1. Human 1-year-old toddler, not an animal, plush toy, older child, teenager, or adult.
2. Big head and short toddler body proportions, with a broad round forehead and soft cheeks.
3. Short dark brown/black hair, slightly spiky on top, with fine separate hair strokes and short front fringe.
4. Large glossy deep brown/black eyes with clear white highlights; innocent gaze is part of the identity.
5. Small nose, small mouth, soft baby face, warm peach skin, gentle cheek blush.
6. Round ears with peach inner-ear detail.
7. Cream loose long-sleeve top with shoulder buttons.
8. Yellow snail graphic on the chest is a key outfit marker and should remain recognizable when the torso appears.
9. Olive green cuffed pants and white velcro toddler shoes for full-body poses.
10. Warm hand-drawn illustration style with soft shading and clean contour edges.
11. Single sticker frames should use transparent backgrounds; no baked checkerboard, no white square, no hard rectangular frame.
12. Cover and icon should use the clearest frontal head or half-body view and avoid white backgrounds or thick white borders.

## Allowed Variations

- Facial expressions: proud grin, innocent wide eyes, pout, fake-good smile, startled face, sleepy yawn, little cry, secret laugh.
- Poses: open-arm hug, hands behind back, arms crossed, holding bowl, holding pillow, running, crouching, sliding, hiding, sitting after a small fall.
- Home scene props: blocks, toy basket, sofa pillow, soft rug, baby bowl, spoon, curtain edge, scattered plush toys.
- Park scene props: grass patch, small slide, ball, leaf, small shovel, pinwheel, low bush, tiny flower.
- Scene handling: keep stickers transparent and use only compact props or small ground cues; do not add large full backgrounds inside sticker PNGs.
- Banner handling: banner can use an opaque split story scene with home and park cues, but must contain no text.
- Framing: head, half-body, and full-body compositions are allowed as long as the toddler identity, face, and outfit markers remain visible.

## Forbidden Variations

- Do not change species, age range, face shape, dominant outfit, hair color, eye style, or rendering style.
- Do not convert the character into 3D, realistic portrait, pixel art, thick oil painting, cyber style, or unrelated anime style.
- Do not add unapproved logos, brand marks, copyrighted IP characters, celebrities, or personally sensitive content.
- Do not replace the yellow snail shirt graphic with a branded or recognizable external logo.
- Do not let the image model invent or alter production captions. Captions must come from `spec.json` and should be composed locally for exact text.
- Do not let captions cover the eyes, mouth, hands, or core action.
- Do not put raw sheets, rejected candidates, checkerboard previews, review contact sheets, or failed variants into `exports/wechat/`.
- Do not use a transparent or white banner background. The banner must be opaque, lively, and related to the pack.

## Caption Style

- Language: Simplified Chinese.
- Source of truth: `spec.json` `captions.items`.
- Rendering: local composition preferred for final captions.
- Default style: white fill, thick dark brown outline, warm yellow/brown accent shadow.
- Placement: usually lower third, centered or slightly arced; must not block eyes, mouth, hands, or core pose.
- Readability target: clear at WeChat small chat display size after resizing to `240x240`.

## Planned Sticker Set

Confirmed caption and visual plan for production generation.

| # | Caption | Scene | Pose |
| --- | --- | --- | --- |
| 01 | 捣蛋中 | 家里 | 蹲在散落积木旁，笑得有点心虚 |
| 02 | 糟糕啦 | 家里 | 翻倒玩具篮旁积木滚一地，小布丁双手捧脸装惊讶，闯祸但可爱 |
| 03 | 我很乖 | 家里 | 乖巧坐好，嘴角偷笑 |
| 04 | 抱抱我 | 家里 | 张开小手求抱，表情软萌 |
| 05 | 开饭啦 | 家里 | 捧着小碗开心张嘴 |
| 06 | 我不嘛 | 家里 | 坐在地垫上抱紧小抱枕，撅嘴撒娇拒绝 |
| 07 | 被发现啦 | 家里 | 从沙发或门边探出半个身子，旁边露出被弄乱的小玩具，像刚被抓包 |
| 08 | 拆家啦 | 家里 | 站在散落玩具中间举手庆祝 |
| 09 | 困啦 | 家里 | 抱枕打哈欠，眼皮下垂 |
| 10 | 冲呀 | 公园 | 在草地上小跑，回头坏笑 |
| 11 | 滑梯冲 | 公园 | 从小滑梯上开心滑下 |
| 12 | 泥巴王 | 公园 | 小手沾泥，骄傲举起小铲子 |
| 13 | 玩沙子 | 公园 | 蹲在小沙坑边，拿小铲子堆沙子，手上沾一点沙，表情专注又得意 |
| 14 | 躲起来啦 | 公园 | 藏在滑梯后或低矮灌木旁，只露出脑袋和一只小手，像在玩捉迷藏 |
| 15 | 小手脏 | 公园 | 举起脏脏小手，表情无辜 |
| 16 | 摔倒啦 | 公园 | 坐在草地上抱球，眼眶委屈但可爱 |
| 17 | 再玩会 | 公园 | 抱着球不肯走，抬头撒娇 |
| 18 | 嘿嘿嘿 | 公园 | 双手捂嘴偷笑，脸颊更红 |

## Approval Questions

Please confirm or adjust these before sticker generation:

1. 已确认：pack 名称使用 `顽皮小布丁`。
2. 已确认：参考图中的米白上衣、黄色蜗牛图案、橄榄绿裤子、白色童鞋作为固定识别特征。
3. 已确认：18 个字幕、道具、场景和画面描述。
4. 已确认：单张表情只保留少量道具提示，完整家里/公园场景主要放在 banner。
5. 已确认：母版卡正式锁定并进入生产生成阶段。
