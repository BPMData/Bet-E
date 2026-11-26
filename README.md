# Bet-E (`vintage_recipes`)

Turn any recipe into a **print-ready 1950s–1960s vintage cookbook sheet**—a self-contained HTML file (with live palette switching and optional `1× / 2×` batch sizing) plus US Letter PDFs, complete with AI-generated period visuals and step-by-step picture instructions.

Like its sister repos [EOMD](https://github.com/BPMData/EOMD) (motion design) and [ProofEr](https://github.com/BPMData/ProofEr) (sourced infographics & data essays), **Bet-E is built to be used through an AI coding assistant** (**Antigravity**, **Codex**, or **Claude Code**). You don't write code or edit HTML yourself—you point your assistant at this folder, paste a recipe, and answer a quick interview.

---

## How to Use It (No Coding Required)

### 1. What you need
- **Google Chrome** (or **Microsoft Edge** on Windows / Chromium on Linux) installed on your computer.
- **An AI coding app** (**Antigravity**, **Codex**, or **Claude Code**) with **Python 3** available (already included on most Macs/Linux setups, and easily added on Windows—your AI assistant automatically sets up any missing Python packages inside a local `.venv/` folder on first run, so you never have to run `pip` yourself):
  - **Gemini Antigravity** or **ChatGPT Codex** *(recommended if you already pay for Gemini or ChatGPT)*: uses the assistant's built-in image generator directly, so cards cost **\$0.00 extra** beyond your existing subscription.
  - **Claude Code**: uses OpenRouter (`~/.openrouter_key`, roughly \$0.14 per image, ~\$1.25–\$2.00 per card) because Claude Code doesn't have a native image generator.

### 2. Download or clone the repo and open it in your AI app
```bash
git clone https://github.com/BPMData/Bet-E.git
```
*(Or click **Code → Download ZIP** on GitHub and unzip it.)*

Open the `Bet-E` folder in **Antigravity**, **Codex**, or **Claude Code**, paste any recipe (even a messy phone note or copied webpage), and say:

> *"Make me a vintage recipe card for this."*

### 3. Answer the opening interview
Before generating any artwork, the assistant will ask a short round of plain-English questions:
1. **Pick a visual style** *(or ask for both)*:
   - **1960s Kodachrome Test-Kitchen Photo (`kodachrome-1960s`):** Warm 1963 *Betty Crocker* / *Good Housekeeping* studio flash photography on avocado-green boomerang Formica, tilted taped hero photo, *Kitchen Tested* seal, and a step-by-step photo grid (`examples/sujuk-twice-baked-potatoes/`).
   - **Mid-Century Illustrated Cookbook (`midcentury-illustrated`):** 1950s–60s flat gouache, screenprint & ink spot art (*Party Cookbook*, *The Fireside Cook Book*, *Chatelaine 401*, *Festive Buffet*), oversized colored capitals, and zero photography (`examples/sujuk-potatoes-illustrated/`).
     - **Flavor:** `editorial-ink` (detailed gouache & crosshatching) or `breezy-upa` (sketchy 1950s ink & off-register spot color with generous open cream space).
     - **Ink palette** *(all four remain switchable live in the HTML)*: `party-modern`, `chatelaine-green`, `festive-buffet`, or `notebook-sketch`.
     - **Comic callouts:** Clean text-free art *(default)*, or playful 1950s hand-lettered labels like `"SIZZLE!"` and `"CHEESE PULL!"`.
2. **Batch sizing:** Single fixed size, or an interactive `1× / 2×` batch toggle (exports matching PDFs for both sizes).
3. **Delivery:** Where you want your finished `.html` and `.pdf` cards saved—the assistant will suggest practical options (**`Documents/Recipes`** on Mac or Windows, **`Desktop/Recipes`** for quick printing/AirDrop, or **`output/`** inside this repo), create the folder for you automatically if you don't have one yet, and tell you the exact path when done. If you're making several recipes at once, it'll also ask whether to merge them into **one tablet-ready cookbook PDF** with a clickable Table of Contents.

The assistant handles everything else automatically: generating the hero illustration first for style review, generating the step visuals, checking a contact sheet, laying out the pages, verifying the PDF previews so nothing clips or overflows, and saving the finished files.

---

## Technical Reference & Architecture Notes

### Directory Layout
```text
Bet-E/
├── CLAUDE.md                                # Project rules, mandatory opening interview & backend policy
├── AGENTS.md                                # Cross-agent workflow notes (Antigravity, Claude Code, Codex)
├── SKILL.md                                 # Canonical recipe-card skill (symlinked into .agents/ & .claude/)
├── README.md
├── LICENSE                                  # GNU AGPL-3.0
├── CLA.md                                   # Simple Contributor License Agreement (relicensing grant)
├── CONTRIBUTING.md                          # Contribution & PR checklist
├── styles/
│   ├── kodachrome-1960s/                    # Style 1 spec
│   └── midcentury-illustrated/              # Style 2 spec, prompts-breezy.json (2B/2C) & refs/
├── scripts/
│   ├── ensure_env.py                        # Auto-bootstraps .venv (Pillow + PyMuPDF) and checks Chrome
│   ├── new_recipe.py                        # Scaffolds work/<slug>/<style>/ cleanly (gitignored)
│   ├── print_prompts.py                     # Prints cohesive style+scene prompts (supports --callouts & 2B/2C flip)
│   ├── gen_images.py                        # OpenRouter runner with request pacing & cost logging
│   ├── make_contact_sheet.py                # Builds labeled grid contact sheet (.png/.jpg/.jpeg/.webp)
│   ├── build.py                             # Crops edges, embeds base64 JPEGs, renders PDFs + 90-DPI previews
│   └── merge_cookbook.py                    # Merges recipe PDFs into a tablet PDF with linked TOC & bookmarks
└── examples/
    ├── sujuk-twice-baked-potatoes/          # Style 1 complete reference example
    └── sujuk-potatoes-illustrated/          # Style 2 complete reference example (4-palette switcher + layout helpers)
```

### Design Optimizations & Lessons Learned
- **Why this is harness-first (not a WebUI copy-paste tool):** A single 2-page card takes 5–14 cohesive illustrations plus two-sided Letter CSS pagination QA. Running it inside an agent harness eliminates manual prompting, file renaming, and layout tweaking.
- **Native subscriptions vs. OpenRouter on multi-card batches:**
  - Built-in native image tools (Antigravity / Codex) cost \$0 extra, but have rolling multi-hour capacity caps. Generating `hero` first and then `s1`–`sN` **sequentially through a single subagent** (one request per turn) prevents duplicate retries and stretches quota far better than parallel subagents.
  - For large 5–6 card batches (~45–55 images) in one sitting, either pace across quota windows or authorize `scripts/gen_images.py` via OpenRouter (`google/gemini-3-pro-image`, ~\$0.14/image with `cost_log.txt` tracking).
- **Cohesive visual style & prompt hygiene:**
  - `print_prompts.py` and `gen_images.py` prepend one verbatim `"style"` block (or flip consistently between `2B-loose-hand-inked` and `2C-hastily-sketched` in `prompts-breezy.json`) so every tile looks like the same cookbook.
  - Never describe scenes as *"scanned from a book page"* (models draw book gutters and gibberish captions). Specify `"full-bleed edge-to-edge"`, describe specialty cookware visually without brand text, and for stacked cookware (e.g., clay pot on a stovetop diffuser) explicitly state where the flames belong relative to the diffuser.
  - Vintage *New Yorker*-inspired ink styles occasionally invent comic labels (`"CHEESE PULL!"`, `"SIZZLE!"`), which can look charming—`--callouts` exposes that as an explicit user choice rather than an accident.
- **Two-stage visual QA & print layout resilience:**
  - `make_contact_sheet.py` catches extra hands, baked-in borders, or garbled text before embedding; `build.py` crops 4% per side (`--crop` overridable per image) to trim edge artifacts, converts to quality-88 base64 JPEGs for compact self-contained HTMLs, and outputs 90-DPI `pymupdf` page previews so layout overflow is caught before delivery.
  - `build.py` and `make_contact_sheet.py` accept `.png`, `.jpg`, `.jpeg`, and `.webp` inputs seamlessly.
  - `examples/sujuk-potatoes-illustrated/template.html` includes `.ing-panel.dense` (`column-count: 2` with `break-inside: avoid`), `.steps.cols-2` (4–6 steps), `.steps.cols-4` (9–12 steps), `.ahead-card.span-2` / `.span-full`, and 4-page spread blocks (`.optb-grid`, `.panel-box`, `.thickener-band`) for multi-option recipes.
- **Tablet-ready merged cookbooks (`merge_cookbook.py`):** Multi-file local HTML folders break under iOS/iPadOS Quick Look sandboxing. Merging recipe PDFs with a period-matched TOC cover, PDF outline bookmarks (`set_toc`), Page-1 `LINK_GOTO` targets, and safe-margin `^ CONTENTS` return pills gives instant offline tapping in Apple Books, Files, or GoodNotes.

### CLI Quickstart
```bash
# 1. Scaffold a new working directory (gitignored under work/)
python3 scripts/new_recipe.py my-dish --style midcentury-illustrated --breezy --palette party-modern --single-size

# 2. Print exact word-for-word prompts (add --callouts for optional 1950s comic labels)
python3 scripts/print_prompts.py work/my-dish/midcentury-illustrated-breezy/prompts.json

# 3. Inspect generated art (supports .png/.jpg/.jpeg/.webp)
python3 scripts/make_contact_sheet.py work/my-dish/midcentury-illustrated-breezy/img /tmp/contact_sheet.png

# 4. Build self-contained HTML, letter PDF(s), and 90-DPI previews
python3 scripts/build.py \
  examples/sujuk-twice-baked-potatoes/template.html \
  examples/sujuk-twice-baked-potatoes/img \
  /tmp/sujuk-twice-baked-potatoes \
  --preview-dir /tmp/previews \
  --alt-hash small \
  --alt-suffix -4-potatoes

# 5. Merge multiple recipe PDFs into one tablet cookbook with linked TOC & bookmarks
python3 scripts/merge_cookbook.py \
  /tmp/Thanksgiving-Cookbook.pdf \
  card1.pdf card2.pdf \
  --style illustrated \
  --title "Thanksgiving Cookbook"
```

## License & Contributing

Licensed under the **GNU AGPL-3.0** (see [`LICENSE`](LICENSE)). Contributions are welcome under the terms of [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CLA.md`](CLA.md).
