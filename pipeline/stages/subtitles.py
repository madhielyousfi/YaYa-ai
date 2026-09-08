from __future__ import annotations

import subprocess
from pathlib import Path

from models.project import ProjectState


def generate_subtitles(
    state: ProjectState,
    model_name: str = "base",
) -> ProjectState:
    if not state.narration_path:
        raise ValueError("Narration must be generated before subtitles")

    import whisper

    model = whisper.load_model(model_name)
    result = model.transcribe(
        str(state.narration_path),
        word_timestamps=True,
    )

    srt_path = state.output_dir / "subtitles.srt"
    ass_path = state.output_dir / "subtitles.ass"

    segments = result["segments"]

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp_srt(seg["start"])
            end = format_timestamp_srt(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    write_ass(segments, ass_path, state)

    state.subtitle_path = ass_path
    state.save()
    return state


def format_timestamp_srt(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_timestamp_ass(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(segments: list[dict], output_path: Path, state: ProjectState) -> None:
    width = 1080
    height = 1920
    font_size = 56
    font_name = "Arial"

    header = f"""[Script Info]
Title: Yoyo Shorts Subtitles
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,10,10,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]
    for seg in segments:
        start = format_timestamp_ass(seg["start"])
        end = format_timestamp_ass(seg["end"])
        text = seg["text"].strip().replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    output_path.write_text("\n".join(lines), encoding="utf-8")
