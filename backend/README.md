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
- OPENAI_MODEL (optional): Defaults to gpt-4o-mini. If a custom model fails, server will retry with gpt-4o-mini before falling back to heuristic.
- CORS_ORIGIN (optional): Defaults to http://localhost:3000.
 - OCR: Implemented with EasyOCR only. We do not use OpenAI for OCR in this project. OpenAI is used for issue classification, eligibility reasoning, and the final report.
- ELIGIBILITY_DEBUG_ERRORS (optional): Set to 1/true to include OpenAI error info in the eligibility reason for troubleshooting.

### Model name note
- Use `OPENAI_MODEL=gpt-4o-mini`. Names like `chatgpt-4o-mini` are invalid and may trigger fallback.

### Troubleshooting
- Symptom: eligibility.model shows `heuristic` and reason contains `OpenAI client/init error: Client.__init__() got an unexpected keyword argument 'proxies'`.
	- Cause: `httpx` >= 0.28 removed the `proxies` parameter; `openai` 1.51.0 still passes it.
	- Fix: pin `httpx==0.27.2` (already in `requirements.txt`), then reinstall deps and restart the server.
	- Verify:
		1) `python -c "import httpx; print(httpx.__version__)"` → `0.27.2`
		2) Call `POST /api/eligibility/check` and confirm `model` is `gpt-4o-mini`.

## Endpoints

- POST /api/eligibility/check → assess eligibility and generate rationale.
- GET /api/health → health check.

### New

 - POST /api/receipt/analyze (multipart/form-data)
	- Fields:
		- receipt_files: one or more files (PNG/JPEG/PDF)
		- issue_description: optional text to help classification
		- case_id: optional; if omitted, the server auto-generates a case ID
	- Behavior:
			- Performs OCR via EasyOCR + PyMuPDF (PDF rendering), no OpenAI used in OCR
			- Parses seller/date/total/items via existing utilities
		- Runs Issue Classification first (OpenAI) and Eligibility second (OpenAI or heuristic fallback)
		- Generates a final handling report (OpenAI) summarizing classification + eligibility

