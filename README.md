# Sticker Hub

本地化的微信表情包生产工作流：从一个想法，到一份可以直接提交到 [微信表情开放平台](https://sticker.weixin.qq.com) 的 18 张 240×240 PNG 上传包。

## 运行环境（重要）

**本项目目前只能在 Codex 客户端里跑通。**

整套流程强依赖 Codex 底层的 GPT 生图能力来产出母版形象和 18 张表情，仓库里没有自带可独立运行的生图脚本。也就是说：

- 你需要一个能用的 [Codex](https://chatgpt.com/codex) 账号和客户端。
- 不在 Codex 里启动，本仓库只是个目录骨架——`brief.md`、`spec.json`、`character-card.md` 这些文本能写，但出不了图。
- 后续如果接入其他生图后端，再单独说明；现阶段请默认按 Codex 流程操作。

## 30 秒上手

```bash
# 1. 克隆仓库
git clone <this-repo>
cd sticker-hub

# 2. 从模板复制一份新 pack（pack-id 用英文小写短横线命名）
cp -r production/packs/_template production/packs/<your-pack-id>
```

3. 打开一个**新的 Codex 窗口**，把 [`docs/start-new-pack-prompt.md`](docs/start-new-pack-prompt.md) 里的启动 prompt 整段粘贴进去，把 `<pack-id>`、名称、版权、角色描述等占位符填上。
4. Codex 会先初始化目录并生成母版角色卡（`master/character-card.md`）——**这一步你必须先确认母版形象，再让它继续**。
5. 母版确认后让 Codex 继续：生成两张 3×3 表情贴纸、加中文字幕、裁切到 240×240、导出到 `exports/wechat/`。

完整生产规范见 [AGENTS.md](AGENTS.md)，**任何疑问以 AGENTS.md 为准**。

## 仓库构成

克隆后你会拿到这些（不含任何真实历史 pack）：

```text
sticker-hub/
├── AGENTS.md                      # 生产规范，agent 必读
├── README.md                      # 本文
├── docs/
│   └── start-new-pack-prompt.md   # 启动新 pack 的 prompt 模板
├── production/packs/
│   └── _template/                 # 新 pack 的骨架，复制它
└── testdata/packs/
    └── sample-pack/               # workflow 验证用样例（非真实产物）
```

真实 pack 目录（你自己创建的 `production/packs/<pack-id>/`）**默认被 `.gitignore` 忽略**，不会进入版本控制。生图结果、审查图、上传包、参考图同理。仓库只发版可复用的骨架与规范。

## 运行结束后：最终产物在哪？

Codex 跑完整套流程后，**可以直接拿去上传的成品都在**：

```
production/packs/<your-pack-id>/exports/wechat/
```

打开这个目录，每个文件/子目录都对应你在 [微信表情开放平台](https://sticker.weixin.qq.com) 提交时的一个动作：

| 文件 / 目录 | 是什么 | 在平台上做什么用 |
| --- | --- | --- |
| `stickers/` | 18 张 240×240 PNG，透明背景，单张 ≤500KB | 平台「上传表情」处一次性上传这 18 张 |
| `cover.png` | 240×240 PNG，透明背景，≤500KB | 「封面」字段上传 |
| `icon.png` | 50×50 PNG，透明背景，≤100KB；干净的正面纯头部裁切，下巴完整露出，底部留透明 padding | 「图标」（聊天页图标）字段上传 |
| `banner.png` 或 `banner.jpg` | 750×400，不透明背景，无文字，≤500KB | 「详情页横幅」字段上传 |
| `form.md` | 纯文本清单：填好的「名称 / 介绍 / 版权」 | **照抄到平台表单**对应文本框，文件本身不上传 |
| `metadata.json` | 机器可读的提交清单（包名、类型、所有资产路径） | **不上传**，本地存档与校验用 |

打开 `form.md` 你会看到形如「名称：xxx / 介绍：xxx / 版权：xxx」的清单——它就是「填写基本信息」表单里三个文本框的内容来源，照抄即可。

> 完整字段约束（名称 ≤8 个汉字、介绍 ≤80 个汉字、版权 ≤10 个汉字、横幅不能有文字、icon 必须独立头部裁切等等）见 [AGENTS.md](AGENTS.md) 的 `WeChat Upload Contract` 一节。

## Pack 内部其它目录的作用

`exports/wechat/` 之外的目录都是**生产过程中的中间产物**，最终上传只看 `exports/wechat/`；但出问题时你可能要回这些目录查或重做：

- `brief.md` — 这次 pack 的简报（角色、画风、使用场景）。
- `spec.json` — pack 的工作流状态机（当前阶段、输入模式、目录映射）。
- `master/character-card.md` — 母版角色卡。**所有 18 张表情都要符合它**。
- `master/input/` — `image-to-master` 模式下你提供的原始母版图。
- `master/candidates/` — 母版候选形象。
- `master/approved/` — 你最终确认的母版形象。
- `source/references/` — 用户提供的参考图（风格、姿势、表情等）。
- `source/prompts/` — 实际生图用的 prompt 记录，方便复盘和迭代。
- `generated/sheets/raw/` — 未加字幕的 3×3 表情大图。
- `generated/sheets/captioned/` — 加好中文字幕的 3×3 大图。
- `generated/stickers/source-crops/` — 从 sheet 裁出的单张原图。
- `generated/stickers/wechat-draft/` — 裁切归一到 240×240 后的草稿单张。
- `review/master/` — 母版审查图（白底/格子底对比、放大检查等）。
- `review/sheets/` — sheet 阶段的审查图。
- `review/stickers/` — 单张表情的审查图。
- `review/wechat/` — 上传前最终自检报告（尺寸、透明、文件大小、规范）。

## 对结果不满意？如何让 Codex 重做单张

最常见的场景：18 张里有 2-3 张表情、或者 `icon.png` / `cover.png` 不满意，但你不想推倒重来。

**推荐做法**：在 Codex 对话里**用 `@` 引用想改的那个文件**，然后用自然语言说清楚问题和方向。Codex 会基于已确认的母版重新生成对应资产，而不是动其它已经过稿的图。

举几个例子：

```
@production/packs/<pack-id>/exports/wechat/stickers/07.png
这张「比心」动作里手指挡住了下巴，表情看不清；
请基于已确认的 master 重做，手保持在脸的左下方、不遮挡五官。
```

```
@production/packs/<pack-id>/exports/wechat/icon.png
下巴贴底了，看起来像被裁掉；
按 AGENTS.md 的 icon 规则重新从 master/approved/ 裁切，
底部至少留 6px 透明 padding。
```

```
@production/packs/<pack-id>/generated/sheets/captioned/sheet-2.png
第 5 格的字幕「emo 中」错排到了第 6 格；
请重排字幕位置，其它格保持不变。
```

几条要点：

- **不要让 Codex 改母版** —— 母版（`master/character-card.md` 和 `master/approved/`）一旦确认就是定型，单张返工只动单张。母版要改请单独说明并走一次新的母版确认。
- **改单张时明确"只动这一张"**，否则 Codex 可能会顺手把整张 sheet 重做一遍。
- **改完后让 Codex 重新跑一次 `review/wechat/` 自检**，确保新图仍满足尺寸、透明、文件大小等规范。
- **不满意的旧文件不要留在 `exports/wechat/`**，让 Codex 覆盖或移到 `review/stickers/rejected/` 之类的位置（AGENTS.md 明确禁止把废稿和成品混放）。

## 关键文件

- [AGENTS.md](AGENTS.md) — 完整生产规范，agent 工作的唯一真理源。
- [docs/start-new-pack-prompt.md](docs/start-new-pack-prompt.md) — 开新窗口时直接粘的启动 prompt。
- [production/packs/_template/](production/packs/_template/) — 新 pack 的目录骨架。

## 一条铁律

**母版角色卡（`master/character-card.md`）确认之前，绝对不要让 Codex 生成最终的 18 张表情。**
