# Style 2: Mid-Century Illustrated Cookbook (`midcentury-illustrated`)

Inspired by 1950s–early 1960s illustrated cookbooks (*Party Cookbook* by Jim Beard, *The Fireside Cook Book*, *Chatelaine 401 Tested Recipes*, *Festive Buffet Cookery*, and hand-tinted notebook recipe art). Zero photography—every visual is stylized mid-century gouache, linocut/screenprint, or minimalist UPA animation art.

## Two Illustration Flavors (Sub-Styles)
1. **`editorial-ink` (Gouache & Crosshatch — `examples/sujuk-potatoes-illustrated/prompts.json`)**
   - *The Fireside Cook Book* / *Party Cookbook* richness: expressive hand-drawn black ink linework with lively crosshatching over flat gouache/screenprint color blocks (`sample-hero.jpg`).
2. **`breezy-upa` (Minimalist UPA / Screenprint — `styles/midcentury-illustrated/prompts-breezy.json`)**
   - *Festive Buffet Cookery* / *Chatelaine 401* / 1950s UPA animation breeziness: ultra-simple iconic geometric silhouettes, single-stroke contours (or lineless flat cutouts), 40–50% open cream breathing room, strictly 2–3 flat spot colors + black, **zero crosshatching and zero fussy detail** (`sample-hero-breezy.jpg`).

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
