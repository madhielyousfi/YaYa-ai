from __future__ import annotations

from models.project import ProjectState
from providers.tts.base import TTSProvider


async def generate_narration(
    state: ProjectState,
    tts: TTSProvider,
) -> ProjectState:
    if not state.script:
        raise ValueError("Script must be generated before TTS")

    narration_path = state.output_dir / "narration.mp3"
    narration_path.parent.mkdir(parents=True, exist_ok=True)

    full_text = state.script.full_narration

    await tts.generate(full_text, str(narration_path))

    state.narration_path = narration_path
    state.save()
    return state
