#!/usr/bin/env python3
"""Crop photo borders, embed photos into HTML, render letter PDF(s), and rasterize previews.

Usage:
  build.py template.html IMG_DIR OUT_BASE
           [--crop name=0.05 ...]
           [--preview-dir DIR]
           [--alt-hash small] [--alt-suffix -4-potatoes]

Template uses {{name}} placeholders for each IMG_DIR/<name>.png.
Writes OUT_BASE.html and OUT_BASE.pdf (and OUT_BASE<alt_suffix>.pdf when --alt-hash is given).
Refuses to overwrite any existing output file.
Default crop is 0.04 per side to remove faded edges sometimes added by image generators.
"""
import argparse
import base64
import glob
import io
import os
import re
import shutil
import subprocess
import sys

from PIL import Image
import pymupdf


def find_chrome() -> str:
    candidates = [
        os.environ.get("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("chrome"),
        shutil.which("msedge"),
    ]
    if os.name == "nt":
        for root in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"), os.environ.get("LocalAppData")):
            if root:
                candidates.append(os.path.join(root, "Google", "Chrome", "Application", "chrome.exe"))
                candidates.append(os.path.join(root, "Microsoft", "Edge", "Application", "msedge.exe"))
    for path in candidates:
        if path and os.path.exists(path):
            return path
    pw_hits = sorted(
        glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-*/chrome"))
        + glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))
        + glob.glob(os.path.expanduser("~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe"))
    )
    if pw_hits:
        return pw_hits[-1]
    sys.exit(
        "Chrome/Chromium/Edge binary not found. Install Google Chrome or Microsoft Edge, "
        "or set CHROME_BIN=/path/to/browser."
    )


def render_pdf(chrome: str, html_url: str, pdf_path: str, preview_dir: str | None = None) -> int:
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--virtual-time-budget=8000",
            f"--print-to-pdf={os.path.abspath(pdf_path)}",
            html_url,
        ],
        stderr=subprocess.DEVNULL,
        check=True,
    )
    doc = pymupdf.open(pdf_path)
    pages = len(doc)
    print(f"{pdf_path}: {pages} pages")
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        for i, page in enumerate(doc):
            fn = os.path.join(preview_dir, f"page{i + 1}.png")
            page.get_pixmap(dpi=90).save(fn)
            print("preview", fn)
    return pages


def main() -> None:
    ap = argparse.ArgumentParser(description="Build vintage picture recipe HTML and PDF(s).")
    ap.add_argument("template")
    ap.add_argument("img_dir")
    ap.add_argument("out_base")
    ap.add_argument("--crop", nargs="*", default=[], help="Per-image border crop ratio, e.g. s4=0.07")
    ap.add_argument("--preview-dir", help="Directory to write 90-DPI PNG page previews")
    ap.add_argument("--alt-hash", help="Optional URL hash for alternate toggle PDF (e.g. small or big)")
    ap.add_argument("--alt-suffix", help="Filename suffix for alternate PDF (defaults to -<alt_hash>)")
    a = ap.parse_args()

    html_out = a.out_base + ".html"
    pdf_out = a.out_base + ".pdf"
    alt_pdf_out = None
    if a.alt_hash:
        suffix = a.alt_suffix if a.alt_suffix is not None else f"-{a.alt_hash}"
        alt_pdf_out = f"{a.out_base}{suffix}.pdf"

    targets = [p for p in (html_out, pdf_out, alt_pdf_out) if p]
    for p in targets:
        if os.path.exists(p):
            sys.exit(f"refusing to overwrite {p}")

    out_parent = os.path.dirname(os.path.abspath(html_out))
    if out_parent:
        os.makedirs(out_parent, exist_ok=True)

    chrome = find_chrome()
    crops = {k: float(v) for k, v in (c.split("=") for c in a.crop)}
    html = open(a.template, encoding="utf-8").read()

    for name in sorted(set(re.findall(r"\{\{(\w+)\}\}", html))):
        img_path = next(
            (
                os.path.join(a.img_dir, f"{name}{ext}")
                for ext in (".png", ".jpg", ".jpeg", ".webp")
                if os.path.exists(os.path.join(a.img_dir, f"{name}{ext}"))
            ),
            None,
        )
        if not img_path:
            sys.exit(f"missing image for {{{{{name}}}}} in {a.img_dir} (.png/.jpg/.jpeg/.webp)")
        im = Image.open(img_path).convert("RGB")
        w, h = im.size
        c = crops.get(name, 0.04)
        im = im.crop((int(w * c), int(h * c), int(w * (1 - c)), int(h * (1 - c))))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=88)
        data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        html = html.replace("{{" + name + "}}", data_uri)

    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html)

    base_url = "file://" + os.path.abspath(html_out)
    render_pdf(chrome, base_url, pdf_out, a.preview_dir)

    if alt_pdf_out:
        alt_preview_dir = f"{a.preview_dir}-alt" if a.preview_dir else None
        render_pdf(chrome, f"{base_url}#{a.alt_hash}", alt_pdf_out, alt_preview_dir)


if __name__ == "__main__":
    main()
