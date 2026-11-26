#!/usr/bin/env python3
"""Print full image prompts (style + scene) for agents using a built-in image generator.

Usage:
  print_prompts.py prompts.json [name ...]
"""
import json
import sys


def main() -> None:
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    aspect = cfg.get("aspect", {})
    names = sys.argv[2:] or list(cfg["prompts"])
    for name in names:
        print(f"=== {name} ===")
        print(f"save as: img/{name}.png")
        print(f"aspect ratio: {aspect.get(name, aspect.get('default', '4:3'))}")
        print("prompt: " + cfg["style"] + cfg["prompts"][name])
        print()


if __name__ == "__main__":
    main()
