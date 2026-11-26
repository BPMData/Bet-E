# CLAUDE.md

**Bet-E** (`github.com/BPMData/Bet-E`) turns recipes into 2-page US Letter vintage cookbook sheets (self-contained HTML + print-ready PDFs) using AI-generated period visuals. Maintained by Bryan Murphy (`BPMData`); finished recipe cards are saved to the folder you choose during the opening interview (created automatically if needed—typically `Documents/Recipes`, `Desktop/Recipes`, or `output/` inside the repo).

Read `AGENTS.md` and `SKILL.md` before starting any build.

## New pieces: mandatory opening interview
Before doing **any** work on a new recipe card—before writing `prompts.json`, generating images, or copying a template—**STOP and interview the user first**, asking for every unspecified option below in one clean round (using multiple-choice buttons where your tool supports them, e.g. `AskUserQuestion` / `ask_question`). Even if the user already pasted a full recipe or gave a quick request (*"make me a vintage card for beef stew"*), that is the start of the conversation, not approval to pick defaults for them.

If the user already specified a style (e.g., `"breezy-upa with party-modern and single-size"`) or asked for **"both styles"**, skip only what they already answered and confirm any remaining unspecified options below—then build **one recipe-style card at a time**.

Offer the two project styles in plain, everyday terms:

1. **1960s Kodachrome Test-Kitchen Photo (`kodachrome-1960s`)**
   - *Betty Crocker* / *Good Housekeeping* look: warm 1963 studio flash photography on an avocado-green boomerang Formica counter, tilted taped hero shot, Kitchen Tested seal, and a 3×3 grid of step photos (`styles/kodachrome-1960s/`, example: `examples/sujuk-twice-baked-potatoes/`).
2. **Mid-Century Illustrated Cookbook (`midcentury-illustrated`)**
   - 1950s–60s screenprint, gouache & ink spot illustrations inspired by *Party Cookbook*, *The Fireside Cook Book*, *Chatelaine 401 Tested Recipes*, and *Festive Buffet Cookery* (`styles/midcentury-illustrated/`, example: `examples/sujuk-potatoes-illustrated/`). Flat bold ink-and-gouache art, oversized two-tone display capitals, high-contrast color blocks, and **zero photography**.
   - If they pick **Mid-Century Illustrated**, confirm:
     - **Illustration flavor:**
       - `editorial-ink` *(gouache & expressive black-ink crosshatching — *Fireside* / *Party Cookbook* detail)*
       - `breezy-upa` *(breezy, ultra-minimalist 1950s UPA animation & flat screenprint silhouettes with generous open cream space and zero crosshatching — *Festive Buffet* / *Chatelaine 401* spirit)*
     - **Ink palette** (all four remain switchable in the HTML):
       - `party-modern` *(vermilion red, ochre & sage on warm parchment)*
       - `chatelaine-green` *(kelly green & printer's black on newsprint cream)*
       - `festive-buffet` *(hot magenta-pink & chartreuse on ivory)*
       - `notebook-sketch` *(faint blue-ruled notebook paper with ink & watercolor washes)*
     - **Comic callouts:** Clean text-free spot illustrations *(default)*, or witty 1950s hand-lettered comic labels like `"SIZZLE!"` / `"CHEESE PULL!"` (`--callouts`)?

In that same opening interview, confirm:
- **Batch-size toggle:** Single size (`--single-size`), or an interactive `1× / 2×` batch toggle (with matching PDFs for both sizes)?
- **Layout & delivery:** Structured editorial grid vs. extra playful/asymmetric quirks; where to save finished cards (suggest **`Documents/Recipes`** on Mac/Windows—or `~/Documents/Personal/Recipes/` if it already exists—**`Desktop/Recipes`** for quick printing/sharing, **`output/`** inside the repo, or a custom path, noting you'll create the folder automatically if it doesn't exist yet); and for 2+ recipes, whether to merge them into one tablet cookbook PDF with a linked TOC (`scripts/merge_cookbook.py`).

Only proceed to `prompts.json` and image generation after the user answers the opening interview.

## Rules for every piece
- **Keep the recipe faithful:** Every amount, temperature, and timing must match what the user gave or agreed to. Never invent doubled cooking times (baking/roasting scales nonlinearly)—confirm them first.
- **Keep the style cohesive:** Use the shared `"style"` block from the chosen style's `prompts.json` word-for-word across `hero` and `s1`–`sN` so the card looks like one real book.
- **Inspect before building, and inspect after building:** Always view a contact sheet (`scripts/make_contact_sheet.py`) of all generated art (`hero` first as a single test shot, then `s1`–`sN`), and inspect rendered 90-DPI preview PNGs (`scripts/build.py --preview-dir ...`) for **every** exported PDF size to catch clipped captions, footer collisions, or extra pages.
- **Never overwrite outputs:** Create the chosen output folder automatically if it doesn't exist yet (`Documents/Recipes`, `Desktop/Recipes`, `output/`, or custom) and save finished files using incremented `-v2`, `-v3`, `-v4` suffixes (`scripts/build.py` refuses to overwrite), reporting exact saved paths. For multi-recipe batches, `scripts/merge_cookbook.py` builds a single tablet-friendly PDF with a linked Table of Contents, outline bookmarks, and `^ CONTENTS` return links.
- **Pace image generation requests:** Generate `hero` first, then run `s1`–`sN` **sequentially through a single subagent / loop** waiting **at least 0.5–1 second** after each image request—never split `s1`–`sN` across concurrent subagents or fire 8–9 requests in one burst, which wastes rolling quota on retries and triggers `429` rate limits.
- **Never use OpenRouter from Gemini/Antigravity or Codex without permission:** Gemini/Antigravity and Codex **must use their native built-in image generation tools only** (`image-generator` / built-in image tool) and **must NEVER call `scripts/gen_images.py` or touch the user's OpenRouter key** (not even as a fallback) unless the user explicitly authorizes OpenRouter in the conversation. **Only Claude Code** (which lacks native image generation) uses `scripts/gen_images.py` via OpenRouter by default, and must report the image cost.

## Where to go
| Task | Go to |
|---|---|
| Full step-by-step build workflow | `SKILL.md` |
| Style 1 specs & reference | `styles/kodachrome-1960s/README.md`, `examples/sujuk-twice-baked-potatoes/` |
| Style 2 specs, palettes & sample art | `styles/midcentury-illustrated/README.md`, `styles/midcentury-illustrated/`, `examples/sujuk-potatoes-illustrated/` |
| Prompt printer, contact sheet, PDF builder & cookbook merger | `scripts/` (`print_prompts.py`, `make_contact_sheet.py`, `build.py`, `merge_cookbook.py`, `gen_images.py`) |
| License & contributor relicensing agreement | `LICENSE` (AGPL-3.0), `CLA.md`, `CONTRIBUTING.md` |
| Final delivered recipe cards | User-chosen folder (`Documents/Recipes`, `Desktop/Recipes`, `output/`, etc.) |
