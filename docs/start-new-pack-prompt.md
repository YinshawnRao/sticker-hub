# 新 Pack 启动 Prompt

每次在 Codex 里启动一个新的微信表情包项目时，把下面的 Prompt 粘贴进去并填好占位符。

## 字段说明

只有 **输入模式** 和 **角色/主题描述** 是必填的。其他字段不想自己定时，直接写 `自动生成`，Codex 会基于主题与日期帮你产出。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| **Pack ID** | 否（可填 `自动生成`） | 这次 pack 的目录名，对应 `production/packs/<pack-id>/`。建议英文小写 + 短横线，并带日期或编号，例如 `cute-cat-20260521`。填 `自动生成` 时 Codex 会按主题 + 当前日期帮你起。 |
| **输入模式** | ✅ 是 | 决定母版角色从哪来：<br>• `text-to-master`：纯文本描述生成母版形象。<br>• `image-to-master`：由你提供一张参考图，再派生母版。 |
| **表情包名称候选** | 否（可填 `自动生成`） | 最终展示在微信表情开放平台上的包名。规则：不超过 8 个汉字（建议 ≤5），不能含标点和空格。填 `自动生成` 时 Codex 会给若干候选让你挑。 |
| **版权信息** | 否（可填 `自动生成`） | 详情页底部的署名，不超过 10 个汉字。一般是工作室名或设计师名。没明确归属就填 `自动生成`。 |
| **角色/主题描述** | ✅ 是 | 母版形象的灵魂。建议覆盖四块：角色设定（是谁／什么动物／什么物件）、画风（手绘 / 像素 / 3D / 二次元 等）、性格基调（呆萌 / 嘴贱 / 温柔 等）、使用场景（日常聊天 / 职场 / 恋爱 等）。`image-to-master` 模式也建议补一句风格说明，帮 Codex 提炼。 |
| **母版图片** | 仅 `image-to-master` 必填 | 你要参考的母版图。先把文件放到 `production/packs/<pack-id>/source/references/` 和 `master/input/`，再在 prompt 里给出路径或说明已上传。`text-to-master` 模式可填 `不适用` 或留空。 |

## 完整 Prompt（粘贴这一段）

```text
请严格按当前仓库的 AGENTS.md 生产规范启动一个新的微信表情包项目。

这是正式环境，不是 testdata。请只在 production/packs/<pack-id>/ 下工作，不要改其他 pack 目录。

Pack ID：<英文小写短横线命名，例如 cute-cat-20260521；或填"自动生成">
输入模式：<text-to-master 或 image-to-master>  ← 必填
表情包名称候选：<不超过 8 个汉字，最好 5 个以内，无标点、无空格；或填"自动生成">
版权信息：<不超过 10 个汉字，例如 工作室名/设计师名；或填"自动生成">
角色/主题描述：<必填。写角色设定、画风、性格、使用场景。image-to-master 模式也建议补一句风格说明>
母版图片：<仅 image-to-master 模式必填。我会上传或提供图片路径；请先放入 source/references/ 和 master/input/。text-to-master 模式填"不适用">

工作要求：
1. 先初始化 production/packs/<pack-id>/ 的目录、brief.md、spec.json、master/character-card.md。
2. 先进入 master-character 阶段，提炼或生成母版卡。
3. 在我确认母版卡和母版形象之前，不要生成最终 18 张表情。
4. 正式产物必须符合微信表情开放平台规范：18 张 240x240 PNG 静态表情、cover.png、icon.png、banner.png、metadata.json、form.md、review/wechat 校验报告。
   - `icon.png` 必须单独做成正面完整头部图：完整露出下巴/下脸轮廓，底部留清晰透明像素，不要包含身体、手势、文字、动作装饰或道具。
5. 中间产物、审查图、最终上传包必须放到各自目录，不要混放。
6. 如果发现名称、尺寸、透明背景、文件大小、版权文案、横幅文字等不符合规范，必须先指出并修正。

请先读取 AGENTS.md，然后给我本次 pack 的初始化结果和下一步需要我确认的母版卡内容。
```

## 极简版

懒得填长 prompt 时用这个，所有可自动生成的字段都不写，Codex 会按默认策略补齐：

```text
按 AGENTS.md 正式生产规范启动一个新微信表情包。只操作 production/packs/<pack-id>/。

输入模式：<text-to-master 或 image-to-master>
角色/主题描述：<必填。写角色设定、画风、性格、使用场景>

其余字段（Pack ID、表情包名称、版权信息）走自动生成。先初始化目录、brief.md、spec.json、master/character-card.md，停在母版卡确认阶段；不要直接生成 18 张最终表情。
```
