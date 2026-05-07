"""Generate 9:16 waveform animation videos from audio files using FFmpeg."""

import subprocess
import json
import re
from pathlib import Path

from config import (
    OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT,
    VIDEO_DURATION_MIN, VIDEO_DURATION_MAX,
    WAVEFORM_COLOR, BG_COLOR, TEXT_COLOR,
)


def get_audio_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(audio_path),
        ],
        capture_output=True, text=True,
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def _sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_").lower()


def generate_reel(
    audio_path: str | Path,
    track_name: str | None = None,
    color: str = WAVEFORM_COLOR,
    bg_color: str = BG_COLOR,
) -> Path:
    """
    Generate a vertical waveform video from an audio file.

    Returns the path to the output .mp4 file.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if track_name is None:
        track_name = audio_path.stem

    slug = _sanitize_filename(track_name)
    output_path = OUTPUT_DIR / f"{slug}.mp4"

    duration = get_audio_duration(audio_path)
    clip_duration = min(duration, VIDEO_DURATION_MAX)
    if duration > VIDEO_DURATION_MAX:
        # Start from 10% into the track to skip intros
        start_time = min(duration * 0.1, duration - clip_duration)
    else:
        start_time = 0

    # Ensure minimum duration
    if clip_duration < VIDEO_DURATION_MIN and duration >= VIDEO_DURATION_MIN:
        clip_duration = VIDEO_DURATION_MIN

    # Display name: clean up the track name for overlay
    display_name = track_name.replace("_", " ").replace("-", " ").strip()

    # FFmpeg filter chain:
    # 1. showwaves: animated waveform from audio
    # 2. pad: center it in the 1080x1920 frame
    # 3. drawtext: overlay track name
    waveform_h = 400
    filter_complex = (
        f"[0:a]showwaves=s={VIDEO_WIDTH}x{waveform_h}"
        f":mode=cline:rate=30:colors={color}"
        f":scale=sqrt[wave];"
        f"color=c={bg_color}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:r=30[bg];"
        f"[bg][wave]overlay=(W-w)/2:(H-h)/2[vid];"
        f"[vid]drawtext=text='{display_name}'"
        f":fontsize=48:fontcolor={TEXT_COLOR}"
        f":x=(w-text_w)/2:y=h-200"
        f":fontfile=/Windows/Fonts/segoeui.ttf[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-t", str(clip_duration),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[out]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(clip_duration),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr[-1000:]}")

    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python visuals.py <audio_file> [track_name]")
        sys.exit(1)
    audio = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    out = generate_reel(audio, name)
    print(f"Generated: {out}")
