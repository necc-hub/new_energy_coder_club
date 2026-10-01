#!/bin/bash
# 帧目录 → mp4（720p H.264/yuv420p/faststart）
# 用法: bash encode.sh [out.mp4] [framesDir]   （默认 dist/final.mp4 frames/）
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="${1:-dist/final.mp4}"
IN="${2:-frames}"

if [[ ! -d "$IN" ]]; then
  echo "错误: 找不到 $IN/ 目录。请先运行 capture 生成帧序列。" >&2
  exit 1
fi
frame_count=$(find "$IN" -maxdepth 1 -name '*.png' | wc -l | tr -d ' ')
if (( frame_count < 360 )); then
  echo "错误: $IN/ 内 PNG 帧数不足（当前 ${frame_count} 张，至少 360）。" >&2
  exit 1
fi

mkdir -p dist
ffmpeg -y -framerate 30 -i "$IN/%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium \
  -movflags +faststart "$OUT"

ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=nw=1 "$OUT"
