#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


FIELDS = [
    "title",
    "uploader",
    "description",
    "duration",
    "view_count",
    "upload_date",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Print a concise summary of Bilibili metadata.json."
    )
    parser.add_argument("metadata_path", help="Path to metadata.json")
    return parser.parse_args()


def main():
    args = parse_args()
    payload = json.loads(Path(args.metadata_path).read_text(encoding="utf-8"))
    for field in FIELDS:
        print(f"{field}: {payload.get(field)}")


if __name__ == "__main__":
    main()
