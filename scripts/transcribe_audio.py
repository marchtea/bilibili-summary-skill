#!/usr/bin/env python3
import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file into a timestamped transcript with faster-whisper."
    )
    parser.add_argument("audio_path", help="Path to an audio file such as .mp3 or .m4a")
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the transcript text file",
    )
    parser.add_argument(
        "--model",
        default="tiny",
        help="Whisper model size or path (default: tiny)",
    )
    parser.add_argument(
        "--language",
        default="zh",
        help="Language code to guide transcription (default: zh)",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="faster-whisper compute type (default: int8)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Inference device, usually cpu or cuda (default: cpu)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: faster-whisper. Install it in the active Python environment before using ASR fallback."
        ) from exc

    audio_path = Path(args.audio_path)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
    )
    segments, info = model.transcribe(
        str(audio_path),
        language=args.language,
        vad_filter=True,
        beam_size=1,
    )

    lines = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        lines.append(f"[{segment.start:06.2f}-{segment.end:06.2f}] {text}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"language={info.language} prob={info.language_probability:.3f}")
    print(output_path)
    for line in lines[:20]:
        print(line)


if __name__ == "__main__":
    main()
