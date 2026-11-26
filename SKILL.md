---
name: vintage-picture-recipe
description: Turn any recipe into a vintage 1950s–1960s 2-page step-by-step recipe card (either 1960s Kodachrome test-kitchen photography or Mid-Century gouache/screenprint illustration), as a self-contained HTML with optional 1x/2x size toggle plus print-ready US Letter PDFs. Use when the user asks for a "vintage", "old-school", "Betty Crocker", "Good Housekeeping", "Party Cookbook", or "step-by-step" recipe card.
---

# Vintage Picture Recipe

Produces a full-color, double-sided US Letter recipe sheet in one of two selectable period styles:
1. **`kodachrome-1960s`** (*Betty Crocker* / *Good Housekeeping*): Warm 1963 Kodachrome studio flash photography on avocado-green boomerang Formica, tilted taped hero photo, Kitchen Tested seal, and a 3×3 step photo grid (`examples/sujuk-twice-baked-potatoes/`).
2. **`midcentury-illustrated`** (*Party Cookbook* / *Fireside* / *Chatelaine 401* / *Festive Buffet*): Bold 1950s–60s flat gouache, screenprint & ink spot illustrations, oversized colored initial capitals, offset ink-block frames, and zero photography (`examples/sujuk-potatoes-illustrated/`). Comes in two illustration flavors—**`editorial-ink`** (detailed gouache & crosshatching) and **`breezy-upa`** (minimalist 1950s UPA animation silhouettes with open negative space, `styles/midcentury-illustrated/prompts-breezy.json`)—plus four selectable ink palettes (`party-modern`, `chatelaine-green`, `festive-buffet`, `notebook-sketch`).

`SKILL_DIR` below refers to the folder containing this `SKILL.md`. Commands assume macOS with `python3` (`Pillow` and `pymupdf`) and Google Chrome installed.

## Step 0: Ask for Style First (Mandatory)
Before creating `prompts.json`, generating images, or copying a template for any new recipe card, **ask the user which style they want first** (see `CLAUDE.md` and `AGENTS.md`):
- **Style 1 (`kodachrome-1960s`)** vs. **Style 2 (`midcentury-illustrated`)**
- If Style 2, which **illustration flavor** (`editorial-ink` vs. `breezy-upa` minimalist UPA) and **ink palette** (`party-modern`, `chatelaine-green`, `festive-buffet`, or `notebook-sketch`)
- Whether they want a **1× / 2× batch-size toggle** (and exact scaled cook times)

## Reference Examples
- `examples/sujuk-twice-baked-potatoes/` — Style 1 (`kodachrome-1960s`): 8 step photos + `"Make It Ahead"`, `4 Potatoes` / `8 Potatoes` toggle.
- `examples/sujuk-potatoes-illustrated/` — Style 2 (`midcentury-illustrated`): 8 illustrated plates + solid-ink `"Make It Ahead"` card, batch toggle + 4-palette switcher (`data-palette`), oversized initial caps.

## Workflow
1. **Confirm style & batch details** with the user (Step 0).
2. **Stage in a scratch directory.** Copy the matching example folder (`examples/sujuk-twice-baked-potatoes/` or `examples/sujuk-potatoes-illustrated/`) into a scratch folder.
3. **Update the recipe faithfully.** Keep every ingredient amount, temperature, and cooking time exact—for both the default batch size and the scaled toggle size. Never invent doubled bake/cook times.
4. **Author `prompts.json`.** Keep the shared `"style"` block from your chosen style word-for-word so the whole card reads like one unified book, and write scene descriptions for `hero` (`3:4`) and `s1`–`sN` (`4:3`).
5. **Generate the `hero` test visual first**, inspect it visually, and confirm the style, framing, and absence of text/borders before generating `s1`–`sN`.
6. **Generate the remaining step visuals** using one of the backends below.
7. **Inspect every visual on a contact sheet:**
   `python3 SKILL_DIR/scripts/make_contact_sheet.py img contact_sheet.png`
   View `contact_sheet.png` and regenerate any shot with extra hands, garbled text, modern digital look, or baked-in white borders.
8. **Adapt `template.html`:** Update title, kicker, meta, intro, ingredients (`data-big` / small defaults), glance strip, equipment footer, steps, hint boxes, and (for Style 2) `data-palette`.
9. **Build HTML, PDF(s), and previews:**
   `python3 SKILL_DIR/scripts/build.py template.html img OUT_BASE --preview-dir previews [--alt-hash small --alt-suffix -4-potatoes]`
   *(Note: headless Chrome needs network access for Google Fonts and macOS permissions outside a restricted sandbox.)*
10. **Verify every preview set** (`previews/page1.png`, `previews/page2.png`, and `previews-alt/` if built):
    - Exactly **2 pages** per size.
    - No `.glance` / `.stats-row` strip or hero caption colliding with the `.p1-foot` border.
    - No Page-2 step caption colliding with `.p2-foot`.
11. **Save final outputs to `~/Documents/Personal/Recipes/`** (or the user's chosen output directory) without overwriting existing files (`-v2`, `-v3`, etc.). Report saved file paths and image generation cost (zero per-image charge if using built-in subscription generation).

## Image Backends (Strict Harness Rule)

### A. Built-In Native Image Generation (Mandatory for Gemini / Antigravity and Codex)
**Gemini / Antigravity and Codex MUST use their native built-in image generation tool ONLY (`image-generator` / native image tool) and MUST NEVER invoke `scripts/gen_images.py` or use the user's OpenRouter key—not even as a fallback.**
1. Print exact word-for-word prompts:
   `python3 SKILL_DIR/scripts/print_prompts.py prompts.json`
2. Invoke `image-generator` (or your native image tool) for `hero` first (`3:4` portrait) and inspect it. Then generate `s1`–`sN` (`4:3` landscape) **with at least a 0.5–1 second wait between image generation requests** (sequentially or in small staggered pairs—never fire 8–9 requests simultaneously in one unthrottled burst, or the image endpoint will hit `429` rate limits).
   - If a call still hits a transient `429` / burst rate limit, wait at least 1 second and retry only the failed image(s) via `send_message`—never switch to OpenRouter.
3. Because the built-in image tool writes `.jpg` files into the agent's artifact directory (`<name>_<timestamp>.jpg`), copy the **exact chosen filename** (avoid blind globs if a prompt was retried) to `img/<name>.png` in your scratch working directory. Pillow handles JPEG bytes inside `.png` seamlessly.

### B. OpenRouter (`scripts/gen_images.py`) — Claude Code ONLY
**Only Claude Code** (which has no native image generation tool) should run `scripts/gen_images.py`. Gemini/Antigravity and Codex must never run this script.
`python3 SKILL_DIR/scripts/gen_images.py prompts.json img hero`
Then run without names for the rest, or with specific names to redo individual shots.
- Default model `google/gemini-3-pro-image` (override via `MODEL=`) reads `OPENROUTER_API_KEY` from the environment or `OPENROUTER_KEY_FILE` (default `~/.openrouter_key`). Never print or log the API key.
- Includes a built-in **1.0 second wait after each image request** (`--delay 0.5` or `IMAGE_DELAY=0.5` minimum) to avoid rate-limit bursts.
- Always report the total from `img/cost_log.txt` when using OpenRouter.

## Prompting & Layout Lessons
- **Never write "scanned from a book page".** The model will draw book gutters and gibberish captions. Use `"full-bleed edge-to-edge"` and `"no text, no captions, no book pages"`.
- **Style 1 (`kodachrome-1960s`):** Count hands explicitly (`"No hands"` for `hero`; `"Exactly ONE person, exactly TWO hands visible"` for action shots). Describe unfamiliar ingredients and garnish sizes visually. Add `"no text on it"` on tins/shakers.
- **Style 2 (`midcentury-illustrated`):** Explicitly forbid photorealism (`"NOT photorealistic, NOT a photograph, NOT 3D, NOT modern digital vector clipart"`) and lock to 3–4 flat gouache/screenprint inks + black ink crosshatching on matte cream paper. Keep Page-1 ingredients compact (`7.9pt`, `line-height: 1.26`) so `.stats-row` clears `.p1-foot`.
- **Style 1 Page-1 overflow guard (16–20 ingredient lines):** Keep `.ing-box ul` around `8.15pt` (`line-height: 1.24`), `.intro` around `9pt`, `.hero` at `5.15in`, and `.p1-foot` at `bottom: .34in`.
- **Style 1 Page-2 inline script spacing:** Keep `margin-right: .2in` on `.p2-head h2 .script` so `"See how easy it is!"` doesn't collide with `"Step by Step"`.
- **Never write a dollar sign followed by a digit in `SKILL.md`** so skill loaders don't mistake it for an argument placeholder.
