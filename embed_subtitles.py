#!/usr/bin/env python3
"""Burn SRT subtitles into a video and create a new output video.

This script uses ffmpeg and hardcodes subtitles into the video frames.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def build_subtitles_filter_path(srt_path: Path) -> str:
    """Convert path to ffmpeg subtitles filter path format.

    On Windows, ffmpeg filter paths need drive colon escaped, for example:
    D:/work/file.srt -> D\\:/work/file.srt
    """
    value = srt_path.resolve().as_posix()

    if re.match(r"^[A-Za-z]:", value):
        value = f"{value[0]}\\:{value[2:]}"

    # Escape single quotes for ffmpeg filter parser.
    value = value.replace("'", r"\'")
    return value


def burn_subtitles(
    input_video: Path,
    input_srt: Path,
    output_video: Path,
    overwrite: bool,
    crf: int,
    preset: str,
) -> None:
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError(
            "ffmpeg is not installed or not in PATH. Install ffmpeg and try again."
        )

    if not input_video.exists():
        raise FileNotFoundError(f"Input video not found: {input_video}")
    if not input_srt.exists():
        raise FileNotFoundError(f"Input subtitle not found: {input_srt}")

    filter_path = build_subtitles_filter_path(input_srt)
    vf_value = f"subtitles='{filter_path}'"

    command = [
        ffmpeg_bin,
        "-y" if overwrite else "-n",
        "-i",
        str(input_video),
        "-vf",
        vf_value,
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        str(crf),
        "-c:a",
        "copy",
        str(output_video),
    ]

    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {result.returncode}")


def default_output_path(input_video: Path) -> Path:
    return input_video.with_name(f"{input_video.stem}_subtitled{input_video.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Burn .srt subtitles into a video and create a new output file"
    )
    parser.add_argument("video", type=Path, help="Input video path")
    parser.add_argument("subtitle", type=Path, help="Input .srt subtitle path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output video path (default: <input>_subtitled.<ext>)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists",
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
    output = args.output or default_output_path(args.video)

    burn_subtitles(
        input_video=args.video,
        input_srt=args.subtitle,
        output_video=output,
        overwrite=args.overwrite,
        crf=args.crf,
        preset=args.preset,
    )

    print(f"Created: {output}")


if __name__ == "__main__":
    main()
