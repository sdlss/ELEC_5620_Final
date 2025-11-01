from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
from typing import Optional
from typing import Dict, Any, List
from dotenv import load_dotenv
# Use package-relative import so module works when run as `backend.main`
try:
    from .config import get_chat_client
except Exception:
    # Fallback for direct script execution
    from config import get_chat_client
from datetime import datetime
import uuid

# Reuse existing OCR parser to enrich payload when only rawText is provided
try:
    from .ocr_utils import parse_receipt_fields  # when used as package
except Exception:
    try:
        from ocr_utils import parse_receipt_fields  # direct script execution
    except Exception:
        parse_receipt_fields = None  # type: ignore

try:
    from .ocr_utils import extract_receipt_info  # when used as package
except Exception:
    try:
        from ocr_utils import extract_receipt_info  # direct script execution
    except Exception:
        extract_receipt_info = None  # type: ignore
# OpenAI-based OCR has been removed; EasyOCR is the only OCR path.

# Issue classification (LLM)
try:
    from .issue_classifier import classify_issue  # when used as package
except Exception:
    try:
        from issue_classifier import classify_issue
    except Exception:
        classify_issue = None  # type: ignore

# Final report generator (reuse existing AI agent summarizer)
try:
    from .ai_agent import analyze_issue  # when used as package
except Exception:
    try:
        from ai_agent import analyze_issue
    except Exception:
        analyze_issue = None  # type: ignore

# PDF rendering
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None  # type: ignore

import tempfile
import shutil

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


class EligibilityRequest(BaseModel):
    # Example fields coming from frontend OCR/extraction output
    item: Optional[str] = Field(None, description="Item name or category")
    price: Optional[dict] = Field(None, description="{ currency: str, value: number }")
    date: Optional[dict] = Field(None, description="{ iso?: str, raw?: str }")
    confidence: Optional[float] = Field(None, description="OCR confidence 0..1")
    rawText: Optional[str] = Field(None, description="Full OCR raw text")


class EligibilityResponse(BaseModel):
    eligible: bool
    reason: str
    model: str


async def generate_rationale_with_fallback(payload: dict) -> tuple[bool, str, str]:
    debug_errors = (os.getenv("ELIGIBILITY_DEBUG_ERRORS", "").lower() in {"1", "true", "yes"})

    # Simple rule-based fallback
    def heuristic() -> tuple[bool, str, str]:
        item = (payload.get("item") or "").lower()
        price_info = payload.get("price") or {}
        value = price_info.get("value")
        eligible = False
        reasons = []
        if item:
            if any(k in item for k in ["food", "meal", "grocer", "restaurant"]):
                eligible = True
                reasons.append("Item appears to be food-related, typically eligible.")
            if any(k in item for k in ["alcohol", "wine", "beer", "tobacco"]):
                eligible = False
                reasons.append("Alcohol/tobacco items are commonly ineligible.")
        if isinstance(value, (int, float)):
            if value > 500:
                eligible = False
                reasons.append("Amount exceeds typical reimbursement limit of 500.")
        if not reasons:
            reasons.append("Applied default policy rules due to limited data.")
        return eligible, " ".join(reasons), "heuristic"

    # Try to obtain an async chat client from config. If unavailable, fall back to heuristic.
    try:
        client, _ = get_chat_client()
    except Exception:
        return heuristic()

    try:
        system = (
            "You are an eligibility adjudicator. Decide if a purchase is eligible "
            "for reimbursement based on general corporate expense policies. "
            "Explain briefly and clearly. Output JSON with fields: eligible (bool), reason (string)."
        )
        user = (
            "Consider this extracted receipt data and determine eligibility.\n\n" +
            json.dumps(payload, ensure_ascii=False)
        )

        # Use responses API; fallback to chat.completions if needed
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        try:
            completion = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content or "{}"
            data = json.loads(content)
            eligible = bool(data.get("eligible", False))
            reason = str(data.get("reason", "No rationale provided."))
            return eligible, reason, model_name
        except Exception as e1:
            # Try a safer fallback model once before heuristic
            try:
                fallback_model = "gpt-4o-mini"
                completion = await client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                content = completion.choices[0].message.content or "{}"
                data = json.loads(content)
                eligible = bool(data.get("eligible", False))
                reason = str(data.get("reason", "No rationale provided."))
                return eligible, reason, fallback_model
            except Exception as e2:
                # If chat api fails, use heuristic
                if debug_errors:
                    ok, rsn, mdl = heuristic()
                    return ok, f"OpenAI error: {str(e1) or ''} | fallback error: {str(e2) or ''} | {rsn}", mdl
                else:
                    # log minimal error to server console
                    try:
                        print(f"[eligibility] OpenAI error: {e1}; fallback error: {e2}")
                    except Exception:
                        pass
                    return heuristic()
    except Exception as e3:
        if debug_errors:
            ok, rsn, mdl = heuristic()
            return ok, f"OpenAI client/init error: {str(e3) or ''} | {rsn}", mdl
        else:
            try:
                print(f"[eligibility] OpenAI client/init error: {e3}")
            except Exception:
                pass
            return heuristic()


app = FastAPI(title="Eligibility API")

# CORS: support multiple dev origins via CORS_ORIGINS (comma-separated) or fallback defaults
_cors_env = os.getenv("CORS_ORIGINS") or os.getenv("CORS_ORIGIN") or ""
if "," in _cors_env:
    _origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
elif _cors_env:
    _origins = [_cors_env.strip()]
else:
    _origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure .env is loaded even when main is entrypoint (eligibility-only path)
_HERE = os.path.dirname(__file__)
load_dotenv()  # load default .env if present in CWD
_BACKEND_ENV = os.path.join(_HERE, ".env")
if os.path.exists(_BACKEND_ENV):
    load_dotenv(_BACKEND_ENV, override=False)


@app.get("/")
def root():
    """Friendly root. Helps when visiting http://localhost:PORT directly."""
    return {
        "ok": True,
        "service": "Eligibility API",
        "hint": "Use /api/health to check status, /docs to explore APIs.",
    }


@app.post("/api/eligibility/check", response_model=EligibilityResponse)
async def check_eligibility(req: EligibilityRequest):
    # Start with the incoming request as a mutable dict
    payload: Dict[str, Any] = req.dict()

    # Minimal enhancement (no new route): if item/price missing but rawText exists,
    # try to parse receipt fields from rawText using existing OCR parser utilities.
    try:
        needs_item = not (payload.get("item") and isinstance(payload.get("item"), str))
        price_obj = payload.get("price") or {}
        price_missing = not isinstance(price_obj, dict) or price_obj.get("value") in (None, "")
        has_raw_text = isinstance(payload.get("rawText"), str) and len(payload.get("rawText") or "") > 0

        if (needs_item or price_missing or not payload.get("date")) and has_raw_text and parse_receipt_fields:
            parsed = parse_receipt_fields(payload["rawText"])  # type: ignore[arg-type]

            # Fill item from first parsed item description, else seller name
            if needs_item:
                item_list = parsed.get("item_list") or []
                item_candidate = None
                if isinstance(item_list, list) and item_list:
                    first = item_list[0] or {}
                    if isinstance(first, dict):
                        item_candidate = first.get("description")
                if not item_candidate and parsed.get("seller_name"):
                    item_candidate = f"purchase at {parsed.get('seller_name')}"
                if item_candidate:
                    payload["item"] = str(item_candidate)

            # Fill price from purchase_total
            if price_missing:
                pt = parsed.get("purchase_total") or {}
                if isinstance(pt, dict):
                    val = pt.get("value")
                    cur = pt.get("currency", "USD")
                    if isinstance(val, (int, float)):
                        payload["price"] = {"currency": str(cur), "value": float(val)}

            # Fill date.raw if missing
            if not payload.get("date"):
                pd = parsed.get("purchase_date")
                if isinstance(pd, str) and pd:
                    payload["date"] = {"raw": pd}

            # Optionally derive a confidence score from parsed field confidences
            if payload.get("confidence") is None:
                fc = parsed.get("field_confidence") or {}
                if isinstance(fc, dict) and fc:
                    vals = [v for v in fc.values() if isinstance(v, (int, float))]
                    if vals:
                        payload["confidence"] = float(sum(vals) / len(vals))
    except Exception:
        # Parsing is best-effort; silently continue with original payload on error
        pass

    eligible, reason, model_name = await generate_rationale_with_fallback(payload)
    return EligibilityResponse(eligible=eligible, reason=reason, model=model_name)


@app.get("/api/health")
def health():
    return {"ok": True}


def _ensure_uploads_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    up = os.path.join(here, "uploads")
    os.makedirs(up, exist_ok=True)
    return up


def _save_upload_to_temp(upload: UploadFile) -> str:
    suffix = os.path.splitext(upload.filename or "")[1] or ""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with tmp as f:
        shutil.copyfileobj(upload.file, f)
    return tmp.name


def _render_pdf_pages_to_images(pdf_path: str) -> List[str]:
    if not fitz:
        raise HTTPException(status_code=500, detail="pymupdf is not available on server")
    doc = fitz.open(pdf_path)
    out_paths: List[str] = []
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            pix = page.get_pixmap(dpi=200)
            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=f"_p{page_index+1}.png").name
            pix.save(img_path)
            out_paths.append(img_path)
    finally:
        doc.close()
    return out_paths


@app.post("/api/receipt/analyze")
async def analyze_receipt(
    receipt_files: List[UploadFile] = File(..., description="Receipt images or PDFs"),
    issue_description: Optional[str] = Form(None),
    case_id: Optional[str] = Form(
        None,
        description="Optional; leave empty and the server will auto-generate a case ID.",
    ),
):
    """
    Accept receipt images/PDFs, run OCR + basic parsing using existing utilities,
    then reuse eligibility logic to provide a determination based on parsed fields.
    """
    if not extract_receipt_info:
        raise HTTPException(status_code=500, detail="OCR utilities not available on server")

    saved_paths: List[str] = []
    page_image_paths: List[str] = []
    per_file_results: List[Dict[str, Any]] = []
    # Normalize/auto-generate case id if not provided
    case_id_normalized = (case_id or "").strip()
    if not case_id_normalized:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        rand = uuid.uuid4().hex[:6].upper()
        case_id_normalized = f"CASE-{ts}-{rand}"

    try:
        # Save uploads to temp and expand PDFs into page images
        for upl in receipt_files:
            tmp_path = _save_upload_to_temp(upl)
            saved_paths.append(tmp_path)
            fname = upl.filename or os.path.basename(tmp_path)
            lower = fname.lower()
            pages: List[str] = []
            if lower.endswith(".pdf") or upl.content_type == "application/pdf":
                pages = _render_pdf_pages_to_images(tmp_path)
            else:
                pages = [tmp_path]
            page_image_paths.extend(pages)

            # OCR each page/image and collect parsed fields using EasyOCR only
            page_results: List[Dict[str, Any]] = []
            for p in pages:
                try:
                    parsed = extract_receipt_info(p)  # EasyOCR path only
                except Exception as e:
                    parsed = {"error": str(e)}
                page_results.append({
                    "image_path": p,
                    "parsed": parsed,
                })
            per_file_results.append({
                "filename": fname,
                "pages": page_results,
            })

        # Build a consolidated payload for eligibility from the first successfully parsed page
        consolidated: Dict[str, Any] = {"item": None, "price": None, "date": None}
        for f in per_file_results:
            for pg in f.get("pages", []):
                parsed = pg.get("parsed") or {}
                if isinstance(parsed, dict) and not parsed.get("error"):
                    # Item
                    item = None
                    items = parsed.get("item_list") or []
                    if isinstance(items, list) and items:
                        first = items[0] or {}
                        if isinstance(first, dict):
                            item = first.get("description")
                    if not item and parsed.get("seller_name"):
                        item = f"purchase at {parsed.get('seller_name')}"
                    if item and not consolidated.get("item"):
                        consolidated["item"] = item

                    # Price
                    pt = parsed.get("purchase_total") or {}
                    if isinstance(pt, dict) and not consolidated.get("price"):
                        raw_val = pt.get("value")
                        val_f = None
                        try:
                            if raw_val is not None and str(raw_val) != "":
                                val_f = float(raw_val)
                        except Exception:
                            val_f = None
                        if val_f is not None:
                            consolidated["price"] = {
                                "currency": pt.get("currency", "USD"),
                                "value": val_f,
                            }

                    # Date
                    pd = parsed.get("purchase_date")
                    if isinstance(pd, str) and pd and not consolidated.get("date"):
                        consolidated["date"] = {"raw": pd}

        # Fallback to issue_description if item still missing
        if not consolidated.get("item") and issue_description:
            consolidated["item"] = issue_description[:80]

        # 1) Issue classification first (uses OCR-derived summary + user description)
        classification = None
        try:
            if classify_issue is not None:
                parts = []
                if issue_description:
                    parts.append(f"Issue: {issue_description}")
                # Build a compact summary line from consolidated fields
                itm = consolidated.get("item")
                pr = consolidated.get("price") or {}
                dt = (consolidated.get("date") or {}).get("raw")
                total_txt = None
                if isinstance(pr, dict) and pr.get("value") is not None:
                    total_txt = f"{pr.get('currency','USD')} {pr.get('value')}"
                fields: List[str] = []
                if itm:
                    fields.append(f"item={itm}")
                if total_txt:
                    fields.append(f"total={total_txt}")
                if dt:
                    fields.append(f"date={dt}")
                if not fields:
                    fields.append("(empty)")
                parts.append("Receipt: " + ", ".join(fields))
                classification_input = "\n".join([p for p in parts if p])
                classification = await classify_issue(classification_input)
        except Exception as e:
            classification = {"error": str(e)}

        # 2) Eligibility check second (reuse existing logic)
        eligible, reason, model_name = await generate_rationale_with_fallback(consolidated)

        # 3) Final handling report via AI agent (optional, reuse existing analyzer)
        final_report = None
        try:
            if analyze_issue is not None:
                # Build a comprehensive context for the agent including OCR summary, classification and eligibility
                agent_payload = {
                    "issue_description": issue_description,
                    "classification": classification,
                    "eligibility": {"eligible": eligible, "reason": reason, "model": model_name},
                    "receipt_summary": consolidated,
                }
                # Provide a compact string to the agent
                combined = (
                    f"Issue: {issue_description or ''}\n"
                    f"Classification: {json.dumps(classification, ensure_ascii=False)}\n"
                    f"Eligibility: {'eligible' if eligible else 'not eligible'}; reason={reason}\n"
                    f"Receipt summary: {json.dumps(consolidated, ensure_ascii=False)}"
                )
                # Call the analyzer and normalize its return value to a dict with an 'analysis' field
                try:
                    resp = await analyze_issue(combined)
                    if isinstance(resp, str):
                        final_report = {"analysis": resp}
                    elif isinstance(resp, dict):
                        # Ensure at minimum 'analysis' exists (may be raw text or structured)
                        if "analysis" not in resp:
                            # try to synthesize a readable analysis
                            resp_text = resp.get("analysis") or json.dumps(resp, ensure_ascii=False)
                            resp["analysis"] = resp_text
                        final_report = resp
                    else:
                        final_report = {"analysis": str(resp)}
                except Exception as e:
                    final_report = {"error": str(e), "analysis": ""}
            else:
                final_report = {"analysis": ""}
        except Exception as e:
            # Catch any unexpected error when preparing the agent call
            final_report = {"error": str(e), "analysis": ""}

        return {
            "ok": True,
            "case_id": case_id_normalized,
            "issue_description": issue_description,
            "classification": classification,
            "eligibility": {
                "eligible": eligible,
                "reason": reason,
                "model": model_name,
                "summary": consolidated,
            },
            "final_report": final_report,
            "receipts": per_file_results,
        }
    finally:
        # Clean up only the temp PDFs; keep page images if they are the same temp path
        for p in saved_paths:
            try:
                if os.path.exists(p):
                    os.unlink(p)
            except Exception:
                pass


