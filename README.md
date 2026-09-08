# 🎬 YaYa AI - YouTube Shorts Generator

> Turn any idea into a publish-ready YouTube Short using AI

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-9.0-purple.svg)](https://ffmpeg.org)

---

## ✨ Features

- 🤖 **AI Script Generation** - Ollama-powered local LLM
- 🎥 **Stock Video Search** - Pexels & Pixabay integration
- 🎤 **Text-to-Speech** - Edge TTS with 47+ voices
- 🎵 **Background Music** - Auto-selected with volume ducking
- 📝 **Auto Subtitles** - Whisper-powered word-level timing
- 🖼️ **Thumbnail Generator** - Auto-generated thumbnails
- 🎬 **HD Video Export** - 1080x1920 MP4 format
- 🌐 **Web Interface** - Modern Next.js frontend
- 💻 **CLI Tool** - Command line for power users

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg
- Ollama (for AI scripts)

### One Command Setup

```bash
# Clone the repo
git clone https://github.com/madhielyousfi/YaYa-ai.git
cd YaYa-ai

# Run the smart launcher (installs everything)
./start.sh
```

Then open: **http://localhost:3000**

---

## 📦 Manual Installation

### 1. Backend (Python)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install typer pydantic pydantic-settings httpx edge-tts pillow python-dotenv fastapi uvicorn websockets
```

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
```

### 3. API Keys (Free)

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Get free API keys:
- **Pexels**: https://www.pexels.com/api/
- **Pixabay**: https://pixabay.com/api/docs/

### 4. Ollama (AI Engine)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull qwen2.5:3b
```

---

## 🎯 Usage

### Web Interface

```bash
./start.sh
# Open http://localhost:3000
```

### Command Line

```bash
source .venv/bin/activate

# Generate a video
python cli.py run --topic "5 facts about Morocco" --duration 60

# List available voices
python cli.py voices --language en

# Check project status
python cli.py status output/<project-id>
```

### API

```bash
# Start API server
uvicorn api.main:app --reload --port 8000

# Create a project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"topic": "5 facts about Morocco", "duration": 60}'
```

---

## 🏗️ Architecture

```
User Input (Topic)
       │
       ▼
┌─────────────────┐
│  Script Agent   │ ← Ollama (Local LLM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Media Search   │ ←→  │  TTS Generator  │
│  (Pexels API)   │     │  (Edge TTS)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Video Clips    │     │  Subtitles      │
│  (FFmpeg)       │     │  (Whisper)      │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
              ┌─────────────┐
              │   Timeline  │
              │   Engine    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   FFmpeg    │
              │   Render    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  1080x1920  │
              │    MP4      │
              └─────────────┘
```

---

## 📁 Project Structure

```
YaYa-ai/
├── start.sh                 # Smart launcher script
├── stop.sh                  # Stop all servers
├── cli.py                   # Command line interface
├── api/
│   └── main.py              # FastAPI backend
├── frontend/
│   └── src/app/page.tsx     # Next.js frontend
├── config/
│   └── settings.py          # Pydantic settings
├── models/                  # Data models
│   ├── script.py
│   ├── media.py
│   ├── timeline.py
│   └── project.py
├── providers/               # AI services
│   ├── llm/                 # Ollama
│   ├── tts/                 # Edge TTS
│   ├── media/               # Pexels, Pixabay
│   └── music/               # Background music
├── pipeline/                # Video generation
│   ├── orchestrator.py
│   └── stages/
│       ├── script.py
│       ├── media.py
│       ├── tts.py
│       ├── subtitles.py
│       ├── assembler.py
│       └── thumbnail.py
└── utils/                   # Helpers
    ├── ffmpeg.py
    ├── files.py
    └── cache.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Ollama + Qwen2.5 |
| TTS | Edge TTS (Free) |
| STT | OpenAI Whisper |
| Media | Pexels + Pixabay APIs |
| Video | FFmpeg |
| Backend | FastAPI + Python |
| Frontend | Next.js + Tailwind CSS |
| Database | File-based (JSON) |

---

## 💰 Cost Per Video

| Service | Cost |
|---------|------|
| Ollama LLM | Free (local) |
| Edge TTS | Free |
| Whisper | Free (local) |
| Pexels/Pixabay | Free (API) |
| FFmpeg | Free |
| **Total** | **$0.00** |

---

## 📝 License

MIT License - feel free to use and modify.

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📧 Contact

- GitHub: [@madhielyousfi](https://github.com/madhielyousfi)

---

## ⭐ Star Us

If you find this project useful, please give it a star on GitHub!
