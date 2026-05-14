# Image Generation Record

- Date: 2026-05-14
- Pack ID: `cool-boy-20260514-163100`
- Tool mode: built-in `image_gen`
- Model/settings: not directly exposed by the built-in tool
- Reference image:
  - `master/input/master-reference-original.png`
  - SHA-256: `a3539bd0ef0bd5f60413ccf1bdddc90ceccb6ce8d5798d6004c08f1c5ca37bf3`
- Post-processing script:
  - `source/prompts/build_wechat_assets.py`

## Generated Raw Sheets

Current selected raw sheets after quality regeneration:

| Sheet | Built-in generated file | Workspace raw sheet | Notes |
| --- | --- | --- | --- |
| 01 | `/Users/yinshawnrao/.codex/generated_images/019e2599-fbfd-7112-803e-6e68464b0e59/ig_0a33221eeaccd0a3016a05945453b08191a466e8be3f4e9435.png` | `generated/sheets/raw/sheet-01-raw.png` | Regenerated to increase pose diversity, shorten hair, add richer props, and avoid clipping. |
| 02 | `/Users/yinshawnrao/.codex/generated_images/019e2599-fbfd-7112-803e-6e68464b0e59/ig_0a33221eeaccd0a3016a0591964454819185c7ec76a1fc70f6.png` | `generated/sheets/raw/sheet-02-raw.png` | Regenerated to increase pose diversity, shorten hair, and add richer props. |

Earlier generated sheets kept in the default Codex generated image folder are superseded by the current selected raw sheets above.

## Earlier Generated Raw Sheets

| Sheet | Built-in generated file | Workspace raw sheet |
| --- | --- | --- |
| 01 | `/Users/yinshawnrao/.codex/generated_images/019e2599-fbfd-7112-803e-6e68464b0e59/ig_0a33221eeaccd0a3016a058aeaac788191abb72e4362aca281.png` | `generated/sheets/raw/sheet-01-raw.png` |
| 02 | `/Users/yinshawnrao/.codex/generated_images/019e2599-fbfd-7112-803e-6e68464b0e59/ig_0a33221eeaccd0a3016a058b76bfec8191b8f27581269ceaa0.png` | `generated/sheets/raw/sheet-02-raw.png` |

## Current Prompt: Sheet 01

```text
Use case: illustration-story
Asset type: WeChat sticker pack raw 3x3 sheet for local post-processing
Input image role: the attached boy image is the identity and style reference. Preserve the same child identity, outfit, face proportions, and clean chibi anime sticker rendering, but improve the design: the boy's black spiky hair should be SHORTER and LIGHTER than the reference, with less thick volume and only a few small spikes. Keep round face, big dark brown eyes, pink cheeks, beige striped bib, dark charcoal cloud-pattern shirt, black loose pants, and white round shoes.

Primary request: Create ONE raw 3x3 sticker sheet with 9 separate sticker illustrations of this same boy. No text, no captions, no speech bubbles, no watermark. Each cell contains exactly one boy, fully separated by flat background space for later cropping.

Critical layout requirement: Each of the 9 stickers must be fully inside its cell with generous margin on all four sides. No head, hair, shoes, hands, props, speed lines, teddy bears, blocks, or check cards may touch or cross a cell edge. Do not let any element from one cell enter a neighboring cell.

Critical quality requirement: Do NOT make copy-paste standing variants. Every cell must have a clearly different silhouette, body angle, weight, action, and emotional staging. Use richer small props where useful. Avoid repeated hands-on-hips/straight-standing poses except where explicitly needed.

Poses in row-major order:
1. 不服: compact crouching or seated pose, puffed cheeks, one tiny fist raised, stubborn kid energy; keep full hair and shoes inside cell.
2. 稳了: confidently balancing one foot on a small toy block or stepping stone, one thumb up, reassuring smile; stable diagonal stance.
3. 冲呀: dynamic running leap forward, one shoe lifted high, small dust puff and speed lines, excited open-mouth face; leave margin around speed lines.
4. 搞定: kneeling beside small finished toy blocks and holding a checkmark card up proudly; not just standing, all blocks inside cell.
5. 夸我: hugging a gold star or little medal with sparkling eyes, leaning forward asking for praise; no neighboring fragments below.
6. 我超乖: sitting cross-legged with hands neatly on knees, angelic innocent face but eyes secretly glancing sideways.
7. 没闹呀: caught with a tipped toy box or scattered toy pieces, both hands raised in denial, guilty innocent smile; toy pieces inside cell.
8. 就要嘛: reaching upward with both hands toward a small dangling toy held completely inside the same cell, one foot stomping, cute stubborn pleading expression; do not crop the head or the toy.
9. 不给你: hugging a teddy bear tightly and turning body away, protective mischievous face; teddy bear fully visible.

Background and technical constraints: perfectly flat solid #00ff00 chroma-key background across the whole sheet, including cell gaps. No shadows, gradients, texture, floor, lighting variation, or contact shadows on the background. Do not use #00ff00 anywhere in characters or props. No baked checkerboard, no white page background, no large white sticker halo, no rectangular frames. Make the 9 illustrations visually consistent with each other and the reference image while using distinct poses.
```

## Current Prompt: Sheet 02

```text
Use case: illustration-story
Asset type: WeChat sticker pack raw 3x3 sheet for local post-processing
Input image role: the attached boy image is the identity and style reference. Preserve the same child identity, outfit, face proportions, and clean chibi anime sticker rendering, but improve the design: the boy's black spiky hair should be SHORTER and LIGHTER than the reference, with less thick volume and only a few small spikes. Keep round face, big dark brown eyes, pink cheeks, beige striped bib, dark charcoal cloud-pattern shirt, black loose pants, and white round shoes.

Primary request: Create ONE raw 3x3 sticker sheet with 9 separate sticker illustrations of this same boy. No text, no captions, no speech bubbles, no watermark. Each cell contains exactly one boy, fully separated by flat background space for later cropping.

Critical quality requirement: Do NOT make copy-paste standing variants. Every cell must have a clearly different silhouette, body angle, weight, action, and emotional staging. Use richer small props where useful. Avoid repeated hands-on-hips/straight-standing poses except where explicitly needed.

Poses in row-major order:
10. 抓不到: looking back while sprinting diagonally away, one arm stretched behind, laughing proudly, chase feeling with small dust puff.
11. 皮一下: crouching or leaning forward after a prank, one hand making a tiny V sign, toy blocks scattered nearby, cheeky eyes.
12. 偷笑中: half-hidden behind a curtain-like cloth or big cushion, only part of body visible, covering mouth while secretly laughing.
13. 假装听话: sitting at a tiny low stool or mat with a picture book upside down, posture overly proper, eyes drifting away, pretending to obey.
14. 脑袋转转: lying belly-down or kneeling over toy blocks, finger on chin, lightbulb and question mark cues, thinking hard.
15. 再玩会: hugging a toy car or little robot with both arms, leaning backward protectively, pleading eyes.
16. 饭饭呢: holding a rice bowl and spoon close to face, sitting or kneeling, earnest hungry expression; bowl should be clear and cute.
17. 小手叉腰: tiny hands on hips, feet wide apart, chest puffed out, head tilted upward, playful proud bossy stance.
18. 小得意: reclining against a large cushion or sitting with one leg out, eyes closed in a smug smile, small sparkle cues, cute proud expression.

Background and technical constraints: perfectly flat solid #00ff00 chroma-key background across the whole sheet, including cell gaps. No shadows, gradients, texture, floor, lighting variation, or contact shadows on the background. Do not use #00ff00 anywhere in characters or props. No baked checkerboard, no white page background, no large white sticker halo, no rectangular frames. Keep all body parts and props inside each cell with generous padding. Make the 9 illustrations visually consistent with each other and the reference image while using distinct poses.
```

## Superseded Prompt: Sheet 01

```text
Use case: illustration-story
Asset type: WeChat sticker pack raw 3x3 sheet for local post-processing
Input image role: the attached boy image is the identity and style reference. Preserve the same character identity: Q-version toddler boy, short black spiky hair, round face, big dark brown eyes, soft pink cheeks, beige striped bib, dark charcoal shirt with subtle dark cloud pattern, black loose pants, white round shoes. Keep the same clean chibi anime sticker rendering, crisp edges, soft shading, cute and slightly cheeky personality.

Primary request: Create ONE raw 3x3 sticker sheet containing 9 separate poses of this same boy, no text, no captions, no speech bubbles, no watermarks. Each cell should contain exactly one full-body or half-body character pose, centered with generous padding and separated by visible flat background space for later cropping.

Poses in row-major order:
1. 不服: puffed cheeks, tiny fist raised, stubborn but cute.
2. 稳了: standing confidently, one hand in pocket or on hip, reassuring expression.
3. 冲呀: running forward with simple speed lines, excited playful face.
4. 搞定: hands on hips, chin slightly raised, proud finished-task feeling.
5. 夸我: looking up expectantly with sparkling eyes, playful proud cuteness.
6. 我超乖: hands behind back, pretending to be very obedient, slightly guilty innocent eyes.
7. 没闹呀: waving hands to deny mischief, innocent face with a tiny sly smile.
8. 就要嘛: reaching forward or lightly stomping, cute stubborn pleading expression.
9. 不给你: hugging a small toy/object protectively, mischievous raised brow.

Background and technical constraints: perfectly flat solid #00ff00 chroma-key background across the whole image, including cell gaps. No shadows, gradients, texture, floor, lighting variation, or contact shadows on the background. Do not use #00ff00 in the character or props. No baked checkerboard, no white page background, no large white sticker halo, no rectangular frames. Keep all body parts inside each cell. Make the 9 characters visually consistent with each other and with the reference image.
```

## Superseded Prompt: Sheet 02

```text
Use case: illustration-story
Asset type: WeChat sticker pack raw 3x3 sheet for local post-processing
Input image role: the attached boy image is the identity and style reference. Preserve the same character identity as the reference and the previous sheet: Q-version toddler boy, short black spiky hair, round face, big dark brown eyes, soft pink cheeks, beige striped bib, dark charcoal shirt with subtle dark cloud pattern, black loose pants, white round shoes. Keep the same clean chibi anime sticker rendering, crisp edges, soft shading, cute and slightly cheeky personality.

Primary request: Create ONE raw 3x3 sticker sheet containing 9 separate poses of this same boy, no text, no captions, no speech bubbles, no watermarks. Each cell should contain exactly one full-body or half-body character pose, centered with generous padding and separated by visible flat background space for later cropping.

Poses in row-major order:
10. 抓不到: looking back while running away, laughing proudly, playful chase feeling.
11. 皮一下: tilting head and making a tiny mischievous gesture, eyes cheeky, as if he just got away with a prank.
12. 偷笑中: peeking from one side and secretly laughing, warm blush.
13. 假装听话: sitting very properly or standing straight, hands neat, eyes drifting away, pretending to obey.
14. 脑袋转转: thinking hard, eyes moving, small lightbulb or question mark cue near head.
15. 再玩会: hugging a small toy and refusing to put it down, hopeful playful look.
16. 饭饭呢: holding a little bowl or spoon, earnest and slightly wronged hungry expression.
17. 小手叉腰: tiny hands on hips, standing firmly, chin raised, proud kid energy.
18. 小得意: eyes half-smiling, leaning back slightly, cute proud expression.

Background and technical constraints: perfectly flat solid #00ff00 chroma-key background across the whole image, including cell gaps. No shadows, gradients, texture, floor, lighting variation, or contact shadows on the background. Do not use #00ff00 in the character or props. No baked checkerboard, no white page background, no large white sticker halo, no rectangular frames. Keep all body parts inside each cell. Make the 9 characters visually consistent with each other and with the first sheet and reference image.
```

## Local Post-Processing

`build_wechat_assets.py` performs:

- chroma-key background removal from raw sheets;
- grid crop into `generated/stickers/source-crops/`;
- deterministic Simplified Chinese caption composition;
- `240x240` WeChat draft and export sticker generation;
- `cover.png`, `icon.png`, `banner.png` generation;
- review contact sheets and validation report generation;
- export-folder cleanliness checks.
