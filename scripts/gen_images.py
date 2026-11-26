#!/usr/bin/env python3
"""Generate vintage cookbook visuals via OpenRouter, paced to avoid rate-limit bursts.

Usage:
  gen_images.py prompts.json OUT_DIR [--delay 1.0] [name ...]

Env:
  MODEL (default google/gemini-3-pro-image)
  IMAGE_DELAY (default 1.0 seconds wait after each request; use >= 0.5)
  OPENROUTER_API_KEY (preferred) or OPENROUTER_KEY_FILE (default ~/.openrouter_key)
"""
import argparse
import base64
import json
import os
import time
import urllib.request

MODEL = os.environ.get("MODEL", "google/gemini-3-pro-image")


def load_key() -> str:
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"].strip()
    key_file = os.path.expanduser(os.environ.get("OPENROUTER_KEY_FILE", "~/.openrouter_key"))
    with open(key_file, encoding="utf-8") as f:
        return f.read().strip()


def generate_one(key: str, cfg: dict, aspect: dict, out: str, name: str) -> tuple[str, float, str]:
    body = {
        "model": MODEL,
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": cfg["style"] + cfg["prompts"][name]}],
        "image_config": {"aspect_ratio": aspect.get(name, aspect.get("default", "4:3"))},
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    r = json.load(urllib.request.urlopen(req, timeout=300))
    cost = (r.get("usage") or {}).get("cost") or 0
    imgs = r["choices"][0]["message"].get("images") or []
    if not imgs:
        return name, cost, "NO IMAGE: " + json.dumps(r)[:300]
    path = os.path.join(out, f"{name}.png")
    if os.path.exists(path):
        k = 1
        while os.path.exists(os.path.join(out, f"{name}_old{k}.png")):
            k += 1
        os.rename(path, os.path.join(out, f"{name}_old{k}.png"))
    with open(path, "wb") as f:
        f.write(base64.b64decode(imgs[0]["image_url"]["url"].split(",", 1)[1]))
    return name, cost, "ok"


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate vintage cookbook visuals via OpenRouter.")
    ap.add_argument("prompts_json")
    ap.add_argument("out_dir")
    ap.add_argument(
        "--delay",
        type=float,
        default=float(os.environ.get("IMAGE_DELAY", "1.0")),
        help="Seconds to wait after each image request (default: 1.0, recommended >= 0.5)",
    )
    ap.add_argument("names", nargs="*", help="Optional subset of prompt names (e.g. hero s1)")
    args = ap.parse_args()

    key = load_key()
    cfg = json.load(open(args.prompts_json, encoding="utf-8"))
    os.makedirs(args.out_dir, exist_ok=True)
    names = args.names or list(cfg["prompts"])
    aspect = cfg.get("aspect", {})
    delay = max(0.5, args.delay)

    total = 0.0
    for idx, name in enumerate(names):
        n, c, s = generate_one(key, cfg, aspect, args.out_dir, name)
        total += c
        print(f"{n}: {s} ${c:.3f}")
        if idx < len(names) - 1:
            time.sleep(delay)

    cost_log = os.path.join(args.out_dir, "cost_log.txt")
    with open(cost_log, "a", encoding="utf-8") as f:
        f.write(f"{MODEL} {' '.join(names)} ${total:.3f}\n")
    alltime = sum(float(line.rsplit("$", 1)[1]) for line in open(cost_log, encoding="utf-8") if "$" in line)
    print(f"this run ${total:.2f} | project total ${alltime:.2f}")


if __name__ == "__main__":
    main()
