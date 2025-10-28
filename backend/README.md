# Backend (FastAPI)

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

## Environment

- OPENAI_API_KEY (optional): Enables LLM rationale; without it, a heuristic is used.
- OPENAI_MODEL (optional): Defaults to gpt-4o-mini.
- CORS_ORIGIN (optional): Defaults to http://localhost:3000.

## Endpoints

- POST /api/eligibility/check → assess eligibility and generate rationale.
- GET /api/health → health check.

