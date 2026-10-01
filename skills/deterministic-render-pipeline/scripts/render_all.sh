#!/bin/bash
# 一键全量出片驱动（多视角 × 多风格 + 片尾卡 concat）
# 复制到项目 render/ 后按实际视角清单修改 CAPTURES 数组即可
set -euo pipefail
cd "$(dirname "$0")/.."

HTTP_PID=""
PORT=""
ensure_server() {
  if [[ -n "$PORT" ]] && curl -sf -o /dev/null "http://127.0.0.1:$PORT/index.html"; then return; fi
  [[ -n "$HTTP_PID" ]] && kill $HTTP_PID 2>/dev/null || true
  for p in 8190 8191 8192 8193 8194 8195; do
    if ! lsof -nP -iTCP:$p -sTCP:LISTEN >/dev/null 2>&1; then PORT=$p; break; fi
  done
  [[ -z "$PORT" ]] && { echo "无空闲端口"; exit 1; }
  nohup python3 -m http.server $PORT >/tmp/render_http_$PORT.log 2>&1 &
  HTTP_PID=$!
  for i in $(seq 1 20); do curl -sf -o /dev/null "http://127.0.0.1:$PORT/index.html" && break; sleep 0.5; done
  export CAPTURE_URL="http://127.0.0.1:$PORT"
  echo "== serving on $CAPTURE_URL =="
}
trap '[[ -n "$HTTP_PID" ]] && kill $HTTP_PID 2>/dev/null || true' EXIT

run_capture() { # $1=帧目录 $2=style $3=view；子 shell 防 env 泄漏到后续调用
  ensure_server
  rm -rf "$1"
  ( export CAPTURE_STYLE="${2:-}" CAPTURE_VIEW="${3:-}"; node render/capture.js "$1" ) \
    || { echo "重试 $1（换端口）"; PORT=""; ensure_server; ( export CAPTURE_STYLE="${2:-}" CAPTURE_VIEW="${3:-}"; node render/capture.js "$1" ); }
}

# 视角/风格清单：按需增删（'帧目录' 'style' 'view'）
run_capture frames ''
run_capture frames-top '' top
run_capture frames-front '' front
run_capture frames-side '' side
run_capture frames-bp blueprint ''
run_capture frames-bp-top blueprint top
ensure_server; rm -rf frames-card; node render/card.js || { PORT=""; ensure_server; node render/card.js; }

bash render/encode.sh dist/_base12.mp4 frames
for v in top front side; do bash render/encode.sh dist/final-$v.mp4 frames-$v; done
bash render/encode.sh dist/final-blueprint.mp4 frames-bp
bash render/encode.sh dist/final-blueprint-top.mp4 frames-bp-top

ffmpeg -y -framerate 30 -i frames-card/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 /tmp/endcard.mp4
ffmpeg -y -i dist/_base12.mp4 -i /tmp/endcard.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[out]" -map "[out]" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart dist/final.mp4
rm -f dist/_base12.mp4

echo "== all done =="
for f in dist/final*.mp4; do echo "$f: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")s"; done
