from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config.settings import settings
from models.project import ProjectState, ProjectStatus
from pipeline.orchestrator import Orchestrator

app = FastAPI(
    title="Yoyo Shorts API",
    description="AI-powered YouTube Shorts generator",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()
active_connections: dict[str, WebSocket] = {}


class GenerateRequest(BaseModel):
    topic: str
    duration: int = 60
    language: str = "en"
    mood: str = "cinematic"


class ProjectResponse(BaseModel):
    id: str
    topic: str
    status: str
    video_url: str | None = None
    thumbnail_url: str | None = None


@app.get("/")
def root():
    return {"message": "Yoyo Shorts API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/projects", response_model=ProjectResponse)
def create_project(request: GenerateRequest):
    state = orchestrator.create_project(request.topic)
    return ProjectResponse(
        id=state.id,
        topic=state.topic,
        status=state.status.value,
    )


@app.post("/api/projects/{project_id}/generate")
async def generate_video(project_id: str, request: GenerateRequest):
    output_dir = settings.paths.output_dir / project_id
    if not output_dir.exists():
        return JSONResponse(status_code=404, content={"error": "Project not found"})

    async def run_pipeline():
        try:
            state = ProjectState.load(output_dir)
            state.topic = request.topic
            state = orchestrator.run(request.topic, request.duration, request.language, request.mood)
            if project_id in active_connections:
                ws = active_connections[project_id]
                try:
                    await ws.send_json({"status": "completed", "video": str(state.video_path)})
                except Exception:
                    pass
        except Exception as e:
            if project_id in active_connections:
                ws = active_connections[project_id]
                try:
                    await ws.send_json({"status": "failed", "error": str(e)})
                except Exception:
                    pass

    asyncio.create_task(run_pipeline())
    return {"status": "started", "project_id": project_id}


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    output_dir = settings.paths.output_dir / project_id
    if not output_dir.exists():
        return JSONResponse(status_code=404, content={"error": "Project not found"})

    state = ProjectState.load(output_dir)
    video_url = f"/api/projects/{project_id}/video" if state.video_path else None
    thumbnail_url = f"/api/projects/{project_id}/thumbnail" if state.thumbnail_path else None

    return ProjectResponse(
        id=state.id,
        topic=state.topic,
        status=state.status.value,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
    )


@app.get("/api/projects")
def list_projects():
    output_dir = settings.paths.output_dir
    projects = []
    if output_dir.exists():
        for project_dir in output_dir.iterdir():
            if project_dir.is_dir():
                state_file = project_dir / "project_state.json"
                if state_file.exists():
                    state = ProjectState.load(project_dir)
                    projects.append({
                        "id": state.id,
                        "topic": state.topic,
                        "status": state.status.value,
                    })
    return {"projects": projects}


@app.get("/api/projects/{project_id}/video")
def get_video(project_id: str):
    output_dir = settings.paths.output_dir / project_id
    state = ProjectState.load(output_dir)
    if not state.video_path or not Path(state.video_path).exists():
        return JSONResponse(status_code=404, content={"error": "Video not found"})
    return FileResponse(
        state.video_path,
        media_type="video/mp4",
        filename=f"{project_id}.mp4",
    )


@app.get("/api/projects/{project_id}/thumbnail")
def get_thumbnail(project_id: str):
    output_dir = settings.paths.output_dir / project_id
    state = ProjectState.load(output_dir)
    if not state.thumbnail_path or not Path(state.thumbnail_path).exists():
        return JSONResponse(status_code=404, content={"error": "Thumbnail not found"})
    return FileResponse(
        state.thumbnail_path,
        media_type="image/jpeg",
    )


@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()
    active_connections[project_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"status": "pong"})
    except WebSocketDisconnect:
        active_connections.pop(project_id, None)
