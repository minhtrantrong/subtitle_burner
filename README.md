# Transcript To Subtitle Video Tools

This project contains three Python scripts for turning a transcript into Japanese subtitles and embedding those subtitles into a video.

## Overview

- `convert_to_srt.py`: Convert a transcript `.txt` file into a Japanese-only `.srt` subtitle file.
- `embed_subtitles.py`: Burn an existing `.srt` subtitle file into a video and create a new video output.
- `main.py`: Run both steps in one command: transcript to `.srt`, then `.srt` into video.

## Requirements

- Python 3.9+.
- UTF-8 text files.
- `ffmpeg` installed and available in `PATH` for subtitle embedding.

## Input Transcript Format

The transcript converter expects blocks like this:

```text
[00:16] Speaker 2:
[Vietnamese] "..."
[Japanese] "..."
```

Rules:

- Time can be `MM:SS` or `HH:MM:SS`.
- Timestamp lines must match `[time] Speaker X:`.
- Only `[Japanese] "..."` lines are kept.
- Speaker labels and other languages are ignored.

## Script Guide

### `convert_to_srt.py`

Use this script when you already have a transcript text file and only need the subtitle file.

What it does:

- Reads timestamped transcript blocks.
- Removes speaker IDs.
- Keeps only Japanese lines.
- Creates a valid `.srt` file.

Basic usage:

```bash
python convert_to_srt.py input.txt
```

This creates `input.srt` in the same folder.

Specify output path:

```bash
python convert_to_srt.py input.txt -o output.srt
```

Control subtitle timing:

```bash
python convert_to_srt.py input.txt -o output.srt --last-duration 6.0 --same-start-duration 0.8
```

Arguments:

- `input`: Input transcript `.txt` file.
- `-o`, `--output`: Output `.srt` path.
- `--last-duration`: Final cue duration in seconds. Default: `6.0`.
- `--same-start-duration`: Duration used when consecutive cues share the same timestamp. Default: `0.8`.

Output behavior:

- Each Japanese line becomes one subtitle cue.
- Cue start time comes from the latest timestamp block.
- Cue end time usually matches the next cue start time.
- If two cues share the same start time, the script uses `--same-start-duration` to prevent overlap.

Example:

```bash
python convert_to_srt.py test.txt -o test.srt
```

### `embed_subtitles.py`

Use this script when you already have a video and a ready `.srt` subtitle file.

What it does:

- Uses `ffmpeg` to burn subtitles into the video.
- Re-encodes video with `libx264`.
- Copies audio without re-encoding.
- Creates a new output video.

Basic usage:

```bash
python embed_subtitles.py input.mp4 input.srt
```

This creates `input_subtitled.mp4`.

Specify output path:

```bash
python embed_subtitles.py input.mp4 input.srt -o output.mp4
```

Overwrite existing output:

```bash
python embed_subtitles.py input.mp4 input.srt -o output.mp4 --overwrite
```

Control video quality and speed:

```bash
python embed_subtitles.py input.mp4 input.srt --crf 18 --preset medium
```

Arguments:

- `video`: Input video path.
- `subtitle`: Input `.srt` path.
- `-o`, `--output`: Output video path.
- `--overwrite`: Replace existing output file.
- `--crf`: Video quality for `libx264`. Lower means better quality. Default: `18`.
- `--preset`: Encoding speed preset. Default: `medium`.

Example:

```bash
python embed_subtitles.py test.mp4 test.srt -o test_subtitled.mp4 --overwrite
```

### `main.py`

Use this script when you want one command for the full workflow.

What it does:

- Converts transcript `.txt` to Japanese-only `.srt`.
- Burns that `.srt` into the input video.
- Produces both subtitle and final video outputs.

Basic usage:

```bash
python main.py transcript.txt input.mp4
```

This creates:

- `transcript.srt`
- `input_subtitled.mp4`

Specify both output paths:

```bash
python main.py transcript.txt input.mp4 --srt-output output.srt -o output.mp4
```

Overwrite outputs:

```bash
python main.py transcript.txt input.mp4 --srt-output output.srt -o output.mp4 --overwrite
```

Control subtitle timing and video encoding:

```bash
python main.py transcript.txt input.mp4 --last-duration 6.0 --same-start-duration 0.8 --crf 18 --preset medium
```

Arguments:

- `transcript`: Input transcript `.txt` path.
- `video`: Input video path.
- `--srt-output`: Output `.srt` path.
- `-o`, `--output`: Output video path.
- `--last-duration`: Final cue duration in seconds. Default: `6.0`.
- `--same-start-duration`: Duration used for same-start subtitle cues. Default: `0.8`.
- `--overwrite`: Replace existing `.srt` and video outputs.
- `--crf`: Video quality for `libx264`. Default: `18`.
- `--preset`: Encoding speed preset. Default: `medium`.

Example:

```bash
python main.py test.txt test.mp4 --srt-output test.main.srt -o test.main.mp4 --overwrite
```

## Recommended Workflow

If you want to inspect the generated subtitle file before embedding it:

1. Run `convert_to_srt.py`.
2. Check the generated `.srt`.
3. Run `embed_subtitles.py`.

If you want the fastest end-to-end command:

1. Run `main.py`.

## Troubleshooting

### No subtitles created

Possible causes:

- No `[Japanese]` lines in the transcript.
- Japanese lines do not use `[Japanese] "..."` format.
- Timestamp lines do not match `[MM:SS] Speaker X:`.

### Video embedding fails

Possible causes:

- `ffmpeg` is not installed.
- `ffmpeg` is not in `PATH`.
- Video or subtitle file path is wrong.

Check `ffmpeg`:

```bash
ffmpeg -version
```

### Output file already exists

Use `--overwrite` if you want to replace an existing output file.

### Japanese text does not render correctly in video

This depends on fonts available to `ffmpeg` and `libass` on the machine.

## Limitations

- Long subtitle lines are not automatically wrapped.
- Nearby short subtitle lines are not merged.
- Subtitle styling is currently left to `ffmpeg` defaults.
- `embed_subtitles.py` creates hardcoded subtitles, not switchable subtitle tracks.

## Example Files In This Workspace

- `test.txt`: Example transcript.
- `test.srt`: Example generated subtitle file.
- `test.mp4`: Example input video.
- `test_subtitled.mp4`: Example output from `embed_subtitles.py`.
- `test.main.srt`: Example subtitle output from `main.py`.
- `test.main.mp4`: Example video output from `main.py`.
