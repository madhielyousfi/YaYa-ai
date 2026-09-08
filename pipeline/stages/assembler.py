from __future__ import annotations

import subprocess
from pathlib import Path

from models.project import ProjectState
from models.timeline import AudioTrack, Timeline, VideoTrack
from utils.ffmpeg import get_duration


def build_timeline(state: ProjectState) -> Timeline:
    if not state.script or not state.narration_path:
        raise ValueError("Script and narration required for timeline")

    narration_duration = get_duration(str(state.narration_path))
    scene_duration = narration_duration / len(state.script.scenes)

    video_tracks = []
    audio_tracks = []

    for i, scene in enumerate(state.script.scenes):
        start = i * scene_duration
        end = (i + 1) * scene_duration

        matching_assets = [
            a for a in state.media_assets
            if a.local_path and any(
                q in a.query
                for q in scene.search_queries
            )
        ]

        asset_path = ""
        if matching_assets:
            asset_path = matching_assets[0].local_path
        elif state.media_assets and state.media_assets[0].local_path:
            asset_path = state.media_assets[0].local_path

        if asset_path:
            video_tracks.append(
                VideoTrack(
                    scene_id=scene.id,
                    start=start,
                    end=end,
                    asset_path=asset_path,
                )
            )

    audio_tracks.append(
        AudioTrack(
            type="voice",
            start=0,
            file_path=str(state.narration_path),
            volume=1.0,
        )
    )

    if state.music_path and Path(state.music_path).exists():
        audio_tracks.append(
            AudioTrack(
                type="music",
                start=0,
                file_path=str(state.music_path),
                volume=0.15,
            )
        )

    timeline = Timeline(
        duration=narration_duration,
        video_tracks=video_tracks,
        audio_tracks=audio_tracks,
        subtitle_path=str(state.subtitle_path) if state.subtitle_path else None,
    )

    state.timeline = timeline
    state.save()
    return timeline


def render_video(state: ProjectState, output_path: str | None = None) -> str:
    if not state.timeline:
        raise ValueError("Timeline must be built before rendering")

    if output_path is None:
        output_path = str(state.output_dir / "final.mp4")

    timeline = state.timeline

    if not timeline.video_tracks:
        raise ValueError("No video tracks in timeline")

    processed_clips = []
    for track in timeline.video_tracks:
        clip_path = str(state.output_dir / "media" / f"clip_{track.scene_id}.mp4")
        _prepare_clip(
            track.asset_path,
            clip_path,
            track.end - track.start,
        )
        processed_clips.append(clip_path)

    concat_path = str(state.output_dir / "media" / "concat.mp4")
    _concat_clips(processed_clips, concat_path)

    voice_path = None
    for audio in timeline.audio_tracks:
        if audio.type == "voice":
            voice_path = audio.file_path
            break

    music_path = None
    for audio in timeline.audio_tracks:
        if audio.type == "music":
            music_path = audio.file_path
            break

    if voice_path and music_path:
        _mix_audio_with_ducking(concat_path, voice_path, music_path, output_path)
    elif voice_path:
        _add_audio(concat_path, voice_path, output_path)
    else:
        _copy_file(concat_path, output_path)

    if timeline.subtitle_path and Path(timeline.subtitle_path).exists():
        subtitled_path = str(state.output_dir / "final_subtitled.mp4")
        _burn_subtitles(output_path, timeline.subtitle_path, subtitled_path)
        Path(subtitled_path).rename(output_path)

    state.video_path = Path(output_path)
    state.save()
    return output_path


def _prepare_clip(input_path: str, output_path: str, target_duration: float) -> None:
    filter_graph = (
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
        "setsar=1"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-t", str(target_duration),
            "-vf", filter_graph,
            "-c:v", "libx264",
            "-preset", "fast",
            "-an",
            "-r", "30",
            output_path,
        ],
        capture_output=True,
        check=True,
    )


def _concat_clips(input_paths: list[str], output_path: str) -> None:
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


def _add_audio(video_path: str, audio_path: str, output_path: str) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path,
        ],
        capture_output=True,
        check=True,
    )


def _mix_audio_with_ducking(
    video_path: str,
    voice_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 0.15,
    attack: float = 0.5,
    release: float = 1.0,
) -> None:
    filter_graph = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]aloop=loop=-1:size=2e+09,volume={music_volume},"
        f"afade=t=in:d={attack},afade=t=out:st=99999:d={release}[music];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", voice_path,
            "-i", music_path,
            "-filter_complex", filter_graph,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path,
        ],
        capture_output=True,
        check=True,
    )


def _burn_subtitles(video_path: str, subtitle_path: str, output_path: str) -> None:
    escaped_path = subtitle_path.replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", f"ass='{escaped_path}'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "copy",
            output_path,
        ],
        capture_output=True,
        check=True,
    )


def _copy_file(src: str, dst: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-c", "copy", dst],
        capture_output=True,
        check=True,
    )
