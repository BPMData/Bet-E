---
name: vintage-picture-recipe
description: Turn any recipe into a vintage 1950s–1960s 2-page step-by-step recipe card (either 1960s Kodachrome test-kitchen photography or Mid-Century gouache/screenprint illustration), as a self-contained HTML with optional 1x/2x size toggle plus print-ready US Letter PDFs. Use when the user asks for a "vintage", "old-school", "Betty Crocker", "Good Housekeeping", "Party Cookbook", or "step-by-step" recipe card.
---

# Vintage Picture Recipe

Produces a full-color, double-sided US Letter recipe sheet in one of two selectable period styles:
1. **`kodachrome-1960s`** (*Betty Crocker* / *Good Housekeeping*): Warm 1963 Kodachrome studio flash photography on avocado-green boomerang Formica, tilted taped hero photo, Kitchen Tested seal, and a 3×3 step photo grid (`examples/sujuk-twice-baked-potatoes/`).
2. **`midcentury-illustrated`** (*Party Cookbook* / *Fireside* / *Chatelaine 401* / *Festive Buffet*): Bold 1950s–60s flat gouache, screenprint & ink spot illustrations, oversized colored initial capitals, offset ink-block frames, and zero photography (`examples/sujuk-potatoes-illustrated/`). Comes in two illustration flavors—**`editorial-ink`** (detailed gouache & crosshatching) and **`breezy-upa`** (minimalist sketchy 1950s ink & off-register spot color in `styles/midcentury-illustrated/prompts-breezy.json`, where `print_prompts.py` / `gen_images.py` flip at random between `2B-loose-hand-inked` and `2C-hastily-sketched`)—plus four selectable ink palettes (`party-modern`, `chatelaine-green`, `festive-buffet`, `notebook-sketch`).

`SKILL_DIR` below refers to the folder containing this `SKILL.md`. Commands assume macOS with `python3` (`Pillow` and `pymupdf`) and Google Chrome installed.

## Step 0: Mandatory Opening Interview (Before Any Work)
Before creating `prompts.json`, generating images, or copying a template for any new recipe card, **interview the user first** (using `ask_question` / `AskUserQuestion` where supported, skipping only choices they already explicitly specified; see `CLAUDE.md` and `AGENTS.md`):
- **Style:** **Style 1 (`kodachrome-1960s`)** vs. **Style 2 (`midcentury-illustrated`)** vs. **both styles**
- **If Style 2 (`midcentury-illustrated`):**
  - **Illustration flavor:** `editorial-ink` vs. `breezy-upa` sketchy minimalist
  - **Ink palette:** `party-modern`, `chatelaine-green`, `festive-buffet`, or `notebook-sketch`
  - **Comic callouts:** Clean text-free spot art *(default)* vs. witty 1950s hand-lettered comic labels (`--callouts`, e.g., `"SIZZLE!"`, `"CHEESE PULL!"`)
- **Batch sizing:** Single size (`--single-size`) vs. **1× / 2× batch-size toggle**
- **Delivery (all cards):** Ask where to save finished cards (suggesting `Documents/Recipes` on Mac/Windows—or `~/Documents/Personal/Recipes/` if present—`Desktop/Recipes` for quick printing/AirDrop, `output/` inside the repo, or a custom folder; explain that you'll create the folder automatically if it doesn't exist yet). For 2+ recipes, also ask whether to merge finished PDFs into one tablet cookbook PDF with a linked TOC (`scripts/merge_cookbook.py`).
- Once confirmed, work **one recipe-style card at a time**.

## Reference Examples
- `examples/sujuk-twice-baked-potatoes/` — Style 1 (`kodachrome-1960s`): 8 step photos + `"Make It Ahead"`, `4 Potatoes` / `8 Potatoes` toggle.
- `examples/sujuk-potatoes-illustrated/` — Style 2 (`midcentury-illustrated`): 8 illustrated plates + solid-ink `"Make It Ahead"` card, batch toggle + 4-palette switcher (`data-palette`), oversized initial caps.

## Workflow
1. **Confirm style & batch details** with the user (Step 0).
2. **Bootstrap Python deps silently if needed:** Run `python3 SKILL_DIR/scripts/ensure_env.py` once; if `Pillow`/`pymupdf` aren't installed globally, it sets up `.venv/` automatically and prints `PYTHON=...` to use for the scripts below.
3. **Scaffold a working dir with `new_recipe.py`:**
   `python3 SKILL_DIR/scripts/new_recipe.py <slug> --style kodachrome-1960s|midcentury-illustrated [--breezy] [--palette ...] [--single-size]`
   This creates `work/<slug>/<style>/` cleanly without modifying `examples/`.
4. **Update the recipe faithfully.** Keep every ingredient amount (including metric `g`/`ml` and `°F`), temperature, and timing exact. For single-batch recipes (`--single-size`), keep `<body data-single-size="true">` and skip `data-big` attributes.
5. **Author `prompts.json`.** Keep the shared `"style"` block (or `"style_variants"`) from your chosen style word-for-word, and write scene descriptions for `hero` (`3:4`) and `s1`–`sN` (`4:3`).
   - Describe specialty gear and ingredients visually without brand-label text (e.g., *La Chamba* matte-black clay pot on a round metal stovetop diffuser, tabletop granite raclette stone with mini cheese-melting trays underneath, unlabeled glass mole jar).
   - For stacked cookware (e.g., clay pot on a stovetop diffuser), explicitly specify `"flames visible underneath the diffuser, pot sitting cleanly on top (no flames between pot and diffuser)"`.
6. **Generate the `hero` test visual first**, inspect it visually, and confirm the style, framing, and absence of text/borders before generating `s1`–`sN`.
7. **Generate the remaining step visuals** one recipe-style card at a time, pacing `≥ 0.5–1 s` between requests.
8. **Inspect every visual on a contact sheet:**
   `python3 SKILL_DIR/scripts/make_contact_sheet.py img contact_sheet.png`
   View `contact_sheet.png` and regenerate any shot with extra hands, garbled text, modern digital look, or baked-in white borders.
9. **Adapt `template.html` for the recipe's size and step count:**
   - **22+ ingredients:** Add `dense` (`<div class="ing-box dense">` / `<div class="ing-panel dense">`) for clean 2-column ingredients.
   - **4–6 steps:** Add `cols-2` (`<div class="steps cols-2">`) for larger step visuals with zero empty filler boxes.
   - **7–8 steps:** Default 3-column `.steps` grid + 1–2 hint/note boxes (or `.ahead-card.span-2` for 7 steps).
   - **9–12 steps:** Use `<div class="steps cols-4">` (fits up to 12 cells on Page 2, e.g., 10 steps + `.ahead-card.span-2`) **or** expand to a **4-page spread** by adding extra `<section class="page">` blocks.
   - **Multi-option / 12+ step recipes** (e.g., Option A & Option B methods): Use a **4-page spread** (Pages 2–3 for steps, Page 4 for alternate option + thickeners + notes using `.optb-grid` / `.panel-box` / `.thickener-band`) rather than cramming text below 7pt.
10. **Build HTML, PDF(s), and previews:**
    `python3 SKILL_DIR/scripts/build.py template.html img OUT_BASE --preview-dir previews [--alt-hash small --alt-suffix -4-potatoes]`
    *(Supports `.png`, `.jpg`, `.jpeg`, and `.webp` in `img/`. Cross-platform Chrome/Chromium auto-detected, or set `CHROME_BIN`; on macOS Chrome headless needs network access for Google Fonts.)*
11. **Verify every preview set** (`previews/page1.png`, `previews/page2.png`, etc.) for zero clipped text or footer overlaps.
12. **Create the chosen output folder automatically if needed and save final outputs** (e.g., `Documents/Recipes`, `Desktop/Recipes`, `output/`, or custom—never overwrite existing files; increment `-v2`, `-v3`, etc.). Report the exact saved file paths (so the user can find them right away on Mac or Windows) and image generation cost (zero per-image charge for Gemini/Codex native tools). For multi-recipe batches, offer to merge them into a single tablet cookbook PDF via `python3 SKILL_DIR/scripts/merge_cookbook.py OUT.pdf *.pdf --style illustrated|kodachrome`.

## Image Backends (Strict Harness Rule)

### A. Built-In Native Image Generation (Mandatory for Gemini / Antigravity and Codex)
**Gemini / Antigravity and Codex MUST use their native built-in image generation tool ONLY (`image-generator` / native image tool) and MUST NEVER invoke `scripts/gen_images.py` or use the user's OpenRouter key—unless the user explicitly authorizes OpenRouter in the conversation.**
1. Print exact word-for-word prompts:
   `python3 SKILL_DIR/scripts/print_prompts.py prompts.json [--callouts]`
2. Invoke `image-generator` (or your native image tool) for `hero` first (`3:4` portrait) and inspect it. Then generate `s1`–`sN` (`4:3` landscape) **sequentially through a single subagent** (one image call per turn, `≥ 0.5–1 s` between requests—never split `s1`–`sN` across concurrent subagents or fire 8–9 requests in one burst, which triggers duplicate retries and `429` rolling-quota exhaustion).
   - If a call still hits a transient `429` / burst rate limit, wait at least 1 second and retry only the failed image(s) via `send_message`—never switch to OpenRouter without explicit user authorization.
3. Because the built-in image tool writes `.jpg` files into the agent's artifact directory (`<name>_<timestamp>.jpg`), copy the **exact chosen filename** (avoid blind globs if a prompt was retried) to `img/<name>.png` (or `.jpg`) in your scratch working directory; `build.py` and `make_contact_sheet.py` handle `.png`, `.jpg`, `.jpeg`, and `.webp` seamlessly.

### B. OpenRouter (`scripts/gen_images.py`) — Claude Code ONLY (or Authorized Fallback)
**Only Claude Code** (which has no native image generation tool) uses `scripts/gen_images.py` by default; Gemini/Antigravity and Codex may run it only when the user explicitly grants permission.
`python3 SKILL_DIR/scripts/gen_images.py prompts.json img [--callouts] hero`
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
