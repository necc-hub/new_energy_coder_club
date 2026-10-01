#!/usr/bin/env python3
"""promo-render: Playwright 确定性逐帧采集

用法:
  python3 capture.py --url http://localhost:5177/tools/render.html \
      --duration 20 --fps 30 --out /tmp/promo-frames
前置: pip install playwright && playwright install chromium
"""
import argparse, os
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="渲染页地址（须实现 __seek/__ready）")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--ready-timeout", type=int, default=60)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    for f in os.listdir(args.out):
        os.remove(os.path.join(args.out, f))

    n = int(round(args.duration * args.fps))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height}, device_scale_factor=1
        )
        page.goto(args.url)
        page.wait_for_function("window.__ready === true", timeout=args.ready_timeout * 1000)
        for i in range(n):
            page.evaluate(f"window.__seek({i / args.fps:.6f})")
            page.screenshot(path=os.path.join(args.out, f"f_{i:04d}.png"))
        browser.close()
    print(f"frames done: {n} -> {args.out}")


if __name__ == "__main__":
    main()
