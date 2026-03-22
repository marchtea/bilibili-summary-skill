# bilibili-summary-skill

A Codex skill for fetching Bilibili video text and producing structured summaries.

## What It Does

- accepts a Bilibili URL, short URL, or BV ID
- fetches metadata and available subtitles with `yt-dlp`
- falls back to audio extraction and ASR when subtitles are missing
- normalizes `.vtt`, `.srt`, and `.json3` subtitle files into clean transcript text
- guides the agent to produce timestamp-aware summaries

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    ├── fetch_bilibili_artifacts.sh
    └── normalize_transcript.py
```

## Install

```bash
npx skills add https://github.com/marchtea/bilibili-summary-skill --skill bilibili-summary
```

## Local Prerequisites

- `yt-dlp`
- `ffmpeg`
- an ASR tool such as `whisper` when no subtitles are available

## Notes

- `danmaku.xml` is not treated as transcript text
- ASR fallback is supported by workflow, but depends on a local ASR tool being available
