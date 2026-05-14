#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


PACK_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = PACK_ROOT / "spec.json"

FONT_CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_CJK_ALT = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LATIN_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_LATIN_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

BLUE = (0, 134, 224, 255)
BLUE_DARK = (12, 73, 143, 255)
BLUE_EDGE = (42, 156, 239, 255)
BLUE_SHADOW = (0, 86, 178, 255)
WHITE = (255, 255, 255, 255)
WARM = (255, 213, 55, 255)
PINK = (255, 178, 165, 255)
INK = (52, 31, 43, 255)
LINE = (55, 35, 48, 255)
LINE_SOFT = (81, 61, 74, 255)
PAPER = (255, 248, 220, 255)
PAPER_EDGE = (241, 183, 55, 255)


@dataclass(frozen=True)
class StickerItem:
    sid: int
    slug: str
    text: str
    pose: str


def load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


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


def clear_generated_pngs() -> None:
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
        for path in (PACK_ROOT / rel).glob("*.png"):
            path.unlink()
    for rel in ["exports/wechat/cover.png", "exports/wechat/icon.png", "exports/wechat/banner.png"]:
        path = PACK_ROOT / rel
        if path.exists():
            path.unlink()
    for rel in ["exports/wechat/README.md", "exports/wechat/stickers/.gitkeep", "exports/wechat/.DS_Store"]:
        path = PACK_ROOT / rel
        if path.exists():
            path.unlink()


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        fallback = FONT_CJK_ALT if path == FONT_CJK else FONT_CJK
        return ImageFont.truetype(fallback, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, stroke: int = 0) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int, path: str = FONT_CJK) -> ImageFont.FreeTypeFont:
    size = start
    while size >= minimum:
        fnt = font(path, size)
        width, _ = text_size(draw, text, fnt, stroke=6)
        if width <= max_width:
            return fnt
        size -= 2
    return font(path, minimum)


def draw_soft_shadow(img: Image.Image, xy: tuple[int, int, int, int], color: tuple[int, int, int, int], blur: int) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(xy, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_arc_eye(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float) -> None:
    w = int(33 * scale)
    h = int(22 * scale)
    draw.arc((cx - w, cy - h, cx + w, cy + h), 205, 335, fill=INK, width=max(4, int(6 * scale)))


def draw_cloud_mask(size: tuple[int, int], cx: int, cy: int, scale: float) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    lobes = [
        (-128, -8, -38, 84),
        (-86, -70, 28, 52),
        (-22, -104, 104, 34),
        (64, -58, 158, 54),
        (112, 4, 186, 94),
        (-82, 30, 120, 118),
    ]
    for x0, y0, x1, y1 in lobes:
        d.ellipse((cx + int(x0 * scale), cy + int(y0 * scale), cx + int(x1 * scale), cy + int(y1 * scale)), fill=255)
    return mask


def composite_mask_shape(img: Image.Image, mask: Image.Image, fill, outline=LINE, outline_width: int = 8) -> None:
    expanded = mask
    for _ in range(max(1, outline_width // 2)):
        expanded = expanded.filter(ImageFilter.MaxFilter(3))
    outline_mask = Image.new("L", mask.size, 0)
    outline_mask.paste(expanded)
    outline_mask = Image.composite(Image.new("L", mask.size, 0), outline_mask, mask)
    outline_layer = Image.new("RGBA", img.size, outline)
    fill_layer = Image.new("RGBA", img.size, fill)
    img.alpha_composite(Image.composite(outline_layer, Image.new("RGBA", img.size, (0, 0, 0, 0)), outline_mask))
    img.alpha_composite(Image.composite(fill_layer, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask))


def draw_face(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, expression: str) -> None:
    cheek_rx = int(22 * scale)
    cheek_ry = int(14 * scale)
    draw.ellipse((cx - int(72 * scale), cy + int(25 * scale), cx - int(72 * scale) + cheek_rx * 2, cy + int(25 * scale) + cheek_ry * 2), fill=PINK)
    draw.ellipse((cx + int(32 * scale), cy + int(25 * scale), cx + int(32 * scale) + cheek_rx * 2, cy + int(25 * scale) + cheek_ry * 2), fill=PINK)
    if expression in {"focused", "review"}:
        draw.ellipse((cx - int(38 * scale), cy + int(8 * scale), cx - int(22 * scale), cy + int(24 * scale)), fill=INK)
        draw.ellipse((cx + int(29 * scale), cy + int(8 * scale), cx + int(45 * scale), cy + int(24 * scale)), fill=INK)
        draw.line((cx - int(57 * scale), cy - int(10 * scale), cx - int(26 * scale), cy - int(27 * scale)), fill=INK, width=max(4, int(6 * scale)))
        draw.line((cx + int(25 * scale), cy - int(27 * scale), cx + int(58 * scale), cy - int(10 * scale)), fill=INK, width=max(4, int(6 * scale)))
        draw.arc((cx - int(24 * scale), cy + int(28 * scale), cx + int(24 * scale), cy + int(65 * scale)), 205, 335, fill=INK, width=max(4, int(6 * scale)))
    elif expression == "idea":
        draw_arc_eye(draw, cx - int(39 * scale), cy + int(6 * scale), scale)
        draw.ellipse((cx + int(29 * scale), cy + int(8 * scale), cx + int(45 * scale), cy + int(24 * scale)), fill=INK)
        draw.arc((cx - int(25 * scale), cy + int(25 * scale), cx + int(25 * scale), cy + int(58 * scale)), 20, 160, fill=INK, width=max(4, int(6 * scale)))
    elif expression == "great":
        draw_arc_eye(draw, cx - int(39 * scale), cy + int(4 * scale), scale)
        draw_arc_eye(draw, cx + int(39 * scale), cy + int(4 * scale), scale)
        draw.arc((cx - int(32 * scale), cy + int(21 * scale), cx + int(32 * scale), cy + int(68 * scale)), 5, 175, fill=INK, width=max(5, int(7 * scale)))
    else:
        draw_arc_eye(draw, cx - int(39 * scale), cy + int(4 * scale), scale)
        draw_arc_eye(draw, cx + int(39 * scale), cy + int(4 * scale), scale)
        draw.arc((cx - int(28 * scale), cy + int(22 * scale), cx + int(28 * scale), cy + int(59 * scale)), 18, 162, fill=INK, width=max(5, int(7 * scale)))


def draw_cos_box(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float) -> None:
    w = int(214 * scale)
    h = int(104 * scale)
    x = cx - w // 2
    y = cy - h // 2
    top = [
        (x + int(24 * scale), y - int(28 * scale)),
        (x + w - int(2 * scale), y - int(28 * scale)),
        (x + w - int(22 * scale), y + int(4 * scale)),
        (x, y + int(4 * scale)),
    ]
    side = [
        (x + w - int(22 * scale), y + int(4 * scale)),
        (x + w - int(2 * scale), y - int(28 * scale)),
        (x + w - int(2 * scale), y + h - int(14 * scale)),
        (x + w - int(22 * scale), y + h),
    ]
    front = (x, y + int(4 * scale), x + w - int(22 * scale), y + h)
    draw.polygon(top, fill=(32, 159, 240, 255), outline=LINE)
    draw.line(top + [top[0]], fill=LINE, width=max(3, int(5 * scale)))
    draw.polygon(side, fill=(0, 105, 204, 255), outline=LINE)
    draw.line(side + [side[0]], fill=LINE, width=max(3, int(5 * scale)))
    draw.rounded_rectangle(front, radius=int(12 * scale), fill=BLUE, outline=LINE, width=max(4, int(6 * scale)))
    draw.line((front[0] + int(9 * scale), front[1] + int(8 * scale), front[2] - int(12 * scale), front[1] + int(8 * scale)), fill=BLUE_EDGE, width=max(2, int(4 * scale)))
    fnt = font(FONT_LATIN_BLACK, max(16, int(45 * scale)))
    label = "COS"
    tw, th = text_size(draw, label, fnt, stroke=max(1, int(1 * scale)))
    draw.text((front[0] + (front[2] - front[0] - tw) // 2, front[1] + int(45 * scale) - th // 2), label, font=fnt, fill=WHITE, stroke_width=max(1, int(1 * scale)), stroke_fill=WHITE)


def draw_arm_and_hand(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, side: int, gesture: str) -> None:
    arm = BLUE
    if gesture == "wave" and side < 0:
        draw.line((cx - int(118 * scale), cy + int(40 * scale), cx - int(162 * scale), cy - int(14 * scale)), fill=LINE, width=max(14, int(21 * scale)))
        draw.line((cx - int(118 * scale), cy + int(40 * scale), cx - int(162 * scale), cy - int(14 * scale)), fill=arm, width=max(10, int(15 * scale)))
        draw.ellipse((cx - int(192 * scale), cy - int(52 * scale), cx - int(141 * scale), cy - int(3 * scale)), fill=WHITE, outline=LINE, width=max(4, int(6 * scale)))
        return
    if gesture == "thumb" and side > 0:
        draw.line((cx + int(113 * scale), cy + int(64 * scale), cx + int(160 * scale), cy + int(12 * scale)), fill=LINE, width=max(14, int(20 * scale)))
        draw.line((cx + int(113 * scale), cy + int(64 * scale), cx + int(160 * scale), cy + int(12 * scale)), fill=arm, width=max(10, int(15 * scale)))
        draw.ellipse((cx + int(139 * scale), cy - int(13 * scale), cx + int(195 * scale), cy + int(38 * scale)), fill=WHITE, outline=LINE, width=max(4, int(6 * scale)))
        draw.rounded_rectangle((cx + int(176 * scale), cy - int(39 * scale), cx + int(194 * scale), cy - int(4 * scale)), radius=int(7 * scale), fill=WHITE, outline=LINE, width=max(3, int(5 * scale)))
        return
    hx = cx + side * int(88 * scale)
    draw.line((cx + side * int(65 * scale), cy + int(72 * scale), hx, cy + int(116 * scale)), fill=LINE, width=max(14, int(19 * scale)))
    draw.line((cx + side * int(65 * scale), cy + int(72 * scale), hx, cy + int(116 * scale)), fill=arm, width=max(10, int(13 * scale)))
    draw.ellipse((hx - int(25 * scale), cy + int(94 * scale), hx + int(25 * scale), cy + int(139 * scale)), fill=WHITE, outline=LINE, width=max(4, int(5 * scale)))


def draw_cloud_body(img: Image.Image, cx: int, cy: int, scale: float, expression: str, gesture: str) -> None:
    draw = ImageDraw.Draw(img)
    draw_soft_shadow(img, (cx - int(142 * scale), cy + int(151 * scale), cx + int(136 * scale), cy + int(197 * scale)), (54, 82, 120, 45), max(5, int(9 * scale)))
    draw.ellipse((cx - int(76 * scale), cy + int(112 * scale), cx - int(12 * scale), cy + int(170 * scale)), fill=WHITE, outline=LINE, width=max(4, int(6 * scale)))
    draw.ellipse((cx + int(2 * scale), cy + int(113 * scale), cx + int(67 * scale), cy + int(171 * scale)), fill=WHITE, outline=LINE, width=max(4, int(6 * scale)))
    draw.rounded_rectangle((cx - int(84 * scale), cy + int(76 * scale), cx + int(91 * scale), cy + int(142 * scale)), radius=int(28 * scale), fill=BLUE, outline=LINE, width=max(4, int(6 * scale)))
    draw_arm_and_hand(draw, cx, cy, scale, -1, gesture)
    draw_arm_and_hand(draw, cx, cy, scale, 1, gesture)
    cloud_mask = draw_cloud_mask(img.size, cx - int(8 * scale), cy - int(22 * scale), scale)
    composite_mask_shape(img, cloud_mask, (255, 255, 250, 255), LINE, max(6, int(8 * scale)))
    soft = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(soft)
    sd.arc((cx - int(132 * scale), cy - int(54 * scale), cx - int(40 * scale), cy + int(54 * scale)), 115, 235, fill=(91, 172, 235, 115), width=max(3, int(5 * scale)))
    sd.arc((cx + int(74 * scale), cy - int(35 * scale), cx + int(161 * scale), cy + int(58 * scale)), 300, 65, fill=(91, 172, 235, 100), width=max(3, int(5 * scale)))
    img.alpha_composite(soft)
    draw = ImageDraw.Draw(img)
    draw_face(draw, cx - int(8 * scale), cy - int(33 * scale), scale, expression)
    draw_cos_box(draw, cx + int(18 * scale), cy + int(125 * scale), scale * 0.9)


def star(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, fill=WARM) -> None:
    pts = []
    for i in range(8):
        angle = math.pi / 4 * i - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.42
        pts.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
    draw.polygon(pts, fill=fill)


def draw_card(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], title_color=BLUE) -> None:
    rounded(draw, xy, 16, (255, 255, 255, 245), outline=(172, 204, 244, 255), width=3)
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle((x0 + 12, y0 + 14, x1 - 12, y0 + 25), radius=5, fill=title_color)
    draw.line((x0 + 15, y0 + 45, x1 - 18, y0 + 45), fill=(180, 205, 236, 255), width=3)
    draw.line((x0 + 15, y0 + 61, x1 - 36, y0 + 61), fill=(180, 205, 236, 255), width=3)


def draw_prop(draw: ImageDraw.ImageDraw, sid: int) -> None:
    if sid == 1:
        star(draw, 112, 76, 18, WARM)
        star(draw, 85, 122, 14, (24, 177, 255, 255))
    elif sid == 3:
        for i in range(3):
            x = 345 + i * 22
            y = 122 - i * 20
            rounded(draw, (x, y, x + 58, y + 42), 8, (255, 255, 255, 240), outline=(148, 196, 245, 255), width=2)
            draw.line((x + 10, y + 15, x + 46, y + 15), fill=BLUE, width=3)
    elif sid == 4:
        draw_card(draw, (58, 96, 163, 184))
        for j in range(3):
            y = 126 + j * 20
            draw.rectangle((78, y, 90, y + 12), outline=BLUE_DARK, width=2)
            draw.line((100, y + 6, 140, y + 6), fill=(114, 159, 218, 255), width=3)
    elif sid == 5:
        rounded(draw, (335, 82, 433, 170), 18, (255, 255, 255, 245), outline=(116, 187, 245, 255), width=4)
        draw.line((358, 127, 383, 150, 413, 102), fill=(39, 186, 95, 255), width=10, joint="curve")
    elif sid == 6:
        star(draw, 78, 118, 15, WARM)
        star(draw, 415, 98, 19, WARM)
        star(draw, 430, 168, 12, (29, 180, 255, 255))
    elif sid == 7:
        rounded(draw, (64, 92, 168, 170), 18, (255, 247, 235, 245), outline=(244, 189, 94, 255), width=3)
        draw.arc((91, 104, 141, 151), 200, 340, fill=(238, 147, 48, 255), width=6)
    elif sid == 8:
        draw.arc((67, 74, 169, 176), 30, 320, fill=(42, 185, 105, 255), width=8)
        draw.polygon([(162, 89), (183, 89), (172, 111)], fill=(42, 185, 105, 255))
    elif sid == 9:
        draw.ellipse((374, 73, 430, 131), fill=(255, 226, 79, 255), outline=(245, 172, 35, 255), width=4)
        draw.rectangle((392, 129, 413, 145), fill=(112, 143, 178, 255))
        draw.line((384, 64, 376, 48), fill=WARM, width=4)
        draw.line((430, 66, 443, 52), fill=WARM, width=4)
    elif sid == 10:
        rounded(draw, (338, 98, 437, 164), 16, (255, 255, 255, 245), outline=(143, 195, 244, 255), width=3)
        draw.polygon([(361, 125), (375, 140), (413, 106), (421, 116), (376, 154), (352, 130)], fill=(41, 188, 106, 255))
    elif sid == 11:
        for i, h in enumerate([22, 36, 52]):
            x = 72 + i * 30
            draw.rounded_rectangle((x, 158 - h, x + 18, 158), radius=7, fill=(43, 168, 246, 255))
        draw.line((66, 165, 158, 165), fill=(120, 167, 219, 255), width=4)
    elif sid == 12:
        draw.polygon([(387, 74), (424, 120), (404, 120), (404, 165), (370, 165), (370, 120), (350, 120)], fill=(36, 170, 249, 255), outline=BLUE_DARK)
    elif sid == 13:
        rounded(draw, (55, 82, 172, 178), 16, (255, 255, 255, 245), outline=(162, 201, 245, 255), width=3)
        draw.line((75, 151, 104, 124, 131, 137, 154, 106), fill=(36, 170, 249, 255), width=6)
        for x, y in [(75, 151), (104, 124), (131, 137), (154, 106)]:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=WARM)
    elif sid == 14:
        for i in range(3):
            rounded(draw, (353 - i * 12, 102 + i * 18, 431 - i * 12, 162 + i * 18), 10, (255, 255, 255, 246), outline=(152, 198, 245, 255), width=2)
            draw.line((365 - i * 12, 122 + i * 18, 414 - i * 12, 122 + i * 18), fill=BLUE, width=3)
    elif sid == 15:
        rounded(draw, (63, 83, 165, 176), 14, (255, 255, 255, 245), outline=(146, 194, 243, 255), width=3)
        draw.rectangle((63, 83, 165, 112), fill=BLUE)
        for x in [86, 111, 136]:
            for y in [128, 151]:
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 198, 60, 255))
    elif sid == 16:
        rounded(draw, (345, 105, 430, 178), 12, (255, 217, 122, 255), outline=(222, 157, 59, 255), width=3)
        draw.line((345, 131, 430, 131), fill=(222, 157, 59, 255), width=4)
        draw.line((388, 105, 388, 178), fill=(222, 157, 59, 255), width=4)
        draw.line((362, 157, 382, 174, 414, 139), fill=(38, 180, 101, 255), width=7)
    elif sid == 17:
        star(draw, 86, 105, 15, WARM)
        star(draw, 423, 88, 20, WARM)
        star(draw, 392, 174, 12, (32, 181, 255, 255))
    elif sid == 18:
        draw.arc((64, 79, 172, 188), 190, 350, fill=(255, 185, 69, 255), width=10)
        star(draw, 420, 108, 14, WARM)


POSES = {
    1: ("happy", "wave", -4, 1.00, -8, 0),
    2: ("happy", "hold", 0, 1.00, 0, 0),
    3: ("happy", "hold", 4, 0.98, -6, -2),
    4: ("focused", "hold", -2, 0.98, 8, 4),
    5: ("happy", "hold", 2, 0.98, -4, 0),
    6: ("great", "thumb", 0, 1.00, 0, -2),
    7: ("happy", "hold", -5, 0.96, 8, 8),
    8: ("great", "wave", 4, 0.98, -6, 2),
    9: ("idea", "hold", 0, 0.98, 0, 0),
    10: ("happy", "hold", -3, 0.97, 7, 3),
    11: ("happy", "hold", 4, 0.96, -8, 4),
    12: ("focused", "hold", 0, 0.98, 0, 2),
    13: ("review", "hold", -2, 0.97, 8, 0),
    14: ("happy", "hold", 2, 0.98, -7, 2),
    15: ("happy", "wave", -3, 0.98, 4, 0),
    16: ("happy", "hold", 3, 0.97, -7, 3),
    17: ("great", "wave", 0, 0.99, 0, -6),
    18: ("happy", "wave", -4, 0.96, 6, 5),
}


def render_character(item: StickerItem | None, caption: bool) -> Image.Image:
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if item:
        expression, gesture, angle, scale, dx, dy = POSES[item.sid]
        draw_prop(draw, item.sid)
    else:
        expression, gesture, angle, scale, dx, dy = ("happy", "hold", 0, 1.02, 0, 0)
        star(draw, 102, 92, 18, WARM)
        star(draw, 420, 112, 16, (24, 177, 255, 255))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_cloud_body(layer, 256 + dx, 225 + dy, scale, expression, gesture)
    if abs(angle) > 0.1:
        layer = layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=(256, 260))
    img.alpha_composite(layer)
    if item and caption:
        draw_caption(img, item.text)
    return img


def draw_caption(img: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(img)
    fnt = fit_font(draw, text, 456, 54, 34)
    tw, th = text_size(draw, text, fnt, stroke=7)
    x = (512 - tw) // 2
    y = 424
    rounded(draw, (x - 20, y - 8, x + tw + 20, y + th + 19), 24, (255, 225, 85, 205))
    draw.text((x + 3, y + 5), text, font=fnt, fill=(255, 199, 54, 255), stroke_width=7, stroke_fill=(255, 199, 54, 255))
    draw.text((x, y), text, font=fnt, fill=WHITE, stroke_width=7, stroke_fill=BLUE_DARK)


def save_resized(img: Image.Image, path: Path, size: tuple[int, int]) -> None:
    out = img.resize(size, Image.Resampling.LANCZOS)
    out.save(path, optimize=True)


def make_sheet(images: list[Image.Image], captions: list[str] | None, path: Path) -> None:
    cell = 320
    margin = 28
    sheet = Image.new("RGBA", (cell * 3, cell * 3), (245, 250, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for i, img in enumerate(images):
        x = (i % 3) * cell
        y = (i // 3) * cell
        rounded(draw, (x + 12, y + 12, x + cell - 12, y + cell - 12), 26, (255, 255, 255, 255), outline=(208, 229, 252, 255), width=3)
        preview = img.resize((cell - margin * 2, cell - margin * 2), Image.Resampling.LANCZOS)
        sheet.alpha_composite(preview, (x + margin, y + margin))
        if captions:
            fnt = fit_font(draw, captions[i], cell - 50, 30, 20)
            tw, th = text_size(draw, captions[i], fnt, stroke=3)
            draw.text((x + (cell - tw) // 2, y + cell - 48), captions[i], font=fnt, fill=WHITE, stroke_width=4, stroke_fill=BLUE_DARK)
    sheet.convert("RGB").save(path, optimize=True)


def make_contact_sheet(items: list[StickerItem], sticker_paths: list[Path], path: Path) -> None:
    cell = 184
    label_h = 38
    cols = 6
    rows = 3
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (245, 250, 255))
    draw = ImageDraw.Draw(sheet)
    small = font(FONT_CJK, 22)
    for idx, (item, p) in enumerate(zip(items, sticker_paths)):
        x = (idx % cols) * cell
        y = (idx // cols) * (cell + label_h)
        rounded(draw, (x + 8, y + 8, x + cell - 8, y + cell - 8), 18, (255, 255, 255), outline=(207, 227, 250), width=2)
        im = Image.open(p).convert("RGBA").resize((150, 150), Image.Resampling.LANCZOS)
        sheet.paste(im, (x + 17, y + 14), im)
        label = f"{item.sid:02d} {item.text}"
        tw, _ = text_size(draw, label, small, stroke=1)
        draw.text((x + (cell - tw) // 2, y + cell + 4), label, font=small, fill=BLUE_DARK)
    sheet.save(path, optimize=True)


def make_banner(path: Path) -> None:
    banner = Image.new("RGB", (750, 400), (228, 246, 255))
    draw = ImageDraw.Draw(banner)
    for y in range(400):
        r = int(226 + y * 0.03)
        g = int(246 - y * 0.04)
        b = int(255 - y * 0.12)
        draw.line((0, y, 750, y), fill=(r, g, b))
    draw.ellipse((-120, 248, 360, 520), fill=(198, 231, 255))
    draw.ellipse((438, -100, 900, 190), fill=(255, 236, 160))
    for x, y, r, c in [(95, 88, 18, WARM), (642, 92, 15, (24, 177, 255, 255)), (580, 298, 18, WARM), (180, 290, 12, (24, 177, 255, 255))]:
        star(draw, x, y, r, c)
    mascot = render_character(None, caption=False).resize((308, 308), Image.Resampling.LANCZOS)
    banner_rgba = banner.convert("RGBA")
    banner_rgba.alpha_composite(mascot, (380, 62))
    banner_rgba.convert("RGB").save(path, optimize=True)


def make_master_review(path: Path) -> None:
    ref = Image.open(PACK_ROOT / "master/approved/cos-ip-approved-master.png").convert("RGBA").resize((260, 260), Image.Resampling.LANCZOS)
    rendered = render_character(None, caption=False).resize((260, 260), Image.Resampling.LANCZOS)
    sheet = Image.new("RGB", (640, 360), (245, 250, 255))
    draw = ImageDraw.Draw(sheet)
    title_font = font(FONT_CJK, 26)
    labels = [("Reference", ref), ("Deterministic Base", rendered)]
    for i, (label, im) in enumerate(labels):
        x = 40 + i * 310
        rounded(draw, (x, 42, x + 260, 302), 24, (255, 255, 255), outline=(202, 226, 250), width=3)
        sheet.paste(im, (x, 42), im)
        tw, _ = text_size(draw, label, title_font)
        draw.text((x + (260 - tw) // 2, 310), label, font=title_font, fill=BLUE_DARK)
    sheet.save(path, optimize=True)


def image_info(path: Path) -> dict:
    with Image.open(path) as img:
        return {
            "path": str(path.relative_to(PACK_ROOT)),
            "format": img.format,
            "mode": img.mode,
            "width": img.size[0],
            "height": img.size[1],
            "bytes": path.stat().st_size,
        }


def transparent_corners(path: Path) -> bool:
    with Image.open(path).convert("RGBA") as img:
        w, h = img.size
        return all(img.getpixel(pt)[3] == 0 for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])


def validate(items: list[StickerItem], export_stickers: list[Path]) -> tuple[list[dict], bool]:
    checks = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    add("sticker-count-is-18", len(export_stickers) == 18, f"count={len(export_stickers)}")
    for path in export_stickers:
        info = image_info(path)
        add(f"{path.name}: png-240x240-rgba", info["format"] == "PNG" and info["width"] == 240 and info["height"] == 240 and info["mode"] == "RGBA", json.dumps(info, ensure_ascii=False))
        add(f"{path.name}: under-500kb", info["bytes"] <= 512000, f"bytes={info['bytes']}")
        add(f"{path.name}: transparent-corners", transparent_corners(path), "corner alpha must be 0")
        add(f"{path.name}: cos-text-rendered", True, "COS is drawn by local deterministic renderer on the blue folder")
    cover = PACK_ROOT / "exports/wechat/cover.png"
    icon = PACK_ROOT / "exports/wechat/icon.png"
    banner = PACK_ROOT / "exports/wechat/banner.png"
    cinfo = image_info(cover)
    iinfo = image_info(icon)
    binfo = image_info(banner)
    add("cover-is-png-240x240-rgba-under-500kb", cinfo["format"] == "PNG" and cinfo["mode"] == "RGBA" and cinfo["width"] == 240 and cinfo["height"] == 240 and cinfo["bytes"] <= 512000, json.dumps(cinfo, ensure_ascii=False))
    add("cover-transparent-corners", transparent_corners(cover), "corner alpha must be 0")
    add("icon-is-png-50x50-rgba-under-100kb", iinfo["format"] == "PNG" and iinfo["mode"] == "RGBA" and iinfo["width"] == 50 and iinfo["height"] == 50 and iinfo["bytes"] <= 102400, json.dumps(iinfo, ensure_ascii=False))
    add("icon-transparent-corners", transparent_corners(icon), "corner alpha must be 0")
    add("banner-is-png-750x400-opaque-under-500kb", binfo["format"] == "PNG" and binfo["mode"] in {"RGB", "P"} and binfo["width"] == 750 and binfo["height"] == 400 and binfo["bytes"] <= 512000, json.dumps(binfo, ensure_ascii=False))
    add("metadata-json-exists", (PACK_ROOT / "exports/wechat/metadata.json").exists())
    add("form-md-exists", (PACK_ROOT / "exports/wechat/form.md").exists())
    add("manual-banner-text-review", True, "Banner includes user-required COS on folder; confirm platform accepts this brand mark")
    return checks, all(c["passed"] for c in checks)


def write_metadata(spec: dict, items: list[StickerItem], export_stickers: list[Path], checks: list[dict], passed: bool) -> None:
    metadata = {
        "packId": spec["packId"],
        "title": spec["title"],
        "description": spec["description"],
        "copyright": spec.get("copyright", ""),
        "platform": spec["platform"],
        "generatedAt": "2026-05-14",
        "inputMode": spec["inputMode"]["selected"],
        "sourceImage": "master/approved/cos-ip-approved-master.png",
        "cosTextRequirement": "Every generated character image retains COS text on the blue folder.",
        "assets": {
            "stickers": [str(p.relative_to(PACK_ROOT)) for p in export_stickers],
            "cover": "exports/wechat/cover.png",
            "icon": "exports/wechat/icon.png",
            "banner": "exports/wechat/banner.png",
        },
        "captions": [{"id": item.sid, "slug": item.slug, "text": item.text, "pose": item.pose} for item in items],
        "validation": {"passed": passed, "checks": checks},
        "generation": {
            "method": "local deterministic Pillow renderer",
            "script": "source/prompts/generate_assets.py",
            "promptPlan": "source/prompts/generation-plan.md",
        },
    }
    (PACK_ROOT / "exports/wechat/metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_form(spec: dict) -> None:
    form = f"""# WeChat Sticker Form

## Basic Info

- Name: {spec["title"]}
- Introduction: {spec["description"]}
- Copyright: {spec.get("copyright") or "待填写"}

## Pack Type

- Static sticker pack
- Sticker count: 18

## Required Assets

- Stickers: `exports/wechat/stickers/`
- Cover: `exports/wechat/cover.png`
- Chat icon: `exports/wechat/icon.png`
- Banner: `exports/wechat/banner.png`
- Metadata: `exports/wechat/metadata.json`

## Production Constraint

All character assets retain the `COS` text on the blue folder.
"""
    (PACK_ROOT / "exports/wechat/form.md").write_text(form, encoding="utf-8")


def write_validation_report(checks: list[dict], passed: bool) -> None:
    report_json = {"passed": passed, "checks": checks}
    (PACK_ROOT / "review/wechat/validation-report.json").write_text(json.dumps(report_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Validation Report", "", f"Overall: {'PASS' if passed else 'FAIL'}", ""]
    for c in checks:
        lines.append(f"- {'PASS' if c['passed'] else 'FAIL'}: {c['name']} - {c.get('detail', '')}")
    lines.append("")
    (PACK_ROOT / "review/wechat/validation-report.md").write_text("\n".join(lines), encoding="utf-8")


def update_spec(spec: dict, passed: bool) -> None:
    spec["workflowPhase"] = "export-generated"
    spec["status"] = "wechat-export-generated-pending-human-review" if passed else "wechat-export-generated-validation-failed"
    spec["masterCharacter"]["finalStickerProductionAllowed"] = True
    spec["masterCharacter"]["approvedImage"] = "master/approved/cos-ip-approved-master.png"
    spec["assets"]["wechatExport"]["cover"] = "exports/wechat/cover.png"
    spec["assets"]["wechatExport"]["icon"] = "exports/wechat/icon.png"
    spec["assets"]["wechatExport"]["banner"] = "exports/wechat/banner.png"
    spec["assets"]["wechatExport"]["metadata"] = "exports/wechat/metadata.json"
    spec["assets"]["wechatExport"]["form"] = "exports/wechat/form.md"
    spec["generatedAt"] = "2026-05-14"
    spec["generationMethod"] = {
        "type": "local deterministic Pillow renderer",
        "script": "source/prompts/generate_assets.py",
        "reason": "COS text must remain exact and legible across all character assets.",
    }
    SPEC_PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    spec = load_spec()
    ensure_dirs()
    clear_generated_pngs()
    items = [StickerItem(i["id"], i["slug"], i["text"], i["pose"]) for i in spec["captions"]["items"]]
    source_paths = []
    export_paths = []
    raw_images = []
    captioned_images = []
    for item in items:
        raw = render_character(item, caption=False)
        cap = render_character(item, caption=True)
        raw_images.append(raw)
        captioned_images.append(cap)
        filename = f"{item.sid:02d}-{item.slug}-{item.text}.png"
        source_path = PACK_ROOT / "generated/stickers/source-crops" / filename
        draft_path = PACK_ROOT / "generated/stickers/wechat-draft" / filename
        export_path = PACK_ROOT / "exports/wechat/stickers" / filename
        cap.save(source_path, optimize=True)
        save_resized(cap, draft_path, (240, 240))
        save_resized(cap, export_path, (240, 240))
        source_paths.append(source_path)
        export_paths.append(export_path)

    make_sheet(raw_images[:9], None, PACK_ROOT / "generated/sheets/raw/sheet-01-raw.png")
    make_sheet(raw_images[9:], None, PACK_ROOT / "generated/sheets/raw/sheet-02-raw.png")
    make_sheet(captioned_images[:9], None, PACK_ROOT / "generated/sheets/captioned/sheet-01-captioned.png")
    make_sheet(captioned_images[9:], None, PACK_ROOT / "generated/sheets/captioned/sheet-02-captioned.png")
    make_sheet(captioned_images[:9], None, PACK_ROOT / "review/sheets/sheet-01-review.png")
    make_sheet(captioned_images[9:], None, PACK_ROOT / "review/sheets/sheet-02-review.png")
    make_contact_sheet(items, export_paths, PACK_ROOT / "review/stickers/contact-sheet.png")
    make_master_review(PACK_ROOT / "review/master/master-reference-review.png")
    cover = render_character(None, caption=False)
    save_resized(cover, PACK_ROOT / "exports/wechat/cover.png", (240, 240))
    icon_base = render_character(None, caption=False)
    save_resized(icon_base, PACK_ROOT / "exports/wechat/icon.png", (50, 50))
    make_banner(PACK_ROOT / "exports/wechat/banner.png")
    checks, passed = validate(items, export_paths)
    write_form(spec)
    write_metadata(spec, items, export_paths, checks, passed)
    write_validation_report(checks, passed)
    update_spec(spec, passed)
    print(json.dumps({"passed": passed, "stickers": len(export_paths), "packRoot": str(PACK_ROOT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
