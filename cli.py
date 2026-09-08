from __future__ import annotations

import asyncio
from pathlib import Path

import typer

from config.settings import settings

app = typer.Typer(
    name="yoyo",
    help="AI-powered YouTube Shorts generator",
)


@app.command()
def run(
    topic: str = typer.Argument(..., help="Topic or idea for the video"),
    duration: int = typer.Option(60, "--duration", "-d", help="Video duration in seconds"),
    language: str = typer.Option("en", "--language", "-l", help="Language code"),
    mood: str = typer.Option("cinematic", "--mood", "-m", help="Background music mood"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
) -> None:
    from pipeline.orchestrator import Orchestrator

    orch = Orchestrator()
    state = orch.run(topic, duration, language, mood)

    typer.echo(f"\n{typer.style('SUCCESS', fg='green')}: Video created at {state.output_dir}")


@app.command()
def voices(
    language: str = typer.Option("en", "--language", "-l", help="Language filter"),
) -> None:
    from providers.tts.edge_tts import EdgeTTSProvider

    tts = EdgeTTSProvider()
    voices = asyncio.run(tts.list_voice_names(language))

    typer.echo(f"Available voices ({language}):\n")
    for voice in voices:
        typer.echo(f"  {voice}")


@app.command()
def status(
    project_dir: Path = typer.Argument(..., help="Project directory"),
) -> None:
    from models.project import ProjectState

    state = ProjectState.load(project_dir)
    typer.echo(f"Project: {state.id}")
    typer.echo(f"Topic: {state.topic}")
    typer.echo(f"Status: {state.status.value}")
    if state.video_path:
        typer.echo(f"Video: {state.video_path}")


@app.command()
def resume(
    project_dir: Path = typer.Argument(..., help="Project directory to resume"),
) -> None:
    from models.project import ProjectState
    from pipeline.orchestrator import Orchestrator

    state = ProjectState.load(project_dir)
    typer.echo(f"Resuming project {state.id} from status: {state.status.value}")

    orch = Orchestrator()
    typer.echo("Resume not yet implemented - please run from start")


if __name__ == "__main__":
    app()
