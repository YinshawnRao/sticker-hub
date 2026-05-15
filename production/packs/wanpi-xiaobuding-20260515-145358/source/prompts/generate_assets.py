#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


PACK_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = PACK_ROOT / "spec.json"

FONT_CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_CJK_ALT = "/System/Library/Fonts/STHeiti Medium.ttc"

WHITE = (255, 255, 255, 255)
INK = (66, 38, 24, 255)
SHADOW = (245, 179, 64, 255)
CREAM = (255, 246, 220, 255)
PINK = (255, 218, 226, 255)
GREEN = (112, 170, 104, 255)
GRASS = (105, 180, 97, 255)
SAND = (238, 197, 122, 255)
WOOD = (177, 118, 70, 255)


@dataclass(frozen=True)
class StickerItem:
    index: int
    slug: str
    caption: str
    scene: str
    props: list[str]
    pose: str

    @property
    def filename(self) -> str:
        return f"{self.slug}-{self.caption}.png"


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_CJK, size)
    except OSError:
        return ImageFont.truetype(FONT_CJK_ALT, size)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, stroke: int) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int) -> ImageFont.FreeTypeFont:
    size = 58
    while size >= 34:
        fnt = font(size)
        box = text_bbox(draw, text, fnt, 7)
        if box[2] - box[0] <= max_width:
            return fnt
        size -= 2
    return font(34)


def ensure_dirs() -> None:
    for rel in [
        "generated/sheets/raw",
        "generated/sheets/captioned",
        "generated/stickers/source-crops",
        "generated/stickers/wechat-draft",
        "review/master",
        "review/sheets",
        "review/stickers",
        "review/wechat",
        "exports/wechat/stickers",
    ]:
        (PACK_ROOT / rel).mkdir(parents=True, exist_ok=True)


def clear_outputs() -> None:
    keep_raw_ai = {"sheet-01-raw-ai.png", "sheet-02-raw-ai.png"}
    for rel in [
        "generated/sheets/raw",
        "generated/sheets/captioned",
        "generated/stickers/source-crops",
        "generated/stickers/wechat-draft",
        "review/master",
        "review/sheets",
        "review/stickers",
        "review/wechat",
        "exports/wechat/stickers",
    ]:
        root = PACK_ROOT / rel
        for path in root.glob("*"):
            if path.is_file() and path.name not in keep_raw_ai and path.name != ".gitkeep":
                path.unlink()
    for rel in [
        "exports/wechat/cover.png",
        "exports/wechat/icon.png",
        "exports/wechat/banner.png",
        "exports/wechat/metadata.json",
        "exports/wechat/form.md",
    ]:
        path = PACK_ROOT / rel
        if path.exists():
            path.unlink()


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def key_to_alpha(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        key = r > 115 and b > 85 and g < 155 and (r - g) > 25 and (b - g) > 15
        if key:
            out.append((r, g, b, 0))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    alpha = rgba.getchannel("A").filter(ImageFilter.MedianFilter(3))
    rgba.putalpha(alpha)
    return rgba


def trim_alpha(img: Image.Image, padding: int = 10) -> Image.Image:
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - padding)
    y0 = max(0, y0 - padding)
    x1 = min(img.width, x1 + padding)
    y1 = min(img.height, y1 + padding)
    return img.crop((x0, y0, x1, y1))


def remove_small_alpha_components(img: Image.Image, min_area: int = 180) -> Image.Image:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    w, h = alpha.size
    src = alpha.load()
    visited = bytearray(w * h)
    keep = Image.new("L", (w, h), 0)
    keep_px = keep.load()
    for sy in range(h):
        for sx in range(w):
            start = sy * w + sx
            if visited[start] or src[sx, sy] <= 8:
                visited[start] = 1
                continue
            stack = [(sx, sy)]
            visited[start] = 1
            pixels: list[tuple[int, int]] = []
            max_alpha = 0
            min_x = max_x = sx
            min_y = max_y = sy
            while stack:
                x, y = stack.pop()
                a = src[x, y]
                if a <= 8:
                    continue
                pixels.append((x, y))
                max_alpha = max(max_alpha, a)
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        idx = ny * w + nx
                        if not visited[idx]:
                            visited[idx] = 1
                            if src[nx, ny] > 8:
                                stack.append((nx, ny))
            area = len(pixels)
            wide_enough = (max_x - min_x) > 24 and (max_y - min_y) > 18
            opaque_enough = max_alpha > 180 and area > 70
            if area >= min_area or wide_enough or opaque_enough:
                for x, y in pixels:
                    keep_px[x, y] = src[x, y]
    rgba.putalpha(keep)
    return rgba


def clear_cell_edges(img: Image.Image, margin: int = 22) -> Image.Image:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    draw = ImageDraw.Draw(alpha)
    draw.rectangle((0, 0, rgba.width, margin), fill=0)
    draw.rectangle((0, rgba.height - margin, rgba.width, rgba.height), fill=0)
    draw.rectangle((0, 0, margin, rgba.height), fill=0)
    draw.rectangle((rgba.width - margin, 0, rgba.width, rgba.height), fill=0)
    rgba.putalpha(alpha)
    return rgba


def contain(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / img.width, max_h / img.height)
    new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def draw_caption(base: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(base)
    fnt = fit_font(draw, text, 430)
    box = text_bbox(draw, text, fnt, 7)
    tw = box[2] - box[0]
    th = box[3] - box[1]
    x = (base.width - tw) // 2 - box[0]
    y = base.height - 68 - th // 2 - box[1]
    draw.text((x + 3, y + 5), text, font=fnt, fill=SHADOW, stroke_width=7, stroke_fill=INK)
    draw.text((x, y), text, font=fnt, fill=WHITE, stroke_width=7, stroke_fill=INK)


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int = 22) -> None:
    fnt = font(size)
    draw.text(xy, text, font=fnt, fill=(80, 60, 50, 255))


def compose_sticker(crop: Image.Image, item: StickerItem) -> Image.Image:
    clean = trim_alpha(crop, 8)
    if item.index in {8, 9, 17}:
        max_subject = (360, 300)
    elif item.caption in {"糟糕啦"}:
        max_subject = (430, 330)
    elif item.caption in {"我很乖", "嘿嘿嘿"}:
        max_subject = (390, 330)
    elif item.caption in {"滑梯冲", "摔倒啦"}:
        max_subject = (378, 320)
    elif item.caption in {"抱抱我", "冲呀", "拆家啦"}:
        max_subject = (390, 330)
    else:
        max_subject = (372, 318)
    subject = contain(clean, *max_subject)
    canvas = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
    if item.index in {8, 9, 17}:
        y = 42
    else:
        y = 34 if subject.height < 300 else 28
    x = (480 - subject.width) // 2
    canvas.alpha_composite(subject, (x, y))
    draw_caption(canvas, item.caption)
    return canvas


def build_from_sheets(items: list[StickerItem]) -> tuple[list[Path], list[Path]]:
    source_paths: list[Path] = []
    draft_paths: list[Path] = []
    replacements = {
        2: PACK_ROOT / "generated/stickers/replacements/raw/02-oops-raw-ai.png",
        3: PACK_ROOT / "generated/stickers/replacements/raw/03-good-boy-raw-ai.png",
        8: PACK_ROOT / "generated/stickers/replacements/raw/08-little-chaos-raw-ai.png",
        9: PACK_ROOT / "generated/stickers/replacements/raw/09-sleepy-raw-ai.png",
        17: PACK_ROOT / "generated/stickers/replacements/raw/17-more-play-raw-ai.png",
        18: PACK_ROOT / "generated/stickers/replacements/raw/18-hehe-raw-ai.png",
    }
    sheet_files = [
        PACK_ROOT / "generated/sheets/raw/sheet-01-raw-ai.png",
        PACK_ROOT / "generated/sheets/raw/sheet-02-raw-ai.png",
    ]
    for sheet_idx, path in enumerate(sheet_files):
        raw = Image.open(path).convert("RGBA")
        keyed = key_to_alpha(raw)
        save_png(keyed, PACK_ROOT / f"generated/sheets/raw/sheet-{sheet_idx + 1:02d}-raw.png")
        cell_w = raw.width // 3
        cell_h = raw.height // 3
        for local_idx in range(9):
            item = items[sheet_idx * 9 + local_idx]
            row = local_idx // 3
            col = local_idx % 3
            replacement = replacements.get(item.index)
            if replacement and replacement.exists():
                crop = Image.open(replacement).convert("RGBA")
                alpha_crop = clear_cell_edges(remove_small_alpha_components(key_to_alpha(crop), 180), 14)
            else:
                crop = raw.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
                alpha_crop = clear_cell_edges(remove_small_alpha_components(key_to_alpha(crop), 180), 22)
            sticker = compose_sticker(alpha_crop, item)
            source_path = PACK_ROOT / "generated/stickers/source-crops" / item.filename
            draft_path = PACK_ROOT / "generated/stickers/wechat-draft" / item.filename
            export_path = PACK_ROOT / "exports/wechat/stickers" / item.filename
            save_png(sticker, source_path)
            draft = sticker.resize((240, 240), Image.Resampling.LANCZOS)
            save_png(draft, draft_path)
            shutil.copy2(draft_path, export_path)
            source_paths.append(source_path)
            draft_paths.append(draft_path)
    return source_paths, draft_paths


def make_grid(paths: list[Path], cell: int, cols: int, bg: tuple[int, int, int, int], label: bool = False) -> Image.Image:
    rows = math.ceil(len(paths) / cols)
    pad = 28
    label_h = 34 if label else 0
    img = Image.new("RGBA", (cols * cell + pad * 2, rows * (cell + label_h) + pad * 2), bg)
    draw = ImageDraw.Draw(img)
    for i, path in enumerate(paths):
        src = Image.open(path).convert("RGBA")
        src = contain(src, cell - 20, cell - 20)
        col = i % cols
        row = i // cols
        x = pad + col * cell + (cell - src.width) // 2
        y = pad + row * (cell + label_h) + (cell - src.height) // 2
        if bg[3] == 255:
            draw.rounded_rectangle((pad + col * cell + 8, pad + row * (cell + label_h) + 8, pad + (col + 1) * cell - 8, pad + row * (cell + label_h) + cell - 8), radius=16, fill=(255, 255, 255, 255), outline=(230, 216, 198, 255), width=2)
        img.alpha_composite(src, (x, y))
        if label:
            parts = path.stem.split("-")
            if parts and parts[0].isdigit():
                label_text = f"{parts[0]} {parts[-1]}"
            else:
                label_text = path.stem[:12]
            draw_label(draw, (pad + col * cell + 14, pad + row * (cell + label_h) + cell + 4), label_text, 15)
    return img


def draw_blocks(draw: ImageDraw.ImageDraw, ox: int, oy: int, scale: float) -> None:
    colors = [(255, 204, 81, 255), (110, 180, 105, 255), (110, 170, 220, 255), (236, 120, 99, 255)]
    for i, color in enumerate(colors):
        x = ox + int((i % 2) * 45 * scale)
        y = oy + int((i // 2) * 42 * scale)
        draw.rounded_rectangle((x, y, x + int(36 * scale), y + int(32 * scale)), radius=int(5 * scale), fill=color, outline=INK, width=max(2, int(3 * scale)))


def draw_banner() -> Image.Image:
    img = Image.new("RGB", (750, 400), (250, 239, 210))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 375, 400), fill=(255, 235, 204))
    draw.rectangle((375, 0, 750, 400), fill=(209, 238, 203))
    draw.rectangle((0, 305, 375, 400), fill=(235, 203, 172))
    draw.rectangle((375, 300, 750, 400), fill=(128, 190, 112))
    draw.rounded_rectangle((35, 72, 150, 150), radius=18, fill=(255, 252, 235), outline=(222, 177, 134), width=5)
    draw_blocks(draw, 62, 248, 1.1)
    draw.ellipse((482, 252, 575, 337), fill=(255, 211, 73), outline=INK, width=5)
    draw.polygon([(620, 250), (690, 250), (651, 198)], fill=(237, 116, 83), outline=INK)
    draw.line((620, 250, 607, 312), fill=INK, width=5)
    draw.line((690, 250, 707, 312), fill=INK, width=5)
    draw.rectangle((605, 246, 707, 262), fill=(89, 147, 215), outline=INK, width=4)
    master = Image.open(PACK_ROOT / "master/approved/xiaobuding-approved-master.png").convert("RGBA")
    cut = trim_alpha(master, 4)
    left = contain(cut, 250, 330)
    right = contain(cut.transpose(Image.Transpose.FLIP_LEFT_RIGHT), 210, 285)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(left, (205, 54))
    img_rgba.alpha_composite(right, (405, 88))
    return img_rgba.convert("RGB")


def make_cover_and_icon() -> tuple[Path, Path, Path]:
    master = Image.open(PACK_ROOT / "master/approved/xiaobuding-approved-master.png").convert("RGBA")
    cut = trim_alpha(master, 4)
    cover = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    upper = cut.crop((0, 0, cut.width, int(cut.height * 0.68)))
    upper = contain(upper, 220, 228)
    cover.alpha_composite(upper, ((240 - upper.width) // 2, 10))
    cover_path = PACK_ROOT / "exports/wechat/cover.png"
    save_png(cover, cover_path)

    icon = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    head = cut.crop((int(cut.width * 0.12), 0, int(cut.width * 0.88), int(cut.height * 0.43)))
    head = trim_alpha(head, 2)
    head = contain(head, 48, 48)
    icon.alpha_composite(head, ((50 - head.width) // 2, (50 - head.height) // 2))
    icon_path = PACK_ROOT / "exports/wechat/icon.png"
    save_png(icon, icon_path)

    banner = draw_banner()
    banner_path = PACK_ROOT / "exports/wechat/banner.png"
    save_png(banner, banner_path)
    return cover_path, icon_path, banner_path


def make_review_images(source_paths: list[Path], draft_paths: list[Path]) -> None:
    master = Image.open(PACK_ROOT / "master/approved/xiaobuding-approved-master.png").convert("RGBA")
    master_review = Image.new("RGBA", (900, 620), (250, 244, 232, 255))
    draw = ImageDraw.Draw(master_review)
    draw_label(draw, (36, 30), "Approved master reference", 34)
    cut = contain(trim_alpha(master, 4), 360, 520)
    master_review.alpha_composite(cut, (80, 78))
    draw_label(draw, (500, 120), "Pack: 顽皮小布丁", 28)
    draw_label(draw, (500, 170), "Mode: image-to-master", 24)
    draw_label(draw, (500, 216), "Status: asset generation", 24)
    draw_label(draw, (500, 262), "Final captions: local composition", 24)
    save_png(master_review, PACK_ROOT / "review/master/master-reference-review.png")

    for i in [1, 2]:
        src = Image.open(PACK_ROOT / f"generated/sheets/raw/sheet-{i:02d}-raw.png").convert("RGBA")
        bg = Image.new("RGBA", src.size, (250, 244, 232, 255))
        bg.alpha_composite(src)
        save_png(bg, PACK_ROOT / f"review/sheets/sheet-{i:02d}-review.png")
    save_png(make_grid(source_paths[:9], 240, 3, (0, 0, 0, 0)), PACK_ROOT / "generated/sheets/captioned/sheet-01-captioned.png")
    save_png(make_grid(source_paths[9:], 240, 3, (0, 0, 0, 0)), PACK_ROOT / "generated/sheets/captioned/sheet-02-captioned.png")
    contact = make_grid(draft_paths, 170, 6, (250, 244, 232, 255), label=True)
    save_png(contact, PACK_ROOT / "review/stickers/contact-sheet.png")
    overview_paths = [PACK_ROOT / "exports/wechat/cover.png", PACK_ROOT / "exports/wechat/icon.png", PACK_ROOT / "exports/wechat/banner.png"] + [PACK_ROOT / "exports/wechat/stickers" / p.name for p in draft_paths]
    overview = make_grid(overview_paths, 150, 7, (250, 244, 232, 255), label=True)
    save_png(overview, PACK_ROOT / "review/wechat/export-assets-overview.png")


def image_info(path: Path) -> dict[str, Any]:
    im = Image.open(path)
    info: dict[str, Any] = {
        "path": str(path.relative_to(PACK_ROOT)),
        "format": im.format,
        "width": im.width,
        "height": im.height,
        "mode": im.mode,
        "bytes": path.stat().st_size,
    }
    if im.mode in {"RGBA", "LA"}:
        alpha = im.convert("RGBA").getchannel("A")
        info["hasAlpha"] = True
        info["cornerAlpha"] = [
            alpha.getpixel((0, 0)),
            alpha.getpixel((im.width - 1, 0)),
            alpha.getpixel((0, im.height - 1)),
            alpha.getpixel((im.width - 1, im.height - 1)),
        ]
    else:
        info["hasAlpha"] = False
        info["cornerAlpha"] = None
    return info


def validate(spec: dict[str, Any], sticker_paths: list[Path], cover: Path, icon: Path, banner: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    add("sticker-count", len(sticker_paths) == 18, f"{len(sticker_paths)} sticker PNG files")
    for path in sticker_paths:
        info = image_info(path)
        add(f"{path.name}: dimension", info["width"] == 240 and info["height"] == 240, f"{info['width']}x{info['height']}")
        add(f"{path.name}: alpha", bool(info["hasAlpha"]) and max(info["cornerAlpha"]) <= 8, f"corner alpha {info['cornerAlpha']}")
        add(f"{path.name}: size", info["bytes"] <= spec["wechatTarget"]["sticker"]["maxBytes"], f"{info['bytes']} bytes")
        im = Image.open(path).convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        if bbox:
            left, top, right, bottom = bbox
            margins = {
                "left": left,
                "top": top,
                "right": im.width - right,
                "bottom": im.height - bottom,
            }
            safe = margins["left"] >= 8 and margins["right"] >= 8 and margins["bottom"] >= 8 and margins["top"] >= 12
            add(f"{path.name}: safe-area", safe, f"margins {margins}")
        else:
            add(f"{path.name}: safe-area", False, "empty alpha bbox")

    for label, path, target in [
        ("cover", cover, spec["wechatTarget"]["cover"]),
        ("icon", icon, spec["wechatTarget"]["icon"]),
    ]:
        info = image_info(path)
        add(f"{label}: dimension", info["width"] == target["width"] and info["height"] == target["height"], f"{info['width']}x{info['height']}")
        add(f"{label}: alpha", bool(info["hasAlpha"]) and max(info["cornerAlpha"]) <= 8, f"corner alpha {info['cornerAlpha']}")
        add(f"{label}: size", info["bytes"] <= target["maxBytes"], f"{info['bytes']} bytes")

    banner_info = image_info(banner)
    banner_target = spec["wechatTarget"]["banner"]
    add("banner: dimension", banner_info["width"] == banner_target["width"] and banner_info["height"] == banner_target["height"], f"{banner_info['width']}x{banner_info['height']}")
    add("banner: opaque", not banner_info["hasAlpha"], f"mode {banner_info['mode']}")
    add("banner: size", banner_info["bytes"] <= banner_target["maxBytes"], f"{banner_info['bytes']} bytes")
    add("form: name", len(spec["title"]) <= 8 and " " not in spec["title"] and "。" not in spec["title"], spec["title"])
    add("form: intro", len(spec["description"]) <= 80, spec["description"])
    add("form: copyright", len(spec["copyright"]) <= 10, spec["copyright"])

    return {
        "packId": spec["packId"],
        "title": spec["title"],
        "generatedBy": "source/prompts/generate_assets.py",
        "passed": all(c["passed"] for c in checks),
        "checks": checks,
        "assets": {
            "stickers": [image_info(p) for p in sticker_paths],
            "cover": image_info(cover),
            "icon": image_info(icon),
            "banner": image_info(banner),
        },
    }


def write_metadata_and_reports(spec: dict[str, Any], items: list[StickerItem], validation: dict[str, Any]) -> None:
    stickers = [
        {
            "index": item.index,
            "caption": item.caption,
            "scene": item.scene,
            "pose": item.pose,
            "exportPath": f"stickers/{item.filename}",
        }
        for item in items
    ]
    metadata = {
        "packId": spec["packId"],
        "title": spec["title"],
        "description": spec["description"],
        "copyright": spec["copyright"],
        "packType": spec["wechatTarget"]["packType"],
        "sourceMaster": spec["masterCharacter"]["approvedImage"],
        "assets": {
            "stickers": stickers,
            "cover": "cover.png",
            "icon": "icon.png",
            "banner": "banner.png",
        },
        "validation": {
            "report": "review/wechat/validation-report.json",
            "passed": validation["passed"],
        },
        "trace": {
            "rawSheets": [
                "generated/sheets/raw/sheet-01-raw-ai.png",
                "generated/sheets/raw/sheet-02-raw-ai.png",
            ],
            "promptPlan": "source/prompts/generation-plan.md",
            "localProcessor": "source/prompts/generate_assets.py",
        },
    }
    (PACK_ROOT / "exports/wechat/metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    form = f"""# 微信表情开放平台表单

- 表情包名称：{spec['title']}
- 简介：{spec['description']}
- 版权：{spec['copyright']}
- 类型：静态表情
- 数量：18

## 文件

- 表情图片：`stickers/` 下 18 张 `240x240` PNG
- 封面：`cover.png`
- 聊天面板图标：`icon.png`
- 详情页横幅：`banner.png`
"""
    (PACK_ROOT / "exports/wechat/form.md").write_text(form, encoding="utf-8")
    report_path = PACK_ROOT / "review/wechat/validation-report.json"
    report_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# WeChat Validation Report",
        "",
        f"- Pack ID: `{spec['packId']}`",
        f"- Title: {spec['title']}",
        f"- Overall: {'PASS' if validation['passed'] else 'FAIL'}",
        "",
        "## Checks",
        "",
    ]
    for check in validation["checks"]:
        mark = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- {mark}: {check['name']} - {check['detail']}")
    (PACK_ROOT / "review/wechat/validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    official = """# Official Spec Check

Current package validation is based on the active local WeChat Upload Contract captured in `AGENTS.md` for this repository.

Live public-web verification was attempted before production export in this session, but a directly accessible official requirements page was not available through public search. Before a real upload, re-check the logged-in WeChat Sticker Open Platform form/tooltips and update `AGENTS.md` or `spec.json` if the platform has changed.

Local contract enforced here:

- Static sticker PNG: 18 files, each `240x240`, transparent, `<=500KB`.
- Cover: `240x240` PNG, transparent, `<=500KB`.
- Icon: `50x50` PNG, transparent, `<=100KB`.
- Banner: `750x400` PNG/JPG, opaque, no text, `<=500KB`.
- Name: no more than 8 Chinese characters, no punctuation or spaces.
- Introduction: no more than 80 Chinese characters.
- Copyright: no more than 10 Chinese characters.
"""
    (PACK_ROOT / "review/wechat/official-spec-check.md").write_text(official, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    clear_outputs()
    spec = load_spec()
    items = [
        StickerItem(
            index=raw["index"],
            slug=raw["fileBase"],
            caption=raw["caption"],
            scene=raw["scene"],
            props=raw["props"],
            pose=raw["pose"],
        )
        for raw in spec["captions"]["items"]
    ]
    source_paths, draft_paths = build_from_sheets(items)
    cover, icon, banner = make_cover_and_icon()
    make_review_images(source_paths, draft_paths)
    export_stickers = [PACK_ROOT / "exports/wechat/stickers" / p.name for p in draft_paths]
    validation = validate(spec, export_stickers, cover, icon, banner)
    write_metadata_and_reports(spec, items, validation)
    if not validation["passed"]:
        failed = [c for c in validation["checks"] if not c["passed"]]
        raise SystemExit("Validation failed: " + "; ".join(f"{c['name']} ({c['detail']})" for c in failed))
    print("Generated WeChat package:", PACK_ROOT / "exports/wechat")


if __name__ == "__main__":
    main()
