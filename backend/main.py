"""
FastAPI application entry (minimal runnable example).

Features:
- /cases accepts receipt files, product images, and an issue description, saves them into local 'uploads', and returns a case_id.

Note: This is a lightweight setup for quick integration. No database or authentication included. For production, add auth, rate limiting, logging, and robust error handling.
"""

import os
import sys
import time
import uuid
import platform
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import get_settings, get_chat_client
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os.path
import status as status_mod
from ai_agent import analyze_issue
from issue_classifier import classify_issue
from ocr_utils import extract_receipt_info

def get_case_data(case_id: str) -> Dict[str, Any]:
    """Get case data including paths to uploaded files and issue description."""
    case_dir = os.path.join(UPLOAD_ROOT, case_id)
    
    # Check if case directory exists
    if not os.path.exists(case_dir):
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Get issue description
    issue_description = ""
    desc_path = os.path.join(case_dir, "issue_description.txt")
    if os.path.exists(desc_path):
        with open(desc_path, "r", encoding="utf-8") as f:
            issue_description = f.read()

    # Get receipt path
    receipts_dir = os.path.join(case_dir, "receipt_files")
    receipt_path = None
    if os.path.exists(receipts_dir):
        files = os.listdir(receipts_dir)
        if files:
            receipt_path = os.path.join(receipts_dir, files[0])

    return {
        "case_id": case_id,
        "issue_description": issue_description,
        "receipt_path": receipt_path,
        "receipt_info": None  # Will be populated during analysis if needed
    }

def update_case_status(case_id: str, update_data: Dict[str, Any]) -> None:
    """Update case status with new data."""
    if not status_mod.case_exists(case_id):
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    status_mod.update_case(case_id, update_data)

# Constants
BACKEND_VERSION = "1.0.0"
FASTAPI_VERSION = "0.100.0"  # Update this to match your installed version
OPENAI_SDK_PRESENT = True  # Set this based on your OpenAI SDK availability

# Initialize FastAPI app
app = FastAPI(title="ELEC5620_Final Backend")

# Add CORS middleware
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
	now = datetime.now(timezone.utc)
	uptime = max(0.0, time.time() - APP_START_TIME)

	# Basic checks
	uploads_writable = _is_writable(UPLOAD_ROOT)

	try:
		s = get_settings()
		openai_key_set = bool(s.openai_api_key)
	except Exception as e:
		openai_key_set = False
		s = None

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
					resp = await client.chat.completions.create(
						model=model,
						messages=[{"role": "user", "content": "ping"}],
						max_tokens=1,
						temperature=0,
					)
					_ = resp.choices[0].message.content if resp.choices and len(resp.choices) > 0 else ""
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
			"openai_model": s.openai_model if s else None,
			"openai_base_url_set": bool(s.openai_base_url) if s else False,
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
async def analyze_case(case_id: str):
    try:
        # Get case data
        case_data = get_case_data(case_id)
        
        try:
            # Extract receipt info if needed
            if not case_data.get('receipt_info') and case_data.get('receipt_path'):
                receipt_info = extract_receipt_info(case_data['receipt_path'])
                case_data['receipt_info'] = receipt_info
        except Exception as e:
            print(f"Receipt extraction error: {str(e)}")
            case_data['receipt_info'] = {
                "error": str(e),
                "status": "failed"
            }
        
        # Analyze issue
        issue_desc = case_data['issue_description']
        try:
            classification = await analyze_issue(issue_desc)
        except Exception as e:
            classification = {
                "error": str(e),
                "status": "failed",
                "requires_manual_review": True
            }
        
        # Update case status
        status_update = {
            'receipt_info': case_data.get('receipt_info'),
            'classification': classification,
            'status': 'analyzed',
            'requires_review': classification.get('requires_manual_review', True)
        }
        
        # Update case status
        update_case_status(case_id, status_update)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "case_id": case_id,
                "receipt_info": case_data.get('receipt_info'),
                "classification": classification
            }
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "case_id": case_id,
                "classification": classification
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "case_id": case_id
            }
        )


class IssueRequest(BaseModel):
    description: str
    case_id: str | None = None

@app.post("/classify")
async def classify_customer_issue(request: IssueRequest):
    try:
        classification = await classify_issue(request.description)
        
        if request.case_id:
            update_case_status(request.case_id, {
                "classification": classification,
                "status": "classified"
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "case_id": request.case_id,
                "classification": classification
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "case_id": request.case_id
            }
        )



@app.post("/upload")
async def upload_files(
    receipt_files: Optional[List[UploadFile]] = File(default=None),
    issue_description: str = Form(...)
):
    """
    Upload receipt files and issue description for processing.

    - **receipt_files**: Optional list of receipt files (images or PDFs).
    - **issue_description**: Description of the issue (required).

    Returns a case_id for tracking and further processing.
    """
    case_id = str(uuid.uuid4())
    case_dir = os.path.join(UPLOAD_ROOT, case_id)
    receipts_dir = os.path.join(case_dir, "receipt_files")
    os.makedirs(receipts_dir, exist_ok=True)

    # Save issue description
    if issue_description is not None:
        with open(os.path.join(case_dir, "issue_description.txt"), "w", encoding="utf-8") as f:
            f.write(issue_description)

    # Save receipt files
    if receipt_files:
        for uf in receipt_files:
            content = await uf.read()
            safe_name = uf.filename or "receipt"
            with open(os.path.join(receipts_dir, safe_name), "wb") as f:
                f.write(content)

    # Initialize status store for this case
    status_mod.init_case(case_id)

    return JSONResponse({"case_id": case_id, "status": "uploaded"})
