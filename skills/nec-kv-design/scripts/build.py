#!/usr/bin/env python3
"""build.py — 把 NEC Logo 注入 HTML 模板，生成可直接打开的自包含设计稿。

用法:
    python scripts/build.py            # 生成全部
    python scripts/build.py kv         # 只生成主 KV (index.html)
    python scripts/build.py feishu     # 只生成飞书宣传栏 (feishu_banner.html)

输出到技能根目录的 dist/。
"""
import base64, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "nec-logo.png"
DIST = ROOT / "dist"

TARGETS = {
    "kv":      ("templates/kv_template.html",            "index.html"),
    "feishu":  ("templates/feishu_banner_template.html", "feishu_banner.html"),
}

def main():
    which = sys.argv[1:] or list(TARGETS)
    logo_b64 = "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()
    DIST.mkdir(exist_ok=True)
    for key in which:
        tpl_rel, out_name = TARGETS[key]
        html = (ROOT / tpl_rel).read_text(encoding="utf-8").replace("__LOGO_B64__", logo_b64)
        (DIST / out_name).write_text(html, encoding="utf-8")
        print(f"[ok] {key}: dist/{out_name} ({len(html)} bytes)")

if __name__ == "__main__":
    main()
