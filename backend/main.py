from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
from typing import Optional

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


def generate_rationale_with_fallback(payload: dict) -> tuple[bool, str, str]:
    api_key = os.getenv("OPENAI_API_KEY")

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

    if not api_key or OpenAI is None:
        return heuristic()

    try:
        client = OpenAI(api_key=api_key)
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
        try:
            completion = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
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
            return eligible, reason, os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        except Exception:
            # If chat api fails, use heuristic
            return heuristic()
    except Exception:
        return heuristic()


app = FastAPI(title="Eligibility API")

# CORS for CRA (http://localhost:3000) by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/eligibility/check", response_model=EligibilityResponse)
def check_eligibility(req: EligibilityRequest):
    eligible, reason, model_name = generate_rationale_with_fallback(req.dict())
    return EligibilityResponse(eligible=eligible, reason=reason, model=model_name)


@app.get("/api/health")
def health():
    return {"ok": True}


