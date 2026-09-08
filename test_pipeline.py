from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from models.script import Script, Scene
from models.project import ProjectState, ProjectStatus
from models.timeline import Timeline, VideoTrack, AudioTrack
from pipeline.stages import assembler, subtitles, thumbnail
from pipeline.orchestrator import Orchestrator


def test_full_pipeline_mock():
    """Test the full pipeline with mock data (no Ollama/API calls)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        print("[1/5] Creating mock script...")
        script = Script(
            title="5 Facts About Morocco",
            hook="You probably don't know these five facts about Morocco.",
            duration=30,
            scenes=[
                Scene(
                    id=1, duration=6,
                    narration="Morocco has a city called Chefchaouen that is entirely blue.",
                    visual_prompt="Blue buildings in Chefchaouen Morocco",
                    search_queries=["Chefchaouen blue city Morocco"],
                ),
                Scene(
                    id=2, duration=6,
                    narration="The Sahara Desert covers most of southern Morocco.",
                    visual_prompt="Sahara desert dunes",
                    search_queries=["Sahara desert Morocco"],
                ),
                Scene(
                    id=3, duration=6,
                    narration="Moroccan tea ceremony is an important cultural tradition.",
                    visual_prompt="Moroccan tea ceremony",
                    search_queries=["Moroccan tea ceremony traditional"],
                ),
                Scene(
                    id=4, duration=6,
                    narration="The medina of Fez is the world's largest car-free zone.",
                    visual_prompt="Fez medina Morocco streets",
                    search_queries=["Fez medina Morocco"],
                ),
                Scene(
                    id=5, duration=6,
                    narration="Morocco produces over 70% of the world's supply of argan oil.",
                    visual_prompt="Argan oil production Morocco",
                    search_queries=["argan oil Morocco production"],
                ),
            ],
        )

        print("[2/5] Creating project state...")
        state = ProjectState(
            id="test123",
            topic="5 facts about Morocco",
            output_dir=output_dir,
            script=script,
            status=ProjectStatus.SCRIPTING,
        )
        state.save()
        print(f"      Project: {state.id}")

        print("[3/5] Generating narration (Edge TTS)...")
        from providers.tts.edge_tts import EdgeTTSProvider
        tts_provider = EdgeTTSProvider()

        narration_path = output_dir / "narration.mp3"
        asyncio.run(tts_provider.generate(script.full_narration, str(narration_path)))
        state.narration_path = narration_path
        state.status = ProjectStatus.AUDIO_GENERATION
        state.save()
        print(f"      Narration: {narration_path} ({narration_path.stat().st_size} bytes)")

        print("[4/5] Generating subtitles (Whisper)...")
        state.status = ProjectStatus.SUBTITLES
        state.save()
        state = subtitles.generate_subtitles(state, model_name="tiny")
        print(f"      Subtitles: {state.subtitle_path}")

        print("[5/5] Building thumbnail...")
        state.status = ProjectStatus.THUMBNAIL
        state.save()
        thumb_path = thumbnail.generate_thumbnail(state)
        print(f"      Thumbnail: {thumb_path}")

        print("\nPipeline test completed successfully!")
        print(f"  Narration: {state.narration_path}")
        print(f"  Subtitles: {state.subtitle_path}")
        print(f"  Thumbnail: {state.thumbnail_path}")
        return True


if __name__ == "__main__":
    test_full_pipeline_mock()
