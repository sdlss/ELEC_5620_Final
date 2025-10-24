"""
FastAPI application entry (minimal runnable example).

Features:
- /cases accepts receipt files, product images, and an issue description, saves them into local 'uploads', and returns a case_id.

Note: This is a lightweight setup for quick integration. No database or authentication included. For production, add auth, rate limiting, logging, and robust error handling.
"""

from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
import sys
import platform
import time
from datetime import datetime, timezone
from .ai_agent import analyze_issue
from . import status as status_mod
from . import __version__ as BACKEND_VERSION

try:
	import fastapi as _fastapi
	FASTAPI_VERSION = getattr(_fastapi, "__version__", "unknown")
except Exception:
	FASTAPI_VERSION = "unknown"

try:
	import openai as _openai  # noqa: F401
	OPENAI_SDK_PRESENT = True
except Exception:  # pragma: no cover
	OPENAI_SDK_PRESENT = False

app = FastAPI(title="ELEC_5620_FINAL Backend")

# Allow local frontend development
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)

# Service start time (for uptime)
APP_START_TIME = time.time()


def _is_writable(path: str) -> bool:
	"""Check if a directory is writable by attempting a temp write/delete."""
	try:
		os.makedirs(path, exist_ok=True)
		test_file = os.path.join(path, ".healthcheck.tmp")
		with open(test_file, "w", encoding="utf-8") as f:
			f.write("ok")
		os.remove(test_file)
		return True
	except Exception:
		return False


def _get_cors_config():
	return {
		"allow_origins": ["*"],
		"allow_credentials": True,
		"allow_methods": ["*"],
		"allow_headers": ["*"],
	}


@app.get("/health")
async def health(deep: bool = Query(False, description="Include deeper external checks (e.g., OpenAI connectivity)") ):
	"""
	Enhanced health check providing runtime, config, storage and optional external connectivity.

	Query:
	- deep: when true, attempts a lightweight OpenAI connectivity check (may incur network call).
	"""
	from .config import get_settings, get_chat_client

	now = datetime.now(timezone.utc)
	uptime = max(0.0, time.time() - APP_START_TIME)

	# Basic checks
	uploads_writable = _is_writable(UPLOAD_ROOT)

	s = get_settings()
	openai_key_set = bool(s.openai_api_key)

	# Optional deep check: try to reach OpenAI endpoint
	openai_connectivity = {
		"checked": False,
		"status": "skipped",
	}
	if deep and OPENAI_SDK_PRESENT and openai_key_set:
		openai_connectivity["checked"] = True
		try:
			client, model = get_chat_client()
			# Use a very cheap listing call if possible; fall back to a tiny completion if needed
			try:
				# Some gateways may not support models.list; ignore errors
				models = client.models.list()
				_ = True if models else True
				openai_connectivity["status"] = "ok"
			except Exception as e:
				# Try a minimal completion with a short timeout
				try:
					resp = client.chat.completions.create(
						model=model,
						messages=[{"role": "user", "content": "ping"}],
						max_tokens=1,
						temperature=0,
					)
					_ = resp.choices[0].message.content if resp.choices else ""
					openai_connectivity["status"] = "ok"
				except Exception as e2:  # pragma: no cover
					openai_connectivity["status"] = "failed"
					openai_connectivity["error"] = str(e2)
		except Exception as e0:  # pragma: no cover
			openai_connectivity["status"] = "failed"
			openai_connectivity["error"] = str(e0)

	# Overall status aggregation
	status = "ok"
	reasons = []
	if not uploads_writable:
		status = "error"
		reasons.append("uploads_not_writable")
	if not openai_key_set:
		status = "degraded" if status == "ok" else status
		reasons.append("openai_key_missing")
	if openai_connectivity.get("status") == "failed":
		status = "degraded" if status == "ok" else status
		reasons.append("openai_connectivity_failed")

	return JSONResponse({
		"status": status,
		"reasons": reasons,
		"time": now.isoformat(),
		"uptime_seconds": round(uptime, 2),
		"app": {
			"name": "ELEC_5620_FINAL Backend",
			"version": BACKEND_VERSION,
		},
		"python": {
			"version": sys.version.split(" ")[0],
			"implementation": platform.python_implementation(),
			"platform": platform.platform(),
		},
		"framework": {
			"fastapi_version": FASTAPI_VERSION,
		},
		"config": {
			"openai_model": s.openai_model,
			"openai_base_url_set": bool(s.openai_base_url),
			"openai_api_key_set": openai_key_set,
		},
		"storage": {
			"uploads_dir": UPLOAD_ROOT,
			"writable": uploads_writable,
		},
		"cors": _get_cors_config(),
		"openai": {
			"sdk_present": OPENAI_SDK_PRESENT,
			"connectivity": openai_connectivity,
		},
	})


@app.post("/cases")
async def create_case(
	receipt_files: Optional[List[UploadFile]] = File(default=None),
	product_images: Optional[List[UploadFile]] = File(default=None),
	issue_description: str = Form(""),
	receipt_id: Optional[str] = Form(default=None),
):
	"""Create a case: save uploaded files/images or persist the provided receipt_id and description, then return case_id.

	Compatible inputs:
	- Legacy path: upload receipt_files (images/PDF)
	- New path: provide receipt_id (to be looked up from DB), no file upload
	"""
	case_id = str(uuid.uuid4())
	case_dir = os.path.join(UPLOAD_ROOT, case_id)
	receipts_dir = os.path.join(case_dir, "receipt_files")
	images_dir = os.path.join(case_dir, "product_images")
	os.makedirs(receipts_dir, exist_ok=True)
	os.makedirs(images_dir, exist_ok=True)

	# Save issue description
	if issue_description is not None:
		with open(os.path.join(case_dir, "issue_description.txt"), "w", encoding="utf-8") as f:
			f.write(issue_description)

	# Save receipt_id (DB reference)
	if receipt_id:
		with open(os.path.join(case_dir, "receipt_id.txt"), "w", encoding="utf-8") as f:
			f.write(receipt_id)

	# Save receipt files
	if receipt_files:
		for uf in receipt_files:
			content = await uf.read()
			safe_name = uf.filename or "receipt"
			with open(os.path.join(receipts_dir, safe_name), "wb") as f:
				f.write(content)

	# Save product images
	if product_images:
		for uf in product_images:
			content = await uf.read()
			safe_name = uf.filename or "image"
			with open(os.path.join(images_dir, safe_name), "wb") as f:
				f.write(content)

	# Initialize status store for this case
	status_mod.init_case(case_id)

	resp = {"case_id": case_id}
	if receipt_id:
		resp["receipt_id"] = receipt_id
	resp.update(status_mod.to_response(case_id))
	return JSONResponse(resp)


@app.post("/analyze")
async def analyze(issue_description: str = Form(""), case_id: Optional[str] = Form(None)):
	"""Run a minimal analysis on the issue description and return suggestions."""
	if not issue_description.strip():
		return JSONResponse({"error": "issue_description is required"}, status_code=400)

	# Mark analysis start if a case_id is provided
	if case_id:
		status_mod.start_analysis(case_id)

	result = analyze_issue(issue_description)

	# Mark analysis finish
	if case_id:
		status_mod.finish_analysis(case_id, success=True)
		# Attach status info to response
		result.update(status_mod.to_response(case_id))
	else:
		# Ephemeral status info for one-off analyze without case
		result.update({
			"status": "analysis_completed",
			"timestamps": {"analysis_started_at": datetime.now(timezone.utc).isoformat(), "analysis_completed_at": datetime.now(timezone.utc).isoformat()},
			"progress_percent": 100,
		})

	return JSONResponse(result)
