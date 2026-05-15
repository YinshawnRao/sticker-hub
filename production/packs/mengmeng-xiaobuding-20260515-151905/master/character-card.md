# Master Character Card - 萌萌小布丁

## Status

Draft card created. Awaiting user approval before any final 19-sticker generation.

## Input Mode

`image-to-master`

## Source Material

- User-provided image archived at `source/references/master-reference-original.png`
- Master input copy archived at `master/input/master-reference-original.png`
- Current approved master image path: not yet approved

The provided image is treated as the identity reference. It must be preserved as the top priority in downstream generation. Style cleanup, transparent-background extraction, and pose/expression variation are allowed only if they do not change the character identity.

## Character

- Pack title candidate: 萌萌小布丁
- Character name: 小布丁
- Personality: soft, curious, clingy, expressive, easy to make people smile
- Role/theme: toddler emotion sticker character for daily chat reactions
- Visual style: polished soft baby illustration, warm shading, clean edges, high cuteness, readable at small chat size

## Locked Visual Traits

1. Human toddler character with round baby proportions, large head, small body, and seated/half-body-friendly silhouette.
2. Warm light skin, rosy cheeks, tiny nose, small pink mouth, soft baby facial features.
3. Large glossy dark brown eyes with bright highlights and gentle eyebrows.
4. Short warm brown hair with soft fringe visible under the cap.
5. Signature cream cap with navy brim, navy rounded ear-like side puffs, navy star pattern, and a small smiling star badge at the front.
6. Cream cardigan or sweater body, beige vertical-striped bib collar, olive-green collar trim.
7. Navy pants and white shoes with small red/green decorative details.
8. Dominant palette: cream, warm beige, navy, soft skin tones, small red/green accents.
9. Clean illustrated edge quality. Final stickers, cover, and icon must use real transparency, not a baked checkerboard.

## Allowed Variations

- Facial expression changes: happy, crying, angry, surprised, shy, sleepy, pleading, apologizing, proud, curious.
- Hand gestures: waving, reaching for a hug, crossed hands, thumbs/fist up, covering mouth, rubbing eyes, holding a small object.
- Poses: seated, half-body close-up, slight lean, tiny jump, bowing, reaching forward.
- Small props: tissue, pillow, bowl, spoon, milk bottle, toy block, tiny flag, small heart.
- Simple emotion marks: tears, blush, sweat drop, sparkle, steam, bounce marks, small motion marks.
- Cropping/framing may vary as long as the star cap and face identity remain recognizable.

## Forbidden Variations

- Do not change 小布丁 into an animal, adult, different child, girl variant, robot, fantasy creature, or unrelated character.
- Do not remove or redesign the star cap, front star badge, large glossy eyes, or cream/navy outfit system.
- Do not change the dominant palette away from cream, beige, navy, and warm baby tones.
- Do not add extra characters unless explicitly approved.
- Do not add unapproved logos, copyrighted IP, brand marks, or personally sensitive content.
- Do not switch to photorealistic, anime-heavy, flat vector, pixel art, horror, dark, or sarcastic adult meme style.
- Do not let the image model generate final caption text. Captions must come from `spec.json` and be composed locally later.
- Do not use full scene backgrounds for stickers. Keep transparent sticker assets clean and focused.
- Do not include text in the final `banner.png`.

## Caption Style

- Language: Simplified Chinese.
- Source of truth: `spec.json` `captions.items`.
- Composition: deterministic local text composition for final captioned assets.
- Visual style: white fill, thick dark navy or dark brown outline, warm soft shadow.
- Placement: lower part of the sticker or beside the body when needed; never cover eyes, mouth, hands, or the main expression.
- Text length: short, readable at `240x240`.

## Planned Sticker Set

| # | Caption | Emotion case | Pose / prop direction |
|---|---|---|---|
| 01 | 嗨呀 | greeting | front-facing wave with bright eyes |
| 02 | 在吗 | curious check-in | peeking from behind a small door or toy blocks |
| 03 | 开心 | joy | big smile, raised hands, small bounce marks |
| 04 | 委屈 | grievance | teary eyes, pout, curled hands |
| 05 | 生气啦 | cute anger | puffed cheeks, tiny stomp, steam marks |
| 06 | 惊呆了 | surprise | wide eyes, open mouth, hands near cheeks |
| 07 | 哭哭 | crying | big tears, holding tissue |
| 08 | 要抱抱 | comfort seeking | arms reaching forward |
| 09 | 好的 | agreement | nodding, small OK gesture |
| 10 | 不要 | refusal | shaking head, crossed hands |
| 11 | 偷笑 | mischievous smile | covering mouth with one hand |
| 12 | 害羞 | shyness | rosy cheeks, looking sideways |
| 13 | 困困 | sleepiness | rubbing eyes, holding small pillow |
| 14 | 加油 | encouragement | tiny flag or small raised fist |
| 15 | 谢谢 | gratitude | small bow or holding a heart |
| 16 | 求求了 | pleading | hands together, sparkling eyes |
| 17 | 我错了 | apology | lowered head, remorseful expression |
| 18 | 开饭啦 | food excitement | holding small bowl and spoon |
| 19 | 拜拜 | farewell | waving goodbye with soft smile |

## Approval Gate

No final sticker sheets, cropped sticker PNGs, WeChat-size drafts, cover, icon, or banner should be generated until the user confirms this card and the master identity.
