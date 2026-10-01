#!/bin/bash
# promo-render: ffmpeg 合成 + 可选 BGM 灌轨
# 用法:
#   encode.sh <frames_dir> <out.mp4> [bgm.wav] [video_duration_s] [fps]
# 示例:
#   encode.sh /tmp/promo-frames public/videos/promo.mp4 /tmp/bgm.wav 20 30
set -e
FRAMES="$1"; OUT="$2"; BGM="${3:-}"; DUR="${4:-}"; FPS="${5:-30}"

if [ -z "$FRAMES" ] || [ -z "$OUT" ]; then
  echo "usage: encode.sh <frames_dir> <out.mp4> [bgm.wav] [duration_s] [fps]" >&2; exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

EXT="$(ls "$FRAMES" | head -1 | sed 's/.*\.//')"
ffmpeg -y -loglevel error -framerate "$FPS" -i "$FRAMES/f_%04d.$EXT" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -movflags +faststart "$TMP/base.mp4"

if [ -n "$BGM" ] && [ -f "$BGM" ]; then
  D="${DUR:-$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/base.mp4")}"
  ffmpeg -y -loglevel error -i "$TMP/base.mp4" -i "$BGM" \
    -c:v copy -c:a aac -b:a 160k -t "$D" -movflags +faststart "$OUT"
else
  cp "$TMP/base.mp4" "$OUT"
fi
echo "encoded: $OUT ($(stat -f%z "$OUT") bytes)"
