#!/usr/bin/env bash
# render.sh — 用无头 Chrome 把设计稿逐画板截成 PNG。
# 依赖: Google Chrome (headless=new)。先运行 build.py 生成 dist/。
#
# 用法:
#   bash scripts/render.sh            # 渲染全部 6 块画板到 dist/
#   SCALE=2 bash scripts/render.sh    # 2 倍图（印刷级）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
SCALE="${SCALE:-1}"

# 找 Chrome
for c in "/c/Program Files/Google/Chrome/Application/chrome.exe" \
         "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
         "$(which chrome chromium google-chrome 2>/dev/null | head -1)"; do
  [ -x "$c" ] && CHROME="$c" && break
done
[ -z "$CHROME" ] && { echo "未找到 Chrome/Edge"; exit 1; }

shot() { # $1=html $2=board $3=WxH $4=outfile
  local url="file:///$(cygpath -m "$DIST")/$1?board=$2"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor="$SCALE" --virtual-time-budget=8000 \
    --window-size="$3" --screenshot="$DIST/$4" \
    "$url" 2>/dev/null
  echo "[ok] $4 ($3, ${SCALE}x)"
}

shot index.html           h  1920,1080 "NEC_KV_横版16-9_1920x1080.png"
shot index.html           v  1080,1920 "NEC_KV_竖版海报_1080x1920.png"
shot index.html           s  1080,1080 "NEC_KV_方版社媒_1080x1080.png"
shot feishu_banner.html   f1 1380,450  "飞书宣传栏_A浅色蓝图版_1380x450.png"
shot feishu_banner.html   f2 1380,450  "飞书宣传栏_B深色科技版_1380x450.png"
shot feishu_banner.html   f3 1380,450  "飞书宣传栏_C极简功能版_1380x450.png"
echo "全部完成 → $DIST"
