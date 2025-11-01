from pydantic import BaseModel
from typing import Optional

class CaseCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    latest_summary: Optional[str] = None

class ReceiptCreate(BaseModel):
    case_id: int
    file_url: str
    purchase_date: Optional[str] = None
    seller: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    ocr_confidence: Optional[float] = None

class IssueCreate(BaseModel):
    case_id: int
    description: str
    classification: Optional[str] = None
    clf_confidence: Optional[float] = None

class EligibilityCreate(BaseModel):
    case_id: int
    status: str       # 'eligible' | 'not_eligible' | 'needs_review'
    rationale: str
    policy_name: Optional[str] = None
    policy_source: Optional[str] = None
