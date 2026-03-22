#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


TIMESTAMP_RE = re.compile(
    r"^\s*(\d{2}:)?\d{2}:\d{2}(?:[.,]\d{3})?\s+-->\s+(\d{2}:)?\d{2}:\d{2}(?:[.,]\d{3})?(?:\s+.*)?\s*$"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Normalize subtitle files into clean transcript text."
    )
    parser.add_argument("input_path", help="Path to .vtt, .srt, or .json3 file")
    parser.add_argument("--output", help="Write result to a file instead of stdout")
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Preserve timestamps where available",
    )
    return parser.parse_args()


def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def parse_vtt_or_srt(raw_text, keep_timestamps):
    lines = raw_text.splitlines()
    items = []
    current_timestamp = None
    buffer = []

    def flush():
        nonlocal buffer, current_timestamp
        if not buffer:
            return
        text = clean_text(" ".join(buffer))
        if text:
            if keep_timestamps and current_timestamp:
                items.append(f"[{current_timestamp}] {text}")
            else:
                items.append(text)
        buffer = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == "WEBVTT" or stripped.isdigit():
            flush()
            continue
        if TIMESTAMP_RE.match(stripped):
            flush()
            current_timestamp = stripped.split("-->")[0].strip().replace(",", ".")
            continue
        buffer.append(stripped)

    flush()

    deduped = []
    for item in items:
        if not deduped or deduped[-1] != item:
            deduped.append(item)
    return "\n".join(deduped)


def parse_json3(raw_text, keep_timestamps):
    payload = json.loads(raw_text)
    events = payload.get("events", [])
    items = []

    for event in events:
        segs = event.get("segs")
        if not segs:
            continue
        text = clean_text("".join(seg.get("utf8", "") for seg in segs))
        if not text:
            continue
        if keep_timestamps and "tStartMs" in event:
            timestamp_ms = int(event["tStartMs"])
            hours = timestamp_ms // 3_600_000
            minutes = (timestamp_ms % 3_600_000) // 60_000
            seconds = (timestamp_ms % 60_000) // 1000
            millis = timestamp_ms % 1000
            if hours:
                stamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"
            else:
                stamp = f"{minutes:02d}:{seconds:02d}.{millis:03d}"
            items.append(f"[{stamp}] {text}")
        else:
            items.append(text)

    deduped = []
    for item in items:
        if not deduped or deduped[-1] != item:
            deduped.append(item)
    return "\n".join(deduped)


def normalize(path, keep_timestamps):
    suffix = path.suffix.lower()
    raw_text = path.read_text(encoding="utf-8")
    if suffix in {".vtt", ".srt"}:
        return parse_vtt_or_srt(raw_text, keep_timestamps)
    if suffix == ".json3":
        return parse_json3(raw_text, keep_timestamps)
    raise ValueError(f"Unsupported subtitle format: {suffix}")


def main():
    args = parse_args()
    input_path = Path(args.input_path)
    result = normalize(input_path, args.timestamps)
    if args.output:
        Path(args.output).write_text(result + "\n", encoding="utf-8")
    else:
        print(result)


if __name__ == "__main__":
    main()
