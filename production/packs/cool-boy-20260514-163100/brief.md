# Pack Brief: 拽宝日常

## Status

- Environment: production
- Pack ID: `cool-boy-20260514-163100`
- Workflow phase: `master-character`
- Current gate: waiting for user approval of the master character card and master image direction
- Final sticker production: blocked until the master character card is approved

## Input Mode

- Selected: `image-to-master`
- Source image copied to:
  - `source/references/master-reference-original.png`
  - `master/input/master-reference-original.png`

## Concept

正式微信静态表情包。主题是一个活泼好动、表情拽拽的小男孩，适合聊天里的日常回应、调侃、催促、卖萌和收尾场景。

## Confirmed Form Copy

- 表情包名称: 拽宝日常
- 角色名: 拽宝
- 版权信息: 小拽工坊
- 简介候选: 活泼好动的小男孩，外表拽拽的，内心机灵又可爱。

名称、角色名和版权信息已由用户确认。正式提交前仍可按真实登记信息再调整版权字段。

## Character

一个 Q 版小男孩，头身比夸张，额头饱满，短黑刺发，大眼睛，眉毛微皱，脸颊圆润带淡红，常见表情是有点不服气、有点拽但不凶。

## Visual Direction

- 保留参考图里的 chibi 动漫贴纸风格。
- 保留黑色短刺发、大眼睛、圆脸、灰黑上衣、米色条纹围嘴、黑色裤子、白色鞋子的核心识别点。
- “微皱眉和轻抿嘴”只作为参考神态，不作为固定模板；每张表情应根据 caption 和动作设计自己的眉眼、嘴型和情绪。
- 最终贴纸应为透明背景 PNG，并避免把参考图里的浅灰背景或宽白色贴纸边直接带入最终 cover/icon。
- 文字由本地合成，使用简体中文短句，不能让模型随机改字。

## Planned Outputs

- 18 static sticker PNGs, `240x240`, transparent background
- `cover.png`, `240x240`, transparent background
- `icon.png`, `50x50`, transparent background
- `banner.png`, `750x400`, opaque background, no text
- `metadata.json`
- `form.md`
- Review contact sheets
- `review/wechat` validation report

## Review Notes

- Source image is a PNG reference with dimensions `1023x1537` and no alpha channel.
- Because the source has an opaque light background and a broad white sticker outline, it is not directly upload-ready for stickers, cover, or icon.
- Next step is user confirmation of the master character card. No final 18-sticker generation should start before that approval.
