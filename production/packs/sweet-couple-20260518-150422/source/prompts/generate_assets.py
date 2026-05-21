#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


PACK_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = PACK_ROOT / "spec.json"

RAW_DIR = PACK_ROOT / "generated" / "sheets" / "raw"
CAPTIONED_DIR = PACK_ROOT / "generated" / "sheets" / "captioned"
SOURCE_CROPS_DIR = PACK_ROOT / "generated" / "stickers" / "source-crops"
DRAFT_DIR = PACK_ROOT / "generated" / "stickers" / "wechat-draft"
REVIEW_MASTER_DIR = PACK_ROOT / "review" / "master"
REVIEW_SHEETS_DIR = PACK_ROOT / "review" / "sheets"
REVIEW_STICKERS_DIR = PACK_ROOT / "review" / "stickers"
REVIEW_WECHAT_DIR = PACK_ROOT / "review" / "wechat"
EXPORT_DIR = PACK_ROOT / "exports" / "wechat"
EXPORT_STICKERS_DIR = EXPORT_DIR / "stickers"
MASTER_APPROVED_PATH = PACK_ROOT / "master" / "approved" / "sweet-couple-approved-master.png"
ICON_SOURCE_PATH = PACK_ROOT / "master" / "approved" / "sweet-couple-approved-icon-source.png"
GENERATION_RECORD_PATH = PACK_ROOT / "source" / "prompts" / "generation-record.md"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

WHITE = (255, 255, 255, 255)
INK = (58, 39, 32, 255)
SHADOW = (239, 156, 55, 230)
BG_TOP = (235, 244, 255, 255)
BG_BOTTOM = (255, 226, 194, 255)
TEAL = (81, 167, 151, 255)
PEACH = (255, 181, 132, 255)
YELLOW = (255, 219, 104, 255)
PINK = (255, 181, 198, 255)
BROWN = (88, 61, 42, 255)
STONE = (214, 196, 172, 255)
SKY = (180, 220, 244, 255)


@dataclass(frozen=True)
class StickerItem:
    index: int
    slug: str
    caption: str
    scenario: str
    pose: str

    @property
    def filename(self) -> str:
        return f"{self.index:02d}-{self.slug}-{self.caption}.png"


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def save_spec(spec: dict[str, Any]) -> None:
    SPEC_PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def font_path() -> str:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("No usable Chinese font found")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path(), size=size)


def ensure_dirs() -> None:
    for path in [
        RAW_DIR,
        CAPTIONED_DIR,
        SOURCE_CROPS_DIR,
        DRAFT_DIR,
        REVIEW_MASTER_DIR,
        REVIEW_SHEETS_DIR,
        REVIEW_STICKERS_DIR,
        REVIEW_WECHAT_DIR,
        EXPORT_DIR,
        EXPORT_STICKERS_DIR,
        MASTER_APPROVED_PATH.parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def clear_outputs() -> None:
    keep_raw = {
        ".gitkeep",
        "sheet-01-raw-ai.png",
        "sheet-02-raw-ai.png",
    }
    for root in [CAPTIONED_DIR, SOURCE_CROPS_DIR, DRAFT_DIR, REVIEW_SHEETS_DIR, REVIEW_STICKERS_DIR, REVIEW_WECHAT_DIR]:
        for path in root.iterdir():
            if path.is_file() and path.name != ".gitkeep":
                path.unlink()
    for path in RAW_DIR.iterdir():
        if path.is_file() and path.name not in keep_raw:
            path.unlink()
    for path in EXPORT_STICKERS_DIR.iterdir():
        if path.is_file():
            path.unlink()
    for path in EXPORT_DIR.iterdir():
        if path.is_file():
            path.unlink()


def save_png(path: Path, image: Image.Image, max_bytes: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True, compress_level=9)
    if max_bytes and path.stat().st_size > max_bytes:
        if image.mode == "RGB":
            image.convert("P", palette=Image.Palette.ADAPTIVE, colors=192).save(path, "PNG", optimize=True, compress_level=9)
        else:
            image.save(path, "PNG", optimize=True, compress_level=9)


def key_to_alpha(image: Image.Image) -> Image.Image:
    arr = np.array(image.convert("RGBA")).astype(np.int16)
    red = arr[..., 0]
    green = arr[..., 1]
    blue = arr[..., 2]
    max_rb = np.maximum(red, blue)

    core = (green > 125) & (red < 135) & (blue < 135) & ((green - max_rb) > 42)
    soft = (green > 105) & (red < 155) & (blue < 155) & ((green - max_rb) > 22) & ~core

    alpha = np.full(green.shape, 255, dtype=np.float32)
    alpha[core] = 0
    alpha[soft] = np.clip(255 - (green[soft] - max_rb[soft] - 22) * 5, 0, 255)

    keep = alpha > 0
    arr[..., 1][keep] = np.minimum(arr[..., 1][keep], max_rb[keep] + 12)
    arr[..., 3] = alpha.astype(np.uint8)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    out.putalpha(out.getchannel("A").filter(ImageFilter.MedianFilter(3)))
    return out


def connected_components(mask: np.ndarray) -> list[dict[str, Any]]:
    h, w = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    components: list[dict[str, Any]] = []
    for sy, sx in zip(*np.where(mask & ~seen)):
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
            "pixels": pixels,
        })
    return components


def remove_small_components(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    components = [c for c in connected_components(alpha > 8) if c["area"] >= 12]
    if not components:
        return rgba

    main = max(components, key=lambda c: c["area"])
    main_area = main["area"]
    keep_alpha = np.zeros_like(alpha)
    for component in components:
        left, top, right, bottom = component["bbox"]
        width = right - left
        height = bottom - top
        area = component["area"]
        keep = (
            component is main
            or area >= 55
            or area >= main_area * 0.006
            or (area >= 24 and width >= 4 and height >= 4)
        )
        if keep:
            ys = [p[0] for p in component["pixels"]]
            xs = [p[1] for p in component["pixels"]]
            keep_alpha[ys, xs] = alpha[ys, xs]

    arr[..., 3] = keep_alpha
    return Image.fromarray(arr, "RGBA")


def clear_edges(image: Image.Image, margin: int = 4) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    draw = ImageDraw.Draw(alpha)
    draw.rectangle((0, 0, rgba.width, margin), fill=0)
    draw.rectangle((0, rgba.height - margin, rgba.width, rgba.height), fill=0)
    draw.rectangle((0, 0, margin, rgba.height), fill=0)
    draw.rectangle((rgba.width - margin, 0, rgba.width, rgba.height), fill=0)
    rgba.putalpha(alpha)
    return rgba


def crop_alpha(image: Image.Image, padding: int = 8) -> Image.Image:
    rgba = image.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if not bbox:
        return rgba
    left, top, right, bottom = bbox
    return rgba.crop((
        max(0, left - padding),
        max(0, top - padding),
        min(rgba.width, right + padding),
        min(rgba.height, bottom + padding),
    ))


def contain(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / image.width, max_h / image.height, 1.0)
    new_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def draw_caption(canvas: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(canvas)
    size = 66
    stroke = 8
    while size >= 40:
        fnt = font(size)
        bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
        if bbox[2] - bbox[0] <= 420:
            break
        size -= 2
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas.width - text_w) // 2 - bbox[0]
    y = 444 - text_h - bbox[1]
    draw.text((x + 5, y + 7), text, font=fnt, fill=SHADOW, stroke_width=stroke, stroke_fill=SHADOW)
    draw.text((x, y), text, font=fnt, fill=WHITE, stroke_width=stroke, stroke_fill=INK)


def compose_sticker(crop: Image.Image, item: StickerItem) -> Image.Image:
    clean = crop_alpha(remove_small_components(crop), padding=6)
    max_h = 305 if len(item.caption) >= 4 else 318
    subject = contain(clean, 420, max_h)
    canvas = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
    x = (480 - subject.width) // 2
    y = 34 if subject.height >= 300 else 42
    canvas.alpha_composite(subject, (x, y))
    draw_caption(canvas, item.caption)
    return canvas.resize((240, 240), Image.Resampling.LANCZOS)


def extract_sheet_cells(path: Path, count: int = 9) -> list[Image.Image]:
    if not path.exists():
        raise FileNotFoundError(path)
    raw = Image.open(path).convert("RGBA")
    save_png(path.with_name(path.name.replace("-raw-ai", "-raw-transparent")), key_to_alpha(raw))
    cell_w = raw.width // 3
    cell_h = raw.height // 3
    cells: list[Image.Image] = []
    for i in range(count):
        row = i // 3
        col = i % 3
        cell = raw.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
        alpha = clear_edges(key_to_alpha(cell), margin=4)
        cells.append(crop_alpha(remove_small_components(alpha), padding=10))
    return cells


def build_stickers(items: list[StickerItem]) -> tuple[list[Path], list[Image.Image], list[Image.Image]]:
    cells: list[Image.Image] = []
    cells.extend(extract_sheet_cells(RAW_DIR / "sheet-01-raw-ai.png", 9))
    cells.extend(extract_sheet_cells(RAW_DIR / "sheet-02-raw-ai.png", 9))
    if len(cells) != len(items):
        raise RuntimeError(f"Expected {len(items)} raw cells, got {len(cells)}")

    draft_paths: list[Path] = []
    source_crops: list[Image.Image] = []
    stickers: list[Image.Image] = []
    for item, crop in zip(items, cells):
        source_path = SOURCE_CROPS_DIR / item.filename
        save_png(source_path, crop)

        sticker = compose_sticker(crop, item)
        draft_path = DRAFT_DIR / item.filename
        export_path = EXPORT_STICKERS_DIR / item.filename
        save_png(draft_path, sticker, max_bytes=512000)
        shutil.copy2(draft_path, export_path)

        draft_paths.append(draft_path)
        source_crops.append(crop)
        stickers.append(sticker)
    return draft_paths, source_crops, stickers


def make_captioned_sheets(stickers: list[Image.Image]) -> None:
    for sheet_idx in range(math.ceil(len(stickers) / 9)):
        transparent = Image.new("RGBA", (720, 720), (0, 0, 0, 0))
        review = Image.new("RGB", (720, 720), (242, 236, 225))
        tile_bg = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
        for j, sticker in enumerate(stickers[sheet_idx * 9:(sheet_idx + 1) * 9]):
            x = (j % 3) * 240
            y = (j // 3) * 240
            transparent.alpha_composite(sticker, (x, y))
            tile = tile_bg.copy()
            tile.alpha_composite(sticker)
            review.paste(tile.convert("RGB"), (x, y))
        save_png(CAPTIONED_DIR / f"sheet-{sheet_idx + 1:02d}-captioned.png", transparent)
        save_png(REVIEW_SHEETS_DIR / f"sheet-{sheet_idx + 1:02d}-review.png", review)


def paste_fit(base: Image.Image, crop: Image.Image, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    fitted = contain(crop_alpha(crop), right - left, bottom - top)
    x = left + (right - left - fitted.width) // 2
    y = top + (bottom - top - fitted.height) // 2
    base.alpha_composite(fitted, (x, y))


def make_cover() -> Image.Image:
    master = Image.open(MASTER_APPROVED_PATH).convert("RGBA")
    crop = crop_alpha(master, padding=0)
    fitted = contain(crop, 220, 220)
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    canvas.alpha_composite(fitted, ((240 - fitted.width) // 2, (240 - fitted.height) // 2))
    return canvas


def make_icon() -> Image.Image:
    source_path = ICON_SOURCE_PATH if ICON_SOURCE_PATH.exists() else MASTER_APPROVED_PATH
    icon_source = Image.open(source_path).convert("RGBA")
    bbox = icon_source.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError("Icon source has empty alpha")
    # Dedicated two-head icon source: full heads/chins only, no chopped torsos.
    crop = crop_alpha(icon_source.crop(bbox), padding=2)
    fitted = contain(crop, 42, 42)
    canvas = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    canvas.alpha_composite(fitted, ((50 - fitted.width) // 2, (50 - fitted.height) // 2))
    return canvas


def make_banner(source_crops: list[Image.Image]) -> Image.Image:
    bg = Image.new("RGBA", (750, 400), BG_TOP)
    draw = ImageDraw.Draw(bg)
    for y in range(400):
        t = y / 399
        color = tuple(round(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(4))
        draw.line((0, y, 750, y), fill=color)

    # Generic museum/travel background only: no logos, text, or specific copyrighted artwork.
    draw.rectangle((0, 280, 750, 400), fill=(236, 218, 194, 255))
    draw.polygon([(0, 280), (750, 280), (690, 400), (60, 400)], fill=(222, 204, 181, 255))
    for x in (80, 210, 540, 670):
        draw.rectangle((x, 92, x + 54, 285), fill=STONE)
        draw.rectangle((x - 10, 82, x + 64, 98), fill=(196, 174, 148, 255))
        draw.rectangle((x - 14, 278, x + 68, 292), fill=(188, 165, 139, 255))
    draw.polygon([(38, 92), (375, 28), (712, 92)], fill=(195, 174, 150, 255))
    draw.rectangle((46, 92, 704, 112), fill=(181, 158, 132, 255))
    for x in (330, 370, 410):
        draw.arc((x - 34, 148, x + 34, 286), 180, 360, fill=(168, 147, 124, 255), width=6)
    for x, y, r, color in [
        (70, 58, 9, (255, 246, 196, 255)),
        (168, 132, 6, YELLOW),
        (276, 74, 8, PEACH),
        (472, 78, 7, (255, 246, 196, 255)),
        (606, 126, 9, PINK),
        (690, 56, 7, YELLOW),
    ]:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    paste_fit(bg, source_crops[0], (34, 94, 208, 350))
    paste_fit(bg, source_crops[2], (214, 70, 388, 342))
    paste_fit(bg, source_crops[11], (392, 88, 568, 354))
    paste_fit(bg, source_crops[17], (552, 78, 728, 348))
    return bg.convert("RGB")


def make_contact_sheet(images: list[Image.Image], labels: list[str] | None = None, cols: int = 5) -> Image.Image:
    cell = 240
    label_h = 38 if labels else 0
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (240, 235, 226))
    draw = ImageDraw.Draw(sheet)
    small = font(18)
    for i, image in enumerate(images):
        col = i % cols
        row = i // cols
        x = col * cell
        y = row * (cell + label_h)
        draw.rounded_rectangle((x + 8, y + 8, x + cell - 8, y + cell - 8), radius=12, fill=(255, 255, 255), outline=(221, 206, 187), width=2)
        render = contain(image, cell - 18, cell - 18)
        tile = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
        tile.alpha_composite(render, ((cell - render.width) // 2, (cell - render.height) // 2))
        sheet.paste(tile.convert("RGB"), (x, y))
        if labels:
            draw.text((x + 14, y + cell + 6), labels[i], font=small, fill=(78, 62, 49))
    return sheet


def make_review_images(source_crops: list[Image.Image], stickers: list[Image.Image], cover: Image.Image, icon: Image.Image, banner: Image.Image, items: list[StickerItem]) -> None:
    master = Image.open(MASTER_APPROVED_PATH).convert("RGBA")
    labels = [f"{item.index:02d} {item.caption}" for item in items]
    source_contact = make_contact_sheet(source_crops, labels=labels, cols=5)
    sticker_contact = make_contact_sheet(stickers, labels=labels, cols=5)
    save_png(REVIEW_STICKERS_DIR / "source-crops-contact-sheet.png", source_contact)
    save_png(REVIEW_STICKERS_DIR / "final-stickers-contact-sheet.png", sticker_contact)

    identity = Image.new("RGB", (1280, 860), (248, 242, 231))
    draw = ImageDraw.Draw(identity)
    draw.text((34, 28), "Sweet couple identity review", font=font(34), fill=(70, 48, 34))
    draw.text((34, 76), "Left: approved master. Right: model-derived source crops. Use this to reject identity drift.", font=font(20), fill=(88, 65, 48))
    master_tile = Image.new("RGBA", (360, 520), (255, 255, 255, 255))
    fitted = contain(crop_alpha(master), 330, 490)
    master_tile.alpha_composite(fitted, ((360 - fitted.width) // 2, (520 - fitted.height) // 2))
    identity.paste(master_tile.convert("RGB"), (34, 124))
    identity.paste(source_contact.resize((820, 626), Image.Resampling.LANCZOS), (424, 124))
    save_png(REVIEW_WECHAT_DIR / "master-output-identity-review.png", identity)

    overview = Image.new("RGB", (1320, 1000), (246, 247, 249))
    draw = ImageDraw.Draw(overview)
    draw.text((34, 24), "Sweet Couple Travel WeChat export review", font=font(30), fill=(30, 34, 40))
    draw.text((34, 68), "18 stickers, cover, icon, banner; upload assets only are in exports/wechat.", font=font(20), fill=(78, 86, 98))
    overview.paste(sticker_contact.resize((760, 608), Image.Resampling.LANCZOS), (34, 112))
    overview.paste(banner.resize((420, 224), Image.Resampling.LANCZOS), (850, 112))
    cover_bg = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
    cover_bg.alpha_composite(cover)
    overview.paste(cover_bg.convert("RGB"), (850, 380))
    icon_bg = Image.new("RGBA", (120, 120), (255, 255, 255, 255))
    icon_bg.alpha_composite(icon.resize((100, 100), Image.Resampling.NEAREST), (10, 10))
    overview.paste(icon_bg.convert("RGB"), (1135, 380))
    draw.text((850, 626), "cover.png", font=font(18), fill=(78, 86, 98))
    draw.text((1135, 506), "icon 2x", font=font(18), fill=(78, 86, 98))
    save_png(REVIEW_WECHAT_DIR / "export-assets-overview.png", overview)

    scale = 8
    checker = Image.new("RGBA", (50 * scale, 50 * scale), (255, 255, 255, 255))
    checker_draw = ImageDraw.Draw(checker)
    cell = 5 * scale
    for y in range(0, checker.height, cell):
        for x in range(0, checker.width, cell):
            if ((x // cell) + (y // cell)) % 2:
                checker_draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(210, 210, 210, 255))
    checker.alpha_composite(icon.resize((50 * scale, 50 * scale), Image.Resampling.NEAREST))
    save_png(REVIEW_WECHAT_DIR / "icon-checkerboard-8x.png", checker.convert("RGB"))


def alpha_margins(path: Path) -> dict[str, int] | None:
    with Image.open(path) as img:
        rgba = img.convert("RGBA")
        arr = np.array(rgba)
        mask = arr[..., 3] > 8
        if not mask.any():
            return None
        ys, xs = np.where(mask)
        left = int(xs.min())
        right = int(rgba.width - 1 - xs.max())
        top = int(ys.min())
        bottom = int(rgba.height - 1 - ys.max())
        return {"left": left, "top": top, "right": right, "bottom": bottom}


def image_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as img:
        rgba = img.convert("RGBA")
        info: dict[str, Any] = {
            "path": str(path.relative_to(PACK_ROOT)),
            "format": img.format,
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "bytes": path.stat().st_size,
            "hasAlpha": "A" in rgba.getbands() and rgba.getchannel("A").getextrema()[0] < 255,
            "cornerAlpha": [
                rgba.getpixel((0, 0))[3],
                rgba.getpixel((img.width - 1, 0))[3],
                rgba.getpixel((0, img.height - 1))[3],
                rgba.getpixel((img.width - 1, img.height - 1))[3],
            ],
        }
        margins = alpha_margins(path)
        if margins is not None:
            info["alphaMargins"] = margins
        return info


def validate(spec: dict[str, Any], sticker_paths: list[Path], cover_path: Path, icon_path: Path, banner_path: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected_count = spec["wechatTarget"]["stickerCount"]
    add("sticker-count-is-18", len(sticker_paths) == expected_count, f"found {len(sticker_paths)} PNG stickers")
    min_pad = spec["wechatTarget"]["sticker"]["safeArea"]["minPaddingPx"]
    min_top = spec["wechatTarget"]["sticker"]["safeArea"]["minTopPaddingPx"]
    for path in sticker_paths:
        info = image_info(path)
        margins = info.get("alphaMargins")
        safe = margins is not None and margins["left"] >= min_pad and margins["right"] >= min_pad and margins["bottom"] >= min_pad and margins["top"] >= min_top
        add(
            f"{path.name}: png-240x240-alpha-transparent-corners-under-500kb-safe-area",
            info["format"] == "PNG"
            and info["width"] == 240
            and info["height"] == 240
            and info["hasAlpha"]
            and max(info["cornerAlpha"]) == 0
            and info["bytes"] <= spec["wechatTarget"]["sticker"]["maxBytes"]
            and safe,
            f"format={info['format']}, size={info['width']}x{info['height']}, corners={info['cornerAlpha']}, bytes={info['bytes']}, margins={margins}",
        )

    for label, path, target in [
        ("cover", cover_path, spec["wechatTarget"]["cover"]),
        ("icon", icon_path, spec["wechatTarget"]["icon"]),
    ]:
        info = image_info(path)
        margins = info.get("alphaMargins")
        add(
            f"{label}: dimension-alpha-size",
            info["format"] == "PNG"
            and info["width"] == target["width"]
            and info["height"] == target["height"]
            and info["hasAlpha"]
            and max(info["cornerAlpha"]) == 0
            and info["bytes"] <= target["maxBytes"],
            f"format={info['format']}, size={info['width']}x{info['height']}, corners={info['cornerAlpha']}, bytes={info['bytes']}, margins={margins}",
        )
        if label == "icon":
            safe = target.get("safeArea", {})
            min_pad = safe.get("minTransparentPaddingPx", 4)
            min_bottom = safe.get("minBottomPaddingBelowChinPx", 6)
            icon_safe = (
                margins is not None
                and margins["left"] >= min_pad
                and margins["right"] >= min_pad
                and margins["top"] >= min_pad
                and margins["bottom"] >= min_bottom
            )
            add(
                "icon: alpha-safe-area-padding",
                icon_safe,
                f"required side>={min_pad}, bottom>={min_bottom}, margins={margins}",
            )

    banner = image_info(banner_path)
    target = spec["wechatTarget"]["banner"]
    add(
        "banner: dimension-opaque-size",
        banner["format"] == "PNG"
        and banner["width"] == target["width"]
        and banner["height"] == target["height"]
        and not banner["hasAlpha"]
        and banner["bytes"] <= target["maxBytes"],
        f"format={banner['format']}, mode={banner['mode']}, size={banner['width']}x{banner['height']}, bytes={banner['bytes']}",
    )

    form = spec["wechatTarget"]["form"]
    name = form["name"]["value"]
    intro = form["introduction"]["value"]
    copyright_text = form["copyright"]["value"]
    add("form-name-under-8-no-punctuation-no-spaces", len(name) <= 8 and " " not in name and all(ch not in name for ch in "，。！？、,.!?"), name)
    add("form-introduction-under-80", len(intro) <= 80, intro)
    add("form-copyright-under-10", len(copyright_text) <= 10, copyright_text)

    record_text = GENERATION_RECORD_PATH.read_text(encoding="utf-8") if GENERATION_RECORD_PATH.exists() else ""
    add("source-linkage-approved-master-exists", MASTER_APPROVED_PATH.exists(), str(MASTER_APPROVED_PATH.relative_to(PACK_ROOT)))
    add("source-linkage-generation-record-names-approved-master", "master/approved/sweet-couple-approved-master.png" in record_text, "generation-record.md contains approved master path")
    add("source-linkage-raw-sheets-exist", (RAW_DIR / "sheet-01-raw-ai.png").exists() and (RAW_DIR / "sheet-02-raw-ai.png").exists(), "two image-model raw sheets exist")

    allowed_root_files = {"cover.png", "icon.png", "banner.png", "metadata.json", "form.md"}
    unexpected = [p.name for p in EXPORT_DIR.iterdir() if p.is_file() and p.name not in allowed_root_files]
    add("wechat-export-root-has-only-upload-files", not unexpected, f"unexpected={unexpected}")
    unexpected_sticker_files = [p.name for p in EXPORT_STICKERS_DIR.iterdir() if p.is_file() and p.suffix.lower() != ".png"]
    add("stickers-dir-has-only-png-upload-files", not unexpected_sticker_files, f"unexpected={unexpected_sticker_files}")
    add("metadata-json-exists", (EXPORT_DIR / "metadata.json").exists(), "exports/wechat/metadata.json")
    add("form-md-exists", (EXPORT_DIR / "form.md").exists(), "exports/wechat/form.md")

    return {
        "packId": spec["packId"],
        "title": spec["title"],
        "generatedBy": "source/prompts/generate_assets.py",
        "passed": all(check["passed"] for check in checks),
        "generatedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "checks": checks,
        "assets": {
            "stickers": [image_info(path) for path in sticker_paths],
            "cover": image_info(cover_path),
            "icon": image_info(icon_path),
            "banner": image_info(banner_path),
        },
        "manualReviewRequired": [
            "identity-preservation-against-master-output-identity-review",
            "semantic-variation-with-captions-hidden",
            "caption-readability-at-small-size",
            "cover-icon-no-white-background-or-square-frame",
            "banner-has-no-text",
        ],
    }


def write_semantic_variation_report(items: list[StickerItem]) -> None:
    lines = [
        "# Semantic Variation Checklist",
        "",
        "Automated validation cannot prove expression quality. Human review must reject the package if most stickers look duplicated when captions are ignored.",
        "",
        "## Planned per-sticker action",
        "",
    ]
    for item in items:
        lines.append(f"- {item.index:02d} `{item.caption}`: {item.pose}")
    lines.extend([
        "",
        "## Manual review rule",
        "",
        "- Check `review/stickers/source-crops-contact-sheet.png` with captions ignored.",
        "- Check `review/stickers/final-stickers-contact-sheet.png` at small display size.",
        "- Reject or regenerate any sticker whose emotion/action is only explained by the caption.",
    ])
    (REVIEW_WECHAT_DIR / "semantic-variation-checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_metadata_form_reports(spec: dict[str, Any], items: list[StickerItem], validation: dict[str, Any]) -> None:
    stickers = [
        {
            "index": item.index,
            "caption": item.caption,
            "scenario": item.scenario,
            "pose": item.pose,
            "exportPath": f"stickers/{item.filename}",
        }
        for item in items
    ]
    metadata = {
        "packId": spec["packId"],
        "platform": spec["platform"],
        "title": spec["title"],
        "description": spec["description"],
        "copyright": spec["copyright"],
        "packType": spec["wechatTarget"]["packType"],
        "stickerCount": spec["wechatTarget"]["stickerCount"],
        "sourceLinkage": {
            "inputMode": spec["inputMode"]["selected"],
            "approvedMaster": str(MASTER_APPROVED_PATH.relative_to(PACK_ROOT)),
            "approvedIconSource": str(ICON_SOURCE_PATH.relative_to(PACK_ROOT)) if ICON_SOURCE_PATH.exists() else None,
            "sourceReference": "source/references/sweet-couple-reference.png",
            "masterInput": "master/input/sweet-couple-master-reference.png",
            "identityPreservationMethod": "master candidate and raw sticker sheets generated by image model after the reference/approved master image was loaded as visual reference; local script only processed model outputs",
        },
        "assets": {
            "stickers": stickers,
            "cover": "cover.png",
            "icon": "icon.png",
            "banner": "banner.png",
        },
        "validation": {
            "report": "review/wechat/validation-report.json",
            "passed": validation["passed"],
            "manualReviewRequired": validation["manualReviewRequired"],
        },
        "trace": {
            "rawSheets": [
                "generated/sheets/raw/sheet-01-raw-ai.png",
                "generated/sheets/raw/sheet-02-raw-ai.png",
            ],
            "generationRecord": "source/prompts/generation-record.md",
            "localProcessor": "source/prompts/generate_assets.py",
        },
    }
    (EXPORT_DIR / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    form = spec["wechatTarget"]["form"]
    lines = [
        "# 微信表情开放平台表单信息",
        "",
        "状态：本地机械校验通过，真实提交前仍需人工复核身份一致性、语义差异和平台最新规则。",
        "",
        "## 上传表情",
        "",
        "- 类型：静态表情",
        f"- 表情：上传 `stickers/` 下的 {spec['wechatTarget']['stickerCount']} 张 `240x240` 透明 PNG 图片",
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
        "## 复核提醒",
        "",
        "- 表情 caption 已按 `spec.json` 本地合成，上传前请人工复核小图可读性。",
        "- 上传前请人工复核欧洲/博物馆元素是否过于接近真实地标、馆方标识或具体艺术作品。",
        "- 真实提交前请重新确认微信表情开放平台页面的最新尺寸、格式、数量和文案规则。",
    ]
    (EXPORT_DIR / "form.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (REVIEW_WECHAT_DIR / "validation-report.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_lines = [
        "# WeChat Validation Report",
        "",
        f"- Pack ID: `{spec['packId']}`",
        f"- Title: {spec['title']}",
        f"- Overall: {'PASS' if validation['passed'] else 'FAIL'}",
        f"- Generated at: {validation['generatedAt']}",
        "",
        "## Checks",
        "",
    ]
    for check in validation["checks"]:
        mark = "PASS" if check["passed"] else "FAIL"
        report_lines.append(f"- {mark}: {check['name']} - {check['detail']}")
    report_lines.extend([
        "",
        "## Manual Review Required",
        "",
    ])
    for item in validation["manualReviewRequired"]:
        report_lines.append(f"- {item}")
    (REVIEW_WECHAT_DIR / "validation-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    official = """# Official Spec Check

Current package validation is based on the active local WeChat Upload Contract captured in `AGENTS.md` for this repository.

Before a real upload, re-check the logged-in WeChat Sticker Open Platform form/tooltips and update `AGENTS.md` or `spec.json` if the platform has changed.

Local contract enforced here:

- Static sticker PNG: 18 files, each `240x240`, transparent, `<=500KB`.
- Cover: `240x240` PNG, transparent, `<=500KB`.
- Icon: `50x50` PNG, transparent, `<=100KB`.
- Banner: `750x400` PNG/JPG, opaque, no text, `<=500KB`.
- Name: no more than 8 Chinese characters, no punctuation or spaces.
- Introduction: no more than 80 Chinese characters.
- Copyright: no more than 10 Chinese characters.
"""
    (REVIEW_WECHAT_DIR / "official-spec-check.md").write_text(official, encoding="utf-8")


def append_generation_record() -> None:
    marker = "## Raw Sticker Sheets 2026-05-18"
    text = GENERATION_RECORD_PATH.read_text(encoding="utf-8") if GENERATION_RECORD_PATH.exists() else """# Generation Record

- Pack: `sweet-couple-20260518-150422`
- Input mode: `image-to-master`
- Local processing not allowed for final artwork: no local drawing of face, eyes, mouth, hair, pose, hands, props, or action marks.

## Master Candidate 01

- Built-in generated source: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0abf4a33148195855297f231ba3bbe.png`
- Chroma-key source: `master/candidates/sweet-couple-master-candidate-01-chromakey.png`
- Transparent candidate: `master/candidates/sweet-couple-master-candidate-01.png`
- Review comparison: `review/master/master-candidate-review-01.png`
- Approved continuation source: `master/approved/sweet-couple-approved-master.png`
- Continuation approval: user invoked `/goal` on 2026-05-18 to generate the full pack under the current repository constraints.

## Prompt Summary

Create a clean anime/chibi master candidate from the visible young married couple reference image. Preserve the girl's long dark-brown hair, large brown eyes, navy outer layer and light top, and preserve the boy's short black hair, black rectangular glasses, gray hoodie and teal shirt. Use a flat green chroma-key background for local background removal. No text, watermark, logo, extra people, specific museum branding, or copied decorative background.
"""
    if marker in text:
        return
    addition = f"""

{marker}

- Built-in generated source sheet 1: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0ac0ad6d508195a9ccf057fe30762a.png`
- Built-in generated source sheet 2: `/Users/yinshawnrao/.codex/generated_images/019e39e5-ce38-7203-ba4b-c63edc5f5455/ig_09e3e297252b839a016a0ac12523508195b70f285395119b1f.png`
- Workspace raw sheet 1: `generated/sheets/raw/sheet-01-raw-ai.png`
- Workspace raw sheet 2: `generated/sheets/raw/sheet-02-raw-ai.png`
- Identity method: the approved master `master/approved/sweet-couple-approved-master.png` was loaded into the conversation and used as the visual reference for both image-model raw sheets.
- Local processing method: `source/prompts/generate_assets.py` removes chroma-key background, crops model outputs, renders exact captions from `spec.json`, creates WeChat-size PNGs, cover, icon, banner, review sheets, metadata, and validation reports. It does not draw or alter character face, eyes, mouth, hair, pose, hands, props, or action marks.
"""
    GENERATION_RECORD_PATH.write_text(text.rstrip() + addition + "\n", encoding="utf-8")


def update_spec_after_build(spec: dict[str, Any], validation: dict[str, Any]) -> None:
    now = validation["generatedAt"]
    spec["workflowPhase"] = "wechat-export-generated-pending-human-review" if validation["passed"] else "wechat-export-needs-fix"
    spec["status"] = "local-mechanical-validation-passed-pending-human-review" if validation["passed"] else "local-mechanical-validation-failed"
    spec["masterCharacter"]["status"] = "approved-master-and-model-derived-assets-generated"
    spec["masterCharacter"]["approvedImage"] = str(MASTER_APPROVED_PATH.relative_to(PACK_ROOT))
    spec["masterCharacter"]["approvalRequired"] = False
    spec["masterCharacter"]["finalStickerProductionAllowed"] = True
    spec["captions"]["status"] = "locked-and-composed"
    spec["assets"].setdefault("generated", {})
    spec["assets"]["generated"]["approvedMaster"] = str(MASTER_APPROVED_PATH.relative_to(PACK_ROOT))
    spec["assets"]["generated"]["rawSheets"] = [
        "generated/sheets/raw/sheet-01-raw-ai.png",
        "generated/sheets/raw/sheet-02-raw-ai.png",
        "generated/sheets/raw/sheet-01-raw-transparent.png",
        "generated/sheets/raw/sheet-02-raw-transparent.png",
    ]
    spec["assets"]["generated"]["captionedSheets"] = [
        "generated/sheets/captioned/sheet-01-captioned.png",
        "generated/sheets/captioned/sheet-02-captioned.png",
    ]
    spec["assets"]["generated"]["review"] = [
        "review/master/master-candidate-review-01.png",
        "review/stickers/source-crops-contact-sheet.png",
        "review/stickers/final-stickers-contact-sheet.png",
        "review/wechat/master-output-identity-review.png",
        "review/wechat/export-assets-overview.png",
        "review/wechat/icon-checkerboard-8x.png",
        "review/wechat/validation-report.json",
        "review/wechat/semantic-variation-checklist.md",
    ]
    spec["assets"]["wechatExport"]["generatedAt"] = now
    spec["assets"]["wechatExport"]["uploadReady"] = False
    spec["assets"]["wechatExport"]["localMechanicalValidationPassed"] = bool(validation["passed"])
    spec["assets"]["wechatExport"]["validationReport"] = "review/wechat/validation-report.json"
    spec["assets"]["wechatExport"]["manualReviewRequired"] = validation["manualReviewRequired"]
    save_spec(spec)


def main() -> None:
    ensure_dirs()
    clear_outputs()
    spec = load_spec()
    items = [
        StickerItem(
            index=raw["id"],
            slug=raw["slug"],
            caption=raw["text"],
            scenario=raw["scenario"],
            pose=raw["pose"],
        )
        for raw in spec["captions"]["items"]
    ]
    if len(items) != spec["wechatTarget"]["stickerCount"]:
        raise RuntimeError(f"Caption count mismatch: {len(items)} vs target {spec['wechatTarget']['stickerCount']}")
    if not MASTER_APPROVED_PATH.exists():
        raise FileNotFoundError(MASTER_APPROVED_PATH)

    draft_paths, source_crops, stickers = build_stickers(items)
    make_captioned_sheets(stickers)

    cover = make_cover()
    icon = make_icon()
    banner = make_banner(source_crops)
    cover_path = EXPORT_DIR / "cover.png"
    icon_path = EXPORT_DIR / "icon.png"
    banner_path = EXPORT_DIR / "banner.png"
    save_png(cover_path, cover, max_bytes=512000)
    save_png(icon_path, icon, max_bytes=102400)
    save_png(banner_path, banner, max_bytes=512000)

    make_review_images(source_crops, stickers, cover, icon, banner, items)
    write_semantic_variation_report(items)
    append_generation_record()

    export_stickers = [EXPORT_STICKERS_DIR / path.name for path in draft_paths]
    validation = validate(spec, export_stickers, cover_path, icon_path, banner_path)
    write_metadata_form_reports(spec, items, validation)
    validation = validate(spec, export_stickers, cover_path, icon_path, banner_path)
    write_metadata_form_reports(spec, items, validation)
    update_spec_after_build(spec, validation)

    if not validation["passed"]:
        failed = [check for check in validation["checks"] if not check["passed"]]
        raise SystemExit("Validation failed: " + json.dumps(failed, ensure_ascii=False, indent=2))
    print(f"Generated WeChat package: {EXPORT_DIR}")


if __name__ == "__main__":
    main()
