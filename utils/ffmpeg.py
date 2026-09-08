from __future__ import annotations

import json
import subprocess
from pathlib import Path


def probe(file_path: str) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def get_duration(file_path: str) -> float:
    info = probe(file_path)
    if "format" in info:
        return float(info["format"].get("duration", 0))
    return 0.0


def get_video_info(file_path: str) -> dict:
    info = probe(file_path)
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            return {
                "width": stream.get("width", 0),
                "height": stream.get("height", 0),
                "fps": eval(stream.get("r_frame_rate", "30/1")),
                "codec": stream.get("codec_name", ""),
            }
    return {}


def scale_to_vertical(input_path: str, output_path: str, width: int = 1080, height: int = 1920) -> str:
    filter_graph = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"setsar=1"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", filter_graph,
            "-c:v", "libx264",
            "-preset", "fast",
            "-an",
            output_path,
        ],
        capture_output=True,
        check=True,
    )
    return output_path


def extract_audio(input_path: str, output_path: str) -> str:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_path,
        ],
        capture_output=True,
        check=True,
    )
    return output_path


def concat_videos(input_paths: list[str], output_path: str) -> str:
    list_file = Path(output_path).parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for path in input_paths:
            f.write(f"file '{path}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            output_path,
        ],
        capture_output=True,
        check=True,
    )
    list_file.unlink(missing_ok=True)
    return output_path
