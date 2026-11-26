#!/usr/bin/env python3
"""Merge multiple recipe PDFs into a single tablet cookbook with linked TOC & bookmarks.

Usage:
  merge_cookbook.py OUT.pdf PDF [PDF ...]
                    [--style illustrated|kodachrome]
                    [--palette party-modern|chatelaine-green|festive-buffet|notebook-sketch]
                    [--title "Holiday Cookbook"]
                    [--kicker "Complete Tablet Cookbook"]
                    [--subtitle "Five Tested Recipes"]
                    [--meta-json items.json]
                    [--preview-dir previews]

If --meta-json is omitted, each PDF's Page 1 title is extracted automatically (via PyMuPDF
text blocks) or derived from its filename. Refuses to overwrite an existing OUT.pdf.
"""
import argparse
import html
import json
import os
import subprocess
import sys
import tempfile

import pymupdf

from build import find_chrome


def infer_entry(pdf_path: str, idx: int, overrides: dict) -> dict:
    doc = pymupdf.open(pdf_path)
    n_pages = len(doc)
    lines = [ln.strip() for ln in doc[0].get_text("text").splitlines() if ln.strip()]
    doc.close()

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    fallback_title = stem.replace("-", " ").title()
    # Heuristic: pick first substantive non-kicker line if overrides didn't specify
    inferred_title = next(
        (ln for ln in lines[:6] if len(ln) > 4 and not ln.isupper() and "·" not in ln),
        fallback_title,
    )
    key = os.path.basename(pdf_path)
    ov = overrides.get(key) or overrides.get(stem) or {}
    return {
        "num": ov.get("num") or f"{idx:02d}",
        "title": ov.get("title") or inferred_title,
        "sub": ov.get("sub") or "",
        "meta": ov.get("meta") or f"{n_pages} {'page' if n_pages == 1 else 'pages'}",
        "path": pdf_path,
        "n_pages": n_pages,
    }


def render_html_to_pdf(chrome: str, html_path: str, pdf_path: str) -> None:
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--virtual-time-budget=8000",
            f"--print-to-pdf={os.path.abspath(pdf_path)}",
            "file://" + os.path.abspath(html_path),
        ],
        stderr=subprocess.DEVNULL,
        check=True,
    )


def build_illustrated_toc(items: list[dict], total_pages: int, title: str, kicker: str, subtitle: str, palette: str) -> str:
    rows = []
    for it in items:
        sub_html = f'<div class="toc-sub">{html.escape(it["sub"])}</div>' if it["sub"] else ""
        meta_html = f'<div class="toc-meta">{html.escape(it["meta"])}</div>' if it["meta"] else ""
        rows.append(
            f'<div class="toc-row">'
            f'<div class="toc-num">{html.escape(it["num"])}</div>'
            f'<div class="toc-body"><div class="toc-title">{html.escape(it["title"])}</div>{sub_html}{meta_html}</div>'
            f'<div class="toc-pg"><b>{html.escape(it["pages_label"])}</b><span>Tap to Open →</span></div>'
            f"</div>"
        )
    words = title.split()
    mid = max(1, len(words) // 2)
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])
    title_html = f"{html.escape(line1)}<br>{html.escape(line2)}" if line2 else html.escape(line1)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Oswald:wght@500;600;700&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap" rel="stylesheet">
<style>
  @page {{ size: letter; margin: 0; }}
  :root, body[data-palette="party-modern"] {{
    --paper: #f5ebd6; --paper-alt: #efe0c1; --ink: #1f1916;
    --accent1: #d43a24; --accent2: #5d7a52; --accent3: #d6a128;
    --on-ink: #f5ebd6; --on-a1: #fff8ec; --rule: rgba(31,25,22,.22);
    --paper-pattern: radial-gradient(rgba(31,25,22,.055) 0.7px, transparent 0.8px);
    --paper-size: 4px 4px;
  }}
  body[data-palette="chatelaine-green"] {{
    --paper: #f6f2e4; --paper-alt: #e6e1cf; --ink: #171717;
    --accent1: #248349; --accent2: #171717; --accent3: #83b892;
    --on-ink: #f6f2e4; --on-a1: #f6f2e4; --rule: rgba(23,23,23,.22);
  }}
  body[data-palette="festive-buffet"] {{
    --paper: #f8f1df; --paper-alt: #efe4c8; --ink: #1c1816;
    --accent1: #d82e7b; --accent2: #b5a81e; --accent3: #d82e7b;
    --on-ink: #f8f1df; --on-a1: #fff9f2; --rule: rgba(28,24,22,.22);
  }}
  body[data-palette="notebook-sketch"] {{
    --paper: #faf4e6; --paper-alt: #eef5f4; --ink: #262320;
    --accent1: #cf3a2e; --accent2: #4f948a; --accent3: #e5ba34;
    --on-ink: #faf4e6; --on-a1: #fffdf8; --rule: rgba(79,148,138,.28);
    --paper-pattern: repeating-linear-gradient(to bottom, transparent 0 21px, rgba(79,148,138,.18) 21px 22px);
    --paper-size: 100% 22px;
  }}
  * {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  html, body {{ margin: 0; padding: 0; background: var(--paper); }}
  body {{ font-family: "Libre Baskerville", Georgia, serif; color: var(--ink); }}
  .page {{
    width: 8.5in; height: 11in; position: relative; overflow: hidden;
    background-color: var(--paper); background-image: var(--paper-pattern); background-size: var(--paper-size);
    padding: 0.42in 0.5in;
  }}
  .page::before {{ content: ""; position: absolute; inset: 0.16in; pointer-events: none; border: 1.5px solid var(--ink); }}
  .top {{
    display: grid; grid-template-columns: 1fr 1.78in; gap: .18in; align-items: stretch;
    border-bottom: 2.5px solid var(--ink); padding-bottom: .13in; margin-bottom: .18in;
  }}
  .kicker {{ font-family: "Courier Prime", monospace; font-weight: 700; text-transform: uppercase; letter-spacing: .16em; font-size: 8.2pt; color: var(--accent1); margin-bottom: .04in; }}
  h1 {{ font-family: "Playfair Display", Georgia, serif; font-weight: 900; font-size: 29pt; line-height: 1.03; margin: 0; color: var(--ink); letter-spacing: -.01em; }}
  .subtitle {{ margin: .06in 0 0; font-family: "Courier Prime", monospace; font-size: 8.6pt; }}
  .stamp-box {{ background: var(--ink); color: var(--on-ink); padding: .1in .12in; display: flex; flex-direction: column; justify-content: center; text-align: center; box-shadow: 4px 4px 0 var(--accent1); }}
  .stamp-box small {{ font-family: Oswald, sans-serif; letter-spacing: .18em; text-transform: uppercase; font-size: 7pt; color: var(--accent3); }}
  .stamp-box b {{ font-family: "Abril Fatface", serif; font-weight: 400; font-size: 16pt; line-height: 1.08; margin: .03in 0; }}
  .stamp-box span {{ font-family: "Courier Prime", monospace; font-size: 7.4pt; opacity: .92; }}
  .sec-label {{ font-family: Oswald, sans-serif; text-transform: uppercase; letter-spacing: .18em; font-size: 9.5pt; color: var(--accent1); margin: 0 0 .1in; display: flex; justify-content: space-between; align-items: baseline; }}
  .sec-label span {{ font-family: "Courier Prime", monospace; font-size: 7.8pt; color: var(--ink); letter-spacing: .06em; }}
  .toc-list {{ display: flex; flex-direction: column; gap: .11in; }}
  .toc-row {{ display: grid; grid-template-columns: .46in 1fr 1.25in; gap: .14in; align-items: center; border: 2px solid var(--ink); background: var(--paper); padding: .09in .13in; }}
  .toc-row:nth-child(odd) {{ box-shadow: 4px 4px 0 var(--accent2); }}
  .toc-row:nth-child(even) {{ box-shadow: 4px 4px 0 var(--accent1); }}
  .toc-num {{ width: .42in; height: .42in; background: var(--accent1); color: var(--on-a1); border: 1.5px solid var(--ink); font-family: "Abril Fatface", serif; font-size: 16pt; display: flex; align-items: center; justify-content: center; }}
  .toc-row:nth-child(even) .toc-num {{ background: var(--ink); color: var(--on-ink); }}
  .toc-title {{ font-family: "Playfair Display", serif; font-weight: 900; font-size: 12.5pt; line-height: 1.12; color: var(--ink); }}
  .toc-sub {{ font-style: italic; font-size: 8.1pt; color: var(--ink); opacity: .88; margin: .02in 0; }}
  .toc-meta {{ font-family: "Courier Prime", monospace; font-size: 7.4pt; color: var(--accent1); font-weight: 700; }}
  .toc-pg {{ text-align: right; border-left: 1.5px dashed var(--rule); padding-left: .12in; }}
  .toc-pg b {{ display: block; font-family: Oswald, sans-serif; font-size: 12pt; letter-spacing: .06em; color: var(--ink); }}
  .toc-pg span {{ display: inline-block; margin-top: .03in; background: var(--accent3); color: var(--ink); border: 1px solid var(--ink); font-family: Oswald, sans-serif; font-size: 7pt; letter-spacing: .12em; text-transform: uppercase; padding: 2px 7px; }}
  .foot {{ position: absolute; left: .5in; right: .5in; bottom: .34in; border-top: 1.5px solid var(--ink); padding-top: .06in; display: flex; justify-content: space-between; font-family: "Courier Prime", monospace; text-transform: uppercase; letter-spacing: .15em; font-size: 7.2pt; }}
</style>
</head>
<body data-palette="{html.escape(palette)}">
<section class="page">
  <div class="top">
    <div>
      <div class="kicker">{html.escape(kicker)}</div>
      <h1>{title_html}</h1>
      <p class="subtitle">{html.escape(subtitle)} · {len(items)} Recipes · {total_pages} Pages</p>
    </div>
    <div class="stamp-box">
      <small>Tap Any Card</small>
      <b>{total_pages} Pages</b>
      <span>Interactive PDF Index</span>
    </div>
  </div>
  <div class="sec-label">
    <div>Table of Contents</div>
    <span>Tap a card to jump · Use top-right “^ CONTENTS” on any page to return</span>
  </div>
  <div class="toc-list">{''.join(rows)}</div>
  <div class="foot">
    <span>{html.escape(title)}</span>
    <span>Mid-Century Illustrated Edition</span>
  </div>
</section>
</body>
</html>"""


def build_kodachrome_toc(items: list[dict], total_pages: int, title: str, kicker: str, subtitle: str) -> str:
    rows = []
    for it in items:
        sub_html = f'<div class="toc-sub">{html.escape(it["sub"])}</div>' if it["sub"] else ""
        meta_html = f'<div class="toc-meta">{html.escape(it["meta"])}</div>' if it["meta"] else ""
        rows.append(
            f'<div class="toc-row">'
            f'<div class="toc-num">{html.escape(it["num"])}</div>'
            f'<div class="toc-body"><div class="toc-title">{html.escape(it["title"])}</div>{sub_html}{meta_html}</div>'
            f'<div class="toc-pg"><b>{html.escape(it["pages_label"])}</b><span>Tap to Open →</span></div>'
            f"</div>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Oswald:wght@500;600&family=Yellowtail&display=swap" rel="stylesheet">
<style>
  @page {{ size: letter; margin: 0; }}
  :root {{ --paper: #f3e7cc; --ink: #2b2118; --red: #b5321f; --mustard: #d49a1c; --avocado: #6f7d2e; --brown: #6b3a1e; }}
  * {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  html, body {{ margin: 0; padding: 0; background: var(--paper); }}
  body {{ font-family: "Libre Caslon Text", Georgia, serif; color: var(--ink); }}
  .page {{
    width: 8.5in; height: 11in; position: relative; overflow: hidden;
    background: radial-gradient(ellipse at 50% 40%, rgba(255,250,235,.55), rgba(0,0,0,0) 70%),
      radial-gradient(ellipse at 100% 100%, rgba(150,100,40,.18), rgba(0,0,0,0) 45%), var(--paper);
    padding: 0.44in 0.52in;
  }}
  .page::after {{ content: ""; position: absolute; inset: 0; pointer-events: none; background-image: radial-gradient(rgba(80,50,20,.07) 0.6px, transparent 0.7px); background-size: 3px 3px; mix-blend-mode: multiply; }}
  .kicker {{ display: flex; align-items: center; gap: .15in; font-family: Oswald, sans-serif; letter-spacing: .22em; text-transform: uppercase; font-size: 9pt; color: var(--red); }}
  .kicker::before, .kicker::after {{ content: ""; flex: 1; height: 0; border-top: 2px solid var(--red); border-bottom: 1px solid var(--red); padding-top: 2px; }}
  h1 {{ font-family: "Abril Fatface", Georgia, serif; font-weight: 400; font-size: 35pt; line-height: 1; margin: .08in 0 0; text-align: center; color: var(--red); }}
  h1 .script {{ display: block; font-family: Yellowtail, cursive; color: var(--brown); font-size: 26pt; margin-bottom: .01in; }}
  .meta {{ text-align: center; margin: .07in 0 .2in; font-family: Oswald, sans-serif; text-transform: uppercase; letter-spacing: .16em; font-size: 8.8pt; color: var(--brown); }}
  .meta span + span::before {{ content: "✦"; margin: 0 .12in; color: var(--mustard); }}
  .toc-box {{ border: 2px solid var(--avocado); background: rgba(255,250,235,.68); padding: .24in .2in .18in; position: relative; }}
  .toc-badge {{ font-family: Oswald, sans-serif; text-transform: uppercase; letter-spacing: .2em; font-size: 10pt; color: #fff; background: var(--avocado); display: inline-block; padding: .03in .14in; position: absolute; top: -.14in; left: .18in; }}
  .toc-hint {{ font-style: italic; font-size: 8.2pt; color: var(--brown); margin: 0 0 .12in; }}
  .toc-list {{ display: flex; flex-direction: column; gap: .11in; }}
  .toc-row {{ display: grid; grid-template-columns: .46in 1fr 1.25in; gap: .14in; align-items: center; border: 1px solid rgba(107,58,30,.32); background: #fffaf0; padding: .1in .14in; box-shadow: 2px 3px 0 rgba(60,35,15,.14); }}
  .toc-num {{ width: .42in; height: .42in; background: var(--red); color: #fbeed2; font-family: "Abril Fatface", serif; font-size: 16pt; display: flex; align-items: center; justify-content: center; border: 2px solid #fbeed2; outline: 1.5px solid var(--red); }}
  .toc-title {{ font-family: "Abril Fatface", Georgia, serif; font-size: 13pt; line-height: 1.12; color: var(--red); }}
  .toc-sub {{ font-style: italic; font-size: 8.2pt; color: var(--brown); margin: .02in 0; }}
  .toc-meta {{ font-family: Oswald, sans-serif; text-transform: uppercase; letter-spacing: .1em; font-size: 7.3pt; color: var(--avocado); }}
  .toc-pg {{ text-align: right; border-left: 1px dashed rgba(107,58,30,.28); padding-left: .12in; }}
  .toc-pg b {{ display: block; font-family: "Abril Fatface", serif; font-size: 12.5pt; color: var(--ink); }}
  .toc-pg span {{ display: inline-block; margin-top: .03in; background: var(--mustard); color: #3a2208; font-family: Oswald, sans-serif; font-size: 7.2pt; letter-spacing: .1em; text-transform: uppercase; padding: 2px 8px; border: 1px solid rgba(107,58,30,.25); }}
  .foot {{ position: absolute; left: .52in; right: .52in; bottom: .38in; border-top: 2px solid var(--red); padding-top: .1in; display: grid; grid-template-columns: auto 1fr; gap: .18in; align-items: center; }}
  .seal {{ width: .92in; height: .92in; border-radius: 50%; background: var(--red); color: #fbeed2; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; font-family: Oswald, sans-serif; text-transform: uppercase; letter-spacing: .08em; font-size: 6.8pt; line-height: 1.15; border: 3px double #fbeed2; outline: 2px solid var(--red); transform: rotate(-7deg); }}
  .seal b {{ font-family: "Abril Fatface", serif; font-weight: 400; font-size: 12.5pt; letter-spacing: 0; text-transform: none; }}
</style>
</head>
<body>
<section class="page">
  <div class="kicker">{html.escape(kicker)}</div>
  <h1><span class="script">{html.escape(title)}</span>Recipe Collection</h1>
  <div class="meta"><span>{html.escape(subtitle)}</span><span>1960s Kodachrome Edition</span><span>{total_pages} Pages</span></div>
  <div class="toc-box">
    <div class="toc-badge">Table of Contents</div>
    <p class="toc-hint">Tap any recipe card below to jump straight to its ingredients &amp; step-by-step photos. Use the “^ CONTENTS” tab at the top-right of any page to return here.</p>
    <div class="toc-list">{''.join(rows)}</div>
  </div>
  <div class="foot">
    <div class="seal">Kitchen<br><b>Tested</b><br>Collection</div>
    <div style="font-size:8.6pt;line-height:1.4;">Tap any recipe card above or open your tablet's PDF outline sidebar to jump directly between dishes.</div>
  </div>
</section>
</body>
</html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge recipe PDFs into a tablet cookbook with linked TOC.")
    ap.add_argument("out_pdf")
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--style", default="illustrated", choices=["illustrated", "kodachrome"])
    ap.add_argument("--palette", default="party-modern")
    ap.add_argument("--title", default="Vintage Recipe Cookbook")
    ap.add_argument("--kicker", default="Complete Tablet Cookbook")
    ap.add_argument("--subtitle", default="Tested Recipes")
    ap.add_argument("--meta-json", help="Optional JSON mapping filename/stem -> {num,title,sub,meta}")
    ap.add_argument("--preview-dir")
    a = ap.parse_args()

    if os.path.exists(a.out_pdf):
        sys.exit(f"refusing to overwrite {a.out_pdf}")

    overrides = json.load(open(a.meta_json, encoding="utf-8")) if a.meta_json else {}
    items = []
    cur = 2
    for idx, p in enumerate(a.pdfs, 1):
        it = infer_entry(p, idx, overrides)
        n = it["n_pages"]
        it["start_1b"] = cur
        it["pages_label"] = f"pp. {cur}–{cur + n - 1}" if n > 1 else f"p. {cur}"
        items.append(it)
        cur += n
    total_pages = cur - 1

    with tempfile.TemporaryDirectory() as tmp:
        toc_html = os.path.join(tmp, "toc.html")
        toc_pdf = os.path.join(tmp, "toc.pdf")
        if a.style == "illustrated":
            content = build_illustrated_toc(items, total_pages, a.title, a.kicker, a.subtitle, a.palette)
        else:
            content = build_kodachrome_toc(items, total_pages, a.title, a.kicker, a.subtitle)
        open(toc_html, "w", encoding="utf-8").write(content)
        render_html_to_pdf(find_chrome(), toc_html, toc_pdf)

        out = pymupdf.open()
        toc_doc = pymupdf.open(toc_pdf)
        out.insert_pdf(toc_doc)
        toc_doc.close()

        bookmarks = [[1, "Table of Contents", 1]]
        for it in items:
            src = pymupdf.open(it["path"])
            out.insert_pdf(src)
            src.close()
            bookmarks.append([1, f"{it['num']}. {it['title']}", it["start_1b"]])
        out.set_toc(bookmarks)

        toc_page = out[0]
        for it in items:
            hits = toc_page.search_for(it["title"])
            if hits:
                r = hits[0]
                toc_page.insert_link({
                    "kind": pymupdf.LINK_GOTO,
                    "from": pymupdf.Rect(34, r.y0 - 8, 578, r.y1 + 32),
                    "page": it["start_1b"] - 1,
                    "to": pymupdf.Point(0, 0),
                })

        for pno in range(1, len(out)):
            pg = out[pno]
            if a.style == "illustrated":
                pill = pymupdf.Rect(518, 13, 592, 26)
                bg, fg, border = (0.94, 0.88, 0.76), (0.12, 0.10, 0.09), (0.12, 0.10, 0.09)
            else:
                pill = pymupdf.Rect(520, 10, 594, 23)
                bg, fg, border = (0.71, 0.20, 0.12), (0.98, 0.93, 0.82), (0.42, 0.23, 0.12)
            pg.draw_rect(pill, color=border, fill=bg, width=0.9)
            pg.insert_text(pymupdf.Point(pill.x0 + 11.5, pill.y0 + 9.2), "^ CONTENTS", fontsize=6.6, fontname="helv", color=fg)
            pg.insert_link({"kind": pymupdf.LINK_GOTO, "from": pill, "page": 0, "to": pymupdf.Point(0, 0)})

        os.makedirs(os.path.dirname(os.path.abspath(a.out_pdf)), exist_ok=True)
        out.save(a.out_pdf, garbage=3, deflate=True)
        if a.preview_dir:
            os.makedirs(a.preview_dir, exist_ok=True)
            for idx in (0, 1):
                if idx < len(out):
                    out[idx].get_pixmap(dpi=90).save(os.path.join(a.preview_dir, f"page{idx + 1}.png"))
        print(f"wrote {a.out_pdf} ({len(out)} pages, {len(out[0].get_links())} TOC links)")
        out.close()


if __name__ == "__main__":
    main()
