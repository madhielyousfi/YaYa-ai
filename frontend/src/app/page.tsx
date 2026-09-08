'use client';

import { useState } from 'react';
import { createProject, generateVideo, Project } from '@/lib/api';

const MOODS = [
  { value: 'cinematic', label: 'Cinematic', emoji: '🎬' },
  { value: 'upbeat', label: 'Upbeat', emoji: '🎵' },
  { value: 'chill', label: 'Chill', emoji: '😌' },
  { value: 'dramatic', label: 'Dramatic', emoji: '🎭' },
  { value: 'horror', label: 'Horror', emoji: '👻' },
  { value: 'motivational', label: 'Motivational', emoji: '💪' },
];

const DURATIONS = [
  { value: 30, label: '30s' },
  { value: 45, label: '45s' },
  { value: 60, label: '60s' },
  { value: 90, label: '90s' },
];

const SUGGESTIONS = [
  '5 facts about Morocco',
  'How black holes work',
  'Top 10 programming languages',
  'History of the internet',
  'Benefits of meditation',
  'How AI is changing the world',
];

export default function Home() {
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(60);
  const [mood, setMood] = useState('cinematic');
  const [isGenerating, setIsGenerating] = useState(false);
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const newProject = await createProject({
        topic: topic.trim(),
        duration,
        mood,
      });
      setProject(newProject);

      await generateVideo(newProject.id, {
        topic: topic.trim(),
        duration,
        mood,
      });

      pollProjectStatus(newProject.id);
    } catch (err) {
      setError('Failed to start generation. Is the API running?');
      setIsGenerating(false);
    }
  };

  const pollProjectStatus = async (projectId: string) => {
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`/api/projects/${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setProject(data);
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(poll);
            setIsGenerating(false);
          }
        }
      } catch {}
    }, 3000);
  };

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 gradient-bg rounded-xl flex items-center justify-center font-bold text-lg">
              Y
            </div>
            <span className="text-xl font-semibold">Yoyo Shorts</span>
          </div>
          <span className="text-sm text-gray-400">AI Video Generator</span>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Hero */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            Create AI Shorts
          </h1>
          <p className="text-xl text-gray-400">
            Turn any idea into a publish-ready YouTube Short
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="card-gradient rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-sm">1</span>
              Enter Your Topic
            </h2>

            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What should the video be about?"
              className="w-full h-32 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors resize-none"
            />

            {/* Suggestions */}
            <div className="mt-3 flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => setTopic(s)}
                  className="text-xs px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-full text-gray-400 hover:text-white transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Duration */}
            <h2 className="text-lg font-semibold mt-6 mb-3 flex items-center gap-2">
              <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-sm">2</span>
              Duration
            </h2>
            <div className="flex gap-2">
              {DURATIONS.map((d) => (
                <button
                  key={d.value}
                  onClick={() => setDuration(d.value)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    duration === d.value
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>

            {/* Mood */}
            <h2 className="text-lg font-semibold mt-6 mb-3 flex items-center gap-2">
              <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-sm">3</span>
              Music Mood
            </h2>
            <div className="grid grid-cols-3 gap-2">
              {MOODS.map((m) => (
                <button
                  key={m.value}
                  onClick={() => setMood(m.value)}
                  className={`px-4 py-3 rounded-xl font-medium transition-all flex flex-col items-center gap-1 ${
                    mood === m.value
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  <span className="text-xl">{m.emoji}</span>
                  <span className="text-sm">{m.label}</span>
                </button>
              ))}
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !topic.trim()}
              className="w-full mt-8 py-4 gradient-bg rounded-xl font-semibold text-lg transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Generate Video
                </>
              )}
            </button>

            {error && (
              <p className="mt-3 text-red-400 text-sm text-center">{error}</p>
            )}
          </div>

          {/* Preview Panel */}
          <div className="card-gradient rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-4">Preview</h2>

            {!project && !isGenerating && (
              <div className="h-96 border-2 border-dashed border-white/10 rounded-xl flex flex-col items-center justify-center text-gray-500">
                <svg className="w-16 h-16 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <p>Your video will appear here</p>
              </div>
            )}

            {isGenerating && (
              <div className="h-96 border border-white/10 rounded-xl flex flex-col items-center justify-center">
                <div className="space-y-4 w-full max-w-xs">
                  {['Script', 'Media', 'Voice', 'Music', 'Subtitles', 'Rendering', 'Thumbnail'].map((step, i) => (
                    <div key={step} className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                        i < 4 ? 'bg-green-500' : i === 4 ? 'bg-blue-500 animate-pulse' : 'bg-white/10'
                      }`}>
                        {i < 4 ? '✓' : i + 1}
                      </div>
                      <span className={`text-sm ${i <= 4 ? 'text-white' : 'text-gray-500'}`}>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {project && project.status === 'completed' && (
              <div className="space-y-4">
                <div className="aspect-[9/16] max-h-96 mx-auto bg-black rounded-xl overflow-hidden">
                  <video
                    src={project.video_url}
                    controls
                    className="w-full h-full object-contain"
                  />
                </div>
                <div className="flex gap-2">
                  <a
                    href={project.video_url}
                    download
                    className="flex-1 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-center font-medium transition-colors"
                  >
                    Download MP4
                  </a>
                  {project.thumbnail_url && (
                    <a
                      href={project.thumbnail_url}
                      download
                      className="py-2 px-4 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                    >
                      Thumbnail
                    </a>
                  )}
                </div>
              </div>
            )}

            {project && project.status === 'failed' && (
              <div className="h-96 border border-red-500/30 rounded-xl flex flex-col items-center justify-center text-red-400">
                <svg className="w-16 h-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <p>Generation failed</p>
                <p className="text-sm mt-2">Check API logs for details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
