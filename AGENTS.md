# AGENTS.md — Notes for AI Agents (Antigravity, Claude Code, Codex, Gemini CLI)

Read `CLAUDE.md` and `SKILL.md` before starting work in this repository.

## Mandatory First Gate: Opening Interview
Whenever a user asks to create a new vintage recipe card (even if they provide a complete recipe upfront):
1. **Interview first before any scaffolding, `prompts.json`, image generation, or HTML editing**—use your interactive multiple-choice question tool (`ask_question` / `AskUserQuestion`) when available, skipping only options the user already explicitly specified:
   - **Main style:** **`kodachrome-1960s`** (1960s test-kitchen photography, *Betty Crocker* / *Good Housekeeping* style) vs. **`midcentury-illustrated`** (1950s–60s gouache, screenprint & ink spot art, *Party Cookbook* / *Fireside* / *Chatelaine 401* / *Festive Buffet* style) vs. **both**.
   - **If `midcentury-illustrated`:**
     - **Illustration flavor:** `editorial-ink` (gouache & crosshatching) vs. `breezy-upa` (minimalist sketchy ink & off-register spot color).
     - **Default ink palette:** `party-modern`, `chatelaine-green`, `festive-buffet`, or `notebook-sketch`.
     - **Comic callouts:** Clean text-free art *(default)* vs. playful 1950s hand-lettered comic labels (`"CHEESE PULL!"`, `"SIZZLE!"`, via `--callouts`).
   - **Batch sizing:** Single size (`--single-size`) vs. interactive `1× / 2×` batch toggle (with matching PDFs for both sizes).
   - **Delivery (all batches, especially multi-recipe):** Tell the user transparently that you'll create the save folder automatically if they don't already have one, and ask where to save finished cards (suggesting `Documents/Recipes` (`~/Documents/Recipes/` on Mac, `Documents\Recipes\` on Windows—or `~/Documents/Personal/Recipes/` if it already exists), `Desktop/Recipes` for quick printing/AirDrop, `output/` inside the repo, or a custom folder). For 2+ recipes, also ask whether to merge the batch into one tablet cookbook PDF with a linked TOC (`scripts/merge_cookbook.py`).
2. **Work one recipe-style card at a time** once the interview answers are confirmed.

## Standard Pipeline (After Interview Answers Are Confirmed)
1. **Bootstrap dependencies silently:** Before running build scripts, run `python3 scripts/ensure_env.py` once; if `Pillow`/`pymupdf` aren't installed globally, it auto-creates `.venv/` and prints `PYTHON=...` to use for `build.py` / `make_contact_sheet.py` / `merge_cookbook.py` (never ask the user to run `pip3 install` themselves).
2. **Scaffold working dir:** Run `python3 scripts/new_recipe.py <slug> --style ... [--breezy] [--palette ...] [--single-size]` to create `work/<slug>/<style>/` without modifying `examples/`.
3. **Prompts & Test Art:** Write `prompts.json` preserving the chosen style's exact `"style"` block, print prompts via `scripts/print_prompts.py` (pass `--callouts` if the user wants playful 1950s hand-lettered comic labels like `"CHEESE PULL!"` or `"SIZZLE!"`), generate `hero` **first**, inspect it, then generate `s1`–`sN` **sequentially using a single `image-generator` subagent (one image call per turn, waiting at least 0.5–1 second after each request)**—never split `s1`–`sN` across concurrent subagents or fire 8–9 requests simultaneously, and never batch multiple recipes' images at once.
   - **Image backend rule (strict):** Gemini/Antigravity and Codex **must use their native built-in image generation tools ONLY** and must **never** invoke `scripts/gen_images.py` or use the user's OpenRouter key (not even on errors or rate limits) **unless the user explicitly authorizes OpenRouter in the conversation**. **Only Claude Code** uses `scripts/gen_images.py` / OpenRouter by default.
4. **Contact Sheet QA:** Run `scripts/make_contact_sheet.py img contact_sheet.png` and visually inspect every tile before embedding.
5. **Adapt & Build:** Update `template.html` with faithful recipe copy (using `.dense` for 22+ ingredients, `.cols-2` for 4–6 steps, `.cols-4` or a 4-page spread for 10+ steps / multi-option recipes, `.ahead-card.span-2` / `.span-full` for balanced grid tails, and `data-single-size="true"` for fixed-batch recipes), then run `scripts/build.py` (works on macOS and Linux with Chrome/Chromium) with `--preview-dir` (and `--alt-hash` / `--alt-suffix` only when dual-sized).
6. **Preview QA & Delivery:** Inspect all generated `page1.png` / `page2.png` previews, confirm clean pagination with zero collisions, create the user's chosen output folder automatically (`mkdir -p`) if it doesn't exist yet, and copy final `.html` / `.pdf` outputs there without overwriting existing versions (reporting the exact saved folder path). For multi-recipe batches, merge them into a single tablet cookbook PDF with clickable TOC links and outline bookmarks via `scripts/merge_cookbook.py` if requested.

## Git Workflow
- **Always use a Pull Request** for repository changes—never push or force-push directly to `main`. Run `python3 -m unittest discover -s tests -v` before opening a PR.
