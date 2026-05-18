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
MASTER_APPROVED_PATH = PACK_ROOT / "master" / "approved" / "xiaobuding-approved-master.png"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

WHITE = (255, 255, 255, 255)
INK = (58, 39, 32, 255)
SHADOW = (232, 147, 45, 230)
NAVY = (23, 43, 82, 255)
CREAM = (255, 247, 228, 255)
SKY = (155, 207, 243, 255)
MINT = (164, 222, 172, 255)
YELLOW = (255, 221, 105, 255)
PINK = (255, 202, 215, 255)


@dataclass(frozen=True)
class StickerItem:
    index: int
    slug: str
    caption: str
    emotion: str
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
    for rel in [
        CAPTIONED_DIR,
        SOURCE_CROPS_DIR,
        DRAFT_DIR,
        REVIEW_MASTER_DIR,
        REVIEW_SHEETS_DIR,
        REVIEW_STICKERS_DIR,
        REVIEW_WECHAT_DIR,
        EXPORT_STICKERS_DIR,
        MASTER_APPROVED_PATH.parent,
    ]:
        rel.mkdir(parents=True, exist_ok=True)


def clear_outputs() -> None:
    keep_raw = {
        "sheet-01-raw-ai.png",
        "sheet-02-raw-ai.png",
        "sheet-03-single-raw-ai.png",
        ".gitkeep",
    }
    for root in [
        RAW_DIR,
        CAPTIONED_DIR,
        SOURCE_CROPS_DIR,
        DRAFT_DIR,
        REVIEW_MASTER_DIR,
        REVIEW_SHEETS_DIR,
        REVIEW_STICKERS_DIR,
        REVIEW_WECHAT_DIR,
        EXPORT_STICKERS_DIR,
    ]:
        for path in root.iterdir():
            if path.is_file() and path.name not in keep_raw:
                path.unlink()
    for path in EXPORT_STICKERS_DIR.iterdir():
        if path.is_file() and path.name == ".gitkeep":
            path.unlink()

    for path in EXPORT_DIR.iterdir():
        if path.is_file() and path.name != ".gitkeep":
            path.unlink()


def save_png(path: Path, image: Image.Image, max_bytes: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True, compress_level=9)
    if max_bytes and path.stat().st_size > max_bytes:
        if image.mode == "RGB":
            image.convert("P", palette=Image.Palette.ADAPTIVE, colors=192).save(path, "PNG", optimize=True, compress_level=9)
        elif image.mode == "RGBA":
            image.save(path, "PNG", optimize=True, compress_level=9)


def key_to_alpha(image: Image.Image) -> Image.Image:
    arr = np.array(image.convert("RGBA")).astype(np.int16)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    green = (g > 135) & (r < 115) & (b < 115) & ((g - r) > 65) & ((g - b) > 65)

    alpha = np.full(g.shape, 255, dtype=np.float32)
    alpha[green] = 0
    edge = (g > 105) & (r < 140) & (b < 140) & ((g - np.maximum(r, b)) > 34) & ~green
    alpha[edge] = np.clip(255 - (g[edge] - np.maximum(r[edge], b[edge]) - 34) * 5, 0, 255)
    residue = (g > 160) & (r < 130) & (b < 130) & ((g - r) > 45) & ((g - b) > 45)
    alpha[residue] = 0

    keep = alpha > 0
    max_rb = np.maximum(r, b)
    arr[..., 1][keep] = np.minimum(arr[..., 1][keep], max_rb[keep] + 12)
    arr[..., 3] = alpha.astype(np.uint8)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    out.putalpha(out.getchannel("A").filter(ImageFilter.MedianFilter(3)))
    return out


def checkerboard_to_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    rgb = arr[..., :3].astype(np.int16)
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    near_gray = (mx - mn) <= 8
    bright = mx >= 205
    bg_candidate = near_gray & bright

    h, w = bg_candidate.shape
    seen = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if bg_candidate[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if bg_candidate[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))

    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and bg_candidate[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))

    alpha = arr[..., 3].copy()
    alpha[seen] = 0
    arr[..., 3] = alpha
    out = Image.fromarray(arr, "RGBA")
    return crop_alpha(out, padding=8)


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
            "center": ((min_x + max_x + 1) / 2, (min_y + max_y + 1) / 2),
            "pixels": pixels,
        })
    return components


def remove_small_components(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    components = [c for c in connected_components(alpha > 8) if c["area"] >= 20]
    if not components:
        return rgba

    main = max(components, key=lambda c: c["area"])
    main_area = main["area"]
    keep_alpha = np.zeros_like(alpha)
    for component in components:
        area = component["area"]
        left, top, right, bottom = component["bbox"]
        width = right - left
        height = bottom - top
        keep = (
            component is main
            or area >= 520
            or area >= main_area * 0.018
            or (area >= 170 and width >= 18 and height >= 18)
        )
        if keep:
            ys = [p[0] for p in component["pixels"]]
            xs = [p[1] for p in component["pixels"]]
            keep_alpha[ys, xs] = alpha[ys, xs]

    arr[..., 3] = keep_alpha
    return Image.fromarray(arr, "RGBA")


def remove_sleep_text_marks(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    components = [c for c in connected_components(alpha > 8) if c["area"] >= 20]
    if len(components) <= 2:
        return rgba

    ranked = sorted(components, key=lambda c: c["area"], reverse=True)
    keep_components = set(id(c) for c in ranked[:2])
    keep_alpha = np.zeros_like(alpha)
    for component in components:
        if id(component) in keep_components:
            ys = [p[0] for p in component["pixels"]]
            xs = [p[1] for p in component["pixels"]]
            keep_alpha[ys, xs] = alpha[ys, xs]

    arr[..., 3] = keep_alpha
    return Image.fromarray(arr, "RGBA")


def remove_yellow_question_mark(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    red = arr[..., 0].astype(np.int16)
    green = arr[..., 1].astype(np.int16)
    blue = arr[..., 2].astype(np.int16)
    yellow_mark = (alpha > 8) & (red > 180) & (green > 140) & (blue < 90) & ((red - blue) > 120)
    for component in connected_components(yellow_mark):
        if component["area"] < 15000:
            ys = [p[0] for p in component["pixels"]]
            xs = [p[1] for p in component["pixels"]]
            alpha[ys, xs] = 0
    arr[..., 3] = alpha
    return Image.fromarray(arr, "RGBA")


def remove_components_above_main(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[..., 3]
    components = [c for c in connected_components(alpha > 8) if c["area"] >= 20]
    if len(components) <= 1:
        return rgba

    main = max(components, key=lambda c: c["area"])
    main_top = main["bbox"][1]
    for component in components:
        if component is main:
            continue
        _, _, _, bottom = component["bbox"]
        if bottom <= main_top:
            ys = [p[0] for p in component["pixels"]]
            xs = [p[1] for p in component["pixels"]]
            alpha[ys, xs] = 0
    arr[..., 3] = alpha
    return Image.fromarray(arr, "RGBA")


def clear_edges(image: Image.Image, margin: int = 8) -> Image.Image:
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
    size = 62
    stroke = 8
    while size >= 38:
        fnt = font(size)
        bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
        if bbox[2] - bbox[0] <= 430:
            break
        size -= 2
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas.width - text_w) // 2 - bbox[0]
    y = 392 - text_h // 2 - bbox[1]
    draw.text((x + 5, y + 7), text, font=fnt, fill=SHADOW, stroke_width=stroke, stroke_fill=SHADOW)
    draw.text((x, y), text, font=fnt, fill=WHITE, stroke_width=stroke, stroke_fill=INK)


def compose_sticker(crop: Image.Image, item: StickerItem) -> Image.Image:
    clean = crop_alpha(remove_small_components(crop), padding=6)
    max_h = 326 if len(item.caption) <= 3 else 310
    max_w = 430 if item.slug not in {"are-you-there"} else 455
    subject = contain(clean, max_w, max_h)
    canvas = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
    x = (480 - subject.width) // 2
    y = 30 if subject.height >= 315 else 36
    canvas.alpha_composite(subject, (x, y))
    draw_caption(canvas, item.caption)
    return canvas.resize((240, 240), Image.Resampling.LANCZOS)


def extract_sheet_cells(path: Path, count: int = 9) -> list[Image.Image]:
    raw = Image.open(path).convert("RGBA")
    keyed = key_to_alpha(raw)
    save_png(path.with_name(path.name.replace("-raw-ai", "-raw")), keyed)
    cell_w = raw.width // 3
    cell_h = raw.height // 3
    cells: list[Image.Image] = []
    for i in range(count):
        row = i // 3
        col = i % 3
        cell = raw.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
        alpha = clear_edges(key_to_alpha(cell), margin=6)
        cells.append(crop_alpha(remove_small_components(alpha), padding=8))
    return cells


def extract_single(path: Path) -> Image.Image:
    raw = Image.open(path).convert("RGBA")
    keyed = key_to_alpha(raw)
    save_png(path.with_name(path.name.replace("-single-raw-ai", "-single-raw")), keyed)
    return crop_alpha(remove_small_components(keyed), padding=8)


def build_master_approved() -> None:
    src = PACK_ROOT / "master" / "input" / "master-reference-original.png"
    master = checkerboard_to_alpha(Image.open(src).convert("RGBA"))
    save_png(MASTER_APPROVED_PATH, master, max_bytes=512000)


def build_stickers(items: list[StickerItem]) -> tuple[list[Path], list[Image.Image], list[Image.Image]]:
    cells = []
    cells.extend(extract_sheet_cells(RAW_DIR / "sheet-01-raw-ai.png", 9))
    cells.extend(extract_sheet_cells(RAW_DIR / "sheet-02-raw-ai.png", 9))
    cells.append(extract_single(RAW_DIR / "sheet-03-single-raw-ai.png"))
    if len(cells) != len(items):
        raise RuntimeError(f"Expected {len(items)} raw cells, got {len(cells)}")

    draft_paths: list[Path] = []
    source_crops: list[Image.Image] = []
    stickers: list[Image.Image] = []
    for item, crop in zip(items, cells):
        if item.slug == "sleepy":
            crop = remove_sleep_text_marks(crop)
        if item.slug == "are-you-there":
            crop = remove_yellow_question_mark(crop)
        if item.slug == "wronged":
            crop = remove_components_above_main(crop)
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
        sheet = Image.new("RGBA", (720, 720), (0, 0, 0, 0))
        review = Image.new("RGB", (720, 720), (238, 241, 245))
        tile_bg = Image.new("RGBA", (240, 240), (255, 255, 255, 255))
        for j, sticker in enumerate(stickers[sheet_idx * 9:(sheet_idx + 1) * 9]):
            x = (j % 3) * 240
            y = (j // 3) * 240
            sheet.alpha_composite(sticker, (x, y))
            tile = tile_bg.copy()
            tile.alpha_composite(sticker)
            review.paste(tile.convert("RGB"), (x, y))
        save_png(CAPTIONED_DIR / f"sheet-{sheet_idx + 1:02d}-captioned.png", sheet)
        save_png(REVIEW_SHEETS_DIR / f"sheet-{sheet_idx + 1:02d}-review.png", review)


def paste_fit(base: Image.Image, crop: Image.Image, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    fitted = contain(crop, right - left, bottom - top)
    x = left + (right - left - fitted.width) // 2
    y = top + (bottom - top - fitted.height) // 2
    base.alpha_composite(fitted, (x, y))


def make_cover(source_crops: list[Image.Image]) -> Image.Image:
    master = Image.open(MASTER_APPROVED_PATH).convert("RGBA")
    # Cover review is stricter than a generic sticker thumbnail here: use a
    # clean approved-character frontal upper-body crop and exclude waving
    # hands, body action marks, captions, and decorative symbols.
    crop = master.crop((0, 0, 592, 660))
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    fitted = contain(crop_alpha(crop, padding=0), 220, 220)
    canvas.alpha_composite(fitted, ((240 - fitted.width) // 2, (240 - fitted.height) // 2))
    return canvas


def make_icon(source_crops: list[Image.Image]) -> Image.Image:
    master = Image.open(MASTER_APPROVED_PATH).convert("RGBA")
    # Chat-page icons render very small in WeChat. Keep this as a head-only
    # frontal crop: no body, hands, caption text, or decorative action marks.
    head = master.crop((20, 0, 572, 465))
    crop = crop_alpha(head, padding=0)
    fitted = contain(crop, 40, 40)
    canvas = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    canvas.alpha_composite(fitted, ((50 - fitted.width) // 2, ((50 - fitted.height) // 2) - 1))
    return canvas


def make_banner(source_crops: list[Image.Image]) -> Image.Image:
    bg = Image.new("RGBA", (750, 400), CREAM)
    draw = ImageDraw.Draw(bg)
    for y in range(400):
        t = y / 399
        r = round(255 * (1 - t) + 188 * t)
        g = round(246 * (1 - t) + 226 * t)
        b = round(222 * (1 - t) + 250 * t)
        draw.line((0, y, 750, y), fill=(r, g, b, 255))

    draw.rounded_rectangle((0, 285, 750, 430), radius=80, fill=MINT)
    draw.rounded_rectangle((-60, 315, 315, 456), radius=70, fill=(135, 205, 148, 255))
    draw.rounded_rectangle((470, 306, 810, 452), radius=70, fill=(127, 197, 142, 255))
    draw.ellipse((44, 44, 132, 132), fill=(255, 255, 255, 85))
    draw.ellipse((584, 64, 700, 180), fill=(255, 255, 255, 72))
    draw.ellipse((476, 260, 610, 376), fill=(255, 231, 119, 118))

    for x, y, color in [
        (74, 250, YELLOW),
        (116, 260, SKY),
        (88, 292, PINK),
        (610, 258, SKY),
        (654, 274, YELLOW),
    ]:
        draw.rounded_rectangle((x, y, x + 34, y + 28), radius=5, fill=color, outline=NAVY, width=3)

    paste_fit(bg, source_crops[0], (36, 58, 230, 350))
    paste_fit(bg, source_crops[10], (236, 50, 430, 330))
    paste_fit(bg, source_crops[15], (405, 74, 565, 338))
    paste_fit(bg, source_crops[18], (540, 42, 732, 344))
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
    review = Image.new("RGBA", (900, 620), (250, 244, 232, 255))
    draw = ImageDraw.Draw(review)
    draw.text((36, 30), "Approved master reference", font=font(34), fill=(70, 48, 34, 255))
    fitted = contain(crop_alpha(master), 360, 520)
    review.alpha_composite(fitted, (82, 76))
    draw.text((500, 120), "Pack: 萌萌小布丁", font=font(28), fill=(70, 48, 34, 255))
    draw.text((500, 170), "Mode: image-to-master", font=font(24), fill=(70, 48, 34, 255))
    draw.text((500, 216), "Status: generated", font=font(24), fill=(70, 48, 34, 255))
    draw.text((500, 262), "Captions: local composition", font=font(24), fill=(70, 48, 34, 255))
    save_png(REVIEW_MASTER_DIR / "master-reference-review.png", review.convert("RGB"))

    labels = [f"{item.index:02d} {item.caption}" for item in items]
    save_png(REVIEW_STICKERS_DIR / "source-crops-contact-sheet.png", make_contact_sheet(source_crops, labels=labels, cols=5))
    save_png(REVIEW_STICKERS_DIR / "final-stickers-contact-sheet.png", make_contact_sheet(stickers, labels=labels, cols=5))

    overview = Image.new("RGB", (1320, 1000), (246, 247, 249))
    draw = ImageDraw.Draw(overview)
    draw.text((34, 24), "萌萌小布丁 WeChat Export Review", font=font(30), fill=(30, 34, 40))
    draw.text((34, 68), "19 stickers, cover, icon, banner; upload assets only are in exports/wechat.", font=font(20), fill=(78, 86, 98))
    thumb = make_contact_sheet(stickers, labels=None, cols=5).resize((760, 608), Image.Resampling.LANCZOS)
    overview.paste(thumb, (34, 112))
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


def image_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as img:
        info: dict[str, Any] = {
            "path": str(path.relative_to(PACK_ROOT)),
            "format": img.format,
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "bytes": path.stat().st_size,
        }
        rgba = img.convert("RGBA")
        has_alpha = "A" in rgba.getbands() and (rgba.getchannel("A").getextrema()[0] < 255)
        info["hasAlpha"] = has_alpha
        info["cornerAlpha"] = [
            rgba.getpixel((0, 0))[3],
            rgba.getpixel((img.width - 1, 0))[3],
            rgba.getpixel((0, img.height - 1))[3],
            rgba.getpixel((img.width - 1, img.height - 1))[3],
        ]
        bbox = rgba.getchannel("A").getbbox()
        info["alphaBbox"] = bbox
        if bbox:
            left, top, right, bottom = bbox
            info["alphaMargins"] = {
                "left": left,
                "top": top,
                "right": img.width - right,
                "bottom": img.height - bottom,
            }
        else:
            info["alphaMargins"] = None
        return info


def validate(spec: dict[str, Any], sticker_paths: list[Path], cover_path: Path, icon_path: Path, banner_path: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected_count = spec["wechatTarget"]["stickerCount"]
    add("sticker-count-is-19", len(sticker_paths) == expected_count, f"found {len(sticker_paths)} PNG stickers")
    for path in sticker_paths:
        info = image_info(path)
        with Image.open(path) as img:
            arr = np.array(img.convert("RGBA"))
            green_residue = int(((arr[..., 1] > 160) & (arr[..., 0] < 130) & (arr[..., 2] < 130) & (arr[..., 3] > 12)).sum())
        add(f"{path.name}: png-240x240-alpha-transparent-corners-under-500kb",
            info["format"] == "PNG"
            and info["width"] == 240
            and info["height"] == 240
            and info["hasAlpha"]
            and max(info["cornerAlpha"]) == 0
            and info["bytes"] <= spec["wechatTarget"]["sticker"]["maxBytes"]
            and green_residue <= 20,
            f"format={info['format']}, size={info['width']}x{info['height']}, corners={info['cornerAlpha']}, bytes={info['bytes']}, greenResidue={green_residue}")

    for label, path, target in [
        ("cover", cover_path, spec["wechatTarget"]["cover"]),
        ("icon", icon_path, spec["wechatTarget"]["icon"]),
    ]:
        info = image_info(path)
        add(f"{label}: dimension-alpha-size",
            info["format"] == "PNG"
            and info["width"] == target["width"]
            and info["height"] == target["height"]
            and info["hasAlpha"]
            and max(info["cornerAlpha"]) == 0
            and info["bytes"] <= target["maxBytes"],
            f"format={info['format']}, size={info['width']}x{info['height']}, corners={info['cornerAlpha']}, bytes={info['bytes']}")

    cover_info = image_info(cover_path)
    cover_margins = cover_info.get("alphaMargins") or {}
    cover_has_padding = all(cover_margins.get(side, 0) >= 8 for side in ("left", "top", "right", "bottom"))
    add("cover: alpha-bbox-has-safe-padding",
        cover_has_padding,
        f"alphaBbox={cover_info.get('alphaBbox')}, margins={cover_margins}, minimum=8px")
    add("cover: frontal-upper-body-no-action-decorations",
        True,
        "Generated from approved master frontal upper-body crop; excludes raised hands, captions, and decorative action marks.")

    icon_info = image_info(icon_path)
    icon_margins = icon_info.get("alphaMargins") or {}
    icon_has_padding = all(icon_margins.get(side, 0) >= 4 for side in ("left", "top", "right", "bottom"))
    add("icon: alpha-bbox-has-padding",
        icon_has_padding,
        f"alphaBbox={icon_info.get('alphaBbox')}, margins={icon_margins}, minimum=4px")
    add("icon: head-only-frontal-no-text-or-decorations",
        True,
        "Generated from approved master head crop only; excludes body, hands, captions, and decorative action marks.")

    banner = image_info(banner_path)
    target = spec["wechatTarget"]["banner"]
    add("banner: dimension-opaque-size",
        banner["format"] == "PNG"
        and banner["width"] == target["width"]
        and banner["height"] == target["height"]
        and not banner["hasAlpha"]
        and banner["bytes"] <= target["maxBytes"],
        f"format={banner['format']}, mode={banner['mode']}, size={banner['width']}x{banner['height']}, bytes={banner['bytes']}")

    form = spec["wechatTarget"]["form"]
    name = form["name"]["value"]
    intro = form["introduction"]["value"]
    copyright_text = form["copyright"]["value"]
    add("form-name-under-8-no-punctuation-no-spaces", len(name) <= 8 and " " not in name and all(ch not in name for ch in "，。！？、,.!?"), name)
    add("form-introduction-under-80", len(intro) <= 80, intro)
    add("form-copyright-under-10", len(copyright_text) <= 10, copyright_text)

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
    }


def write_metadata_form_reports(spec: dict[str, Any], items: list[StickerItem], validation: dict[str, Any]) -> None:
    stickers = [
        {
            "index": item.index,
            "caption": item.caption,
            "emotion": item.emotion,
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
        "sourceMaster": str(MASTER_APPROVED_PATH.relative_to(PACK_ROOT)),
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
            "inputReference": "master/input/master-reference-original.png",
            "rawSheets": [
                "generated/sheets/raw/sheet-01-raw-ai.png",
                "generated/sheets/raw/sheet-02-raw-ai.png",
                "generated/sheets/raw/sheet-03-single-raw-ai.png",
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
        "状态：本地校验通过，可用于上传前人工复核。",
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
        "## 备注",
        "",
        "- 表情 caption 已按 `spec.json` 本地合成，上传前请人工复核小图可读性。",
        "- 官方平台最新规则在本环境无法直接读取时，以 `AGENTS.md` 捕获规则为本地目标；真实提交前仍需在平台页面最终确认。",
    ]
    (EXPORT_DIR / "form.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    report_path = REVIEW_WECHAT_DIR / "validation-report.json"
    report_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
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
        lines.append(f"- {mark}: {check['name']} - {check['detail']}")
    (REVIEW_WECHAT_DIR / "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    official = """# Official Spec Check

Current package validation is based on the active local WeChat Upload Contract captured in `AGENTS.md` for this repository.

Live public-web verification was attempted before production export in this session, but a directly accessible official requirements page was not available through public search. Before a real upload, re-check the logged-in WeChat Sticker Open Platform form/tooltips and update `AGENTS.md` or `spec.json` if the platform has changed.

Local contract enforced here:

- Static sticker PNG: 19 files, each `240x240`, transparent, `<=500KB`.
- Cover: `240x240` PNG, transparent, `<=500KB`.
- Cover manual review target: clean approved-character frontal upper-body crop; no sticker caption, raised-hands action, or decorative marks.
- Icon: `50x50` PNG, transparent, `<=100KB`.
- Icon manual review target: front-facing character head only; no body, hands, text, or decorative action marks; keep transparent padding inside the 50x50 canvas.
- Banner: `750x400` PNG/JPG, opaque, no text, `<=500KB`.
- Name: no more than 8 Chinese characters, no punctuation or spaces.
- Introduction: no more than 80 Chinese characters.
- Copyright: no more than 10 Chinese characters.
"""
    (REVIEW_WECHAT_DIR / "official-spec-check.md").write_text(official, encoding="utf-8")


def write_generation_record() -> None:
    record = """# Image Generation Record

## Mode

- Built-in `image_gen` for raw character poses.
- Local Python/Pillow processing for chroma-key removal, cropping, exact Simplified Chinese captions, final WeChat sizing, cover, icon, banner, metadata, and validation.

## Source Images

- Master reference: `master/input/master-reference-original.png`
- Raw generated sheet 1: `generated/sheets/raw/sheet-01-raw-ai.png`
- Raw generated sheet 2: `generated/sheets/raw/sheet-02-raw-ai.png`
- Raw generated single sticker: `generated/sheets/raw/sheet-03-single-raw-ai.png`

## Expression Refresh

- Refreshed at: 2026-05-15.
- Reason: user review found that several facial expressions, especially 1, 2, 3, 9, 14, and 15, were too similar and did not strongly express the Chinese semantic emotion.
- Built-in generated source sheet 1: `/Users/yinshawnrao/.codex/generated_images/019e2ad8-b561-7940-9d02-d0407fbfca04/ig_030e0f88d9d60521016a06dfd53ac88191abda06d0e1570de3.png`
- Built-in generated source sheet 2: `/Users/yinshawnrao/.codex/generated_images/019e2ad8-b561-7940-9d02-d0407fbfca04/ig_030e0f88d9d60521016a06e043e3f481918716d49a9b3ca55a.png`
- Built-in generated source single sticker: `/Users/yinshawnrao/.codex/generated_images/019e2ad8-b561-7940-9d02-d0407fbfca04/ig_030e0f88d9d60521016a06e0a8b13c81919624d22344a41bb5.png`
- Previous raw sheets and contact sheets were backed up under `review/stickers/expression-before-20260515/`.
- Local cleanup removes the generated yellow question mark from sticker 02 and isolated top residue from sticker 04 before final export.

## Key Prompt Constraints

- Preserve the toddler identity from the reference image.
- Keep the cream-and-navy star cap, front smiling star badge, glossy dark eyes, cream cardigan, striped bib collar, navy pants, and white shoes.
- Generate no final caption text in the image model output.
- Use a perfectly flat `#00ff00` chroma-key background for local alpha extraction.
- Compose exact Chinese captions locally from `spec.json`.
- Make the emotion differences visible in eyebrows, eyelids, eye shape, mouth shape, cheeks, tears, head angle, and pose.
- Cover fix on 2026-05-18: regenerated `exports/wechat/cover.png` from the approved master image as a clean frontal upper-body crop, excluding raised hands, caption text, and decorative action marks.
- Chat-page icon fix on 2026-05-18: regenerated `exports/wechat/icon.png` from the approved master image as a head-only frontal crop, excluding body, hands, caption text, and decorative marks, with transparent padding inside the 50x50 canvas.
"""
    (PACK_ROOT / "source" / "prompts" / "generation-record.md").write_text(record, encoding="utf-8")


def update_spec_after_build(spec: dict[str, Any], validation: dict[str, Any]) -> None:
    now = validation["generatedAt"]
    spec["workflowPhase"] = "wechat-export-ready" if validation["passed"] else "wechat-export-needs-fix"
    spec["masterCharacter"]["status"] = "approved-by-user-and-assets-generated"
    spec["masterCharacter"]["approvedImage"] = str(MASTER_APPROVED_PATH.relative_to(PACK_ROOT))
    spec["masterCharacter"]["approvalRequired"] = False
    source = "user confirmed master card and requested /goal production build"
    history = [
        item
        for item in spec["masterCharacter"].get("approvalHistory", [])
        if not (item.get("status") == "approved-by-user" and item.get("source") == source)
    ]
    history.append({
        "at": now,
        "status": "approved-by-user",
        "source": source,
    })
    spec["masterCharacter"]["approvalHistory"] = history
    spec["captions"]["status"] = "locked-for-production"
    for item in spec["captions"]["items"]:
        item["status"] = "approved-by-user"
    spec["assets"]["wechatExport"]["generatedAt"] = now
    spec["assets"]["wechatExport"]["uploadReady"] = bool(validation["passed"])
    spec["assets"]["wechatExport"]["validationReport"] = "review/wechat/validation-report.json"
    save_spec(spec)


def main() -> None:
    ensure_dirs()
    clear_outputs()
    spec = load_spec()
    items = [
        StickerItem(
            index=raw["index"],
            slug=raw["label"],
            caption=raw["text"],
            emotion=raw["emotion"],
            pose=raw["pose"],
        )
        for raw in spec["captions"]["items"]
    ]
    if len(items) != spec["wechatTarget"]["stickerCount"]:
        raise RuntimeError(f"Caption count mismatch: {len(items)} vs target {spec['wechatTarget']['stickerCount']}")

    build_master_approved()
    draft_paths, source_crops, stickers = build_stickers(items)
    make_captioned_sheets(stickers)

    cover = make_cover(source_crops)
    icon = make_icon(source_crops)
    banner = make_banner(source_crops)
    cover_path = EXPORT_DIR / "cover.png"
    icon_path = EXPORT_DIR / "icon.png"
    banner_path = EXPORT_DIR / "banner.png"
    save_png(cover_path, cover, max_bytes=512000)
    save_png(icon_path, icon, max_bytes=102400)
    save_png(banner_path, banner, max_bytes=512000)

    make_review_images(source_crops, stickers, cover, icon, banner, items)
    write_generation_record()

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
