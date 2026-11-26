# Bet-E (`vintage_recipes`)

A dual-style skill and Python/Chrome build toolkit for turning recipes into **2-page US Letter vintage cookbook sheets**, with AI-generated period visuals, interactive batch-size toggles in HTML, and print-ready PDFs.

## Available Styles

1. **1960s Kodachrome Test-Kitchen Photo (`kodachrome-1960s`)** — Warm 1963 *Betty Crocker* / *Good Housekeeping* flash photography on an avocado-green boomerang counter, Kitchen Tested seal, and 3×3 photo grid (`styles/kodachrome-1960s/`).
2. **Mid-Century Illustrated Cookbook (`midcentury-illustrated`)** — 1950s–60s flat gouache, screenprint & ink spot art (*Party Cookbook*, *Fireside*, *Chatelaine 401*, *Festive Buffet*), oversized colored initial capitals, offset ink-block frames, two illustration flavors (`editorial-ink` vs. `breezy-upa` minimalist UPA animation), and 4 built-in ink palettes (`party-modern`, `chatelaine-green`, `festive-buffet`, `notebook-sketch`) (`styles/midcentury-illustrated/`).

> **Important:** `CLAUDE.md`, `AGENTS.md`, and `SKILL.md` instruct agents to **always ask which style you want first** before starting any new recipe card.

## Directory Layout

```text
Bet-E/
├── CLAUDE.md                                # Project rules & mandatory style-first gate
├── AGENTS.md                                # Cross-agent workflow notes (Antigravity/Claude/Codex)
├── SKILL.md                                 # Complete step-by-step recipe card skill
├── README.md                                # Tooling usage & dependencies
├── LICENSE                                  # GNU AGPL-3.0
├── CLA.md                                   # Simple Contributor License Agreement (relicensing grant)
├── CONTRIBUTING.md                          # Contribution & PR checklist
├── styles/
│   ├── kodachrome-1960s/                    # Style 1 spec
│   └── midcentury-illustrated/              # Style 2 spec + refs/ moodboard images
├── scripts/
│   ├── new_recipe.py                        # Scaffolds work/<slug>/<style>/ for a new recipe card
│   ├── build.py                             # Crops borders, embeds base64, renders PDF(s) + previews (macOS/Linux)
│   ├── make_contact_sheet.py                # Builds labeled grid contact sheet for QA inspection
│   ├── print_prompts.py                     # Prints word-for-word prompts (with random 2B/2C breezy flip)
│   └── gen_images.py                        # Claude Code-only OpenRouter runner with pacing & cost logging
└── examples/
    ├── sujuk-twice-baked-potatoes/          # Style 1 complete example (template, prompts, img/)
    └── sujuk-potatoes-illustrated/          # Style 2 example (4-palette template + prompts)
```

## Requirements

- macOS with **Google Chrome** (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`)
- **Python 3** with `Pillow` and `pymupdf`:
  ```bash
  pip3 install pillow pymupdf
  ```
- Network access when running Chrome headless (used to load Google Fonts).

## Quickstart

1. Print prompts for your chosen style:
   ```bash
   python3 scripts/print_prompts.py examples/sujuk-potatoes-illustrated/prompts.json
   ```
2. Visually inspect your `img/` folder with a contact sheet:
   ```bash
   python3 scripts/make_contact_sheet.py examples/sujuk-twice-baked-potatoes/img /tmp/contact_sheet.png
   ```
3. Build HTML, both batch-size PDFs, and page previews:
   ```bash
   python3 scripts/build.py \
     examples/sujuk-twice-baked-potatoes/template.html \
     examples/sujuk-twice-baked-potatoes/img \
     /tmp/sujuk-twice-baked-potatoes \
     --preview-dir /tmp/previews \
     --alt-hash small \
     --alt-suffix -4-potatoes
   ```

## License & Contributing

Licensed under the **GNU AGPL-3.0** (see [`LICENSE`](LICENSE)). Contributions are welcome under the terms of [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CLA.md`](CLA.md).
