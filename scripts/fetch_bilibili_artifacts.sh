#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  fetch_bilibili_artifacts.sh <bilibili-url-or-bvid> <output-dir> [--with-audio]

Examples:
  fetch_bilibili_artifacts.sh "https://www.bilibili.com/video/BV1xx411c7mD" /tmp/bili-job
  fetch_bilibili_artifacts.sh "BV1xx411c7mD" /tmp/bili-job --with-audio
EOF
}

if [[ $# -lt 2 ]]; then
  usage >&2
  exit 1
fi

input="$1"
output_dir="$2"
with_audio="false"

if [[ ${3:-} == "--with-audio" ]]; then
  with_audio="true"
fi

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "Missing dependency: yt-dlp" >&2
  exit 2
fi

mkdir -p "$output_dir"

if [[ "$input" =~ ^BV[0-9A-Za-z]+$ ]]; then
  url="https://www.bilibili.com/video/$input"
else
  url="$input"
fi

template="$output_dir/%(id)s-%(title).120B.%(ext)s"
metadata_path="$output_dir/metadata.json"
subtitle_log="$output_dir/subtitles.log"

yt-dlp --dump-single-json "$url" > "$metadata_path"

if ! yt-dlp \
  --skip-download \
  --write-subs \
  --write-auto-subs \
  --sub-langs "all,-live_chat" \
  --sub-format "vtt/srt/json3/best" \
  -o "$template" \
  "$url" >"$subtitle_log" 2>&1; then
  echo "Subtitle fetch failed. See $subtitle_log for details." >&2
  cat "$subtitle_log" >&2
  exit 3
fi

if [[ "$with_audio" == "true" ]]; then
  yt-dlp \
    --extract-audio \
    --audio-format mp3 \
    --audio-quality 0 \
    -o "$template" \
    "$url"
fi

echo "Fetched artifacts into: $output_dir"
echo "Metadata: $metadata_path"
echo "Subtitle fetch log: $subtitle_log"
echo "Subtitle files:"
find "$output_dir" -maxdepth 1 \( -name "*.vtt" -o -name "*.srt" -o -name "*.json3" \) -print | sort || true
echo "Danmaku files (not speech subtitles):"
find "$output_dir" -maxdepth 1 -name "*.danmaku.xml" -print | sort || true

if [[ "$with_audio" == "true" ]]; then
  echo "Audio files:"
  find "$output_dir" -maxdepth 1 \( -name "*.mp3" -o -name "*.m4a" -o -name "*.webm" \) -print | sort || true
fi
