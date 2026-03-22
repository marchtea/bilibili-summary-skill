---
name: bilibili-summary
description: Fetch a Bilibili video transcript and turn it into a structured summary. Use when the user provides a Bilibili URL or BV ID and wants key points, chapter notes, takeaways, transcript cleanup, or a fallback ASR workflow when subtitles are missing.
---

# Bilibili Summary

## Overview

Use this skill when the task is "take a Bilibili video, extract text from it, then summarize it". The preferred path is subtitles first, ASR second, then a structured summary that cites timestamps when possible.

Assume the skill directory is:

```bash
SKILL_DIR=/Users/summer/.codex/skills/bilibili-summary
```

## When To Use

Trigger this skill when the user:

- gives a Bilibili video URL, short link, or BV ID
- asks to summarize, outline, digest, or extract key takeaways from a Bilibili video
- wants chapter notes, study notes, action items, or a cleaned transcript from Bilibili content
- needs a fallback when a Bilibili video has no usable subtitles

Do not use this skill for general video editing or cross-platform posting. Use `video-editing` for editing footage and `content-engine` or `article-writing` after the summary exists.

## Workflow

### 1. Normalize The Input

Accept any of:

- full Bilibili URL, such as `https://www.bilibili.com/video/BV...`
- short URL such as `https://b23.tv/...`
- raw BV ID such as `BV1xx411c7mD`

If the user only gives a BV ID, build the canonical URL before running tools.

### 2. Check Local Tooling

Prefer this order:

1. `yt-dlp` for metadata, subtitles, and optional audio extraction
2. `ffmpeg` for audio conversion if needed
3. a local ASR tool only when subtitles are unavailable

Check availability with:

```bash
command -v yt-dlp
command -v ffmpeg
python3 --version
python3 -c "import faster_whisper"
```

If `yt-dlp` is missing, explain that the skill cannot fetch Bilibili content directly until it is installed.

### 3. Fetch Metadata And Subtitles

Use the helper script first:

```bash
bash "$SKILL_DIR/scripts/fetch_bilibili_artifacts.sh" "<bilibili-url>" /tmp/bili-job
```

What this does:

- saves `metadata.json`
- downloads manual subtitles or auto subtitles when available
- optionally downloads an audio file when `--with-audio` is passed

If you need to inspect what was fetched, list the output directory and identify:

- subtitle files: `.vtt`, `.srt`, `.json3`
- metadata: `metadata.json`
- danmaku: `.danmaku.xml` comments, which are not spoken subtitles
- audio: `.m4a`, `.mp3`, `.webm`

### 4. Normalize Transcript Text

Convert the best subtitle file to clean text:

```bash
python3 "$SKILL_DIR/scripts/normalize_transcript.py" /tmp/bili-job/<subtitle-file> --output /tmp/bili-job/transcript.txt
```

Use `--timestamps` when the user wants timestamped notes.

Preferred subtitle order:

1. human subtitles
2. auto subtitles
3. ASR output generated from audio

Treat `*.danmaku.xml` as viewer comments only. Do not summarize a video from danmaku unless the user explicitly asks for comment analysis.

### 5. Fallback To ASR When Needed

If no subtitle file exists:

- rerun fetch with audio enabled
- transcribe only after confirming there is a local ASR tool or service path available

Use the bundled ASR helper when `faster-whisper` is installed in the active Python environment:

```bash
python3 "$SKILL_DIR/scripts/transcribe_audio.py" /tmp/bili-job/<audio-file> --output /tmp/bili-job/transcript.txt
```

Example:

```bash
bash "$SKILL_DIR/scripts/fetch_bilibili_artifacts.sh" "<bilibili-url>" /tmp/bili-job --with-audio
python3 "$SKILL_DIR/scripts/transcribe_audio.py" /tmp/bili-job/<audio-file> --output /tmp/bili-job/transcript.txt
```

If no ASR tool is available, stop and tell the user exactly which dependency is missing instead of pretending the transcript is complete.

### 5.1 Inspect Metadata Before Summarizing

Use the metadata helper to confirm title, uploader, duration, and publish date before writing the summary:

```bash
python3 "$SKILL_DIR/scripts/inspect_metadata.py" /tmp/bili-job/metadata.json
```

This is useful for:

- checking whether the video topic matches the user request
- surfacing the exact publish date in your answer when relevant
- spotting whether the video is a guide, vlog, news clip, or repost before you summarize it

### 6. Produce The Summary

Base the final answer on the cleaned transcript, not on guessed video content. Prefer this structure:

1. one-paragraph overview
2. key points
3. chapter-by-chapter notes
4. notable quotes or claims
5. action items or takeaways

If timestamps exist, preserve them for claims, quotes, and chapter headings.

## Output Guidance

For short videos, produce:

- overview
- 3 to 6 key points
- concise takeaway

For long educational videos, produce:

- overview
- chapter notes with timestamps
- important concepts explained in plain language
- open questions or caveats
- practical takeaways

When the user asks for a reusable artifact, save:

- cleaned transcript as `transcript.txt`
- structured notes as `summary.md`

## Example Input And Output

Example user request:

```text
总结这个 B 站视频：https://www.bilibili.com/video/BV1Zv411v7Tc
给我一个 5 点摘要，再列出每一段讲了什么。
```

Example execution flow:

```bash
SKILL_DIR=/Users/summer/.codex/skills/bilibili-summary
bash "$SKILL_DIR/scripts/fetch_bilibili_artifacts.sh" "https://www.bilibili.com/video/BV1Zv411v7Tc" /tmp/bili-job
python3 "$SKILL_DIR/scripts/normalize_transcript.py" /tmp/bili-job/<subtitle-file> --timestamps --output /tmp/bili-job/transcript.txt
```

Example final output shape:

```markdown
# 视频总结

## 概览
这是一支面向入门观众的数据科学科普视频，核心目标是解释数据科学是什么、常见工作内容有哪些，以及它和机器学习、数据分析的关系。

## 5 点摘要
- 数据科学的核心是从数据里提取可执行的信息。
- 工作内容通常包括收集、清洗、分析、建模和解释结果。
- 数据科学不等于机器学习，但机器学习是常见手段之一。
- 业务问题定义比单纯跑模型更重要。
- 输出结果必须能服务决策，而不只是展示图表。

## 分段笔记
- `00:00` 开场：定义数据科学和视频目标
- `00:45` 数据科学常见流程
- `01:30` 与数据分析、机器学习的区别
- `03:10` 典型应用场景
- `04:20` 总结与学习建议
```

## Scripts

### `scripts/fetch_bilibili_artifacts.sh`

Fetches Bilibili metadata, subtitles, and optional audio into one directory.

### `scripts/normalize_transcript.py`

Turns `.vtt`, `.srt`, or `.json3` subtitle files into clean plain text, with optional timestamps.

### `scripts/transcribe_audio.py`

Runs `faster-whisper` on a downloaded audio file, auto-detects language by default, and writes a timestamped transcript.

### `scripts/inspect_metadata.py`

Prints a concise metadata summary from `metadata.json`, including title, uploader, duration, and publish date.

## Failure Modes

- Bilibili blocks unauthenticated access: report the fetch failure and keep the exact error text.
- `yt-dlp` is missing: stop and ask to install it.
- no subtitles and no ASR available: state that transcript extraction is blocked.
- `faster-whisper` is missing from the active Python environment: explain that ASR fallback cannot run yet.
- only `danmaku.xml` exists: explain that it is comment overlay data, not transcript text, then switch to ASR fallback.
- transcript quality is low: say whether the source was auto subtitles or ASR.

## Minimal Example

```bash
bash "$SKILL_DIR/scripts/fetch_bilibili_artifacts.sh" "https://www.bilibili.com/video/BV1xx411c7mD" /tmp/bili-job
python3 "$SKILL_DIR/scripts/normalize_transcript.py" /tmp/bili-job/example.zh-Hans.vtt --output /tmp/bili-job/transcript.txt
```

Then summarize `/tmp/bili-job/transcript.txt` instead of the raw subtitle file.
