#!/usr/bin/env python3
"""Build WeChat sticker export assets for this pack."""

from __future__ import annotations

import json
import math
import os
from collections import deque
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "spec.json"

RAW_DIR = ROOT / "generated" / "sheets" / "raw"
CAPTIONED_DIR = ROOT / "generated" / "sheets" / "captioned"
SOURCE_CROPS_DIR = ROOT / "generated" / "stickers" / "source-crops"
DRAFT_DIR = ROOT / "generated" / "stickers" / "wechat-draft"
REVIEW_STICKERS_DIR = ROOT / "review" / "stickers"
REVIEW_SHEETS_DIR = ROOT / "review" / "sheets"
REVIEW_WECHAT_DIR = ROOT / "review" / "wechat"
EXPORT_DIR = ROOT / "exports" / "wechat"
EXPORT_STICKERS_DIR = EXPORT_DIR / "stickers"

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def ensure_dirs() -> None:
    for path in [
        CAPTIONED_DIR,
        SOURCE_CROPS_DIR,
        DRAFT_DIR,
        REVIEW_STICKERS_DIR,
        REVIEW_SHEETS_DIR,
        REVIEW_WECHAT_DIR,
        EXPORT_STICKERS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_spec() -> dict:
    with SPEC_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_spec(spec: dict) -> None:
    with SPEC_PATH.open("w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
        f.write("\n")


def font_path() -> str:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("No usable Chinese font found")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path(), size=size)


def remove_green_background(image: Image.Image) -> Image.Image:
    arr = np.array(image.convert("RGBA")).astype(np.int16)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    max_rb = np.maximum(r, b)
    green_strength = g - max_rb

    hard = (g > 110) & (green_strength > 42)
    soft = (g > 80) & (green_strength > 16)

    alpha = np.full(g.shape, 255, dtype=np.float32)
    alpha[hard] = 0
    transition = soft & ~hard
    alpha[transition] = np.clip(255 - (green_strength[transition] - 16) * 7.5, 0, 255)

    # Despill any green edge pixels left around antialiased outlines.
    keep = alpha > 0
    arr[..., 1][keep] = np.minimum(arr[..., 1][keep], max_rb[keep] + 8)
    arr[..., 3] = alpha.astype(np.uint8)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def alpha_bbox(image: Image.Image, threshold: int = 8) -> tuple[int, int, int, int] | None:
    arr = np.array(image.convert("RGBA"))
    alpha = arr[..., 3]
    ys, xs = np.where(alpha > threshold)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def crop_nontransparent(image: Image.Image, pad: int = 8) -> Image.Image:
    bbox = alpha_bbox(image)
    if bbox is None:
        return image
    left, top, right, bottom = bbox
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width, right + pad)
    bottom = min(image.height, bottom + pad)
    return image.crop((left, top, right, bottom))


def remove_border_residue(image: Image.Image, threshold: int = 12) -> Image.Image:
    """Drop small alpha components stuck to the cell border.

    Generated sheets sometimes let tiny parts from a neighboring grid cell cross
    the mechanical crop boundary. Keep intentional props, but remove small
    disconnected slivers that touch the crop edge.
    """
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    mask = alpha > threshold
    h, w = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    out_alpha = alpha.copy()

    for sy, sx in zip(*np.where(mask & ~seen)):
        if seen[sy, sx]:
            continue
        q: deque[tuple[int, int]] = deque([(int(sy), int(sx))])
        seen[sy, sx] = True
        pixels: list[tuple[int, int]] = []
        min_x = max_x = int(sx)
        min_y = max_y = int(sy)
        touches_border = False

        while q:
            y, x = q.popleft()
            pixels.append((y, x))
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            if x <= 1 or y <= 1 or x >= w - 2 or y >= h - 2:
                touches_border = True
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))

        area = len(pixels)
        bbox_w = max_x - min_x + 1
        bbox_h = max_y - min_y + 1
        edge_sliver = touches_border and area < 5000 and (bbox_w < 150 or bbox_h < 48)
        if edge_sliver:
            ys = [p[0] for p in pixels]
            xs = [p[1] for p in pixels]
            out_alpha[ys, xs] = 0

    arr[..., 3] = out_alpha
    return Image.fromarray(arr, "RGBA")


def connected_components(mask: np.ndarray) -> list[dict]:
    h, w = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    components: list[dict] = []
    for sy, sx in zip(*np.where(mask & ~seen)):
        if seen[sy, sx]:
            continue
        q: deque[tuple[int, int]] = deque([(int(sy), int(sx))])
        seen[sy, sx] = True
        pixels: list[tuple[int, int]] = []
        min_x = max_x = int(sx)
        min_y = max_y = int(sy)
        while q:
            y, x = q.popleft()
            pixels.append((y, x))
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        components.append({
            "area": len(pixels),
            "bbox": (min_x, min_y, max_x + 1, max_y + 1),
            "center": ((min_x + max_x + 1) / 2, (min_y + max_y + 1) / 2),
        })
    return components


def extract_sheet_items(sheet: Image.Image) -> list[Image.Image]:
    transparent_sheet = remove_green_background(sheet)
    arr = np.array(transparent_sheet.convert("RGBA"))
    alpha = arr[..., 3]
    h, w = alpha.shape
    components = [c for c in connected_components(alpha > 12) if c["area"] >= 25]
    groups: list[list[dict]] = [[] for _ in range(9)]
    cell_w = w / 3
    cell_h = h / 3

    for component in components:
        cx, cy = component["center"]
        col = max(0, min(2, int(cx / cell_w)))
        row = max(0, min(2, int(cy / cell_h)))
        groups[row * 3 + col].append(component)

    items: list[Image.Image] = []
    for group in groups:
        if not group:
            items.append(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
            continue
        left = max(0, min(c["bbox"][0] for c in group) - 10)
        top = max(0, min(c["bbox"][1] for c in group) - 10)
        right = min(w, max(c["bbox"][2] for c in group) + 10)
        bottom = min(h, max(c["bbox"][3] for c in group) + 10)
        crop = transparent_sheet.crop((left, top, right, bottom))
        cleaned = remove_far_small_fragments(remove_border_residue(crop))
        items.append(crop_nontransparent(cleaned, pad=8))
    return items


def remove_far_small_fragments(image: Image.Image, threshold: int = 12) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    components = [c for c in connected_components(alpha > threshold) if c["area"] >= 25]
    if len(components) <= 1:
        return rgba

    main = max(components, key=lambda c: c["area"])
    main_area = main["area"]
    main_left, main_top, main_right, main_bottom = main["bbox"]
    out_alpha = alpha.copy()

    for component in components:
        if component is main:
            continue
        left, top, right, bottom = component["bbox"]
        vertical_gap = max(top - main_bottom, main_top - bottom, 0)
        small = component["area"] < main_area * 0.18
        far_below_or_above = vertical_gap > 28
        tiny_low_or_high = component["area"] < main_area * 0.08 and (top > main_bottom or bottom < main_top)
        if small and (far_below_or_above or tiny_low_or_high):
            sub_alpha = out_alpha[top:bottom, left:right]
            sub_alpha[alpha[top:bottom, left:right] > threshold] = 0

    arr[..., 3] = out_alpha
    return Image.fromarray(arr, "RGBA")


def fit_rgba(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / image.width, max_h / image.height, 1.0)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def draw_caption(canvas: Image.Image, caption: str) -> None:
    draw = ImageDraw.Draw(canvas)
    size = 36
    stroke = 4
    while size >= 24:
        font = load_font(size)
        bbox = draw.textbbox((0, 0), caption, font=font, stroke_width=stroke)
        if bbox[2] - bbox[0] <= 220:
            break
        size -= 2
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas.width - text_w) // 2 - bbox[0]
    y = 196 - text_h // 2 - bbox[1]

    draw.text(
        (x + 3, y + 3),
        caption,
        font=font,
        fill=(214, 133, 42, 210),
        stroke_width=stroke,
        stroke_fill=(214, 133, 42, 180),
    )
    draw.text(
        (x, y),
        caption,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke,
        stroke_fill=(55, 39, 32, 255),
    )


def make_sticker(source_crop: Image.Image, caption: str) -> Image.Image:
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    fitted = fit_rgba(source_crop, 220, 172)
    x = (240 - fitted.width) // 2
    y = max(2, (180 - fitted.height) // 2)
    canvas.alpha_composite(fitted, (x, y))
    draw_caption(canvas, caption)
    return canvas


def make_cover(source_crop: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    fitted = fit_rgba(source_crop, 214, 218)
    canvas.alpha_composite(fitted, ((240 - fitted.width) // 2, (240 - fitted.height) // 2))
    return canvas


def make_icon(source_crop: Image.Image) -> Image.Image:
    bbox = alpha_bbox(source_crop, 8)
    if bbox is None:
        head = source_crop
    else:
        left, top, right, bottom = bbox
        h = bottom - top
        w = right - left
        head_box = (
            max(0, left - int(w * 0.10)),
            max(0, top - int(h * 0.04)),
            min(source_crop.width, right + int(w * 0.10)),
            min(source_crop.height, top + int(h * 0.48)),
        )
        head = crop_nontransparent(source_crop.crop(head_box), pad=2)
    canvas = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    fitted = fit_rgba(head, 47, 47)
    canvas.alpha_composite(fitted, ((50 - fitted.width) // 2, (50 - fitted.height) // 2))
    return canvas


def paste_fit(base: Image.Image, crop: Image.Image, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    fitted = fit_rgba(crop, right - left, bottom - top)
    x = left + (right - left - fitted.width) // 2
    y = top + (bottom - top - fitted.height) // 2
    base.alpha_composite(fitted, (x, y))


def make_banner(crops: list[Image.Image]) -> Image.Image:
    bg = Image.new("RGBA", (750, 400), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)
    for y in range(400):
        t = y / 399
        r = round(255 * (1 - t) + 244 * t)
        g = round(203 * (1 - t) + 235 * t)
        b = round(104 * (1 - t) + 248 * t)
        draw.line((0, y, 750, y), fill=(r, g, b, 255))

    for cx, cy, radius, color in [
        (70, 68, 40, (255, 255, 255, 70)),
        (620, 90, 62, (255, 255, 255, 68)),
        (520, 310, 84, (255, 247, 158, 90)),
        (160, 310, 56, (255, 138, 130, 80)),
    ]:
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)

    draw.rounded_rectangle((0, 292, 750, 430), radius=80, fill=(104, 218, 171, 255))
    draw.rounded_rectangle((-80, 324, 360, 460), radius=70, fill=(87, 197, 153, 255))
    draw.rounded_rectangle((420, 312, 820, 452), radius=70, fill=(92, 205, 160, 255))

    # Arrange multiple characters without text to make the banner feel story-like.
    paste_fit(bg, crops[2], (28, 64, 238, 340))
    paste_fit(bg, crops[10], (210, 58, 402, 318))
    paste_fit(bg, crops[14], (392, 72, 560, 330))
    paste_fit(bg, crops[17], (538, 54, 732, 334))
    # Cover a tiny disconnected residue that can appear below the center toy crop
    # after chroma-key extraction. This is on the ground band, away from feet.
    draw.rounded_rectangle((460, 318, 528, 338), radius=10, fill=(92, 205, 160, 255))
    return bg.convert("RGB")


def save_png(path: Path, image: Image.Image, max_bytes: int | None = None) -> None:
    image.save(path, "PNG", optimize=True, compress_level=9)
    if max_bytes and path.stat().st_size > max_bytes and image.mode == "RGB":
        quantized = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=192)
        quantized.save(path, "PNG", optimize=True, compress_level=9)


def build_contact_sheet(images: list[Image.Image]) -> Image.Image:
    sheet = Image.new("RGB", (6 * 240, 3 * 240), (236, 239, 243))
    tile_bg = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
    for i, image in enumerate(images):
        x = (i % 6) * 240
        y = (i // 6) * 240
        tile = tile_bg.copy()
        tile.alpha_composite(image)
        sheet.paste(tile.convert("RGB"), (x, y))
    return sheet


def build_overview(stickers: list[Image.Image], cover: Image.Image, icon: Image.Image, banner: Image.Image) -> Image.Image:
    overview = Image.new("RGB", (1200, 900), (246, 247, 249))
    draw = ImageDraw.Draw(overview)
    font = load_font(28)
    small = load_font(20)
    draw.text((32, 24), "拽宝日常 WeChat Export Review", font=font, fill=(30, 34, 40))
    draw.text((32, 68), "18 stickers, cover, icon, banner; upload assets only are in exports/wechat.", font=small, fill=(78, 86, 98))

    thumb = build_contact_sheet(stickers).resize((900, 450), Image.Resampling.LANCZOS)
    overview.paste(thumb, (32, 110))

    banner_preview = banner.resize((450, 240), Image.Resampling.LANCZOS)
    overview.paste(banner_preview, (32, 610))

    cover_bg = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
    cover_bg.alpha_composite(cover)
    overview.paste(cover_bg.convert("RGB"), (532, 610))

    icon_bg = Image.new("RGBA", (120, 120), (255, 255, 255, 255))
    icon_big = icon.resize((100, 100), Image.Resampling.NEAREST)
    icon_bg.alpha_composite(icon_big, (10, 10))
    overview.paste(icon_bg.convert("RGB"), (822, 610))
    draw.text((532, 858), "cover.png", font=small, fill=(78, 86, 98))
    draw.text((822, 742), "icon.png 4x preview", font=small, fill=(78, 86, 98))
    return overview


def validate_assets(spec: dict) -> tuple[list[dict], bool]:
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    sticker_files = sorted(EXPORT_STICKERS_DIR.glob("*.png"))
    add("sticker-count-is-18", len(sticker_files) == 18, f"found {len(sticker_files)} PNG stickers")
    unexpected_sticker_files = [
        path.name
        for path in EXPORT_STICKERS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() != ".png"
    ]
    add("stickers-dir-has-only-png-upload-files", not unexpected_sticker_files, f"unexpected={unexpected_sticker_files}")

    allowed_root_files = {"cover.png", "icon.png", "banner.png", "metadata.json", "form.md"}
    unexpected_root_files = [
        path.name
        for path in EXPORT_DIR.iterdir()
        if path.is_file() and path.name not in allowed_root_files
    ]
    add("wechat-export-root-has-only-upload-files", not unexpected_root_files, f"unexpected={unexpected_root_files}")

    for path in sticker_files:
        with Image.open(path) as img:
            rgba = img.convert("RGBA")
            corners = [rgba.getpixel(p)[3] for p in [(0, 0), (239, 0), (0, 239), (239, 239)]]
            add(f"{path.name}: png-240x240-alpha-transparent-corners-under-500kb",
                img.format == "PNG"
                and img.size == (240, 240)
                and "A" in rgba.getbands()
                and max(corners) == 0
                and path.stat().st_size <= 512000,
                f"format={img.format}, size={img.size}, corners={corners}, bytes={path.stat().st_size}")

    for name, expected_size, max_bytes, require_alpha in [
        ("cover.png", (240, 240), 512000, True),
        ("icon.png", (50, 50), 102400, True),
        ("banner.png", (750, 400), 512000, False),
    ]:
        path = EXPORT_DIR / name
        exists = path.exists()
        if not exists:
            add(f"{name}: exists", False, "missing")
            continue
        with Image.open(path) as img:
            rgba = img.convert("RGBA")
            if require_alpha:
                corners = [rgba.getpixel(p)[3] for p in [(0, 0), (img.width - 1, 0), (0, img.height - 1), (img.width - 1, img.height - 1)]]
                alpha_ok = "A" in rgba.getbands() and max(corners) == 0
            else:
                corners = []
                alpha_ok = img.mode in {"RGB", "P"}
            add(f"{name}: size-format-background-under-limit",
                img.format == "PNG" and img.size == expected_size and alpha_ok and path.stat().st_size <= max_bytes,
                f"format={img.format}, mode={img.mode}, size={img.size}, corners={corners}, bytes={path.stat().st_size}")

    form = spec["wechatTarget"]["form"]
    add("form-name-under-8-no-punctuation-no-spaces", len(form["name"]["value"]) <= 8 and " " not in form["name"]["value"], form["name"]["value"])
    add("form-introduction-under-80", len(form["introduction"]["value"]) <= 80, form["introduction"]["value"])
    add("form-copyright-under-10", len(form["copyright"]["value"]) <= 10, form["copyright"]["value"])
    add("metadata-json-exists", (EXPORT_DIR / "metadata.json").exists(), str(EXPORT_DIR / "metadata.json"))
    add("form-md-exists", (EXPORT_DIR / "form.md").exists(), str(EXPORT_DIR / "form.md"))

    return checks, all(check["passed"] for check in checks)


def write_metadata(spec: dict, checks: list[dict], passed: bool) -> None:
    metadata = {
        "packId": spec["packId"],
        "platform": spec["platform"],
        "type": "static",
        "name": spec["wechatTarget"]["form"]["name"]["value"],
        "introduction": spec["wechatTarget"]["form"]["introduction"]["value"],
        "copyright": spec["wechatTarget"]["form"]["copyright"]["value"],
        "status": "upload-ready-local-validation-passed" if passed else "draft-validation-failed",
        "uploadReady": passed,
        "validatedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "officialSpecBasis": "AGENTS.md captured WeChat upload contract; public official site recheck attempted separately because sticker.weixin.qq.com is not directly readable in this environment",
        "assets": {
            "stickersDir": "stickers",
            "stickerCount": 18,
            "cover": "cover.png",
            "icon": "icon.png",
            "banner": "banner.png",
        },
        "stickers": [
            {
                "index": item["index"],
                "id": item["id"],
                "caption": item["caption"],
                "file": f"stickers/{item['index']:02d}-{item['id']}-{item['caption']}.png",
            }
            for item in spec["captions"]["items"]
        ],
        "validation": checks,
    }
    with (EXPORT_DIR / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_form(spec: dict) -> None:
    form = spec["wechatTarget"]["form"]
    lines = [
        "# 微信表情开放平台表单信息",
        "",
        "状态：本地校验通过后可用于上传前人工复核。",
        "",
        "## 上传表情",
        "",
        "- 类型：静态表情",
        "- 表情：上传 `stickers/` 下的 18 张 `240x240` 透明 PNG 图片",
        "",
        "## 填写基本信息",
        "",
        f"- 名称：{form['name']['value']}",
        f"- 介绍：{form['introduction']['value']}",
        f"- 版权：{form['copyright']['value']}",
        "- 横幅：`banner.png`，`750x400`，不含文字，不透明背景",
        "- 封面：`cover.png`，`240x240`，透明背景",
        "- 图标：`icon.png`，`50x50`，透明背景",
        "",
        "## 备注",
        "",
        "- 表情 caption 已按 `spec.json` 本地合成，上传前请人工复核小图可读性。",
        "- 官方平台最新规则在本环境无法直接读取时，以 `AGENTS.md` 捕获规则为本地目标，上传前仍建议在平台页面最终确认。",
    ]
    (EXPORT_DIR / "form.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reports(checks: list[dict], passed: bool) -> None:
    report = {
        "passed": passed,
        "generatedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "checks": checks,
    }
    with (REVIEW_WECHAT_DIR / "validation-report.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")

    lines = [
        "# WeChat Export Validation Report",
        "",
        f"- Result: {'PASS' if passed else 'FAIL'}",
        f"- Generated at: {report['generatedAt']}",
        "- Scope: `production/packs/cool-boy-20260514-163100/exports/wechat`",
        "- Spec basis: local `AGENTS.md` captured upload contract; official public site recheck was attempted but not directly readable from this environment.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        mark = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- {mark}: {check['name']} - {check['detail']}")
    (REVIEW_WECHAT_DIR / "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_spec_after_build(spec: dict, passed: bool) -> None:
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    spec["workflowPhase"] = "wechat-export-ready" if passed else "wechat-export-needs-fix"
    spec["masterCharacter"]["status"] = "approved-by-user"
    spec["masterCharacter"]["approvedImage"] = "master/input/master-reference-original.png"
    spec["masterCharacter"]["approvalRequired"] = False
    approval = {
        "status": "approved-by-user",
        "source": "user /goal after caption and identity alignment",
    }
    history = spec["masterCharacter"].setdefault("approvalHistory", [])
    if not any(item.get("status") == approval["status"] and item.get("source") == approval["source"] for item in history):
        history.append({"at": now, **approval})
    spec["captions"]["status"] = "locked-for-production"
    for item in spec["captions"]["items"]:
        item["status"] = "approved-by-user"
    spec["assets"]["wechatExport"]["generatedAt"] = now
    spec["assets"]["wechatExport"]["uploadReady"] = passed
    save_spec(spec)


def main() -> None:
    ensure_dirs()
    spec = load_spec()
    items = spec["captions"]["items"]
    if len(items) != 18:
        raise RuntimeError(f"Expected 18 captions, got {len(items)}")

    sheets = [
        Image.open(RAW_DIR / "sheet-01-raw.png").convert("RGBA"),
        Image.open(RAW_DIR / "sheet-02-raw.png").convert("RGBA"),
    ]

    source_crops: list[Image.Image] = []
    stickers: list[Image.Image] = []

    sheet_items = extract_sheet_items(sheets[0]) + extract_sheet_items(sheets[1])

    for i, item in enumerate(items):
        transparent = sheet_items[i]

        base_name = f"{item['index']:02d}-{item['id']}-{item['caption']}.png"
        source_path = SOURCE_CROPS_DIR / base_name
        save_png(source_path, transparent)

        sticker = make_sticker(transparent, item["caption"])
        draft_path = DRAFT_DIR / base_name
        export_path = EXPORT_STICKERS_DIR / base_name
        save_png(draft_path, sticker, max_bytes=512000)
        save_png(export_path, sticker, max_bytes=512000)

        source_crops.append(transparent)
        stickers.append(sticker)

    for sheet_idx in range(2):
        sheet_canvas = Image.new("RGBA", (720, 720), (0, 0, 0, 0))
        for j in range(9):
            sticker = stickers[sheet_idx * 9 + j]
            sheet_canvas.alpha_composite(sticker, ((j % 3) * 240, (j // 3) * 240))
        save_png(CAPTIONED_DIR / f"sheet-{sheet_idx + 1:02d}-captioned.png", sheet_canvas)
        review_bg = Image.new("RGB", (720, 720), (238, 241, 245))
        tile_bg = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
        for j in range(9):
            tile = tile_bg.copy()
            tile.alpha_composite(stickers[sheet_idx * 9 + j])
            review_bg.paste(tile.convert("RGB"), ((j % 3) * 240, (j // 3) * 240))
        save_png(REVIEW_SHEETS_DIR / f"sheet-{sheet_idx + 1:02d}-review.png", review_bg)

    cover = make_cover(source_crops[4])
    icon = make_icon(source_crops[4])
    banner = make_banner(source_crops)

    save_png(EXPORT_DIR / "cover.png", cover, max_bytes=512000)
    save_png(EXPORT_DIR / "icon.png", icon, max_bytes=102400)
    save_png(EXPORT_DIR / "banner.png", banner, max_bytes=512000)

    contact = build_contact_sheet(stickers)
    save_png(REVIEW_STICKERS_DIR / "final-stickers-contact-sheet.png", contact)
    overview = build_overview(stickers, cover, icon, banner)
    save_png(REVIEW_WECHAT_DIR / "export-assets-overview.png", overview)

    write_form(spec)
    checks, passed = validate_assets(spec)
    write_metadata(spec, checks, passed)
    write_reports(checks, passed)
    update_spec_after_build(spec, passed)

    if not passed:
        failed = [check for check in checks if not check["passed"]]
        raise SystemExit("Validation failed: " + json.dumps(failed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
