#!/usr/bin/env python3
"""Scaffold a clean working directory for a new vintage recipe card.

Copies the chosen style's template and prompts.json into work/<slug>/<style>/
without modifying examples/, and prints the exact next build commands.

Usage:
  new_recipe.py SLUG --style kodachrome-1960s|midcentury-illustrated
                [--breezy] [--palette party-modern|chatelaine-green|festive-buffet|notebook-sketch]
                [--single-size] [--work-root work]
"""
import argparse
import os
import re
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold a new vintage recipe working directory.")
    ap.add_argument("slug", help="Short URL-safe recipe slug, e.g. upcycled-baked-beans")
    ap.add_argument(
        "--style",
        required=True,
        choices=["kodachrome-1960s", "midcentury-illustrated"],
        help="Recipe card style",
    )
    ap.add_argument(
        "--breezy",
        action="store_true",
        help="For midcentury-illustrated: start from prompts-breezy.json (random 2B/2C sketchy style)",
    )
    ap.add_argument(
        "--palette",
        default="party-modern",
        choices=["party-modern", "chatelaine-green", "festive-buffet", "notebook-sketch"],
        help="Default ink palette for midcentury-illustrated",
    )
    ap.add_argument(
        "--single-size",
        action="store_true",
        help="Hide batch-size toggle controls (for single-batch recipes)",
    )
    ap.add_argument("--work-root", default=os.path.join(REPO_ROOT, "work"))
    a = ap.parse_args()

    slug = re.sub(r"[^a-z0-9-]+", "-", a.slug.lower()).strip("-")
    if not slug:
        sys.exit("invalid slug")

    style_dir = f"{a.style}{'-breezy' if (a.style == 'midcentury-illustrated' and a.breezy) else ''}"
    dest = os.path.join(a.work_root, slug, style_dir)
    if os.path.exists(dest):
        sys.exit(f"working dir already exists: {dest}")

    src_ex = os.path.join(
        REPO_ROOT,
        "examples",
        "sujuk-twice-baked-potatoes" if a.style == "kodachrome-1960s" else "sujuk-potatoes-illustrated",
    )
    os.makedirs(os.path.join(dest, "img"), exist_ok=True)
    shutil.copy2(os.path.join(src_ex, "template.html"), os.path.join(dest, "template.html"))

    prompts_src = (
        os.path.join(REPO_ROOT, "styles", "midcentury-illustrated", "prompts-breezy.json")
        if (a.style == "midcentury-illustrated" and a.breezy)
        else os.path.join(src_ex, "prompts.json")
    )
    shutil.copy2(prompts_src, os.path.join(dest, "prompts.json"))

    tpl_path = os.path.join(dest, "template.html")
    html = open(tpl_path, encoding="utf-8").read()
    if a.style == "midcentury-illustrated":
        html = re.sub(r'data-palette="[^"]+"', f'data-palette="{a.palette}"', html, count=1)
    if a.single_size:
        html = html.replace("<body ", '<body data-single-size="true" ', 1)
    with open(tpl_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"scaffolded: {dest}")
    print("next:")
    print(f"  1. edit {dest}/prompts.json and {dest}/template.html")
    print(f"  2. python3 {REPO_ROOT}/scripts/print_prompts.py {dest}/prompts.json hero")
    print(f"  3. generate hero first, then s1..sN with >=0.5-1s wait between calls into {dest}/img/<name>.png")
    print(f"  4. python3 {REPO_ROOT}/scripts/make_contact_sheet.py {dest}/img {dest}/contact_sheet.png")
    print(f"  5. python3 {REPO_ROOT}/scripts/build.py {dest}/template.html {dest}/img {dest}/{slug}-{style_dir} --preview-dir {dest}/previews")


if __name__ == "__main__":
    main()
