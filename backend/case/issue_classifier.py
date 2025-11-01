# issue_classifier.py
def classify_issue(text: str) -> dict:
    # 简单规则分类（演示）
    lower = (text or "").lower()
    if "not received" in lower or "missing" in lower:
        label = "物流未送达"
    elif "broken" in lower or "damage" in lower:
        label = "破损/质量问题"
    elif "fake" in lower or "counterfeit" in lower:
        label = "疑似假货"
    elif "refund" in lower or "return" in lower:
        label = "退货退款"
    else:
        label = "其他"
    return {"label": label, "confidence": 0.85, "model": "demo-rule-based"}
