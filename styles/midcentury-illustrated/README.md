# Style 2: Mid-Century Illustrated Cookbook (`midcentury-illustrated`)

Inspired by 1950s–early 1960s illustrated cookbooks (*Party Cookbook* by Jim Beard, *The Fireside Cook Book*, *Chatelaine 401 Tested Recipes*, *Festive Buffet Cookery*, and hand-tinted notebook recipe art). Zero photography—every visual is stylized mid-century gouache, linocut/screenprint, or minimalist UPA animation art.

## Two Illustration Flavors (Sub-Styles)
1. **`editorial-ink` (Gouache & Crosshatch — `examples/sujuk-potatoes-illustrated/prompts.json`)**
   - *The Fireside Cook Book* / *Party Cookbook* richness: expressive hand-drawn black ink linework with lively crosshatching over flat gouache/screenprint color blocks (`sample-hero.jpg`).
2. **`breezy-upa` (Minimalist Sketch & Screenprint — `styles/midcentury-illustrated/prompts-breezy.json`)**
   - *Party Cookbook (Cocktails for a Few)* / *Kiddie Cocktails* / *Festive Buffet Cookery* breeziness: generous open cream breathing room, zero crosshatching, strictly 2–3 flat spot colors + black, and **no stiff SVG-clipart symmetry**.
   - `prompts-breezy.json` includes **two `style_variants`** that `print_prompts.py` and `gen_images.py` flip between at random by default (or lock with `--style-variant 0|1`):
     - **`2B-loose-hand-inked`** (`sample-hero-breezy-2b.jpg`): loose, slightly wobbly fountain-pen contours with off-register flat screenprint color blocks.
     - **`2C-hastily-sketched`** (`sample-hero-breezy.jpg`): energetic, hastily sketched variable-nib ink lines with dry-textured spot colors slipping playfully outside the lines.

## Visual Signature
- **Typography:** Expressive editorial serif display titles with **oversized colored initial capitals** (like *Party Cookbook*'s large vermilion `P` and `C`), clean block-printed uppercase kickers/headers, and crisp book serif or typewriter bylines.
- **Layout:** Asymmetric editorial grids with bold solid-ink feature blocks, alternating positive/negative color-block panels, crisp ink borders with hard flat offset shadows (no photo tape), and illustrated step tiles paired with a high-contrast solid-ink `"Make It Ahead"` / `"Hostess Notes"` panel.

## Built-In Color Palettes (`<body data-palette="...">`)
1. `party-modern` *(default — Party Cookbook / Fireside vibe)*: Warm parchment (`#f5ebd6`), charcoal ink (`#1f1916`), vermilion red (`#d43a24`), mustard ochre (`#cfa12b`), muted sage (`#5d7a52`).
2. `chatelaine-green` *(Chatelaine 401 vibe)*: Crisp newsprint cream (`#f6f2e4`), printer's black (`#181818`), bold kelly green (`#248349`), warm grey tint (`#e6e2d2`).
3. `festive-buffet` *(Festive Buffet Cookery vibe)*: Ivory stock (`#f8f1df`), ink black (`#1b1715`), hot magenta-rose (`#d82e7b`), chartreuse olive (`#b5a81e`).
4. `notebook-sketch` *(Ruled notebook gouache vibe)*: Faint horizontal blue-ruled cream paper (`#faf4e6`), fountain-pen charcoal (`#262320`), lemon-butter yellow (`#e5ba34`), cherry red (`#cf3a2e`), aqua mint (`#5da89d`).

## Reference Example
- `examples/sujuk-potatoes-illustrated/` (`template.html`, `prompts.json`)
