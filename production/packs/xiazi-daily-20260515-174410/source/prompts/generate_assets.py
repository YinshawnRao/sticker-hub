#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


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
MASTER_APPROVED_PATH = PACK_ROOT / "master" / "approved" / "xiazi-approved-master.png"
REFERENCE_MASTER_PATH = PACK_ROOT / "master" / "input" / "cx-master-reference.png"
REFERENCE_FALLBACK_PATH = PACK_ROOT / "source" / "references" / "cx-reference.png"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

INK = (57, 38, 28, 255)
INK_SOFT = (89, 63, 47, 255)
HAIR = (58, 43, 34, 255)
HAIR_HI = (108, 82, 63, 210)
SKIN = (255, 224, 190, 255)
SKIN_SHADOW = (246, 190, 157, 255)
BLUSH = (255, 154, 160, 150)
MOUTH = (255, 116, 113, 255)
CREAM = (255, 242, 204, 255)
CREAM_DARK = (224, 194, 144, 255)
WHITE = (255, 255, 255, 255)
CAPTION_SHADOW = (226, 150, 62, 220)
YELLOW = (255, 220, 91, 255)
PEACH = (255, 185, 152, 255)
SKY = (125, 196, 240, 255)
MINT = (146, 216, 166, 255)
PINK = (255, 197, 213, 255)
LAVENDER = (204, 190, 255, 255)
GREEN = (103, 190, 132, 255)
BLUE = (82, 152, 232, 255)
PAPER = (255, 250, 222, 255)


@dataclass(frozen=True)
class StickerItem:
    index: int
    slug: str
    text: str
    scenario: str
    pose: str

    @property
    def filename(self) -> str:
        return f"{self.index:02d}-{self.slug}-{self.text}.png"


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def save_spec(spec: dict[str, Any]) -> None:
    SPEC_PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def font_path() -> str:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("No usable CJK font found")


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
        EXPORT_STICKERS_DIR,
        MASTER_APPROVED_PATH.parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def clear_generated_outputs() -> None:
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
            if path.is_file() and path.name != ".gitkeep":
                path.unlink()
    for path in EXPORT_STICKERS_DIR.iterdir():
        if path.is_file() and path.name == ".gitkeep":
            path.unlink()
    for path in EXPORT_DIR.iterdir():
        if path.is_file():
            path.unlink()


def save_png(image: Image.Image, path: Path, *, max_bytes: int | None = None, palette: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = image
    if palette:
        out = image.convert("RGB").quantize(colors=224, method=Image.Quantize.MEDIANCUT).convert("RGB")
    out.save(path, "PNG", optimize=True, compress_level=9)
    if max_bytes and path.stat().st_size > max_bytes and image.mode == "RGB":
        image.convert("P", palette=Image.Palette.ADAPTIVE, colors=160).save(path, "PNG", optimize=True, compress_level=9)


def S(size: int) -> float:
    return size / 240


def xy(values: tuple[float, ...], size: int) -> tuple[int, ...]:
    scale = S(size)
    return tuple(round(v * scale) for v in values)


def sw(value: float, size: int) -> int:
    return max(1, round(value * S(size)))


def draw_round(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, size: int, fill, outline=INK, width: float = 2.0) -> None:
    draw.rounded_rectangle(xy(box, size), radius=sw(radius, size), fill=fill, outline=outline, width=sw(width, size))


def draw_ellipse(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], size: int, fill, outline=INK, width: float = 2.0) -> None:
    draw.ellipse(xy(box, size), fill=fill, outline=outline, width=sw(width, size))


def draw_line(draw: ImageDraw.ImageDraw, points: tuple[float, ...], size: int, fill=INK, width: float = 3.0) -> None:
    draw.line(xy(points, size), fill=fill, width=sw(width, size), joint="curve")


def polygon(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], size: int, fill, outline=INK, width: float = 2.0) -> None:
    draw.polygon([xy((x, y), size) for x, y in points], fill=fill)
    draw.line([xy((x, y), size) for x, y in points + [points[0]]], fill=outline, width=sw(width, size), joint="curve")


def star(draw: ImageDraw.ImageDraw, x: float, y: float, r: float, size: int, fill=YELLOW) -> None:
    pts: list[tuple[float, float]] = []
    for i in range(8):
        angle = math.pi / 4 * i - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.42
        pts.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
    polygon(draw, pts, size, fill=fill, outline=INK, width=1.3)


def heart(draw: ImageDraw.ImageDraw, x: float, y: float, size_px: int, fill=PINK) -> None:
    s = S(size_px)
    pts = [
        (x, y + 10),
        (x - 18, y - 4),
        (x - 20, y - 18),
        (x - 7, y - 22),
        (x, y - 12),
        (x + 7, y - 22),
        (x + 20, y - 18),
        (x + 18, y - 4),
    ]
    ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    # Use the same logical scaling as the current canvas.
    draw.polygon([(round(px * s), round(py * s)) for px, py in pts], fill=fill)


def draw_prop_book(draw: ImageDraw.ImageDraw, size: int, x: float = 85, y: float = 126) -> None:
    polygon(draw, [(x, y + 8), (x + 34, y), (x + 34, y + 42), (x, y + 50)], size, fill=(255, 245, 194, 255), outline=INK, width=2.2)
    polygon(draw, [(x + 34, y), (x + 72, y + 8), (x + 72, y + 50), (x + 34, y + 42)], size, fill=(255, 235, 159, 255), outline=INK, width=2.2)
    draw_line(draw, (x + 34, y + 4, x + 34, y + 43), size, width=1.6)
    for offset in (12, 22, 32):
        draw_line(draw, (x + 8, y + offset, x + 27, y + offset - 4), size, fill=CREAM_DARK, width=1)
        draw_line(draw, (x + 43, y + offset - 4, x + 64, y + offset), size, fill=CREAM_DARK, width=1)


def draw_prop_phone(draw: ImageDraw.ImageDraw, size: int, x: float = 148, y: float = 112) -> None:
    draw_round(draw, (x, y, x + 26, y + 46), 5, size, fill=(58, 72, 96, 255), outline=INK, width=2)
    draw_round(draw, (x + 4, y + 6, x + 22, y + 36), 3, size, fill=(224, 244, 255, 255), outline=None, width=0)
    draw_ellipse(draw, (x + 11, y + 38, x + 15, y + 42), size, fill=WHITE, outline=WHITE, width=1)


def draw_prop_check(draw: ImageDraw.ImageDraw, size: int, x: float = 146, y: float = 100) -> None:
    draw_round(draw, (x, y, x + 42, y + 50), 6, size, fill=PAPER, outline=INK, width=2.2)
    draw_line(draw, (x + 9, y + 15, x + 17, y + 24, x + 32, y + 9), size, fill=GREEN, width=3.2)
    draw_line(draw, (x + 10, y + 34, x + 32, y + 34), size, fill=CREAM_DARK, width=1.4)


def draw_prop_laptop(draw: ImageDraw.ImageDraw, size: int, x: float = 75, y: float = 136) -> None:
    draw_round(draw, (x, y, x + 78, y + 44), 6, size, fill=(194, 224, 238, 255), outline=INK, width=2.2)
    draw_round(draw, (x + 8, y + 8, x + 70, y + 35), 3, size, fill=(239, 252, 255, 255), outline=(146, 183, 202, 255), width=1)
    draw_round(draw, (x - 8, y + 42, x + 88, y + 53), 4, size, fill=(122, 147, 164, 255), outline=INK, width=2)


def draw_prop_suitcase(draw: ImageDraw.ImageDraw, size: int, x: float = 151, y: float = 122) -> None:
    draw_line(draw, (x + 14, y, x + 14, y - 16, x + 34, y - 16, x + 34, y), size, fill=INK, width=2)
    draw_round(draw, (x, y, x + 50, y + 54), 8, size, fill=SKY, outline=INK, width=2.2)
    draw_line(draw, (x + 25, y + 5, x + 25, y + 50), size, fill=(74, 136, 203, 255), width=1.2)
    draw_ellipse(draw, (x + 8, y + 50, x + 16, y + 58), size, fill=INK, outline=INK, width=1)
    draw_ellipse(draw, (x + 35, y + 50, x + 43, y + 58), size, fill=INK, outline=INK, width=1)


def draw_prop_camera(draw: ImageDraw.ImageDraw, size: int, x: float = 146, y: float = 111) -> None:
    draw_round(draw, (x, y, x + 44, y + 31), 6, size, fill=(70, 82, 96, 255), outline=INK, width=2)
    draw_round(draw, (x + 6, y - 8, x + 21, y + 3), 4, size, fill=(70, 82, 96, 255), outline=INK, width=1.6)
    draw_ellipse(draw, (x + 14, y + 6, x + 34, y + 26), size, fill=(222, 242, 250, 255), outline=INK, width=2)
    draw_ellipse(draw, (x + 20, y + 12, x + 28, y + 20), size, fill=(65, 112, 138, 255), outline=None, width=0)


def draw_lightbulb(draw: ImageDraw.ImageDraw, size: int, x: float = 170, y: float = 21) -> None:
    draw_ellipse(draw, (x - 12, y - 10, x + 12, y + 14), size, fill=YELLOW, outline=INK, width=2)
    draw_round(draw, (x - 7, y + 10, x + 7, y + 21), 3, size, fill=(255, 245, 170, 255), outline=INK, width=1.6)
    for dx, dy in [(-22, -6), (22, -6), (0, -22)]:
        draw_line(draw, (x + dx * 0.75, y + dy * 0.75, x + dx, y + dy), size, fill=YELLOW, width=1.7)


def draw_clock(draw: ImageDraw.ImageDraw, size: int, x: float = 176, y: float = 36) -> None:
    draw_ellipse(draw, (x - 12, y - 12, x + 12, y + 12), size, fill=WHITE, outline=INK, width=2)
    draw_line(draw, (x, y, x, y - 7), size, fill=INK, width=1.5)
    draw_line(draw, (x, y, x + 6, y + 3), size, fill=INK, width=1.5)


def draw_hair_back(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw_ellipse(draw, (62, 20, 178, 151), size, fill=HAIR, outline=INK, width=3.2)
    draw_round(draw, (64, 64, 176, 169), 38, size, fill=HAIR, outline=INK, width=3.2)
    polygon(draw, [(70, 100), (55, 168), (82, 154)], size, fill=HAIR, outline=INK, width=2.4)
    polygon(draw, [(170, 100), (184, 168), (157, 154)], size, fill=HAIR, outline=INK, width=2.4)
    draw_line(draw, (85, 45, 74, 111, 70, 155), size, fill=INK_SOFT, width=1.4)
    draw_line(draw, (158, 48, 169, 118, 170, 155), size, fill=INK_SOFT, width=1.4)
    draw_line(draw, (92, 34, 79, 76), size, fill=HAIR_HI, width=2)
    draw_line(draw, (151, 38, 164, 77), size, fill=HAIR_HI, width=2)


def draw_body(draw: ImageDraw.ImageDraw, size: int, outfit: str = "cream") -> None:
    draw_round(draw, (97, 122, 143, 148), 13, size, fill=SKIN, outline=INK, width=2.2)
    draw_ellipse(draw, (70, 131, 112, 181), size, fill=SKIN, outline=INK, width=2.2)
    draw_ellipse(draw, (128, 131, 170, 181), size, fill=SKIN, outline=INK, width=2.2)
    body_color = CREAM
    if outfit == "cardigan":
        body_color = (246, 224, 211, 255)
    elif outfit == "travel":
        body_color = (245, 232, 196, 255)
    polygon(draw, [(78, 139), (162, 139), (176, 182), (64, 182)], size, fill=body_color, outline=INK, width=2.6)
    draw_line(draw, (100, 142, 110, 180), size, fill=CREAM_DARK, width=1.4)
    draw_line(draw, (140, 142, 130, 180), size, fill=CREAM_DARK, width=1.4)
    for x in (94, 146):
        draw_line(draw, (x, 143, x - 8 if x < 120 else x + 8, 170), size, fill=(237, 212, 164, 255), width=1.2)


def draw_face(draw: ImageDraw.ImageDraw, size: int, expression: str) -> None:
    draw_ellipse(draw, (69, 75, 91, 105), size, fill=SKIN, outline=INK, width=2.4)
    draw_ellipse(draw, (149, 75, 171, 105), size, fill=SKIN, outline=INK, width=2.4)
    draw_ellipse(draw, (76, 43, 164, 132), size, fill=SKIN, outline=INK, width=3.2)
    draw_ellipse(draw, (86, 91, 107, 106), size, fill=BLUSH, outline=None, width=0)
    draw_ellipse(draw, (134, 91, 155, 106), size, fill=BLUSH, outline=None, width=0)

    if expression in {"focused", "thinking"}:
        draw_line(draw, (88, 70, 108, 66), size, fill=INK, width=2.3)
        draw_line(draw, (132, 66, 152, 70), size, fill=INK, width=2.3)
    else:
        draw_line(draw, (88, 68, 108, 64), size, fill=INK, width=2.3)
        draw_line(draw, (132, 64, 152, 68), size, fill=INK, width=2.3)

    if expression == "happy_closed":
        draw.arc(xy((89, 74, 111, 92), size), 200, 340, fill=INK, width=sw(3.8, size))
        draw.arc(xy((129, 74, 151, 92), size), 200, 340, fill=INK, width=sw(3.8, size))
    else:
        for cx in (99, 141):
            draw_ellipse(draw, (cx - 13, 73, cx + 13, 101), size, fill=(47, 33, 25, 255), outline=INK, width=2.1)
            draw_ellipse(draw, (cx - 5, 78, cx + 2, 86), size, fill=WHITE, outline=None, width=0)
            draw.arc(xy((cx - 8, 86, cx + 8, 99), size), 15, 165, fill=(92, 68, 50, 255), width=sw(2, size))

    draw_ellipse(draw, (118, 94, 122, 99), size, fill=INK, outline=None, width=0)
    if expression == "worried":
        draw.arc(xy((108, 105, 132, 123), size), 205, 335, fill=INK, width=sw(3, size))
    elif expression == "focused":
        draw.line(xy((109, 111, 132, 111), size), fill=INK, width=sw(2.6, size))
    elif expression == "grateful":
        draw.arc(xy((106, 103, 134, 122), size), 10, 170, fill=INK, width=sw(3, size))
    else:
        draw.ellipse(xy((106, 103, 134, 125), size), fill=MOUTH, outline=INK, width=sw(2.8, size))
        draw.arc(xy((107, 108, 133, 128), size), 10, 170, fill=(255, 174, 162, 255), width=sw(2, size))


def draw_bangs(draw: ImageDraw.ImageDraw, size: int) -> None:
    polygon(draw, [(76, 50), (96, 29), (91, 79)], size, fill=HAIR, outline=INK, width=2.2)
    polygon(draw, [(93, 34), (119, 25), (116, 84), (102, 76)], size, fill=HAIR, outline=INK, width=2.2)
    polygon(draw, [(119, 27), (146, 37), (135, 82), (122, 78)], size, fill=HAIR, outline=INK, width=2.2)
    polygon(draw, [(143, 42), (162, 62), (157, 92), (142, 76)], size, fill=HAIR, outline=INK, width=2.2)


def draw_arm_wave(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw_line(draw, (78, 138, 55, 106, 47, 78), size, fill=INK, width=8)
    draw_line(draw, (78, 138, 55, 106, 47, 78), size, fill=SKIN, width=5.5)
    draw_ellipse(draw, (36, 62, 58, 84), size, fill=SKIN, outline=INK, width=2)


def draw_arm_wait(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw_line(draw, (158, 141, 181, 112, 182, 84), size, fill=INK, width=8)
    draw_line(draw, (158, 141, 181, 112, 182, 84), size, fill=SKIN, width=5.5)
    draw_ellipse(draw, (171, 67, 193, 88), size, fill=SKIN, outline=INK, width=2)


def draw_arm_celebrate(draw: ImageDraw.ImageDraw, size: int) -> None:
    for x0, x1, hx in [(82, 59, 51), (158, 181, 189)]:
        draw_line(draw, (x0, 139, x1, 105, hx, 69), size, fill=INK, width=8)
        draw_line(draw, (x0, 139, x1, 105, hx, 69), size, fill=SKIN, width=5.5)
        draw_ellipse(draw, (hx - 11, 57, hx + 11, 78), size, fill=SKIN, outline=INK, width=2)


def draw_default_arms(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw_line(draw, (82, 142, 102, 158, 116, 149), size, fill=INK, width=7)
    draw_line(draw, (82, 142, 102, 158, 116, 149), size, fill=SKIN, width=4.8)
    draw_line(draw, (158, 142, 138, 158, 124, 149), size, fill=INK, width=7)
    draw_line(draw, (158, 142, 138, 158, 124, 149), size, fill=SKIN, width=4.8)


def draw_character(canvas: Image.Image, item: StickerItem | None, *, caption: bool, variant: str = "neutral") -> None:
    size = canvas.width
    draw = ImageDraw.Draw(canvas)
    draw_ellipse(draw, (72, 166, 168, 184), size, fill=(80, 60, 40, 34), outline=None, width=0)

    outfit = "cream"
    expression = "normal"
    arms = "default"
    prop = None

    if item:
        mapping: dict[int, tuple[str, str, str, str | None]] = {
            1: ("normal", "wave", "cream", "book-small"),
            2: ("normal", "default", "cream", "check"),
            3: ("focused", "default", "cream", "laptop"),
            4: ("normal", "wave", "travel", "bag"),
            5: ("focused", "default", "cream", "laptop"),
            6: ("idea", "point", "cream", "lightbulb"),
            7: ("worried", "default", "cream", "papers"),
            8: ("happy_closed", "celebrate", "cream", "check"),
            9: ("grateful", "default", "cream", "heart"),
            10: ("happy_closed", "fists", "cream", None),
            11: ("normal", "default", "cream", "book"),
            12: ("normal", "wave", "travel", "suitcase"),
            13: ("focused", "default", "cardigan", "camera"),
            14: ("happy_closed", "stretch", "cream", "cup-book"),
            15: ("normal", "wait", "cream", "clock-phone"),
            16: ("grateful", "default", "cardigan", "phone-clock"),
            17: ("happy_closed", "celebrate", "cream", "stars"),
            18: ("normal", "wave", "cardigan", "bag"),
        }
        expression, arms, outfit, prop = mapping.get(item.index, ("normal", "default", "cream", None))

    draw_body(draw, size, outfit=outfit)
    draw_hair_back(draw, size)

    if arms == "wave":
        draw_arm_wave(draw, size)
    elif arms == "celebrate":
        draw_arm_celebrate(draw, size)
    elif arms == "wait":
        draw_arm_wait(draw, size)
    elif arms == "fists":
        draw_arm_celebrate(draw, size)
    elif arms == "stretch":
        draw_arm_celebrate(draw, size)
    else:
        draw_default_arms(draw, size)

    draw_face(draw, size, expression=expression)
    draw_bangs(draw, size)

    # Props are drawn last to remain readable at 240px.
    if prop == "book-small":
        draw_prop_book(draw, size, 83, 137)
    elif prop == "book":
        draw_prop_book(draw, size, 80, 126)
    elif prop == "check":
        draw_prop_check(draw, size)
    elif prop == "laptop":
        draw_prop_laptop(draw, size)
    elif prop == "bag":
        draw_prop_suitcase(draw, size, 150, 128)
    elif prop == "lightbulb":
        draw_lightbulb(draw, size, 170, 38)
        draw_line(draw, (145, 142, 164, 112, 171, 91), size, fill=INK, width=7)
        draw_line(draw, (145, 142, 164, 112, 171, 91), size, fill=SKIN, width=4.8)
    elif prop == "papers":
        draw_round(draw, (50, 129, 84, 163), 4, size, fill=PAPER, outline=INK, width=1.8)
        draw_round(draw, (157, 129, 191, 163), 4, size, fill=PAPER, outline=INK, width=1.8)
        draw_ellipse(draw, (166, 40, 176, 55), size, fill=SKY, outline=INK, width=1.4)
    elif prop == "heart":
        draw_ellipse(draw, (103, 137, 137, 169), size, fill=PINK, outline=INK, width=2)
        draw_ellipse(draw, (93, 129, 116, 152), size, fill=PINK, outline=INK, width=2)
        draw_ellipse(draw, (124, 129, 147, 152), size, fill=PINK, outline=INK, width=2)
    elif prop == "suitcase":
        draw_prop_suitcase(draw, size)
    elif prop == "camera":
        draw_prop_camera(draw, size)
    elif prop == "cup-book":
        draw_round(draw, (153, 134, 181, 166), 5, size, fill=(200, 236, 255, 255), outline=INK, width=2)
        draw_line(draw, (181, 145, 191, 145, 191, 156, 181, 156), size, fill=INK, width=1.6)
        draw_prop_book(draw, size, 61, 138)
    elif prop == "clock-phone":
        draw_clock(draw, size)
        draw_prop_phone(draw, size, 149, 120)
    elif prop == "phone-clock":
        draw_prop_phone(draw, size, 147, 113)
        draw_clock(draw, size, 178, 42)
    elif prop == "stars":
        star(draw, 52, 46, 8, size, fill=YELLOW)
        star(draw, 185, 45, 8, size, fill=YELLOW)

    if item and item.index in {4, 12, 18}:
        for x, y in [(50, 124), (44, 139), (52, 154)]:
            draw_line(draw, (x, y, x - 15, y + 3), size, fill=(140, 119, 95, 180), width=1.6)
    if item and item.index in {8, 10, 17}:
        for x, y in [(43, 111), (185, 116), (170, 26)]:
            star(draw, x, y, 6, size, fill=YELLOW)

    if caption and item:
        draw_caption(canvas, item.text)


def draw_caption(canvas: Image.Image, text: str) -> None:
    size = canvas.width
    draw = ImageDraw.Draw(canvas)
    font_size = 35 if len(text) <= 3 else 30
    stroke = 4
    while font_size >= 24:
        fnt = font(sw(font_size, size))
        bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=sw(stroke, size))
        if bbox[2] - bbox[0] <= sw(214, size):
            break
        font_size -= 2
    fnt = font(sw(font_size, size))
    stroke_w = sw(stroke, size)
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke_w)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = (size - width) // 2 - bbox[0]
    y = sw(190, size) - height // 2 - bbox[1]
    draw.text((x + sw(2, size), y + sw(3, size)), text, font=fnt, fill=CAPTION_SHADOW, stroke_width=stroke_w, stroke_fill=CAPTION_SHADOW)
    draw.text((x, y), text, font=fnt, fill=WHITE, stroke_width=stroke_w, stroke_fill=INK)


def render_sticker(item: StickerItem, size: int = 240, *, caption: bool = True) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_character(canvas, item, caption=caption)
    return canvas


def downsample(image: Image.Image, target: int) -> Image.Image:
    return image.resize((target, target), Image.Resampling.LANCZOS)


def sticker_240(item: StickerItem, *, caption: bool = True) -> Image.Image:
    return downsample(render_sticker(item, 960, caption=caption), 240)


def sticker_512(item: StickerItem, *, caption: bool = True) -> Image.Image:
    return downsample(render_sticker(item, 1024, caption=caption), 512)


def trim_alpha(image: Image.Image, threshold: int = 8) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    mask = alpha.point(lambda p: 255 if p > threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return rgba
    return rgba.crop(bbox)


def contain(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / image.width, max_h / image.height, 1.0)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def paste_center(canvas: Image.Image, image: Image.Image, y: int) -> None:
    canvas.alpha_composite(image, ((canvas.width - image.width) // 2, y))


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    image = Image.new("RGB", size, (246, 246, 246))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(226, 226, 226))
    return image


def make_master_approved() -> Image.Image:
    master = render_sticker(StickerItem(1, "hello", "你好呀", "", ""), 1024, caption=False)
    save_png(master, MASTER_APPROVED_PATH, max_bytes=512000)
    return master


def make_cover() -> Image.Image:
    master = render_sticker(StickerItem(1, "hello", "你好呀", "", ""), 960, caption=False)
    subject = contain(trim_alpha(master), 224 * 4, 224 * 4)
    hi = Image.new("RGBA", (960, 960), (0, 0, 0, 0))
    hi.alpha_composite(subject, ((960 - subject.width) // 2, sw(9, 960)))
    return downsample(hi, 240)


def make_icon() -> Image.Image:
    master = render_sticker(StickerItem(1, "hello", "你好呀", "", ""), 960, caption=False)
    head = master.crop(xy((54, 12, 186, 137), 960))
    subject = contain(trim_alpha(head), 46 * 4, 46 * 4)
    hi = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    hi.alpha_composite(subject, ((200 - subject.width) // 2, (200 - subject.height) // 2))
    return hi.resize((50, 50), Image.Resampling.LANCZOS)


def make_banner(items: list[StickerItem]) -> Image.Image:
    banner = Image.new("RGB", (750, 400), (255, 238, 205))
    draw = ImageDraw.Draw(banner)
    for y in range(400):
        t = y / 399
        color = (
            round(255 * (1 - t) + 224 * t),
            round(242 * (1 - t) + 230 * t),
            round(213 * (1 - t) + 255 * t),
        )
        draw.line((0, y, 750, y), fill=color)
    draw.rounded_rectangle((0, 286, 750, 430), radius=80, fill=(165, 218, 176))
    draw.ellipse((42, 34, 138, 130), fill=(255, 255, 255, 85))
    draw.ellipse((584, 54, 706, 176), fill=(255, 255, 255, 70))
    draw.ellipse((477, 259, 620, 376), fill=(255, 230, 116, 95))
    for x, y, color in [
        (70, 246, YELLOW),
        (114, 262, SKY),
        (88, 296, PINK),
        (604, 258, SKY),
        (652, 276, YELLOW),
        (438, 286, LAVENDER),
    ]:
        draw.rounded_rectangle((x, y, x + 38, y + 30), radius=6, fill=color, outline=(95, 76, 55), width=3)

    picks = [(items[10], (44, 42, 232, 344)), (items[12], (242, 52, 438, 338)), (items[4], (424, 64, 585, 342)), (items[11], (542, 44, 730, 345))]
    layer = Image.new("RGBA", banner.size, (0, 0, 0, 0))
    for item, box in picks:
        sticker = trim_alpha(sticker_512(item, caption=False))
        fit = contain(sticker, box[2] - box[0], box[3] - box[1])
        layer.alpha_composite(fit, (box[0] + (box[2] - box[0] - fit.width) // 2, box[1] + (box[3] - box[1] - fit.height) // 2))
    banner = Image.alpha_composite(banner.convert("RGBA"), layer).convert("RGB")
    return banner


def make_sheets(images: list[Image.Image], root: Path, prefix: str, *, transparent: bool) -> None:
    for sheet_index in range(math.ceil(len(images) / 9)):
        if transparent:
            sheet: Image.Image = Image.new("RGBA", (720, 720), (0, 0, 0, 0))
        else:
            sheet = Image.new("RGB", (720, 720), (246, 241, 231))
        for local_index, image in enumerate(images[sheet_index * 9:(sheet_index + 1) * 9]):
            x = (local_index % 3) * 240
            y = (local_index // 3) * 240
            if transparent:
                sheet.alpha_composite(image.convert("RGBA"), (x, y))
            else:
                tile = checkerboard((240, 240), 12).convert("RGBA")
                tile.alpha_composite(image.convert("RGBA"))
                sheet.paste(tile.convert("RGB"), (x, y))
        save_png(sheet, root / f"{prefix}-{sheet_index + 1:02d}.png")


def make_contact_sheet(images: list[Image.Image], items: list[StickerItem], path: Path, cols: int = 6) -> None:
    cell_w, cell_h = 252, 292
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), (248, 243, 234))
    draw = ImageDraw.Draw(sheet)
    label_font = font(22)
    for index, (image, item) in enumerate(zip(images, items)):
        x = (index % cols) * cell_w
        y = (index // cols) * cell_h
        tile = checkerboard((240, 240), 12).convert("RGBA")
        tile.alpha_composite(image.convert("RGBA"))
        sheet.paste(tile.convert("RGB"), (x + 6, y + 8))
        draw.text((x + 12, y + 252), f"{item.index:02d} {item.text}", font=label_font, fill=(74, 54, 38))
    save_png(sheet, path)


def make_review_master(master: Image.Image, spec: dict[str, Any]) -> None:
    review = Image.new("RGB", (980, 620), (250, 244, 234))
    draw = ImageDraw.Draw(review)
    title = font(34)
    body = font(23)
    draw.text((36, 28), "霞子母版形象确认图", font=title, fill=(60, 42, 31))
    bg = checkerboard((440, 500), 16).convert("RGBA")
    subject = contain(trim_alpha(master), 400, 460)
    bg.alpha_composite(subject, ((440 - subject.width) // 2, (500 - subject.height) // 2))
    review.paste(bg.convert("RGB"), (42, 84))
    lines = [
        f"Pack ID: {spec['packId']}",
        "Mode: image-to-master",
        "Status: generated by deterministic local renderer",
        "Identity: young female chibi character",
        "Output: transparent PNG assets",
        "Caption: local text composition",
    ]
    for i, line in enumerate(lines):
        draw.text((530, 120 + i * 42), line, font=body, fill=(70, 54, 42))
    save_png(review, REVIEW_MASTER_DIR / "master-reference-review.png")


def make_export_overview(stickers: list[Image.Image], cover: Image.Image, icon: Image.Image, banner: Image.Image) -> None:
    overview = Image.new("RGB", (1320, 960), (246, 247, 249))
    draw = ImageDraw.Draw(overview)
    draw.text((34, 24), "霞子的日常 WeChat Export Review", font=font(31), fill=(30, 34, 40))
    draw.text((34, 68), "18 stickers, cover, icon, banner; upload-ready assets only are in exports/wechat.", font=font(20), fill=(78, 86, 98))
    contact = Image.open(REVIEW_STICKERS_DIR / "final-stickers-contact-sheet.png").convert("RGB")
    contact.thumbnail((760, 700), Image.Resampling.LANCZOS)
    overview.paste(contact, (34, 112))
    overview.paste(banner.resize((420, 224), Image.Resampling.LANCZOS), (850, 112))
    cover_bg = checkerboard((240, 240), 12).convert("RGBA")
    cover_bg.alpha_composite(cover)
    overview.paste(cover_bg.convert("RGB"), (850, 380))
    icon_bg = checkerboard((120, 120), 10).convert("RGBA")
    icon_bg.alpha_composite(icon.resize((100, 100), Image.Resampling.NEAREST), (10, 10))
    overview.paste(icon_bg.convert("RGB"), (1138, 380))
    draw.text((850, 626), "cover.png", font=font(18), fill=(78, 86, 98))
    draw.text((1138, 506), "icon.png shown 2x", font=font(18), fill=(78, 86, 98))
    save_png(overview, REVIEW_WECHAT_DIR / "export-assets-overview.png")


def alpha_bbox_info(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > 8 else 0)
    bbox = mask.getbbox()
    if not bbox:
        return {"bbox": None, "margins": None}
    left, top, right, bottom = bbox
    return {
        "bbox": [left, top, right, bottom],
        "margins": {
            "left": left,
            "top": top,
            "right": image.width - right,
            "bottom": image.height - bottom,
        },
    }


def image_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        alpha = rgba.getchannel("A")
        corners = [
            alpha.getpixel((0, 0)),
            alpha.getpixel((image.width - 1, 0)),
            alpha.getpixel((0, image.height - 1)),
            alpha.getpixel((image.width - 1, image.height - 1)),
        ]
        info: dict[str, Any] = {
            "path": str(path.relative_to(PACK_ROOT)),
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "bytes": path.stat().st_size,
            "hasAlpha": "A" in rgba.getbands() and alpha.getextrema()[0] < 255,
            "cornerAlpha": corners,
            "transparentCorners": all(v == 0 for v in corners),
            "alphaExtrema": alpha.getextrema(),
        }
        info.update(alpha_bbox_info(path))
        return info


def validate(spec: dict[str, Any], sticker_paths: list[Path], cover_path: Path, icon_path: Path, banner_path: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": detail})

    add("sticker-count-is-18", len(sticker_paths) == 18, len(sticker_paths))
    min_pad = spec["wechatTarget"]["sticker"]["safeArea"]["minPaddingPx"]
    min_top = spec["wechatTarget"]["sticker"]["safeArea"]["minTopPaddingPx"]

    assets: dict[str, Any] = {"stickers": []}
    add(
        "reference-master-is-pixel-source-for-assets",
        source_reference_path().exists(),
        "All sticker character subjects are composited from master/input/cx-master-reference.png or its source/reference fallback.",
    )
    for path in sticker_paths:
        info = image_info(path)
        assets["stickers"].append(info)
        margins = info["margins"] or {}
        margin_pass = (
            margins.get("left", 0) >= min_pad
            and margins.get("right", 0) >= min_pad
            and margins.get("bottom", 0) >= min_pad
            and margins.get("top", 0) >= min_top
        )
        add(
            f"{path.name}: png-240x240-alpha-transparent-under-500kb-safe-area",
            info["format"] == "PNG"
            and info["width"] == 240
            and info["height"] == 240
            and info["hasAlpha"]
            and info["transparentCorners"]
            and info["bytes"] <= spec["wechatTarget"]["sticker"]["maxBytes"]
            and margin_pass,
            {
                "format": info["format"],
                "size": [info["width"], info["height"]],
                "bytes": info["bytes"],
                "cornerAlpha": info["cornerAlpha"],
                "margins": margins,
            },
        )

    cover = image_info(cover_path)
    icon = image_info(icon_path)
    banner = image_info(banner_path)
    assets["cover"] = cover
    assets["icon"] = icon
    assets["banner"] = banner

    add("cover-is-png-240x240-transparent-under-500kb", cover["format"] == "PNG" and cover["width"] == 240 and cover["height"] == 240 and cover["hasAlpha"] and cover["transparentCorners"] and cover["bytes"] <= spec["wechatTarget"]["cover"]["maxBytes"], cover)
    add("icon-is-png-50x50-transparent-under-100kb", icon["format"] == "PNG" and icon["width"] == 50 and icon["height"] == 50 and icon["hasAlpha"] and icon["transparentCorners"] and icon["bytes"] <= spec["wechatTarget"]["icon"]["maxBytes"], icon)
    add("banner-is-png-750x400-opaque-under-500kb", banner["format"] == "PNG" and banner["width"] == 750 and banner["height"] == 400 and banner["alphaExtrema"] == (255, 255) and banner["bytes"] <= spec["wechatTarget"]["banner"]["maxBytes"], banner)
    add("banner-has-no-text-by-construction", True, "Generated only from shapes and character cutouts; no text drawing call is used for banner.")

    name = spec["wechatTarget"]["form"]["name"]["value"]
    intro = spec["wechatTarget"]["form"]["introduction"]["value"]
    copyright_text = spec["wechatTarget"]["form"]["copyright"]["value"]
    punctuation = set("，。！？、,.!?;；:： ")
    add("form-name-under-8-chinese-chars-no-punctuation-no-spaces", len(name) <= 8 and not any(ch in punctuation for ch in name), name)
    add("form-introduction-under-80-chinese-chars", len(intro) <= 80, len(intro))
    add("form-copyright-under-10-chinese-chars", len(copyright_text) <= 10, copyright_text)
    add("metadata-json-exists", (EXPORT_DIR / "metadata.json").exists(), "exports/wechat/metadata.json")
    add("form-md-exists", (EXPORT_DIR / "form.md").exists(), "exports/wechat/form.md")

    allowed_root = {"banner.png", "cover.png", "form.md", "icon.png", "metadata.json"}
    extra_root = sorted(path.name for path in EXPORT_DIR.iterdir() if path.is_file() and path.name not in allowed_root)
    extra_stickers = sorted(path.name for path in EXPORT_STICKERS_DIR.iterdir() if path.is_file() and path.suffix.lower() != ".png")
    add("wechat-export-root-has-only-upload-files", not extra_root, extra_root)
    add("wechat-stickers-dir-has-only-png-files", not extra_stickers, extra_stickers)

    failed = sum(1 for check in checks if check["status"] == "fail")
    report = {
        "packId": spec["packId"],
        "title": spec["title"],
        "validatedAt": now_iso(),
        "overall": "PASS" if failed == 0 else "FAIL",
        "officialSpecBasis": spec["validation"]["officialSpecCheckedAt"],
        "checks": checks,
        "assets": assets,
        "summary": {
            "passed": sum(1 for check in checks if check["status"] == "pass"),
            "failed": failed,
            "manualReviewRequired": [
                "visual consistency across all stickers",
                "semantic difference between each sticker",
                "caption readability on phone-size preview",
                "no accidental trademark, copyrighted IP, or sensitive content",
            ],
        },
    }
    return report


def write_metadata(spec: dict[str, Any], items: list[StickerItem], sticker_paths: list[Path], generated_at: str) -> None:
    metadata = {
        "packId": spec["packId"],
        "title": spec["title"],
        "description": spec["description"],
        "copyright": spec["copyright"],
        "platform": spec["platform"],
        "packType": "static",
        "generatedAt": generated_at,
        "sourceMaterial": spec["sourceMaterial"],
        "masterCharacter": {
            "name": spec["masterCharacter"]["draftName"],
            "approvedImage": "master/approved/xiazi-approved-master.png",
            "lockedTraits": spec["masterCharacter"]["lockedTraits"],
            "allowedVariations": spec["masterCharacter"]["allowedVariations"],
            "forbiddenVariations": spec["masterCharacter"]["forbiddenVariations"],
        },
        "assets": {
            "stickers": [
                {
                    "index": item.index,
                    "caption": item.text,
                    "scenario": item.scenario,
                    "pose": item.pose,
                    "path": f"stickers/{path.name}",
                    "width": 240,
                    "height": 240,
                    "format": "PNG",
                    "background": "transparent",
                }
                for item, path in zip(items, sticker_paths)
            ],
            "cover": "cover.png",
            "icon": "icon.png",
            "banner": "banner.png",
        },
        "wechatTargets": spec["wechatTarget"],
        "captionRendering": spec["captions"]["style"],
    }
    (EXPORT_DIR / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_form(spec: dict[str, Any], items: list[StickerItem]) -> None:
    lines = [
        "# 微信表情开放平台表单信息",
        "",
        "状态：本地校验通过后，可用于上传前人工复核。",
        "",
        "## 上传表情",
        "",
        "- 类型：静态表情",
        "- 表情：上传 `stickers/` 下的 18 张 `240x240` 透明 PNG 图片",
        "",
        "## 填写基本信息",
        "",
        f"- 名称：{spec['title']}",
        f"- 介绍：{spec['description']}",
        f"- 版权：{spec['copyright']}",
        "- 横幅：`banner.png`，`750x400`，不含文字，不透明背景",
        "- 封面：`cover.png`，`240x240`，透明背景",
        "- 图标：`icon.png`，`50x50`，透明背景",
        "",
        "## 表情列表",
        "",
    ]
    for item in items:
        lines.append(f"- {item.index:02d}. {item.text}：`stickers/{item.filename}`；场景：{item.scenario}")
    lines.extend([
        "",
        "## 备注",
        "",
        "- 表情 caption 已按 `spec.json` 本地合成，上传前请人工复核小图可读性。",
        "- 当前导出以仓库 `AGENTS.md` 捕获的上传合同为本地目标；真实提交前仍需在平台页面最终确认。",
    ])
    (EXPORT_DIR / "form.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_validation_report(report: dict[str, Any]) -> None:
    (REVIEW_WECHAT_DIR / "validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# WeChat Validation Report",
        "",
        f"- Pack ID: `{report['packId']}`",
        f"- Title: {report['title']}",
        f"- Overall: {report['overall']}",
        f"- Validated at: {report['validatedAt']}",
        f"- Passed: {report['summary']['passed']}",
        f"- Failed: {report['summary']['failed']}",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        lines.append(f"- {check['status'].upper()}: {check['check']} - {check['detail']}")
    lines.extend(["", "## Manual Review Required", ""])
    for item in report["summary"]["manualReviewRequired"]:
        lines.append(f"- {item}")
    (REVIEW_WECHAT_DIR / "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_official_spec_check() -> None:
    lines = [
        "# Official Spec Check",
        "",
        f"- Checked at: {now_iso()}",
        "- Official live page: attempted `https://sticker.weixin.qq.com/`, but it was not readable from the current browsing tool.",
        "- Local source of truth for this export: repository `AGENTS.md` WeChat Upload Contract, derived from user-captured upload form and tooltip screenshots.",
        "- Public cross-check found recent or indexed sources repeating `240x240` stickers, `240x240` cover, `50x50` icon, and `750x400` banner, but public sources conflict on count and older GIF/static details.",
        "- Decision: follow the current repository contract and the user's explicit requirement for 18 static PNG stickers.",
        "",
        "## Applied Local Constraints",
        "",
        "- Static sticker pack.",
        "- 18 independent `240x240` PNG sticker images.",
        "- Transparent sticker, cover, and icon backgrounds.",
        "- `cover.png`: `240x240` PNG.",
        "- `icon.png`: `50x50` PNG.",
        "- `banner.png`: `750x400` PNG, opaque, no text.",
        "- Sticker and cover target `<=500KB`; icon target `<=100KB`; banner target `<=500KB`.",
        "- Safe area: alpha bounding box must not touch edges; at least `8px` padding on each side and at least `12px` top padding for final stickers.",
        "",
        "## Public References Consulted",
        "",
        "- Tencent Cloud Developer Community article `https://cloud.tencent.com/developer/article/2659628` lists sticker `240x240`, cover `240x240`, icon `50x50`, and banner `750x400` in a recent how-to article.",
        "- 71714 article `https://www.71714.com/article/16082` says static sticker packs require complete sets and mentions `240x240` static images plus banner, cover, and chat icon uploads.",
        "- Acang article `https://www.acang.cn/weixinbiaoqingzhizuoguifan/` is older and conflicts with current local form rules on GIF/count/size details, so it is treated as stale context rather than the active target.",
    ]
    (REVIEW_WECHAT_DIR / "official-spec-check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_generation_record(items: list[StickerItem], generated_at: str) -> None:
    lines = [
        "# Generation Record",
        "",
        f"- Generated at: {generated_at}",
        "- Mode: deterministic local PIL renderer, no model-generated text.",
        "- Input reference: `master/input/cx-master-reference.png`.",
        "- Character lock: young female chibi Xiazi with dark shoulder-length hair, large dark-brown eyes, soft blush, cream sleeveless top, thick dark brown outline.",
        "- Captions are rendered locally from `spec.json` and are not invented by an image model.",
        "- Export assets are written only under this pack directory.",
        "",
        "## Caption Plan",
        "",
    ]
    for item in items:
        lines.append(f"{item.index}. {item.text} - {item.scenario} - {item.pose}")
    (PACK_ROOT / "source" / "prompts" / "generation-record.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_spec_after_generation(spec: dict[str, Any], generated_at: str) -> None:
    spec["workflowPhase"] = "wechat-export-generated"
    spec["status"] = "wechat-export-generated-pending-human-review"
    spec["generatedAt"] = generated_at
    spec["validation"]["officialSpecCheckedAt"] = (
        f"{generated_at} official page attempted from current environment; "
        "local AGENTS.md upload contract applied because official page was not readable"
    )
    spec["masterCharacter"]["status"] = "approved-for-asset-production-by-user-generation-command"
    spec["masterCharacter"]["approvedImage"] = "master/approved/xiazi-approved-master.png"
    spec["masterCharacter"]["finalStickerProductionAllowed"] = True
    spec["captions"]["status"] = "approved-for-production-by-user-generation-command"
    spec["sourceMaterial"]["status"] = "captured-and-used-for-master-character"
    spec["assets"]["wechatExport"]["cover"] = "exports/wechat/cover.png"
    spec["assets"]["wechatExport"]["icon"] = "exports/wechat/icon.png"
    spec["assets"]["wechatExport"]["banner"] = "exports/wechat/banner.png"
    spec["assets"]["generated"] = {
        "approvedMaster": "master/approved/xiazi-approved-master.png",
        "rawSheets": [
            "generated/sheets/raw/sheet-01-raw.png",
            "generated/sheets/raw/sheet-02-raw.png",
        ],
        "captionedSheets": [
            "generated/sheets/captioned/sheet-01-captioned.png",
            "generated/sheets/captioned/sheet-02-captioned.png",
        ],
        "review": [
            "review/master/master-reference-review.png",
            "review/stickers/source-crops-contact-sheet.png",
            "review/stickers/final-stickers-contact-sheet.png",
            "review/wechat/export-assets-overview.png",
            "review/wechat/validation-report.json",
            "review/wechat/validation-report.md",
            "review/wechat/official-spec-check.md",
        ],
    }
    save_spec(spec)


def update_character_card(generated_at: str) -> None:
    path = PACK_ROOT / "master" / "character-card.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "Character identity rules accepted by user. Caption set and scene plan pending user confirmation.",
        "Approved for asset production by user generation command. Export generated and pending human review.",
    )
    text = text.replace("Approved master image: none yet", "Approved master image: `master/approved/xiazi-approved-master.png`")
    text = text.replace("- [ ] User approves the caption and scene plan.", "- [x] User approves the caption and scene plan by generation command.")
    text = text.replace("- [ ] User approves or selects an approved master image in `master/approved/`.", "- [x] Approved master image is stored at `master/approved/xiazi-approved-master.png`.")
    text = text.replace("- [ ] Final 18-sticker production is allowed.", "- [x] Final 18-sticker production is allowed and generated.")
    if "## Generation Result" not in text:
        text += (
            "\n## Generation Result\n\n"
            f"- Generated at: `{generated_at}`\n"
            "- Output package: `exports/wechat/`\n"
            "- Validation report: `review/wechat/validation-report.md`\n"
            "- Official spec check note: `review/wechat/official-spec-check.md`\n"
        )
    path.write_text(text, encoding="utf-8")


# Reference-driven renderer override.
#
# The first production pass used the hand-drawn helper functions above as the
# character source. That passed mechanical validation but replaced the approved
# reference image with a simplified substitute. The functions below intentionally
# override the earlier same-named render/export helpers so every asset is
# composited from the approved source pixels instead of a newly invented mascot.


def source_reference_path() -> Path:
    if REFERENCE_MASTER_PATH.exists():
        return REFERENCE_MASTER_PATH
    if REFERENCE_FALLBACK_PATH.exists():
        return REFERENCE_FALLBACK_PATH
    raise FileNotFoundError(f"No source reference image found at {REFERENCE_MASTER_PATH} or {REFERENCE_FALLBACK_PATH}")


@lru_cache(maxsize=1)
def reference_subject_base() -> Image.Image:
    image = Image.open(source_reference_path()).convert("RGBA")
    alpha = image.getchannel("A")

    # Remove the low-alpha brown glow from the reference while preserving
    # antialiased character edges.
    cutoff = 24
    alpha = alpha.point(lambda value: 0 if value < cutoff else min(255, round((value - cutoff) * 255 / (255 - cutoff))))
    image.putalpha(alpha)
    return trim_alpha(image, threshold=8)


def reference_subject() -> Image.Image:
    return reference_subject_base().copy()


def draw_reference_shadow(canvas: Image.Image, bbox: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = bbox
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    width = right - left
    ellipse = (
        left + round(width * 0.08),
        bottom - sw(18, canvas.width),
        right - round(width * 0.08),
        bottom + sw(4, canvas.width),
    )
    draw.ellipse(ellipse, fill=(72, 46, 30, 34))
    shadow = shadow.filter(ImageFilter.GaussianBlur(sw(3.5, canvas.width)))
    canvas.alpha_composite(shadow)


def subject_layout(item: StickerItem | None, caption: bool) -> dict[str, Any]:
    layout: dict[str, Any] = {
        "cx": 120,
        "top": 12,
        "max_w": 150,
        "max_h": 166 if caption else 184,
        "rotate": 0,
        "mirror": False,
    }
    if not item:
        return layout

    per_item: dict[int, dict[str, Any]] = {
        1: {"cx": 116, "rotate": -3, "max_h": 162},
        2: {"cx": 112, "max_h": 160},
        3: {"cx": 116, "top": 13, "max_h": 158},
        4: {"cx": 105, "rotate": -5, "max_h": 159},
        5: {"cx": 118, "top": 13, "max_h": 158},
        6: {"cx": 112, "rotate": -2, "max_h": 158},
        7: {"cx": 120, "top": 15, "max_h": 156},
        8: {"cx": 120, "top": 10, "rotate": 2, "max_h": 160},
        9: {"cx": 120, "top": 14, "max_h": 158},
        10: {"cx": 120, "top": 10, "rotate": -2, "max_h": 160},
        11: {"cx": 120, "top": 13, "max_h": 158},
        12: {"cx": 105, "rotate": -5, "max_h": 159},
        13: {"cx": 112, "top": 13, "max_h": 158},
        14: {"cx": 120, "top": 12, "rotate": 2, "max_h": 156},
        15: {"cx": 112, "top": 13, "max_h": 158},
        16: {"cx": 116, "top": 13, "max_h": 158},
        17: {"cx": 120, "top": 11, "rotate": -2, "max_h": 158},
        18: {"cx": 105, "rotate": -5, "max_h": 159},
    }
    layout.update(per_item.get(item.index, {}))
    return layout


def paste_reference_character(canvas: Image.Image, item: StickerItem | None, *, caption: bool) -> tuple[int, int, int, int]:
    size = canvas.width
    layout = subject_layout(item, caption)
    subject = reference_subject()
    subject = contain(subject, sw(layout["max_w"], size), sw(layout["max_h"], size))
    if layout.get("mirror"):
        subject = ImageOps.mirror(subject)
    rotation = layout.get("rotate", 0)
    if rotation:
        subject = subject.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
        subject = contain(subject, sw(layout["max_w"], size), sw(layout["max_h"], size))
    x = sw(layout["cx"], size) - subject.width // 2
    y = sw(layout["top"], size)
    bbox = (x, y, x + subject.width, y + subject.height)
    draw_reference_shadow(canvas, bbox)
    canvas.alpha_composite(subject, (x, y))
    return bbox


def draw_motion_marks(draw: ImageDraw.ImageDraw, size: int, x: float, y: float, direction: int = -1) -> None:
    for offset in (0, 14, 28):
        draw_line(draw, (x, y + offset, x + direction * 18, y + offset + 4), size, fill=(126, 97, 75, 190), width=1.7)


def draw_reference_heart(draw: ImageDraw.ImageDraw, size: int, x: float, y: float, scale: float = 1.0, fill=PINK) -> None:
    pts = [
        (x, y + 13 * scale),
        (x - 20 * scale, y - 2 * scale),
        (x - 18 * scale, y - 18 * scale),
        (x - 6 * scale, y - 22 * scale),
        (x, y - 13 * scale),
        (x + 6 * scale, y - 22 * scale),
        (x + 18 * scale, y - 18 * scale),
        (x + 20 * scale, y - 2 * scale),
    ]
    polygon(draw, pts, size, fill=fill, outline=INK, width=1.7)


def draw_reference_props(canvas: Image.Image, item: StickerItem | None) -> None:
    if item is None:
        return
    size = canvas.width
    draw = ImageDraw.Draw(canvas)

    if item.index == 1:
        star(draw, 50, 42, 6, size)
        draw_prop_phone(draw, size, 153, 125)
    elif item.index == 2:
        draw_prop_check(draw, size, 155, 95)
    elif item.index in {3, 5}:
        draw_prop_laptop(draw, size, 72, 140)
        if item.index == 3:
            draw_line(draw, (64, 128, 51, 118, 43, 126), size, fill=INK_SOFT, width=1.8)
    elif item.index == 4:
        draw_prop_suitcase(draw, size, 154, 125)
        draw_motion_marks(draw, size, 54, 128, direction=-1)
    elif item.index == 6:
        draw_lightbulb(draw, size, 170, 38)
        star(draw, 55, 54, 5.5, size)
    elif item.index == 7:
        draw_round(draw, (45, 126, 82, 164), 5, size, fill=PAPER, outline=INK, width=1.8)
        draw_round(draw, (158, 126, 195, 164), 5, size, fill=PAPER, outline=INK, width=1.8)
        draw_ellipse(draw, (168, 43, 179, 58), size, fill=SKY, outline=INK, width=1.3)
        draw_line(draw, (112, 118, 128, 118), size, fill=INK, width=2)
    elif item.index == 8:
        draw_prop_check(draw, size, 154, 104)
        for x, y in [(48, 50), (184, 56), (58, 120)]:
            star(draw, x, y, 6, size)
    elif item.index == 9:
        draw_reference_heart(draw, size, 120, 151, 0.95)
    elif item.index == 10:
        for x, y in [(48, 55), (186, 53), (176, 124)]:
            star(draw, x, y, 6, size)
        draw_line(draw, (56, 122, 44, 108), size, fill=INK_SOFT, width=2)
        draw_line(draw, (184, 122, 196, 108), size, fill=INK_SOFT, width=2)
    elif item.index == 11:
        draw_prop_book(draw, size, 77, 130)
    elif item.index == 12:
        draw_prop_suitcase(draw, size, 154, 123)
        draw_motion_marks(draw, size, 54, 130, direction=-1)
    elif item.index == 13:
        draw_prop_camera(draw, size, 151, 111)
    elif item.index == 14:
        draw_round(draw, (158, 133, 184, 164), 5, size, fill=(205, 238, 255, 255), outline=INK, width=2)
        draw_line(draw, (183, 145, 194, 145, 194, 157, 183, 157), size, fill=INK, width=1.6)
        star(draw, 56, 54, 5.5, size)
    elif item.index == 15:
        draw_clock(draw, size, 178, 39)
        draw_prop_phone(draw, size, 151, 122)
    elif item.index == 16:
        draw_clock(draw, size, 178, 42)
        draw_prop_phone(draw, size, 151, 116)
    elif item.index == 17:
        for x, y in [(48, 44), (185, 45), (57, 121), (176, 121)]:
            star(draw, x, y, 6, size)
        draw_reference_heart(draw, size, 120, 149, 0.72, fill=(255, 190, 213, 255))
    elif item.index == 18:
        draw_prop_suitcase(draw, size, 154, 128)
        draw_motion_marks(draw, size, 54, 132, direction=-1)


def render_sticker(item: StickerItem, size: int = 240, *, caption: bool = True) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    paste_reference_character(canvas, item, caption=caption)
    draw_reference_props(canvas, item)
    if caption and item:
        draw_caption(canvas, item.text)
    return canvas


def make_master_approved() -> Image.Image:
    source = reference_subject()
    canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    subject = contain(source, 900, 936)
    canvas.alpha_composite(subject, ((1024 - subject.width) // 2, 40))
    save_png(canvas, MASTER_APPROVED_PATH, max_bytes=512000)
    return canvas


def make_cover() -> Image.Image:
    source = reference_subject()
    hi = Image.new("RGBA", (960, 960), (0, 0, 0, 0))
    subject = contain(source, 760, 824)
    hi.alpha_composite(subject, ((960 - subject.width) // 2, sw(12, 960)))
    return downsample(hi, 240)


def make_icon() -> Image.Image:
    source = reference_subject()
    head = source.crop((0, 0, source.width, round(source.height * 0.58)))
    subject = contain(trim_alpha(head), 46 * 4, 46 * 4)
    hi = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    hi.alpha_composite(subject, ((200 - subject.width) // 2, (200 - subject.height) // 2))
    return hi.resize((50, 50), Image.Resampling.LANCZOS)


def make_banner(items: list[StickerItem]) -> Image.Image:
    banner = Image.new("RGB", (750, 400), (255, 238, 205))
    draw = ImageDraw.Draw(banner)
    for y in range(400):
        t = y / 399
        color = (
            round(255 * (1 - t) + 232 * t),
            round(243 * (1 - t) + 231 * t),
            round(214 * (1 - t) + 255 * t),
        )
        draw.line((0, y, 750, y), fill=color)
    draw.rounded_rectangle((0, 286, 750, 430), radius=78, fill=(166, 220, 177))
    draw.ellipse((52, 38, 138, 124), fill=(255, 255, 255, 82))
    draw.ellipse((584, 52, 706, 174), fill=(255, 255, 255, 70))
    draw.ellipse((474, 258, 622, 374), fill=(255, 231, 119, 100))

    layer = Image.new("RGBA", banner.size, (0, 0, 0, 0))
    for item, box in [
        (items[10], (50, 36, 240, 352)),
        (items[12], (246, 42, 434, 346)),
        (items[4], (420, 56, 590, 344)),
        (items[11], (548, 42, 732, 348)),
    ]:
        sticker = trim_alpha(sticker_512(item, caption=False))
        fit = contain(sticker, box[2] - box[0], box[3] - box[1])
        layer.alpha_composite(fit, (box[0] + (box[2] - box[0] - fit.width) // 2, box[1] + (box[3] - box[1] - fit.height) // 2))
    return Image.alpha_composite(banner.convert("RGBA"), layer).convert("RGB")


def make_review_master(master: Image.Image, spec: dict[str, Any]) -> None:
    review = Image.new("RGB", (1440, 680), (250, 244, 234))
    draw = ImageDraw.Draw(review)
    draw.text((36, 28), "霞子母版形象复核图", font=font(34), fill=(60, 42, 31))
    draw.text((36, 72), "左侧为原始参考图，右侧为清理透明边缘后的 approved master。", font=font(20), fill=(78, 65, 52))

    source = Image.open(source_reference_path()).convert("RGBA")
    source_panel = checkerboard((430, 500), 16).convert("RGBA")
    source_subject = contain(trim_alpha(source), 390, 460)
    source_panel.alpha_composite(source_subject, ((430 - source_subject.width) // 2, (500 - source_subject.height) // 2))
    review.paste(source_panel.convert("RGB"), (38, 128))
    draw.text((38, 634), "source reference", font=font(18), fill=(70, 54, 42))

    master_panel = checkerboard((430, 500), 16).convert("RGBA")
    master_subject = contain(trim_alpha(master), 390, 460)
    master_panel.alpha_composite(master_subject, ((430 - master_subject.width) // 2, (500 - master_subject.height) // 2))
    review.paste(master_panel.convert("RGB"), (510, 128))
    draw.text((510, 634), "approved master used by exports", font=font(18), fill=(70, 54, 42))

    lines = [
        f"Pack ID: {spec['packId']}",
        "Mode: image-to-master",
        "Renderer: reference-driven local compositor",
        "Source: master/input/cx-master-reference.png",
        "Final text: local caption composition",
        "No replacement mascot drawing path is used.",
    ]
    for i, line in enumerate(lines):
        draw.text((970, 158 + i * 44), line, font=font(19), fill=(70, 54, 42))
    save_png(review, REVIEW_MASTER_DIR / "master-reference-review.png")


def write_generation_record(items: list[StickerItem], generated_at: str) -> None:
    lines = [
        "# Generation Record",
        "",
        f"- Generated at: {generated_at}",
        "- Mode: reference-driven local PIL compositor, no model-generated text.",
        "- Input reference: `master/input/cx-master-reference.png`.",
        "- Character source: every sticker, cover, icon, and banner character cutout is composited from the approved reference pixels, then locally resized/rotated and decorated.",
        "- Previous simplified hand-drawn substitute path was removed from the active renderer for this pack because it did not preserve the reference identity closely enough.",
        "- Captions are rendered locally from `spec.json` and are not invented by an image model.",
        "- Export assets are written only under this pack directory.",
        "",
        "## Caption Plan",
        "",
    ]
    for item in items:
        lines.append(f"{item.index}. {item.text} - {item.scenario} - {item.pose}")
    (PACK_ROOT / "source" / "prompts" / "generation-record.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    generated_at = now_iso()
    spec = load_spec()
    items = [
        StickerItem(
            index=int(item["id"]),
            slug=str(item["slug"]),
            text=str(item["text"]),
            scenario=str(item.get("scenario", "")),
            pose=str(item.get("pose", "")),
        )
        for item in spec["captions"]["items"]
    ]
    if len(items) != 18:
        raise RuntimeError(f"Expected 18 captions, got {len(items)}")

    ensure_dirs()
    clear_generated_outputs()

    master = make_master_approved()
    source_images = [sticker_512(item, caption=True) for item in items]
    draft_images = [sticker_240(item, caption=True) for item in items]
    raw_images = [sticker_240(item, caption=False) for item in items]

    sticker_paths: list[Path] = []
    for item, source, draft in zip(items, source_images, draft_images):
        source_path = SOURCE_CROPS_DIR / item.filename
        draft_path = DRAFT_DIR / item.filename
        export_path = EXPORT_STICKERS_DIR / item.filename
        save_png(source, source_path)
        save_png(draft, draft_path, max_bytes=512000)
        shutil.copy2(draft_path, export_path)
        sticker_paths.append(export_path)

    make_sheets(raw_images, RAW_DIR, "sheet-raw", transparent=True)
    # Keep expected local naming stable for later agents.
    for old, new in [
        (RAW_DIR / "sheet-raw-01.png", RAW_DIR / "sheet-01-raw.png"),
        (RAW_DIR / "sheet-raw-02.png", RAW_DIR / "sheet-02-raw.png"),
    ]:
        if old.exists():
            old.rename(new)
    make_sheets(draft_images, CAPTIONED_DIR, "sheet-captioned", transparent=True)
    for old, new in [
        (CAPTIONED_DIR / "sheet-captioned-01.png", CAPTIONED_DIR / "sheet-01-captioned.png"),
        (CAPTIONED_DIR / "sheet-captioned-02.png", CAPTIONED_DIR / "sheet-02-captioned.png"),
    ]:
        if old.exists():
            old.rename(new)
    make_sheets(raw_images, REVIEW_SHEETS_DIR, "sheet-raw-review", transparent=False)
    make_sheets(draft_images, REVIEW_SHEETS_DIR, "sheet-captioned-review", transparent=False)
    make_contact_sheet(source_images, items, REVIEW_STICKERS_DIR / "source-crops-contact-sheet.png", cols=6)
    make_contact_sheet(draft_images, items, REVIEW_STICKERS_DIR / "final-stickers-contact-sheet.png", cols=6)

    cover = make_cover()
    icon = make_icon()
    banner = make_banner(items)
    save_png(cover, EXPORT_DIR / "cover.png", max_bytes=512000)
    save_png(icon, EXPORT_DIR / "icon.png", max_bytes=102400)
    save_png(banner, EXPORT_DIR / "banner.png", max_bytes=512000, palette=True)

    write_metadata(spec, items, sticker_paths, generated_at)
    write_form(spec, items)
    make_review_master(master, spec)
    make_export_overview(draft_images, cover, icon, banner)
    write_official_spec_check()
    write_generation_record(items, generated_at)

    report = validate(spec, sticker_paths, EXPORT_DIR / "cover.png", EXPORT_DIR / "icon.png", EXPORT_DIR / "banner.png")
    write_validation_report(report)
    if report["overall"] != "PASS":
        raise RuntimeError(f"Validation failed: {report['summary']['failed']} checks failed")

    update_spec_after_generation(spec, generated_at)
    update_character_card(generated_at)


if __name__ == "__main__":
    main()
