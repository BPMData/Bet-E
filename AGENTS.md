# AGENTS.md — Notes for AI Agents (Antigravity, Claude Code, Codex, Gemini CLI)

Read `CLAUDE.md` and `SKILL.md` before starting work in this repository.

## Mandatory First Gate: Style Selection
Whenever a user asks to create a new vintage recipe card (even if they provide a complete recipe upfront):
1. **Do NOT jump straight into `prompts.json`, image generation, or HTML editing.**
2. **Ask the user first** which card style they want:
   - **`kodachrome-1960s`** — 1960s Kodachrome test-kitchen photography (*Betty Crocker* / *Good Housekeeping* style).
   - **`midcentury-illustrated`** — 1950s–60s gouache, screenprint & ink spot illustrations (*Party Cookbook* / *Fireside* / *Chatelaine 401* / *Festive Buffet* style), plus their preferred flavor (**`editorial-ink`** vs. **`breezy-upa`** minimalist UPA animation) and palette (`party-modern`, `chatelaine-green`, `festive-buffet`, or `notebook-sketch`).
3. Confirm whether they want a **`1× / 2×` batch-size toggle** (plus scaled cooking times if applicable) and any special layout quirks.

## Standard Pipeline (After Style Is Chosen)
1. **Stage in scratch:** Copy the matching example (`examples/sujuk-twice-baked-potatoes/` for `kodachrome-1960s` or `examples/sujuk-potatoes-illustrated/` for `midcentury-illustrated`) into a temporary scratch folder. Never edit `examples/` when creating a new user recipe.
2. **Prompts & Test Art:** Write `prompts.json` preserving the chosen style's exact `"style"` block, print prompts via `scripts/print_prompts.py`, generate `hero` **first**, inspect it, then generate `s1`–`sN` **waiting at least 0.5–1 second after each image generation request** (never fire 8–9 image calls simultaneously in one unthrottled burst).
3. **Contact Sheet QA:** Run `scripts/make_contact_sheet.py img contact_sheet.png` and visually inspect every tile before embedding.
4. **Adapt & Build:** Update `template.html` with faithful recipe copy, then run `scripts/build.py` (unsandboxed on macOS so headless Chrome can load Google Fonts) with `--preview-dir` (and `--alt-hash` / `--alt-suffix` if dual-sized).
5. **Preview QA & Delivery:** Inspect all generated `page1.png` / `page2.png` previews, confirm 2 clean pages with zero collisions, and copy final `.html` / `.pdf` outputs to `~/Documents/Personal/Recipes/` (or the user's chosen output folder) without overwriting existing versions.
