#!/usr/bin/env python3
"""Print full image prompts (style + scene) for native image tools (Gemini / Codex).

Supports optional `style_variants` in prompts.json and flips between them at random
per run (keeping a single recipe visually cohesive) unless `--style-variant` overrides it.

Usage:
  print_prompts.py prompts.json [--style-variant random|mix|0|1...] [name ...]
"""
import argparse
import json
import random


def pick_style(cfg: dict, variant_arg: str) -> tuple[str, str | None]:
    variants = cfg.get("style_variants")
    if not variants:
        return cfg["style"], None
    if variant_arg == "mix":
        chosen = random.choice(variants)
    elif variant_arg == "random":
        chosen = random.choice(variants)
    else:
        chosen = variants[int(variant_arg)]
    if isinstance(chosen, dict):
        return chosen["prompt"], chosen.get("name")
    return str(chosen), None


def main() -> None:
    ap = argparse.ArgumentParser(description="Print word-for-word style+scene prompts.")
    ap.add_argument("prompts_json")
    ap.add_argument(
        "--style-variant",
        default="random",
        help="Variant selection when prompts.json has style_variants: random (default), mix (per-image), or 0-based index",
    )
    ap.add_argument(
        "--callouts",
        action="store_true",
        help="Opt in to playful 1950s hand-lettered comic callout labels (e.g. 'SIZZLE!', 'CHEESE PULL!')",
    )
    ap.add_argument("names", nargs="*")
    a = ap.parse_args()

    cfg = json.load(open(a.prompts_json, encoding="utf-8"))
    aspect = cfg.get("aspect", {})
    names = a.names or list(cfg["prompts"])
    callout_suffix = (
        " Optionally include 1–2 witty, cleanly spelled 1950s hand-lettered editorial ink callouts "
        "(such as 'SIZZLE!' or an ingredient pointer) in the margin."
        if a.callouts
        else ""
    )

    fixed_style, fixed_name = (None, None)
    if a.style_variant != "mix":
        fixed_style, fixed_name = pick_style(cfg, a.style_variant)
        if fixed_name:
            print(f"# style variant: {fixed_name}")

    for name in names:
        if a.style_variant == "mix":
            style, vname = pick_style(cfg, "mix")
            if vname:
                print(f"# style variant ({name}): {vname}")
        else:
            style = fixed_style
        print(f"=== {name} ===")
        print(f"save as: img/{name}.png")
        print(f"aspect ratio: {aspect.get(name, aspect.get('default', '4:3'))}")
        print("prompt: " + style + cfg["prompts"][name] + callout_suffix)
        print()


if __name__ == "__main__":
    main()
