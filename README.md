# MediaBoard AI - Backend

FastAPI backend scaffold for MediaBoard AI. This repo contains the API, database models, and the AI engine adapter (Langraph/OpenAI fallback).

Structure
- `app/` - main API code (MVC style)
- `engine/` - AI engine integrations (Langraph wrapper with OpenAI fallback)
- `alembic/` - migrations (placeholder)

Requirements
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

