#!/usr/bin/env python3
"""Create a labeled contact sheet from IMG_DIR/*.png for visual QA before building.

Usage:
  make_contact_sheet.py IMG_DIR OUT_PNG [--cols 3] [--tile-w 420] [--tile-h 315] [name ...]
"""
import argparse
import math
import os
import re
import sys

from PIL import Image, ImageDraw


def sort_key(filename: str) -> tuple[int, int, str]:
    stem = os.path.splitext(filename)[0]
    if stem == "hero":
        return (0, 0, stem)
    m = re.fullmatch(r"s(\d+)", stem)
    if m:
        return (1, int(m.group(1)), stem)
    return (2, 0, stem)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a labeled contact sheet of recipe photos.")
    ap.add_argument("img_dir")
    ap.add_argument("out_png")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--tile-w", type=int, default=420)
    ap.add_argument("--tile-h", type=int, default=315)
    ap.add_argument("names", nargs="*", help="Optional subset of image stems (e.g. hero s1 s2)")
    a = ap.parse_args()

    if a.names:
        files = [f"{n}.png" for n in a.names]
    else:
        files = sorted(
            (f for f in os.listdir(a.img_dir) if f.endswith(".png") and "_old" not in f),
            key=sort_key,
        )

    if not files:
        sys.exit(f"no .png files found in {a.img_dir}")

    rows = math.ceil(len(files) / a.cols)
    sheet = Image.new("RGB", (a.cols * a.tile_w, rows * a.tile_h), (240, 236, 226))
    draw = ImageDraw.Draw(sheet)

    for idx, fname in enumerate(files):
        path = os.path.join(a.img_dir, fname)
        im = Image.open(path).convert("RGB")
        im.thumbnail((a.tile_w, a.tile_h))
        col = idx % a.cols
        row = idx // a.cols
        x = col * a.tile_w + (a.tile_w - im.width) // 2
        y = row * a.tile_h + (a.tile_h - im.height) // 2
        sheet.paste(im, (x, y))

        label = os.path.splitext(fname)[0]
        bx, by = col * a.tile_w + 6, row * a.tile_h + 6
        draw.rectangle([bx, by, bx + max(56, len(label) * 9 + 16), by + 22], fill=(20, 20, 20))
        draw.text((bx + 8, by + 5), label, fill=(255, 250, 235))

    os.makedirs(os.path.dirname(os.path.abspath(a.out_png)), exist_ok=True)
    sheet.save(a.out_png)
    print(f"wrote {a.out_png} ({len(files)} images)")


if __name__ == "__main__":
    main()
