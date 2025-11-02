from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
# from backend.database import Base, engine, get_db
# from backend import models, schemas

from database import Base, engine, get_db
import models, schemas

app = FastAPI(title="ELEC-5620 Minimal Backend")

# If you want to create tables via ORM (dev only; use SQL scripts in production)
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

# 1) Create a new case (minimal flow: set status='new')
@app.post("/cases")
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = models.Case(user_id=payload.user_id, status="new",
                       title=payload.title, latest_summary=payload.latest_summary)
    db.add(case); db.commit(); db.refresh(case)
    return {"case_id": case.id, "status": case.status}

# 2) Record receipt info (decoupled from upload service; store metadata only)
@app.post("/receipts")
def add_receipt(payload: schemas.ReceiptCreate, db: Session = Depends(get_db)):
    # Simple validation: case exists
    if not db.get(models.Case, payload.case_id):
        raise HTTPException(404, "case not found")
    if not hasattr(models, "Receipt"):
        raise HTTPException(501, "Receipt model is not available")
    r = models.Receipt(**payload.dict())  # type: ignore[attr-defined]
    db.add(r); db.commit(); db.refresh(r)
    return {"receipt_id": r.id}

# 3) Record issue and classification
@app.post("/issues")
def add_issue(payload: schemas.IssueCreate, db: Session = Depends(get_db)):
    if not db.get(models.Case, payload.case_id):
        raise HTTPException(404, "case not found")
    i = models.Issue(**payload.dict())
    db.add(i); db.commit(); db.refresh(i)
    return {"issue_id": i.id}

# 4) Eligibility decision (Case status is synced by DB trigger)
@app.post("/eligibility")
def add_eligibility(payload: schemas.EligibilityCreate, db: Session = Depends(get_db)):
    if not db.get(models.Case, payload.case_id):
        raise HTTPException(404, "case not found")

    # Optional: create or reuse policy_snapshot
    ps_id = None
    if payload.policy_name and payload.policy_source:
        ps = models.PolicySnapshot(name=payload.policy_name,
                                   source=payload.policy_source,
                                   matched_rules={"rules": []})
        db.add(ps); db.flush()
        ps_id = ps.id

    ed = models.EligibilityDecision(case_id=payload.case_id,
                                    policy_snapshot_id=ps_id,
                                    status=payload.status,
                                    rationale=payload.rationale)
    db.add(ed); db.commit(); db.refresh(ed)
    # CASE.status has been updated by trigger
    current_case = db.get(models.Case, payload.case_id)
    case_status = getattr(current_case, "status", None)
    return {"eligibility_id": ed.id, "case_status": case_status}

# 5) Dashboard: query view directly
@app.get("/dashboard/overview")
def dashboard_overview(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM v_case_overview ORDER BY case_id DESC")).mappings().all()
    return {"items": [dict(r) for r in rows]}
