const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Project {
  id: string;
  topic: string;
  status: string;
  video_url?: string;
  thumbnail_url?: string;
}

export interface GenerateRequest {
  topic: string;
  duration?: number;
  language?: string;
  mood?: string;
}

export async function createProject(request: GenerateRequest): Promise<Project> {
  const res = await fetch(`${API_BASE}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error('Failed to create project');
  return res.json();
}

export async function generateVideo(projectId: string, request: GenerateRequest): Promise<void> {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error('Failed to start generation');
}

export async function getProject(projectId: string): Promise<Project> {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}`);
  if (!res.ok) throw new Error('Project not found');
  return res.json();
}

export async function listProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/api/projects`);
  if (!res.ok) throw new Error('Failed to list projects');
  const data = await res.json();
  return data.projects || [];
}

export function getVideoUrl(projectId: string): string {
  return `${API_BASE}/api/projects/${projectId}/video`;
}

export function getThumbnailUrl(projectId: string): string {
  return `${API_BASE}/api/projects/${projectId}/thumbnail`;
}

export function connectWebSocket(projectId: string): WebSocket {
  const wsUrl = API_BASE.replace('http', 'ws') + `/ws/${projectId}`;
  return new WebSocket(wsUrl);
}
