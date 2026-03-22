#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$ROOT_DIR/tests/fixtures"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

python3 "$ROOT_DIR/scripts/inspect_metadata.py" "$FIXTURES_DIR/sample_metadata.json" > "$TMP_DIR/metadata.out"
grep -q "title: Sample Bilibili Video" "$TMP_DIR/metadata.out"
grep -q "upload_date: 20260323" "$TMP_DIR/metadata.out"

python3 "$ROOT_DIR/scripts/normalize_transcript.py" \
  "$FIXTURES_DIR/sample.vtt" \
  --timestamps \
  --output "$TMP_DIR/transcript-vtt.txt"
grep -q "\[00:00:01.000\] Hello world" "$TMP_DIR/transcript-vtt.txt"
grep -q "\[00:00:04.000\] Second line" "$TMP_DIR/transcript-vtt.txt"

python3 "$ROOT_DIR/scripts/normalize_transcript.py" \
  "$FIXTURES_DIR/sample.json3" \
  --timestamps \
  --output "$TMP_DIR/transcript-json3.txt"
grep -q "\[00:01.250\] 你好世界" "$TMP_DIR/transcript-json3.txt"
grep -q "\[00:04.500\] 第二句" "$TMP_DIR/transcript-json3.txt"

python3 - <<PY
from pathlib import Path
for path in [
    Path("$ROOT_DIR/scripts/normalize_transcript.py"),
    Path("$ROOT_DIR/scripts/transcribe_audio.py"),
    Path("$ROOT_DIR/scripts/inspect_metadata.py"),
]:
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
print("syntax-ok")
PY

echo "smoke-ok"
