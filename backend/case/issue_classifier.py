# issue_classifier.py
def classify_issue(text: str) -> dict:
    # Simple rule-based classification (demo)
    lower = (text or "").lower()
    if "not received" in lower or "missing" in lower:
        label = "Not delivered"
    elif "broken" in lower or "damage" in lower:
        label = "Damaged/Quality issue"
    elif "fake" in lower or "counterfeit" in lower:
        label = "Suspected counterfeit"
    elif "refund" in lower or "return" in lower:
        label = "Return/Refund"
    else:
        label = "Other"
    return {"label": label, "confidence": 0.85, "model": "demo-rule-based"}
