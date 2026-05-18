# New Pack Startup Prompt

Use this prompt when opening a new Codex window for a production sticker pack.

```text
请严格按当前仓库的 AGENTS.md 生产规范启动一个新的微信表情包项目。

这是正式环境，不是 testdata。请只在 production/packs/<pack-id>/ 下工作，不要改其他 pack 目录。

Pack ID：<填写英文小写短横线命名，例如 cute-cat-001>
输入模式：<text-to-master 或 image-to-master>
表情包名称候选：<不超过 8 个汉字，最好 5 个以内，无标点、无空格>
版权信息：<不超过 10 个汉字，例如 工作室名/设计师名>
角色/主题描述：<如果是 text-to-master，在这里写角色设定、画风、性格、使用场景>
母版图片：<如果是 image-to-master，我会上传或提供图片路径；请先放入 source/references/ 和 master/input/>

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

## Minimal Version

```text
按 AGENTS.md 正式生产规范启动一个新微信表情包。只操作 production/packs/<pack-id>/。输入模式是 <text-to-master/image-to-master>。先初始化目录、brief.md、spec.json、master/character-card.md，并停在母版卡确认阶段；不要直接生成 18 张最终表情。
```
