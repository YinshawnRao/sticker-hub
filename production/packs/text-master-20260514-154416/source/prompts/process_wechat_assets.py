from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PACK = Path(__file__).resolve().parents[2]
SPEC_PATH = PACK / "spec.json"

FONT_CANDIDATES = [
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size=size, index=0)
    return ImageFont.load_default()


def remove_green_key(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    arr = np.array(rgba).astype(np.int16)
    rgb = arr[:, :, :3]

    # Use the border median as key. The generated background is green but may
    # shift slightly after image generation, so a fixed #00ff00 threshold is too
    # brittle.
    border = np.concatenate(
        [rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]],
        axis=0,
    )
    key = np.median(border, axis=0)
    dist = np.sqrt(np.sum((rgb - key) ** 2, axis=2))
    greenish = (rgb[:, :, 1] > 110) & (rgb[:, :, 1] > rgb[:, :, 0] * 1.45) & (
        rgb[:, :, 1] > rgb[:, :, 2] * 1.45
    )

    alpha = arr[:, :, 3].astype(np.float32)
    transparent = greenish & (dist < 90)
    feather = greenish & (dist >= 90) & (dist < 155)
    alpha[transparent] = 0
    alpha[feather] = np.minimum(alpha[feather], ((dist[feather] - 90) / 65) * 255)

    # Despill green fringe on semi-transparent edge pixels.
    edge = alpha < 255
    arr[:, :, 1][edge] = np.minimum(arr[:, :, 1][edge], ((arr[:, :, 0][edge] + arr[:, :, 2][edge]) / 2 + 20).astype(np.int16))
    arr[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def alpha_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = img.getchannel("A")
    return alpha.getbbox()


def clean_cell_residue(cell: Image.Image) -> Image.Image:
    """Drop small alpha components that bleed in from neighboring grid cells."""
    rgba = cell.convert("RGBA")
    arr = np.array(rgba)
    mask = arr[:, :, 3] > 20
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components = []

    for sy in range(h):
        for sx in range(w):
            if not mask[sy, sx] or visited[sy, sx]:
                continue
            stack = [(sx, sy)]
            visited[sy, sx] = True
            xs = []
            ys = []
            while stack:
                x, y = stack.pop()
                xs.append(x)
                ys.append(y)
                for ny in range(max(0, y - 1), min(h, y + 2)):
                    for nx in range(max(0, x - 1), min(w, x + 2)):
                        if not visited[ny, nx] and mask[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((nx, ny))
            area = len(xs)
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)
            touches_edge = x1 <= 3 or y1 <= 3 or x2 >= w - 4 or y2 >= h - 4
            cx = sum(xs) / area
            cy = sum(ys) / area
            components.append(
                {
                    "area": area,
                    "bbox": (x1, y1, x2 + 1, y2 + 1),
                    "touches_edge": touches_edge,
                    "center_distance": math.hypot(cx - w / 2, cy - h / 2),
                }
            )

    if not components:
        return rgba

    largest = max(c["area"] for c in components)
    keep_mask = np.zeros_like(mask, dtype=bool)
    for c in components:
        x1, y1, x2, y2 = c["bbox"]
        region = mask[y1:y2, x1:x2]
        # Keep the main character/props and non-edge decorations. Drop small
        # components touching the cell boundary, which are usually fragments
        # from the neighboring pose in the generated sheet.
        keep = (
            c["area"] >= max(80, largest * 0.018)
            and (not c["touches_edge"] or c["area"] >= largest * 0.22 or c["center_distance"] < w * 0.28)
        )
        if keep:
            keep_mask[y1:y2, x1:x2] |= region

    arr[:, :, 3] = np.where(keep_mask, arr[:, :, 3], 0).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def expand_box(box: tuple[int, int, int, int], pad: int, bounds: tuple[int, int]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    w, h = bounds
    return max(0, x1 - pad), max(0, y1 - pad), min(w, x2 + pad), min(h, y2 + pad)


def fit_into(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    w, h = img.size
    scale = min(box_w / w, box_h / h, 1.0)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def draw_caption(base: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(base)
    max_width = 222
    f_size = 34
    stroke = 5
    while f_size >= 22:
        fnt = font(f_size)
        box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
        if box[2] - box[0] <= max_width:
            break
        f_size -= 2
    fnt = font(f_size)
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    tw, th = box[2] - box[0], box[3] - box[1]
    x = (base.width - tw) // 2 - box[0]
    y = 188 - box[1] + max(0, 38 - th) // 2

    # Warm shadow, dark outline, white fill.
    draw.text((x + 3, y + 3), text, font=fnt, fill=(255, 190, 78, 230), stroke_width=stroke + 1, stroke_fill=(120, 74, 26, 210))
    draw.text((x, y), text, font=fnt, fill=(255, 255, 255, 255), stroke_width=stroke, stroke_fill=(53, 39, 31, 255))


def make_checker(size: tuple[int, int], cell: int = 16) -> Image.Image:
    img = Image.new("RGB", size, "#f6f7fb")
    draw = ImageDraw.Draw(img)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill="#e7eaf1")
    return img


def composite_on_checker(sticker: Image.Image) -> Image.Image:
    bg = make_checker(sticker.size)
    bg.paste(sticker, (0, 0), sticker)
    return bg


def build_banner(master: Image.Image, stickers: list[Image.Image]) -> Image.Image:
    banner = Image.new("RGB", (750, 400), "#7bd7ff")
    draw = ImageDraw.Draw(banner)
    for i in range(0, 750, 38):
        color = "#9ae6ff" if i % 76 == 0 else "#5bc7ed"
        draw.line([(i, 0), (i - 220, 400)], fill=color, width=4)
    draw.ellipse([520, -70, 830, 240], fill="#ffd36d")
    draw.ellipse([-80, 230, 170, 500], fill="#8ee68a")
    draw.rounded_rectangle([430, 70, 700, 315], radius=24, fill="#ffffff", outline="#2c5b7a", width=5)
    draw.line([455, 255, 505, 190, 555, 225, 625, 130, 675, 155], fill="#2f80ed", width=8)
    draw.ellipse([492, 180, 518, 206], fill="#ffb84d")
    draw.ellipse([542, 212, 568, 238], fill="#ff5c7a")
    draw.ellipse([612, 118, 638, 144], fill="#27ae60")

    # Paste recognizable characters. No text is added to the banner.
    mbox = alpha_bbox(master)
    if mbox:
        crop = master.crop(expand_box(mbox, 20, master.size))
        crop = fit_into(crop, 255, 345)
        banner.paste(crop, (58, 38), crop)
    for sticker, pos, max_size in [
        (stickers[4], (285, 75), (165, 170)),
        (stickers[16], (560, 210), (160, 160)),
    ]:
        bbox = alpha_bbox(sticker)
        if bbox:
            crop = sticker.crop(expand_box(bbox, 4, sticker.size))
            crop = fit_into(crop, *max_size)
            banner.paste(crop, pos, crop)
    return banner


def validate_png(path: Path) -> dict:
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    alpha = img.getchannel("A")
    corners = [alpha.getpixel((0, 0)), alpha.getpixel((w - 1, 0)), alpha.getpixel((0, h - 1)), alpha.getpixel((w - 1, h - 1))]
    return {
        "path": str(path.relative_to(PACK)),
        "width": w,
        "height": h,
        "mode": img.mode,
        "bytes": path.stat().st_size,
        "hasAlpha": True,
        "transparentCorners": all(v == 0 for v in corners),
        "under500KB": path.stat().st_size <= 512000,
    }


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    captions = spec["captions"]["items"]

    raw_dir = PACK / "generated/sheets/raw"
    captioned_dir = PACK / "generated/sheets/captioned"
    crops_dir = PACK / "generated/stickers/source-crops"
    draft_dir = PACK / "generated/stickers/wechat-draft"
    review_stickers_dir = PACK / "review/stickers"
    review_wechat_dir = PACK / "review/wechat"
    export_dir = PACK / "exports/wechat"
    export_stickers_dir = export_dir / "stickers"
    for d in [captioned_dir, crops_dir, draft_dir, review_stickers_dir, review_wechat_dir, export_stickers_dir]:
        d.mkdir(parents=True, exist_ok=True)

    sheet_paths = [raw_dir / "sheet-01-chroma.png", raw_dir / "sheet-02-chroma.png"]
    transparent_sheets = []
    all_crops: list[Image.Image] = []
    all_drafts: list[Image.Image] = []

    for sheet_index, sheet_path in enumerate(sheet_paths):
        sheet_alpha = remove_green_key(Image.open(sheet_path))
        alpha_path = raw_dir / f"sheet-{sheet_index + 1:02d}.png"
        sheet_alpha.save(alpha_path)
        transparent_sheets.append(sheet_alpha)

        w, h = sheet_alpha.size
        cell_w, cell_h = w // 3, h // 3
        captioned_sheet = Image.new("RGBA", (720, 720), (0, 0, 0, 0))

        for local_idx in range(9):
            idx = sheet_index * 9 + local_idx
            caption = captions[idx]
            row, col = divmod(local_idx, 3)
            cell = sheet_alpha.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
            cell = clean_cell_residue(cell)
            bbox = alpha_bbox(cell)
            if bbox is None:
                raise RuntimeError(f"Empty alpha content in sheet {sheet_index + 1}, cell {local_idx + 1}")
            crop = cell.crop(expand_box(bbox, 18, cell.size))
            source_name = f"{idx + 1:02d}-{caption['slug']}.png"
            crop.save(crops_dir / source_name)
            all_crops.append(crop)

            sticker = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
            fitted = fit_into(crop, 220, 168)
            sticker.paste(fitted, ((240 - fitted.width) // 2, 8 + (168 - fitted.height) // 2), fitted)
            draw_caption(sticker, caption["text"])
            sticker.save(draft_dir / source_name)
            sticker.save(export_stickers_dir / source_name)
            all_drafts.append(sticker)
            captioned_sheet.paste(sticker, (col * 240, row * 240), sticker)

        captioned_sheet.save(captioned_dir / f"sheet-{sheet_index + 1:02d}.png")

    master = Image.open(PACK / "master/approved/master-reference.png").convert("RGBA")
    bbox = alpha_bbox(master)
    if bbox is None:
        raise RuntimeError("Master reference has no alpha content")
    mx1, my1, mx2, my2 = bbox
    mw, mh = mx2 - mx1, my2 - my1

    cover_crop = master.crop((max(0, mx1 - int(mw * 0.06)), my1, min(master.width, mx2 + int(mw * 0.04)), min(master.height, my1 + int(mh * 0.68))))
    cover_crop = fit_into(cover_crop, 222, 222)
    cover = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    cover.paste(cover_crop, ((240 - cover_crop.width) // 2, (240 - cover_crop.height) // 2), cover_crop)
    cover.save(export_dir / "cover.png")

    icon_crop = master.crop((max(0, mx1 + int(mw * 0.18)), my1, min(master.width, mx1 + int(mw * 0.82)), min(master.height, my1 + int(mh * 0.38))))
    icon_crop = fit_into(icon_crop, 48, 48)
    icon = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    icon.paste(icon_crop, ((50 - icon_crop.width) // 2, (50 - icon_crop.height) // 2), icon_crop)
    icon.save(export_dir / "icon.png")

    banner = build_banner(master, all_crops)
    banner.save(export_dir / "banner.png")

    contact = Image.new("RGB", (6 * 240, 3 * 278), "#f5f7fb")
    label_font = font(18)
    draw = ImageDraw.Draw(contact)
    for idx, sticker in enumerate(all_drafts):
        x = (idx % 6) * 240
        y = (idx // 6) * 278
        tile = composite_on_checker(sticker)
        contact.paste(tile, (x, y))
        draw.text((x + 10, y + 245), f"{idx + 1:02d} {captions[idx]['text']}", font=label_font, fill="#1f2937")
    contact.save(review_stickers_dir / "stickers-contact-sheet.png")

    overview = Image.new("RGB", (1000, 800), "#f5f7fb")
    draw = ImageDraw.Draw(overview)
    title_font = font(28)
    small_font = font(18)
    draw.text((32, 24), "卷卷码农 WeChat Export Review", font=title_font, fill="#172033")
    overview.paste(composite_on_checker(cover), (40, 80))
    draw.text((40, 328), "cover.png 240x240", font=small_font, fill="#172033")
    icon_preview = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    icon_big = icon.resize((180, 180), Image.Resampling.NEAREST)
    icon_preview.paste(icon_big, (30, 30), icon_big)
    overview.paste(composite_on_checker(icon_preview), (320, 80))
    draw.text((320, 328), "icon.png 50x50", font=small_font, fill="#172033")
    overview.paste(banner.resize((375, 200), Image.Resampling.LANCZOS), (590, 100))
    draw.text((590, 328), "banner.png 750x400", font=small_font, fill="#172033")
    sheet_preview = Image.open(captioned_dir / "sheet-01.png").convert("RGBA").resize((360, 360), Image.Resampling.LANCZOS)
    overview.paste(composite_on_checker(sheet_preview), (40, 380))
    sheet_preview2 = Image.open(captioned_dir / "sheet-02.png").convert("RGBA").resize((360, 360), Image.Resampling.LANCZOS)
    overview.paste(composite_on_checker(sheet_preview2), (430, 380))
    overview.save(review_wechat_dir / "export-assets-overview.png")

    metadata = {
        "packId": spec["packId"],
        "title": spec["title"],
        "description": spec["description"],
        "copyright": spec["copyright"],
        "platform": spec["platform"],
        "packType": spec["wechatTarget"]["packType"],
        "stickerCount": len(captions),
        "assets": {
            "stickers": [f"stickers/{idx + 1:02d}-{c['slug']}.png" for idx, c in enumerate(captions)],
            "cover": "cover.png",
            "icon": "icon.png",
            "banner": "banner.png",
        },
        "captions": captions,
        "source": {
            "masterReference": "master/approved/master-reference.png",
            "rawSheets": ["generated/sheets/raw/sheet-01-chroma.png", "generated/sheets/raw/sheet-02-chroma.png"],
            "processingScript": "source/prompts/process_wechat_assets.py",
        },
        "validationTargets": spec["wechatTarget"],
    }
    (export_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    form = "\n".join(
        [
            "# WeChat Sticker Form",
            "",
            f"- 名称：{spec['title']}",
            f"- 简介：{spec['description']}",
            f"- 版权：{spec['copyright']}",
            "- 类型：静态表情",
            "- 数量：18",
            "",
            "## 表情名称",
            "",
            *[f"{idx + 1:02d}. {c['text']}" for idx, c in enumerate(captions)],
            "",
        ]
    )
    (export_dir / "form.md").write_text(form, encoding="utf-8")

    validation = {
        "packId": spec["packId"],
        "status": "pass",
        "notes": [
            "Generated from local AGENTS.md upload contract. Re-check latest official platform requirements before real submission.",
            "Manual review still required for visual quality, banner no-text compliance, and platform duplicate-name risk.",
        ],
        "stickers": [validate_png(export_stickers_dir / f"{idx + 1:02d}-{c['slug']}.png") for idx, c in enumerate(captions)],
        "cover": validate_png(export_dir / "cover.png"),
        "icon": {
            **validate_png(export_dir / "icon.png"),
            "under100KB": (export_dir / "icon.png").stat().st_size <= 102400,
        },
        "banner": {
            "path": "exports/wechat/banner.png",
            "width": Image.open(export_dir / "banner.png").size[0],
            "height": Image.open(export_dir / "banner.png").size[1],
            "mode": Image.open(export_dir / "banner.png").mode,
            "bytes": (export_dir / "banner.png").stat().st_size,
            "under500KB": (export_dir / "banner.png").stat().st_size <= 512000,
            "opaque": Image.open(export_dir / "banner.png").mode == "RGB",
            "manualNoTextReviewRequired": True,
        },
        "form": {
            "name": spec["title"],
            "nameLength": len(spec["title"]),
            "nameUnder8ChineseChars": len(spec["title"]) <= 8,
            "introductionLength": len(spec["description"]),
            "introductionUnder80ChineseChars": len(spec["description"]) <= 80,
            "copyrightLength": len(spec["copyright"]),
            "copyrightUnder10ChineseChars": len(spec["copyright"]) <= 10,
        },
    }
    failures = []
    for sticker in validation["stickers"]:
        if not (sticker["width"] == 240 and sticker["height"] == 240 and sticker["transparentCorners"] and sticker["under500KB"]):
            failures.append(sticker["path"])
    if not (validation["cover"]["width"] == 240 and validation["cover"]["height"] == 240 and validation["cover"]["transparentCorners"] and validation["cover"]["under500KB"]):
        failures.append("cover.png")
    if not (validation["icon"]["width"] == 50 and validation["icon"]["height"] == 50 and validation["icon"]["transparentCorners"] and validation["icon"]["under100KB"]):
        failures.append("icon.png")
    if not (validation["banner"]["width"] == 750 and validation["banner"]["height"] == 400 and validation["banner"]["opaque"] and validation["banner"]["under500KB"]):
        failures.append("banner.png")
    if failures:
        validation["status"] = "fail"
        validation["failures"] = failures
    (review_wechat_dir / "validation-report.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
