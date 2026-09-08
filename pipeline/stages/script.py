from __future__ import annotations

import json
import re

from models.project import ProjectState
from providers.llm.base import LLMProvider
from models.script import Script, Scene


SCRIPT_SYSTEM = """You are a YouTube Shorts script writer.
Output ONLY valid JSON, no markdown, no code blocks.
The JSON must match this exact structure:
{
  "title": "string",
  "hook": "string - attention grabbing first sentence",
  "duration": 60,
  "scenes": [
    {
      "id": 1,
      "duration": 5.0,
      "narration": "string - what the voice says",
      "visual_prompt": "string - description of what to show",
      "search_queries": ["query1", "query2"]
    }
  ]
}
Rules:
- Each scene narration should be 1-3 sentences
- Total duration must match the requested duration
- search_queries should be specific stock video/image search terms
- visual_prompt describes what the viewer should see"""


def generate_script(
    state: ProjectState,
    llm: LLMProvider,
    duration: int = 60,
    language: str = "en",
) -> ProjectState:
    prompt = f"""Write a YouTube Shorts script about: {state.topic}

Requirements:
- Duration: {duration} seconds
- Language: {language}
- Style: engaging, informative
- Start with a strong hook
- Break into {max(3, duration // 10)} scenes

Output ONLY the JSON."""

    raw = llm.generate(prompt, system=SCRIPT_SYSTEM)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Failed to parse script JSON from LLM output: {raw[:200]}")

    data = json.loads(match.group())
    script = Script.model_validate(data)
    state.script = script
    state.save()
    return state
