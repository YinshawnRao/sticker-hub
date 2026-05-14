from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PACK_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = PACK_ROOT / "spec.json"
FONT_PATH = Path("/System/Library/Fonts/STHeiti Medium.ttc")
SONGTI_FONT_PATH = Path("/System/Library/Fonts/Supplemental/Songti.ttc")
CAPTION_RENDER_OVERRIDES = {
    "嘴硬": {
        "font_path": SONGTI_FONT_PATH,
        "font_size": 44,
        "stroke_width": 3,
        "tracking": 4,
    },
}


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def ensure_dirs() -> None:
    for rel in [
        "generated/stickers/source-crops",
        "generated/stickers/wechat-draft",
        "generated/sheets/captioned",
        "review/master",
        "review/sheets",
        "review/stickers",
        "review/wechat",
        "exports/wechat/stickers",
    ]:
        (PACK_ROOT / rel).mkdir(parents=True, exist_ok=True)


def font(size: int, path: Path = FONT_PATH) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def save_png(im: Image.Image, path: Path, *, palette: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if palette:
        rgb = im.convert("RGB")
        rgb = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT).convert("RGB")
        rgb.save(path, optimize=True, compress_level=9)
    else:
        im.save(path, optimize=True, compress_level=9)


def green_background_mask(im: Image.Image) -> np.ndarray:
    arr = np.array(im.convert("RGBA"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    keyish = (g > 130) & ((g - r) > 45) & ((g - b) > 45)

    visited = np.zeros(keyish.shape, dtype=bool)
    visited[0, :] = keyish[0, :]
    visited[-1, :] = keyish[-1, :]
    visited[:, 0] = keyish[:, 0]
    visited[:, -1] = keyish[:, -1]

    while True:
        nbr = np.zeros_like(visited)
        nbr[1:, :] |= visited[:-1, :]
        nbr[:-1, :] |= visited[1:, :]
        nbr[:, 1:] |= visited[:, :-1]
        nbr[:, :-1] |= visited[:, 1:]
        new = keyish & nbr & ~visited
        if not new.any():
            break
        visited |= new

    near_key = (g > 105) & ((g - r) > 30) & ((g - b) > 30)
    expanded = visited.copy()
    for _ in range(2):
        nbr = np.zeros_like(expanded)
        nbr[1:, :] |= expanded[:-1, :]
        nbr[:-1, :] |= expanded[1:, :]
        nbr[:, 1:] |= expanded[:, :-1]
        nbr[:, :-1] |= expanded[:, 1:]
        expanded |= near_key & nbr

    return expanded


def remove_green(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    mask = green_background_mask(rgba)
    arr[mask, 3] = 0

    alpha = arr[:, :, 3] > 0
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    fringe = alpha & (g > 120) & ((g - r) > 25) & ((g - b) > 25)
    arr[fringe, 1] = np.minimum(np.maximum(arr[fringe, 0], arr[fringe, 2]) + 16, 255)
    return clean_residual_green(Image.fromarray(arr, "RGBA"))


def clean_residual_green(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3].astype(np.int16)
    low_alpha_green = (a < 150) & (g > 120) & ((g - r) > 30) & ((g - b) > 30)
    vivid_key = (g > 170) & (r < 120) & (b < 120) & (a < 180)
    arr[low_alpha_green | vivid_key, 3] = 0
    return Image.fromarray(arr, "RGBA")


def trim_alpha(im: Image.Image, threshold: int = 8) -> Image.Image:
    alpha = im.getchannel("A")
    mask = alpha.point(lambda p: 255 if p > threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return im
    return im.crop(bbox)


def remove_small_alpha_components(im: Image.Image, min_area: int = 450) -> Image.Image:
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    mask = arr[:, :, 3] > 8
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    keep = np.zeros_like(mask, dtype=bool)
    components: list[tuple[int, list[tuple[int, int]]]] = []

    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(x, y)]
            seen[y, x] = True
            pts: list[tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                pts.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            components.append((len(pts), pts))

    if not components:
        return rgba

    largest = max(area for area, _ in components)
    for area, pts in components:
        if area >= min_area or area == largest:
            for x, y in pts:
                keep[y, x] = True
    arr[~keep, 3] = 0
    return Image.fromarray(arr, "RGBA")


def fit_image(im: Image.Image, max_w: int, max_h: int) -> Image.Image:
    ratio = min(max_w / im.width, max_h / im.height)
    size = (max(1, int(im.width * ratio)), max(1, int(im.height * ratio)))
    return im.resize(size, Image.Resampling.LANCZOS)


def paste_center(canvas: Image.Image, im: Image.Image, y: int) -> None:
    x = (canvas.width - im.width) // 2
    canvas.alpha_composite(im, (x, y))


def make_square_source(crop: Image.Image, pose_index: int) -> Image.Image:
    subject = trim_alpha(remove_small_alpha_components(crop))
    subject = fit_image(subject, 470, 450)
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    y = 28
    if pose_index in {8, 13}:
        y = 52
    paste_center(canvas, subject, y)
    return clean_residual_green(canvas)


def caption_font_size(text: str) -> int:
    if len(text) <= 2:
        return 44
    if len(text) == 3:
        return 40
    return 34


def tracked_text_bbox(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, stroke_width: int, tracking: int) -> tuple[int, int, int, int]:
    boxes = [draw.textbbox((0, 0), ch, font=f, stroke_width=stroke_width) for ch in text]
    width = sum(b[2] - b[0] for b in boxes) + max(0, len(boxes) - 1) * tracking
    top = min(b[1] for b in boxes)
    bottom = max(b[3] for b in boxes)
    return (0, top, width, bottom)


def draw_tracked_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    f: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    stroke_width: int,
    stroke_fill: tuple[int, int, int, int],
    tracking: int,
) -> None:
    x, y = xy
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=f, stroke_width=stroke_width)
        draw.text((x - bbox[0], y), ch, font=f, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        x += bbox[2] - bbox[0] + tracking


def draw_caption(canvas: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(canvas)
    override = CAPTION_RENDER_OVERRIDES.get(text, {})
    size = override.get("font_size", caption_font_size(text))
    font_path = override.get("font_path", FONT_PATH)
    stroke_width = override.get("stroke_width", 4)
    tracking = override.get("tracking", 0)
    while size >= 24:
        f = font(size, font_path)
        bbox = tracked_text_bbox(draw, text, f, stroke_width, tracking) if tracking else draw.textbbox((0, 0), text, font=f, stroke_width=stroke_width)
        if bbox[2] - bbox[0] <= 222:
            break
        size -= 2
    f = font(size, font_path)
    bbox = tracked_text_bbox(draw, text, f, stroke_width, tracking) if tracking else draw.textbbox((0, 0), text, font=f, stroke_width=stroke_width)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (canvas.width - w) // 2 - bbox[0]
    y = 198 - h // 2 - bbox[1]
    if tracking:
        draw_tracked_text(draw, (x + 2, y + 3), text, f, (194, 127, 42, 210), stroke_width, (194, 127, 42, 180), tracking)
        draw_tracked_text(draw, (x, y), text, f, (255, 255, 255, 255), stroke_width, (52, 34, 22, 255), tracking)
    else:
        draw.text((x + 2, y + 3), text, font=f, fill=(194, 127, 42, 210), stroke_width=stroke_width, stroke_fill=(194, 127, 42, 180))
        draw.text((x, y), text, font=f, fill=(255, 255, 255, 255), stroke_width=stroke_width, stroke_fill=(52, 34, 22, 255))


def make_wechat_sticker(source: Image.Image, caption: str, pose_index: int) -> Image.Image:
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    subject = trim_alpha(source)
    max_h = 168
    max_w = 222
    if pose_index in {8, 13}:
        max_h = 150
    subject = fit_image(subject, max_w, max_h)
    y = 8
    if pose_index in {8, 13}:
        y = 22
    paste_center(canvas, subject, y)
    draw_caption(canvas, caption)
    return clean_residual_green(canvas)


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    w, h = size
    im = Image.new("RGB", size, (245, 245, 245))
    draw = ImageDraw.Draw(im)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(225, 225, 225))
    return im


def make_captioned_sheets(stickers: list[tuple[dict[str, Any], Image.Image]]) -> None:
    for sheet_idx in range(2):
        sheet = Image.new("RGBA", (720, 720), (0, 0, 0, 0))
        for local_idx, (_, sticker) in enumerate(stickers[sheet_idx * 9 : sheet_idx * 9 + 9]):
            x = (local_idx % 3) * 240
            y = (local_idx // 3) * 240
            sheet.alpha_composite(sticker, (x, y))
        save_png(sheet, PACK_ROOT / f"generated/sheets/captioned/captioned-sheet-{sheet_idx + 1:02d}.png")


def make_sheet_reviews() -> None:
    raw_paths = [
        PACK_ROOT / "generated/sheets/raw/raw-sheet-01-ai.png",
        PACK_ROOT / "generated/sheets/raw/raw-sheet-02-ai.png",
    ]
    raw_review = Image.new("RGB", (1300, 660), (250, 246, 236))
    draw = ImageDraw.Draw(raw_review)
    label_font = font(24)
    for i, path in enumerate(raw_paths):
        im = Image.open(path).convert("RGB")
        im.thumbnail((610, 610), Image.Resampling.LANCZOS)
        x = 25 + i * 640
        raw_review.paste(im, (x, 20))
        draw.text((x, 635), f"Raw sheet {i + 1}", font=label_font, fill=(54, 38, 26))
    save_png(raw_review, PACK_ROOT / "review/sheets/raw-sheets-review.png")

    cap_paths = [
        PACK_ROOT / "generated/sheets/captioned/captioned-sheet-01.png",
        PACK_ROOT / "generated/sheets/captioned/captioned-sheet-02.png",
    ]
    cap_review = Image.new("RGB", (1300, 660), (250, 246, 236))
    draw = ImageDraw.Draw(cap_review)
    for i, path in enumerate(cap_paths):
        im = Image.open(path).convert("RGBA")
        bg = checkerboard(im.size, 16).convert("RGBA")
        bg.alpha_composite(im, (0, 0))
        bg.thumbnail((610, 610), Image.Resampling.LANCZOS)
        x = 25 + i * 640
        cap_review.paste(bg.convert("RGB"), (x, 20))
        draw.text((x, 635), f"Captioned sheet {i + 1}", font=label_font, fill=(54, 38, 26))
    save_png(cap_review, PACK_ROOT / "review/sheets/captioned-sheets-review.png")


def make_review_sheets(stickers: list[tuple[dict[str, Any], Image.Image]]) -> None:
    cell_w, cell_h = 260, 300
    cols = 6
    rows = math.ceil(len(stickers) / cols)
    review = Image.new("RGB", (cell_w * cols, cell_h * rows), (250, 246, 236))
    draw = ImageDraw.Draw(review)
    label_font = font(22)
    for i, (item, sticker) in enumerate(stickers):
        x = (i % cols) * cell_w
        y = (i // cols) * cell_h
        bg = checkerboard((240, 240), 12)
        bg = bg.convert("RGBA")
        bg.alpha_composite(sticker, (0, 0))
        review.paste(bg.convert("RGB"), (x + 10, y + 8))
        label = f"{item['index']:02d} {item['caption']}"
        draw.text((x + 14, y + 254), label, font=label_font, fill=(54, 38, 26))
    save_png(review, PACK_ROOT / "review/stickers/all-stickers-contact-sheet.png")


def make_master_review() -> None:
    refs = [
        Image.open(PACK_ROOT / "source/references/xbd-big-reference.png").convert("RGBA"),
        Image.open(PACK_ROOT / "source/references/xbd-small-reference.png").convert("RGBA"),
    ]
    canvas = Image.new("RGB", (900, 520), (250, 246, 236))
    draw = ImageDraw.Draw(canvas)
    title_font = font(30)
    label_font = font(24)
    draw.text((30, 24), "小布丁03母版参考", font=title_font, fill=(54, 38, 26))
    labels = ["参考图1：全身衣服细节", "参考图2：主脸型和围嘴身份"]
    for idx, ref in enumerate(refs):
        thumb = fit_image(ref, 360, 360)
        bg = checkerboard((380, 380), 16).convert("RGBA")
        bg.alpha_composite(thumb, ((380 - thumb.width) // 2, (380 - thumb.height) // 2))
        x = 45 + idx * 430
        canvas.paste(bg.convert("RGB"), (x, 84))
        draw.text((x, 470), labels[idx], font=label_font, fill=(54, 38, 26))
    save_png(canvas, PACK_ROOT / "review/master/master-reference-review.png")


def make_cover_icon_banner(stickers: list[tuple[dict[str, Any], Image.Image]], sources: list[Image.Image]) -> None:
    cover_src = sources[0]
    cover = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    subj = fit_image(trim_alpha(cover_src), 220, 218)
    paste_center(cover, subj, 10)
    cover = clean_residual_green(cover)
    save_png(cover, PACK_ROOT / "exports/wechat/cover.png")

    icon = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    icon_src = trim_alpha(sources[0])
    icon_subj = fit_image(icon_src, 48, 48)
    icon.alpha_composite(icon_subj, ((50 - icon_subj.width) // 2, (50 - icon_subj.height) // 2))
    icon = clean_residual_green(icon)
    save_png(icon, PACK_ROOT / "exports/wechat/icon.png")

    banner = Image.new("RGB", (750, 400), (151, 219, 205))
    draw = ImageDraw.Draw(banner)
    for i, color in enumerate([(255, 222, 147), (255, 181, 166), (116, 178, 203), (238, 246, 210)]):
        cx = [110, 640, 560, 230][i]
        cy = [95, 92, 310, 300][i]
        r = [82, 70, 88, 60][i]
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    picks = [sources[0], sources[12], sources[16]]
    sizes = [(250, 250), (190, 190), (180, 180)]
    positions = [(70, 82), (420, 72), (535, 180)]
    for sticker, size, pos in zip(picks, sizes, positions):
        subj = trim_alpha(sticker)
        subj = fit_image(subj, *size)
        layer = Image.new("RGBA", banner.size, (0, 0, 0, 0))
        layer.alpha_composite(subj, pos)
        banner = Image.alpha_composite(banner.convert("RGBA"), layer).convert("RGB")
    save_png(banner, PACK_ROOT / "exports/wechat/banner.png", palette=True)


def make_export_metadata(spec: dict[str, Any], stickers: list[tuple[dict[str, Any], Image.Image]]) -> None:
    sticker_entries = []
    for item, _ in stickers:
        name = f"{item['fileBase']}-{item['caption']}.png"
        sticker_entries.append(
            {
                "index": item["index"],
                "caption": item["caption"],
                "pose": item["pose"],
                "path": f"stickers/{name}",
                "width": 240,
                "height": 240,
                "format": "PNG",
                "background": "transparent",
            }
        )
    metadata = {
        "packId": spec["packId"],
        "title": spec["title"],
        "description": spec["description"],
        "copyright": spec["copyright"],
        "platform": spec["platform"],
        "packType": "static",
        "createdAt": spec["createdAt"],
        "generatedAt": "2026-05-14T16:05:00+08:00",
        "sourceMaterial": spec["masterCharacter"]["sourceImages"],
        "masterCharacter": {
            "name": spec["masterCharacter"]["characterName"],
            "approvedImage": spec["masterCharacter"]["approvedImage"],
            "lockedTraits": spec["masterCharacter"]["lockedTraits"],
            "forbiddenVariations": spec["masterCharacter"]["forbiddenVariations"],
        },
        "assets": {
            "stickers": sticker_entries,
            "cover": "cover.png",
            "icon": "icon.png",
            "banner": "banner.png",
        },
        "wechatTargets": spec["wechatTarget"],
        "captionRendering": spec["captions"]["style"],
    }
    (PACK_ROOT / "exports/wechat/metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    form = f"""# 微信表情开放平台表单

- 表情包名称：{spec['title']}
- 简介：{spec['description']}
- 版权：{spec['copyright']}
- 类型：静态表情
- 表情数量：18
- 封面：cover.png
- 聊天面板图标：icon.png
- 详情页横幅：banner.png
- 表情文件夹：stickers/

## 表情列表

"""
    for item, _ in stickers:
        form += f"- {item['index']:02d}. {item['caption']}：stickers/{item['fileBase']}-{item['caption']}.png\n"
    (PACK_ROOT / "exports/wechat/form.md").write_text(form, encoding="utf-8")


def image_info(path: Path) -> dict[str, Any]:
    im = Image.open(path)
    info: dict[str, Any] = {
        "path": str(path.relative_to(PACK_ROOT)),
        "exists": True,
        "format": im.format,
        "width": im.width,
        "height": im.height,
        "mode": im.mode,
        "bytes": path.stat().st_size,
    }
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    corners = [alpha.getpixel((0, 0)), alpha.getpixel((im.width - 1, 0)), alpha.getpixel((0, im.height - 1)), alpha.getpixel((im.width - 1, im.height - 1))]
    info["hasAlpha"] = "A" in im.getbands() or im.mode in {"LA", "RGBA"}
    info["cornerAlpha"] = corners
    info["transparentCorners"] = all(v == 0 for v in corners)
    info["alphaExtrema"] = alpha.getextrema()
    return info


def validate(spec: dict[str, Any]) -> None:
    report: dict[str, Any] = {
        "packId": spec["packId"],
        "validatedAt": "2026-05-14T16:05:00+08:00",
        "officialSpecBasis": spec["validation"]["officialSpecCheckedAt"],
        "checks": [],
        "assets": {},
    }

    sticker_dir = PACK_ROOT / "exports/wechat/stickers"
    sticker_files = sorted(p for p in sticker_dir.glob("*.png"))
    report["assets"]["stickers"] = [image_info(p) for p in sticker_files]
    report["assets"]["cover"] = image_info(PACK_ROOT / "exports/wechat/cover.png")
    report["assets"]["icon"] = image_info(PACK_ROOT / "exports/wechat/icon.png")
    report["assets"]["banner"] = image_info(PACK_ROOT / "exports/wechat/banner.png")

    def add(name: str, ok: bool, detail: Any = None) -> None:
        report["checks"].append({"check": name, "status": "pass" if ok else "fail", "detail": detail})

    add("sticker-count-is-18", len(sticker_files) == 18, len(sticker_files))
    for info in report["assets"]["stickers"]:
        rel = info["path"]
        add(f"{rel}-is-png", info["format"] == "PNG", info["format"])
        add(f"{rel}-is-240x240", info["width"] == 240 and info["height"] == 240, [info["width"], info["height"]])
        add(f"{rel}-has-alpha", info["hasAlpha"], info["mode"])
        add(f"{rel}-transparent-corners", info["transparentCorners"], info["cornerAlpha"])
        add(f"{rel}-under-500kb", info["bytes"] <= 512000, info["bytes"])

    cover = report["assets"]["cover"]
    add("cover-is-png-240x240", cover["format"] == "PNG" and cover["width"] == 240 and cover["height"] == 240, cover)
    add("cover-transparent-corners", cover["transparentCorners"], cover["cornerAlpha"])
    add("cover-under-500kb", cover["bytes"] <= 512000, cover["bytes"])

    icon = report["assets"]["icon"]
    add("icon-is-png-50x50", icon["format"] == "PNG" and icon["width"] == 50 and icon["height"] == 50, icon)
    add("icon-transparent-corners", icon["transparentCorners"], icon["cornerAlpha"])
    add("icon-under-100kb", icon["bytes"] <= 102400, icon["bytes"])

    banner = report["assets"]["banner"]
    alpha_extrema = banner["alphaExtrema"]
    add("banner-is-png-750x400", banner["format"] == "PNG" and banner["width"] == 750 and banner["height"] == 400, banner)
    add("banner-opaque", alpha_extrema == (255, 255), alpha_extrema)
    add("banner-under-500kb", banner["bytes"] <= 512000, banner["bytes"])

    name = spec["wechatTarget"]["form"]["name"]["value"]
    intro = spec["wechatTarget"]["form"]["introduction"]["value"]
    copyright_text = spec["wechatTarget"]["form"]["copyright"]["value"]
    add("form-name-under-8-chinese-chars-no-punctuation-no-spaces", len(name) <= 8 and " " not in name and all(ch not in "，。！？、,.!? " for ch in name), name)
    add("form-introduction-under-80-chinese-chars", len(intro) <= 80, len(intro))
    add("form-copyright-under-10-chinese-chars", len(copyright_text) <= 10, copyright_text)
    add("metadata-json-exists", (PACK_ROOT / "exports/wechat/metadata.json").exists(), None)
    add("form-md-exists", (PACK_ROOT / "exports/wechat/form.md").exists(), None)
    allowed_export_files = {
        "banner.png",
        "cover.png",
        "form.md",
        "icon.png",
        "metadata.json",
    }
    export_root = PACK_ROOT / "exports/wechat"
    extra_root_files = sorted(p.name for p in export_root.iterdir() if p.is_file() and p.name not in allowed_export_files)
    extra_sticker_files = sorted(p.name for p in sticker_dir.iterdir() if p.is_file() and p.suffix.lower() != ".png")
    add("wechat-export-root-has-no-extra-files", not extra_root_files, extra_root_files)
    add("wechat-stickers-dir-has-only-png-files", not extra_sticker_files, extra_sticker_files)

    report["summary"] = {
        "passed": sum(1 for c in report["checks"] if c["status"] == "pass"),
        "failed": sum(1 for c in report["checks"] if c["status"] == "fail"),
        "manualReviewRequired": [
            "banner-has-no-text",
            "cover-and-icon-have-no-white-background-or-square-frame",
            "visual-consistency-and-semantic-difference",
            "no-copyright-trademark-sensitive-content",
        ],
    }

    report_path = PACK_ROOT / "review/wechat/validation-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = ["# WeChat Validation Report", "", f"- Pack ID: `{spec['packId']}`", f"- Title: {spec['title']}", f"- Generated at: 2026-05-14T16:05:00+08:00", f"- Passed: {report['summary']['passed']}", f"- Failed: {report['summary']['failed']}", "", "## Checks", ""]
    for check in report["checks"]:
        mark = "PASS" if check["status"] == "pass" else "FAIL"
        md.append(f"- {mark}: {check['check']} ({check['detail']})")
    md.extend(["", "## Manual Review Required", ""])
    for item in report["summary"]["manualReviewRequired"]:
        md.append(f"- {item}")
    (PACK_ROOT / "review/wechat/validation-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    spec = load_spec()
    ensure_dirs()

    raw_paths = [
        PACK_ROOT / "generated/sheets/raw/raw-sheet-01-ai.png",
        PACK_ROOT / "generated/sheets/raw/raw-sheet-02-ai.png",
    ]
    raw_images = [Image.open(p).convert("RGBA") for p in raw_paths]
    items = spec["captions"]["items"]

    source_images: list[Image.Image] = []
    stickers: list[tuple[dict[str, Any], Image.Image]] = []
    for sheet_idx, sheet in enumerate(raw_images):
        cell_w = sheet.width // 3
        cell_h = sheet.height // 3
        for local_idx in range(9):
            item = items[sheet_idx * 9 + local_idx]
            x0 = (local_idx % 3) * cell_w
            y0 = (local_idx // 3) * cell_h
            crop = sheet.crop((x0, y0, x0 + cell_w, y0 + cell_h))
            alpha_crop = remove_green(crop)
            source = make_square_source(alpha_crop, item["index"])
            source_images.append(source)
            source_name = f"{item['fileBase']}-{item['caption']}.png"
            save_png(source, PACK_ROOT / "generated/stickers/source-crops" / source_name)

            sticker = make_wechat_sticker(source, item["caption"], item["index"])
            stickers.append((item, sticker))
            save_png(sticker, PACK_ROOT / "generated/stickers/wechat-draft" / source_name)
            save_png(sticker, PACK_ROOT / "exports/wechat/stickers" / source_name)

    make_captioned_sheets(stickers)
    make_sheet_reviews()
    make_review_sheets(stickers)
    make_master_review()
    make_cover_icon_banner(stickers, source_images)
    make_export_metadata(spec, stickers)
    validate(spec)


if __name__ == "__main__":
    main()
