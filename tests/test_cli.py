#!/usr/bin/env python3
"""CLI and build pipeline tests for Bet-E scripts (offline, zero API spend)."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import pymupdf

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def run_script(script_name: str, args: list[str], env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name), *args]
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(cmd, cwd=REPO_ROOT, env=merged_env, text=True, capture_output=True, check=check)


def make_dummy_image(path: str, size: tuple[int, int] = (120, 90), color: tuple[int, int, int] = (212, 58, 36)) -> None:
    fmt = {".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP", ".png": "PNG"}[os.path.splitext(path)[1].lower()]
    Image.new("RGB", size, color).save(path, fmt)


def make_dummy_pdf(path: str, titles: list[str]) -> None:
    doc = pymupdf.open()
    for t in titles:
        pg = doc.new_page(width=612, height=792)
        pg.insert_text(pymupdf.Point(72, 72), t, fontsize=18)
    doc.save(path)
    doc.close()


def make_stub_chrome(bin_dir: str, lines: list[str] | None = None) -> str:
    """Create a tiny cross-platform stub browser script that writes a 1-page PDF for --print-to-pdf=..."""
    stub = os.path.join(bin_dir, "stub-chrome")
    render_lines = lines or ["Stub Rendered Page"]
    draws = "\n".join(
        f"pg.insert_text(pymupdf.Point(72, {100 + i * 80}), {line!r}, fontsize=14)"
        for i, line in enumerate(render_lines)
    )
    Path(stub).write_text(
        f"#!{sys.executable}\n"
        "import sys, pymupdf\n"
        "pdf_out = next(a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--print-to-pdf='))\n"
        "doc = pymupdf.open()\n"
        "pg = doc.new_page(width=612, height=792)\n"
        f"{draws}\n"
        "doc.save(pdf_out)\n",
        encoding="utf-8",
    )
    os.chmod(stub, 0o755)
    return stub


class BetECLITests(unittest.TestCase):
    def test_scripts_compile(self) -> None:
        scripts = sorted(str(p) for p in SCRIPTS_DIR.glob("*.py"))
        r = subprocess.run([sys.executable, "-m", "py_compile", *scripts], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_skill_has_no_dollar_digit_placeholders(self) -> None:
        txt = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\$\d", txt), "SKILL.md should avoid $<digit> placeholders")
        for rel in (".agents/skills/vintage-picture-recipe/SKILL.md", ".claude/skills/vintage-picture-recipe/SKILL.md"):
            self.assertTrue((REPO_ROOT / rel).exists(), f"missing {rel}")

    def test_new_recipe_scaffold_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            r = run_script(
                "new_recipe.py",
                ["test-stew", "--style", "midcentury-illustrated", "--breezy", "--palette", "festive-buffet", "--single-size", "--work-root", tmp],
            )
            dest = Path(tmp) / "test-stew" / "midcentury-illustrated-breezy"
            self.assertIn("scaffolded:", r.stdout)
            tpl = (dest / "template.html").read_text(encoding="utf-8")
            self.assertIn('data-palette="festive-buffet"', tpl)
            self.assertIn('data-single-size="true"', tpl)
            prompts = json.loads((dest / "prompts.json").read_text(encoding="utf-8"))
            self.assertIn("style_variants", prompts)

            r2 = run_script(
                "new_recipe.py",
                ["test-stew", "--style", "midcentury-illustrated", "--breezy", "--work-root", tmp],
                check=False,
            )
            self.assertNotEqual(r2.returncode, 0)

    def test_print_prompts_variants_and_callouts(self) -> None:
        prompts_path = str(REPO_ROOT / "styles" / "midcentury-illustrated" / "prompts-breezy.json")
        plain = run_script("print_prompts.py", [prompts_path, "--style-variant", "0", "hero"])
        self.assertIn("# style variant: 2B-loose-hand-inked", plain.stdout)
        self.assertNotIn("hand-lettered editorial ink callouts", plain.stdout)

        with_callouts = run_script("print_prompts.py", [prompts_path, "--style-variant", "1", "--callouts", "hero"])
        self.assertIn("# style variant: 2C-hastily-sketched", with_callouts.stdout)
        self.assertIn("hand-lettered editorial ink callouts", with_callouts.stdout)

    def test_make_contact_sheet_mixed_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            img_dir = os.path.join(tmp, "img")
            os.makedirs(img_dir)
            make_dummy_image(os.path.join(img_dir, "hero.png"), (90, 120))
            make_dummy_image(os.path.join(img_dir, "s1.jpg"), (120, 90))
            make_dummy_image(os.path.join(img_dir, "s2.webp"), (120, 90))
            make_dummy_image(os.path.join(img_dir, "s1_old1.png"), (120, 90))

            out_png = os.path.join(tmp, "sheet.png")
            r = run_script("make_contact_sheet.py", [img_dir, out_png])
            self.assertIn("(3 images)", r.stdout)
            with Image.open(out_png) as im:
                self.assertEqual(im.size, (1260, 315))

    def test_build_mixed_extensions_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            img_dir = os.path.join(tmp, "img")
            os.makedirs(img_dir)
            make_dummy_image(os.path.join(img_dir, "hero.jpg"))
            make_dummy_image(os.path.join(img_dir, "s1.webp"))
            tpl = Path(tmp) / "tpl.html"
            tpl.write_text("<html><body><img src='{{hero}}'><img src='{{s1}}'></body></html>", encoding="utf-8")
            stub = make_stub_chrome(tmp)
            out_base = os.path.join(tmp, "out", "card")
            previews = os.path.join(tmp, "previews")
            r = run_script(
                "build.py",
                [str(tpl), img_dir, out_base, "--preview-dir", previews],
                env={"CHROME_BIN": stub},
            )
            self.assertIn("card.pdf: 1 pages", r.stdout)
            html_out = Path(out_base + ".html").read_text(encoding="utf-8")
            self.assertIn("data:image/jpeg;base64,", html_out)
            self.assertNotIn("{{hero}}", html_out)
            self.assertTrue(os.path.exists(os.path.join(previews, "page1.png")))

            r2 = run_script("build.py", [str(tpl), img_dir, out_base], env={"CHROME_BIN": stub}, check=False)
            self.assertNotEqual(r2.returncode, 0)

    def test_merge_cookbook_links_bookmarks_and_return_pills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pdf1 = os.path.join(tmp, "first-dish.pdf")
            pdf2 = os.path.join(tmp, "second-dish.pdf")
            make_dummy_pdf(pdf1, ["First Dish", "First Dish Steps"])
            make_dummy_pdf(pdf2, ["Second Dish", "Second Dish Page 2", "Second Dish Page 3"])

            stub = make_stub_chrome(tmp, ["First Dish", "Second Dish"])
            out_pdf = os.path.join(tmp, "Cookbook.pdf")
            r = run_script(
                "merge_cookbook.py",
                [out_pdf, pdf1, pdf2, "--style", "illustrated", "--title", "Test Cookbook"],
                env={"CHROME_BIN": stub},
            )
            self.assertIn("(6 pages, 2 TOC links)", r.stdout)

            merged = pymupdf.open(out_pdf)
            self.assertEqual(len(merged), 6)
            self.assertEqual([l["page"] + 1 for l in merged[0].get_links()], [2, 4])
            self.assertEqual(
                merged.get_toc(),
                [[1, "Table of Contents", 1], [1, "01. First Dish", 2], [1, "02. Second Dish", 4]],
            )
            for pno in range(1, len(merged)):
                self.assertTrue(any(l["page"] == 0 for l in merged[pno].get_links()))
            merged.close()

            r2 = run_script(
                "merge_cookbook.py",
                [out_pdf, pdf1, pdf2],
                env={"CHROME_BIN": stub},
                check=False,
            )
            self.assertNotEqual(r2.returncode, 0)

    def test_ensure_env_outputs_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stub = make_stub_chrome(tmp)
            r = run_script("ensure_env.py", [], env={"CHROME_BIN": stub})
            self.assertIn("PYTHON=", r.stdout)
            self.assertIn(f"CHROME={stub}", r.stdout)
            self.assertIn("SUGGESTED_OUT_DIR=", r.stdout)
            self.assertIn("DESKTOP_OUT_DIR=", r.stdout)
            self.assertIn("REPO_OUT_DIR=", r.stdout)


if __name__ == "__main__":
    unittest.main()
