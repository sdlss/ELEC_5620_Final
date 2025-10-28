"""
status.py

Minimal in-memory status store and helpers for case lifecycle and analysis progress.
This is intended for demo purposes and can be replaced with a DB-backed store later.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any

# Suggested status values
CASE_CREATED = "case_created"
ANALYZING_ISSUE = "analyzing_issue"
ANALYSIS_COMPLETED = "analysis_completed"
ANALYSIS_FAILED = "analysis_failed"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# In-memory store: { case_id: { status, timestamps: {}, progress_percent } }
_STORE: Dict[str, Dict[str, Any]] = {}


def init_case(case_id: str) -> Dict[str, Any]:
    entry = {
        "status": CASE_CREATED,
        "timestamps": {
            "created_at": _now_iso(),
        },
        "progress_percent": 0,
    }
    _STORE[case_id] = entry
    return entry


def start_analysis(case_id: str) -> Dict[str, Any]:
    entry = _STORE.get(case_id) or init_case(case_id)
    entry["status"] = ANALYZING_ISSUE
    ts = entry.setdefault("timestamps", {})
    ts["analysis_started_at"] = _now_iso()
    # Optional: set a baseline progress when analysis starts
    entry["progress_percent"] = max(10, int(entry.get("progress_percent") or 0))
    return entry


def finish_analysis(case_id: str, success: bool = True) -> Dict[str, Any]:
    entry = _STORE.get(case_id) or init_case(case_id)
    entry["status"] = ANALYSIS_COMPLETED if success else ANALYSIS_FAILED
    ts = entry.setdefault("timestamps", {})
    ts["analysis_completed_at"] = _now_iso()
    entry["progress_percent"] = 100 if success else int(entry.get("progress_percent") or 0)
    return entry


def set_status(case_id: str, status: str, **extras) -> Dict[str, Any]:
    entry = _STORE.get(case_id) or init_case(case_id)
    entry["status"] = status
    if extras:
        entry.update(extras)
    return entry


def get_case_status(case_id: str) -> Dict[str, Any]:
    return _STORE.get(case_id, {
        "status": None,
        "timestamps": {},
        "progress_percent": None,
    })


def to_response(case_id: str) -> Dict[str, Any]:
    s = get_case_status(case_id)
    # Return a shallow copy to avoid accidental external mutation
    return {
        "status": s.get("status"),
        "timestamps": s.get("timestamps", {}),
        "progress_percent": s.get("progress_percent"),
    }

def case_exists(case_id: str) -> bool:
    """Check if a case exists in the store."""
    return case_id in _STORE

def update_case(case_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update case data with new fields."""
    if not case_exists(case_id):
        raise KeyError(f"Case {case_id} not found")
    
    entry = _STORE[case_id]
    entry.update(update_data)
    return entry
