# Generation Record

## Pack

- Pack ID: `text-master-20260514-154416`
- Character: 卷卷码农
- Mode: `text-to-master`
- Date: 2026-05-14
- Image generation path: built-in Codex `image_gen`
- Local post-processing runtime: bundled Python at `/Users/yinshawnrao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`
- Local post-processing script: `source/prompts/process_wechat_assets.py`

## Generated Source Images

- Master chroma source copied from Codex generated image storage to `master/candidates/master-reference-chroma.png`
- Transparent approved master: `master/approved/master-reference.png`
- Raw sheet 1 chroma source: `generated/sheets/raw/sheet-01-chroma.png`
- Raw sheet 2 chroma source: `generated/sheets/raw/sheet-02-chroma.png`

## Master Prompt Summary

Create a single full-body clean anime sticker character named 卷卷码农: a long-overtime programmer with messy black hair, mild under-eye shadows, expressive dark eyes, dark hoodie with muted tech-blue accents, warm skin tone, blank ID badge, laptop, and coffee cup. Use a flat #00ff00 chroma-key background, no text, no logo, no company name, no trademarked IP.

## Sheet Prompt Summary

Create two square 3x3 raw sticker sheets of the same character, no text, no logos, no company names, flat #00ff00 chroma-key background. Each cell contains one pose mapped to the 18 confirmed captions:

1. 先对齐下
2. 拉个群吧
3. 需求变更
4. 排期爆了
5. 今晚发版
6. 还在联调
7. 灰度一下
8. 快速闭环
9. 风险可控
10. 底层逻辑
11. 颗粒度粗
12. 这个抓手
13. 赋能一下
14. 沉淀文档
15. 数据说话
16. 周报已写
17. 再压测下
18. 先跑起来

## Local Processing

The local script performs:

- Chroma-key removal to real alpha transparency.
- 3x3 grid extraction with alpha-component filtering to remove neighboring-cell residue.
- Source crop export under `generated/stickers/source-crops/`.
- Deterministic Simplified Chinese caption composition.
- 240x240 WeChat draft/export PNG creation.
- Cover, icon, and no-text opaque banner generation.
- Review contact sheet and export overview generation.
- Validation report generation under `review/wechat/validation-report.json`.
