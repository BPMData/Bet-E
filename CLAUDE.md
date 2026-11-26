# CLAUDE.md

**Bet-E** (`github.com/BPMData/Bet-E`) turns recipes into 2-page US Letter vintage cookbook sheets (self-contained HTML + print-ready PDFs) using AI-generated period visuals. Maintained by Bryan Murphy (`BPMData`); finished recipe cards are saved to `~/Documents/Personal/Recipes/` (or a user-chosen output folder).

Read `AGENTS.md` and `SKILL.md` before starting any build.

## New pieces: ask style first
Before doing **any** work on a new recipe card—before writing `prompts.json`, generating images, or copying a template—**STOP and ask the user which style they want first.** Even if the user already pasted a full recipe or gave a quick request (*"make me a vintage card for beef stew"*), that is the start of the conversation, not approval to pick a style for them.

Offer the two project styles in plain, everyday terms (using multiple-choice buttons where your tool supports them, e.g. `AskUserQuestion` / `ask_question`):

1. **1960s Kodachrome Test-Kitchen Photo (`kodachrome-1960s`)**
   - *Betty Crocker* / *Good Housekeeping* look: warm 1963 studio flash photography on an avocado-green boomerang Formica counter, tilted taped hero shot, Kitchen Tested seal, and a 3×3 grid of step photos (`styles/kodachrome-1960s/`, example: `examples/sujuk-twice-baked-potatoes/`).
2. **Mid-Century Illustrated Cookbook (`midcentury-illustrated`)**
   - 1950s–60s screenprint, gouache & ink spot illustrations inspired by *Party Cookbook*, *The Fireside Cook Book*, *Chatelaine 401 Tested Recipes*, and *Festive Buffet Cookery* (`styles/midcentury-illustrated/`, example: `examples/sujuk-potatoes-illustrated/`). Flat bold ink-and-gouache art, oversized two-tone display capitals, high-contrast color blocks, and **zero photography**.
   - If they pick **Mid-Century Illustrated**, confirm both:
     - **Illustration flavor:**
       - `editorial-ink` *(gouache & expressive black-ink crosshatching — *Fireside* / *Party Cookbook* detail)*
       - `breezy-upa` *(breezy, ultra-minimalist 1950s UPA animation & flat screenprint silhouettes with generous open cream space and zero crosshatching — *Festive Buffet* / *Chatelaine 401* spirit)*
     - **Ink palette** (all four remain switchable in the HTML):
       - `party-modern` *(vermilion red, ochre & sage on warm parchment)*
       - `chatelaine-green` *(kelly green & printer's black on newsprint cream)*
       - `festive-buffet` *(hot magenta-pink & chartreuse on ivory)*
       - `notebook-sketch` *(faint blue-ruled notebook paper with ink & watercolor washes)*

In that same short opening round, confirm:
- **Batch-size toggle:** Single size, or an interactive `1× / 2×` batch toggle (with matching PDFs for both sizes)?
- **Layout feel:** Structured editorial grid, or extra playful/asymmetric quirks?

Only proceed to `prompts.json` and image generation after the user picks a style.

## Rules for every piece
- **Keep the recipe faithful:** Every amount, temperature, and timing must match what the user gave or agreed to. Never invent doubled cooking times (baking/roasting scales nonlinearly)—confirm them first.
- **Keep the style cohesive:** Use the shared `"style"` block from the chosen style's `prompts.json` word-for-word across `hero` and `s1`–`sN` so the card looks like one real book.
- **Inspect before building, and inspect after building:** Always view a contact sheet (`scripts/make_contact_sheet.py`) of all generated art (`hero` first as a single test shot, then `s1`–`sN`), and inspect rendered 90-DPI preview PNGs (`scripts/build.py --preview-dir ...`) for **every** exported PDF size to catch clipped captions, footer collisions, or extra pages.
- **Never overwrite outputs:** Save finished files into `~/Documents/Personal/Recipes/` (or your chosen output directory) using incremented `-v2`, `-v3`, `-v4` suffixes (`scripts/build.py` refuses to overwrite).
- **Pace image generation requests:** Wait **at least 0.5–1 second** after each image generation request (`hero` first, then `s1`–`sN` paced—never fire 8–9 requests simultaneously in one burst, which triggers `429` rate limits).
- **Zero-cost native generation first:** Prefer the agent's built-in image generator (`image-generator` / Gemini subscription) when available; only fall back to `scripts/gen_images.py` (OpenRouter) if needed, and always report image costs.

## Where to go
| Task | Go to |
|---|---|
| Full step-by-step build workflow | `SKILL.md` |
| Style 1 specs & reference | `styles/kodachrome-1960s/README.md`, `examples/sujuk-twice-baked-potatoes/` |
| Style 2 specs, palettes & sample art | `styles/midcentury-illustrated/README.md`, `styles/midcentury-illustrated/`, `examples/sujuk-potatoes-illustrated/` |
| Prompt printer, contact sheet & PDF builder | `scripts/` (`print_prompts.py`, `make_contact_sheet.py`, `build.py`, `gen_images.py`) |
| License & contributor relicensing agreement | `LICENSE` (AGPL-3.0), `CLA.md`, `CONTRIBUTING.md` |
| Final delivered recipe cards | `~/Documents/Personal/Recipes/` (or user-specified folder) |
