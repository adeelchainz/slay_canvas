# MediaBoard AI - Collaborative AI-Powered SaaS Platform

A modern, scalable multimedia workflow platform that integrates AI-powered transcription, analysis, and content generation with real-time collaboration features.

## 🎯 Features

- **Media Processing**: Upload and process video, audio, images, and documents
- **AI-Powered Analysis**: Automatic transcription, summarization, and insights using LangGraph
- **Content Generation**: Generate blogs, scripts, social media posts, and Q&A from media
- **Real-time Collaboration**: Multi-user workspaces with live updates
- **Google OAuth**: Secure authentication with Google Sign-In
- **Project Management**: Organize media files in collaborative projects
- **Canvas Workspace**: Drag-and-drop interface for visual organization

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **FastAPI**: High-performance REST API with async support
- **PostgreSQL**: Robust relational database for structured data
- **SQLAlchemy**: Modern ORM with async support
- **Alembic**: Database migrations

### AI Engine (LangGraph)
- **LangGraph**: Multi-agent AI workflows for media processing
- **OpenAI**: GPT-4 for content generation and analysis
- **Anthropic**: Claude for advanced reasoning tasks
- **Whisper**: Speech-to-text transcription

### Authentication & Security
- **Google OAuth 2.0**: Secure social authentication
- **JWT**: Token-based API authentication
- **bcrypt**: Password hashing
- **Role-based access control**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Google OAuth credentials

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Slay-Canvas
python setup_and_run.py
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/mediaboard_ai

# Security
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Frontend
FRONTEND_ORIGIN=http://localhost:3000
```
- Python 3.10+ (this project was tested with 3.12 in the workspace virtualenv)
- See `requirements.txt` for Python packages.

Environment
Create a `.env` file (copy `.env.example`) and set at minimum:

- DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mediaboard
- SECRET_KEY=replace-me-with-secure-random
- FRONTEND_ORIGIN=http://localhost:3000
- OPENAI_API_KEY=sk-... (if you want OpenAI fallback)
- LANGRAPH_API_KEY=... (optional if integrating Langraph SDK)

Install
```powershell
cd 'D:\Slay Canvas\backend'
& '.venv\Scripts\python.exe' -m pip install -r requirements.txt
```

Run (development)
```powershell
cd 'D:\Slay Canvas\backend'
& '.venv\Scripts\python.exe' main.py
# or
python main.py
```

API
- OpenAPI docs: http://127.0.0.1:8000/docs
- Main router mounted under `/api` (auth, users, media, ai)

Notes
- The engine prefers Langraph if installed; otherwise it will use OpenAI if `OPENAI_API_KEY` is provided. If you want Langraph integration, provide the correct SDK package name and API key.
- Alembic is scaffolded but migrations need configuration before use.

