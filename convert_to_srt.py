#!/usr/bin/env python3
"""Convert meeting transcript text files to Japanese-only SRT subtitles.

Expected input pattern example:
[00:16] Speaker 2:
[Japanese] "..."
[Vietnamese] "..."

The script keeps only [Japanese] lines and ignores speaker IDs and other languages.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


TIME_MARK_RE = re.compile(r"^\[(\d{2}:\d{2}(?::\d{2})?)\]\s*Speaker\s*\d+\s*:\s*$")
JAPANESE_LINE_RE = re.compile(r'^\[Japanese\]\s*"(.*)"\s*$')


@dataclass
class Cue:
    start_seconds: float
    text: str


def parse_time_to_seconds(raw: str) -> float:
    parts = [int(p) for p in raw.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"Invalid time format: {raw}")


def format_srt_time(total_seconds: float) -> str:
    if total_seconds < 0:
        total_seconds = 0

    millis = int(round(total_seconds * 1000))
    hours = millis // 3_600_000
    millis %= 3_600_000
    minutes = millis // 60_000
    millis %= 60_000
    seconds = millis // 1000
    millis %= 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def extract_japanese_cues(content: str) -> list[Cue]:
    cues: list[Cue] = []
    current_start: float | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        time_match = TIME_MARK_RE.match(line)
        if time_match:
            current_start = parse_time_to_seconds(time_match.group(1))
            continue

        jp_match = JAPANESE_LINE_RE.match(line)
        if jp_match and current_start is not None:
            text = jp_match.group(1).strip()
            if text:
                cues.append(Cue(start_seconds=current_start, text=text))

    return cues


def build_srt(cues: list[Cue], last_duration: float, same_start_duration: float) -> str:
    if not cues:
        return ""

    lines: list[str] = []
    previous_end = 0.0

    for i, cue in enumerate(cues):
        start = max(cue.start_seconds, previous_end)

        if i < len(cues) - 1:
            next_start = cues[i + 1].start_seconds
            if next_start > start:
                end = next_start
            else:
                end = start + same_start_duration
        else:
            end = start + last_duration

        previous_end = end

        lines.append(str(i + 1))
        lines.append(f"{format_srt_time(start)} --> {format_srt_time(end)}")
        lines.append(cue.text)
        lines.append("")

    return "\n".join(lines)


def convert_file(input_path: Path, output_path: Path, last_duration: float, same_start_duration: float) -> None:
    content = input_path.read_text(encoding="utf-8")
    cues = extract_japanese_cues(content)
    srt = build_srt(cues, last_duration=last_duration, same_start_duration=same_start_duration)
    output_path.write_text(srt, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert transcript text to Japanese-only .srt subtitles"
    )
    parser.add_argument("input", type=Path, help="Path to transcript .txt file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .srt file path (default: same name as input)",
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
            "Duration in seconds when two consecutive cues have the same start "
            "timestamp (default: 0.8)"
        ),
    )

    args = parser.parse_args()
    output = args.output or args.input.with_suffix(".srt")

    convert_file(
        input_path=args.input,
        output_path=output,
        last_duration=args.last_duration,
        same_start_duration=args.same_start_duration,
    )

    print(f"Created: {output}")


if __name__ == "__main__":
    main()
