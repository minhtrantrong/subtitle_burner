#!/usr/bin/env python3
"""Convert transcript text to Japanese-only SRT and burn it into a video.

This script combines the workflow from convert_to_srt.py and embed_subtitles.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from convert_to_srt import convert_file
from embed_subtitles import burn_subtitles, default_output_path


def default_srt_path(transcript_path: Path) -> Path:
    return transcript_path.with_suffix(".srt")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert transcript text to Japanese-only .srt and burn subtitles "
            "into a video"
        )
    )
    parser.add_argument("transcript", type=Path, help="Input transcript .txt path")
    parser.add_argument("video", type=Path, help="Input video path")
    parser.add_argument(
        "--srt-output",
        type=Path,
        help="Output .srt path (default: same name as transcript)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output video path (default: <video>_subtitled.<ext>)",
    )
    parser.add_argument(
        "--last-duration",
        type=float,
        default=6.0,
        help="Duration in seconds for the last subtitle cue (default: 6.0)",
    )
    parser.add_argument(
        "--same-start-duration",
        type=float,
        default=0.8,
        help=(
            "Duration in seconds when consecutive subtitle cues share the same "
            "timestamp (default: 0.8)"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output files if they already exist",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=18,
        help="Video quality for libx264 (lower is better quality, default: 18)",
    )
    parser.add_argument(
        "--preset",
        default="medium",
        choices=[
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ],
        help="Encoding speed/efficiency preset (default: medium)",
    )

    args = parser.parse_args()

    srt_output = args.srt_output or default_srt_path(args.transcript)
    video_output = args.output or default_output_path(args.video)

    if srt_output.exists() and not args.overwrite:
        raise FileExistsError(
            f"SRT output already exists: {srt_output}. Use --overwrite to replace it."
        )
    if video_output.exists() and not args.overwrite:
        raise FileExistsError(
            f"Video output already exists: {video_output}. Use --overwrite to replace it."
        )

    convert_file(
        input_path=args.transcript,
        output_path=srt_output,
        last_duration=args.last_duration,
        same_start_duration=args.same_start_duration,
    )
    print(f"Created subtitle: {srt_output}")

    burn_subtitles(
        input_video=args.video,
        input_srt=srt_output,
        output_video=video_output,
        overwrite=args.overwrite,
        crf=args.crf,
        preset=args.preset,
    )
    print(f"Created video: {video_output}")


if __name__ == "__main__":
    main()
