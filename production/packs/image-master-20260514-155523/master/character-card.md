# Master Character Card

## Status

Approved for asset production.

The user confirmed production should begin and every generated character image must retain the `COS` text.

## Input Mode

`image-to-master`

## Source Material

- Original local path: `/Users/yinshawnrao/Desktop/cos-ip.png`
- Pack reference copy: `source/references/cos-ip-reference.png`
- Master input copy: `master/input/cos-ip-master-reference.png`
- Approved master image: `master/approved/cos-ip-approved-master.png`

Source image facts:

- PNG
- `512x512`
- RGBA
- `320692` bytes

## Character

- Draft name: 云朵同事
- Personality: friendly, reliable, upbeat, collaborative, clean and professional.
- Visual style: 2D chibi line-art mascot sticker, thick dark outline, rounded forms, bright blue and white palette, cute office companion.

## Theme Direction

互联网大厂日常工作氛围，但不是加班黑话主题。

The pack should feel positive, normal, and collaborative: morning greetings, receiving tasks, syncing updates, checking details, confirming progress, documenting, meeting, reviewing, launching, delivering, thanking teammates, and ending the day in a good mood.

Avoid making the character look exhausted, bitter, overworked, or trapped in overtime. Keep humor light and daily-life friendly.

## Identity Preservation Rule

The provided master/reference image is the source of truth. Downstream generation must preserve the character identity before optimizing style, expression, pose, or sticker readability.

## Locked Traits

- White cloud-shaped mascot body.
- Soft rounded fluffy cloud silhouette, with larger top cloud lobes and smaller side lobes.
- Closed smiling crescent eyes.
- Small curved smiling mouth.
- Round pink cheek blush on both sides.
- Bright blue rounded arms.
- Small rounded white feet.
- Bright blue file folder held in front of the body.
- Folder contains light yellow/white document tabs.
- Clean 2D chibi line-art sticker rendering, with a thick dark outline and simple flat fills.
- Gentle blue edge shading on the cloud body.
- Friendly sparkle accents are allowed as mood cues.

## COS Text Requirement

The source image includes visible `COS` text on the folder.

Production constraint confirmed by user:

- Every character image must retain the `COS` text.
- Do not remove, replace, blur, crop out, or obscure the `COS` text.
- Keep `COS` legible on the blue folder whenever the folder is visible.
- Do not introduce any additional unapproved logos, trademarks, real company names, copyrighted IP, or personally sensitive content.

## Allowed Variations

- Facial expression within the same cute cloud identity.
- Pose and hand gesture.
- Folder angle or document contents when needed.
- Simple workday props related to the caption: laptop, checklist, calendar, document, coffee cup, small chart, upload arrow, note card, progress dots.
- Small scene cues that do not change character identity.
- Small positive sparkle or motion marks.

## Forbidden Variations

- Changing the cloud mascot into a human, animal, robot, or different species.
- Changing the dominant white-and-blue color identity without approval.
- Changing face shape, eye style, blush style, body shape, or signature folder without approval.
- Adding unrelated characters.
- Changing the approved 2D chibi line-art sticker rendering style.
- Turning the pack into a dark overtime, complaint, or exhausted-worker theme.
- Adding unapproved logos, trademarks, copyrighted IP, or personally sensitive content.
- Letting image generation invent, rewrite, or misspell production captions.

## Caption Style

- Language: Simplified Chinese.
- Exact captions must come from `spec.json` or another explicit config.
- Prefer local text composition for final captions.
- Default style: white fill, thick dark blue outline, warm yellow accent shadow.
- Placement should avoid covering eyes, mouth, hands, and the main expression.

## Planned Sticker Set

Draft captions and poses for confirmation:

1. 早呀: cheerful wave beside the blue folder with small sunrise sparkle.
2. 收到: holding folder close with a confident nod.
3. 马上同步: sending small document icons from the folder.
4. 我来看看: leaning over a checklist with focused smile.
5. 已确认: showing a clean checkmark card.
6. 很棒: thumbs up with bright sparkle accents.
7. 谢谢支持: slight bow while holding the folder.
8. 一起加油: raising both rounded hands with energetic smile.
9. 有想法了: small lightbulb sparkle above the cloud head.
10. 安排上啦: placing a task card into the blue folder.
11. 稳步推进: walking forward with folder and small progress dots.
12. 准备上线: holding a small upload arrow with happy focus.
13. 复盘一下: pointing at a simple chart board with calm smile.
14. 文档齐啦: folder opened with neatly stacked documents.
15. 开会啦: holding a tiny calendar card and waving.
16. 准时交付: presenting a completed package with checkmark.
17. 搞定: happy jump with folder and small stars.
18. 下班快乐: relaxed wave with sunset-colored sparkle, still positive and clean.

## Approval Gate

- [x] Source/reference image is stored in the pack directory.
- [x] Character identity traits are drafted in this card.
- [x] Allowed and forbidden variations are drafted.
- [x] Planned captions and poses are drafted.
- [x] User confirms final assets must retain `COS` folder text.
- [x] User approves this card for asset production.
- [x] Approved master image is stored at `master/approved/cos-ip-approved-master.png`.
