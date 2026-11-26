#!/usr/bin/env python3
"""Ensure Python dependencies (Pillow, PyMuPDF) and Chrome/Chromium/Edge are ready.

Uses current Python if Pillow + PyMuPDF are already available; otherwise creates a
local repo `.venv/` (avoiding PEP 668 global pip errors) and installs them there.
Prints the Python interpreter path, browser path, and suggested output folders.
"""
import glob
import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(REPO_ROOT, ".venv")
VENV_PY = os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python3")


def has_deps(py: str) -> bool:
    r = subprocess.run([py, "-c", "import PIL, pymupdf"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


def find_chrome() -> str | None:
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
    return pw_hits[-1] if pw_hits else None


def suggest_output_dirs() -> tuple[str, str, str]:
    home = os.path.expanduser("~")
    personal_recipes = os.path.join(home, "Documents", "Personal", "Recipes")
    docs_dir = os.path.join(home, "Documents")
    if not os.path.isdir(docs_dir) and os.path.isdir(os.path.join(home, "OneDrive", "Documents")):
        docs_dir = os.path.join(home, "OneDrive", "Documents")
    suggested = personal_recipes if os.path.isdir(personal_recipes) else os.path.join(docs_dir, "Recipes")

    desktop_dir = os.path.join(home, "Desktop")
    if not os.path.isdir(desktop_dir) and os.path.isdir(os.path.join(home, "OneDrive", "Desktop")):
        desktop_dir = os.path.join(home, "OneDrive", "Desktop")
    desktop_recipes = os.path.join(desktop_dir, "Recipes")

    repo_output = os.path.join(REPO_ROOT, "output")
    return suggested, desktop_recipes, repo_output


def main() -> None:
    py = sys.executable
    if not has_deps(py):
        if os.path.exists(VENV_PY) and has_deps(VENV_PY):
            py = VENV_PY
        else:
            print(f"Bootstrapping local virtualenv in {VENV_DIR}...", file=sys.stderr)
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
            subprocess.run([VENV_PY, "-m", "pip", "install", "--quiet", "pillow", "pymupdf"], check=True)
            py = VENV_PY

    chrome = find_chrome()
    if not chrome:
        sys.exit(
            "Google Chrome, Chromium, or Microsoft Edge not found. Install Google Chrome (or set CHROME_BIN) and re-run."
        )

    suggested_out, desktop_out, repo_out = suggest_output_dirs()
    print(f"PYTHON={py}")
    print(f"CHROME={chrome}")
    print(f"SUGGESTED_OUT_DIR={suggested_out}")
    print(f"DESKTOP_OUT_DIR={desktop_out}")
    print(f"REPO_OUT_DIR={repo_out}")


if __name__ == "__main__":
    main()
