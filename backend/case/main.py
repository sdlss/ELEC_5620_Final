from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
# from backend.database import Base, engine, get_db
# from backend import models, schemas

from database import Base, engine, get_db
import models, schemas

app = FastAPI(title="ELEC-5620 Minimal Backend")

# 如果你想用 ORM 自动建表（仅开发期使用；正式用SQL脚本）
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

# 1) 新建工单（最小闭环：设置为 new）
@app.post("/cases")
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = models.Case(user_id=payload.user_id, status="new",
                       title=payload.title, latest_summary=payload.latest_summary)
    db.add(case); db.commit(); db.refresh(case)
    return {"case_id": case.id, "status": case.status}

# 2) 录入收据信息（可与上传服务解耦；这里只存元数据）
@app.post("/receipts")
def add_receipt(payload: schemas.ReceiptCreate, db: Session = Depends(get_db)):
    # 简单校验：工单存在
    if not db.get(models.Case, payload.case_id):
        raise HTTPException(404, "case not found")
    r = models.Receipt(**payload.dict())
    db.add(r); db.commit(); db.refresh(r)
    return {"receipt_id": r.id}

# 3) 记录问题与分类
@app.post("/issues")
def add_issue(payload: schemas.IssueCreate, db: Session = Depends(get_db)):
    if not db.get(models.Case, payload.case_id):
        raise HTTPException(404, "case not found")
    i = models.Issue(**payload.dict())
    db.add(i); db.commit(); db.refresh(i)
    return {"issue_id": i.id}

# 4) 资格判定（同时同步 Case 状态 —— 由数据库触发器完成）
@app.post("/eligibility")
def add_eligibility(payload: schemas.EligibilityCreate, db: Session = Depends(get_db)):
    if not db.get(models.Case, payload.case_id):
        raise HTTPException(404, "case not found")

    # 可选：新建或复用 policy_snapshot
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
    # 由于触发器，CASE.status 已被刷新
    current_case = db.get(models.Case, payload.case_id)
    return {"eligibility_id": ed.id, "case_status": current_case.status}

# 5) 仪表盘：直接查视图
@app.get("/dashboard/overview")
def dashboard_overview(db: Session = Depends(get_db)):
    rows = db.execute("""
        SELECT * FROM v_case_overview ORDER BY case_id DESC
    """).mappings().all()
    return {"items": [dict(r) for r in rows]}
