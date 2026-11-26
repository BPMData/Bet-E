# AGENTS.md — Notes for AI Agents (Antigravity, Claude Code, Codex, Gemini CLI)

Read `CLAUDE.md` and `SKILL.md` before starting work in this repository.

## Mandatory First Gate: Style Selection
Whenever a user asks to create a new vintage recipe card (even if they provide a complete recipe upfront):
1. **If the style is not specified**, do **not** jump straight into `prompts.json`, image generation, or HTML editing. Ask the user first which card style they want:
   - **`kodachrome-1960s`** — 1960s Kodachrome test-kitchen photography (*Betty Crocker* / *Good Housekeeping* style).
   - **`midcentury-illustrated`** — 1950s–60s gouache, screenprint & ink spot illustrations (*Party Cookbook* / *Fireside* / *Chatelaine 401* / *Festive Buffet* style), plus their preferred flavor (**`editorial-ink`** vs. **`breezy-upa`** minimalist sketchy ink) and palette (`party-modern`, `chatelaine-green`, `festive-buffet`, or `notebook-sketch`).
2. **If the user already specified a style or asked for `"both styles"`** (including multi-recipe batches): skip asking which main style; confirm any missing sub-choices (`editorial-ink` vs. `breezy-upa`/random for Style 2, ink palette, single-size vs. `1× / 2×` toggle) in one brief check, then work **one recipe-style card at a time**.

## Standard Pipeline (After Style Is Confirmed)
1. **Scaffold working dir:** Run `python3 scripts/new_recipe.py <slug> --style ... [--breezy] [--palette ...] [--single-size]` to create `work/<slug>/<style>/` without modifying `examples/`.
2. **Prompts & Test Art:** Write `prompts.json` preserving the chosen style's exact `"style"` block, print prompts via `scripts/print_prompts.py`, generate `hero` **first**, inspect it, then generate `s1`–`sN` **waiting at least 0.5–1 second after each image generation request** (never fire 8–9 image calls simultaneously, and never batch multiple recipes' images at once).
   - **Image backend rule (strict):** Gemini/Antigravity and Codex **must use their native built-in image generation tools ONLY** and must **never** invoke `scripts/gen_images.py` or use the user's OpenRouter key (not even on errors or rate limits). **Only Claude Code** uses `scripts/gen_images.py` / OpenRouter.
3. **Contact Sheet QA:** Run `scripts/make_contact_sheet.py img contact_sheet.png` and visually inspect every tile before embedding.
4. **Adapt & Build:** Update `template.html` with faithful recipe copy (using `.dense` for 22+ ingredients, `.cols-2` for 4–6 steps, `.cols-4` or a 4-page spread for 10+ steps / multi-option recipes, and `data-single-size="true"` for fixed-batch recipes), then run `scripts/build.py` (works on macOS and Linux with Chrome/Chromium) with `--preview-dir` (and `--alt-hash` / `--alt-suffix` only when dual-sized).
5. **Preview QA & Delivery:** Inspect all generated `page1.png` / `page2.png` previews, confirm clean pagination with zero collisions, and copy final `.html` / `.pdf` outputs to `~/Documents/Personal/Recipes/` (or the user's chosen output folder) without overwriting existing versions.
