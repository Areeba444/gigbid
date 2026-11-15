import time
import uuid
from typing import Dict, Any
from langgraph.types import interrupt
from agent.state import BidGraphState
from agent.marketplace_port import get_marketplace_port
from agent.memory.store import memory_store

def approval_gate_node(state: BidGraphState) -> Dict[str, Any]:
    """Human-in-the-Loop Approval Gate: triggers interrupt() before any proposal or Connects spend."""
    draft = state.get("proposal_draft") or {}
    price = state.get("price_quote") or {}
    evidence = state.get("evidence_items") or []
    risk = state.get("risk_report") or {}
    job_id = state.get("job_id", "unknown")
    
    # 1. Fetch dry_run preview from marketplace port
    port = get_marketplace_port()
    try:
        preview = port.submit_proposal(
            job_id=job_id,
            bid_amount_usd=price.get("bid_amount_usd", 500.0),
            cover_letter=draft.get("cover_letter", ""),
            screening_answers=draft.get("screening_answers", []),
            idempotency_key=f"preview-{job_id}",
            dry_run=True
        )
    except Exception as e:
        preview = {"status": "dry_run_offline", "detail": str(e), "connects_cost": 8}
        
    approval_payload = {
        "job_id": job_id,
        "proposal_draft": draft,
        "price_quote": price,
        "evidence_citations": evidence[:3],
        "risk_report": risk,
        "dry_run_preview": preview,
        "message": "Human approval required before submitting proposal and spending Connects."
    }
    
    # Trigger LangGraph interrupt - pauses thread execution until resumed with human input
    human_decision = interrupt(approval_payload)
    
    action = human_decision.get("action", "approve")  # 'approve', 'edit', 'reject'
    feedback = human_decision.get("feedback", "")
    edited_text = human_decision.get("edited_draft")
    
    # If user edited text, record diff into style memory
    if action == "edit" and edited_text:
        draft["cover_letter"] = edited_text
        memory_store.promote_style_rule(f"User modified proposal wording to prioritize: '{edited_text[:80]}...'")
        
    trace = {
        "node": "approval_gate",
        "timestamp": time.time(),
        "human_action": action,
        "feedback": feedback
    }
    
    return {
        "approval_status": action,
        "human_feedback": feedback,
        "human_edited_draft": edited_text,
        "proposal_draft": draft,
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }

def submission_node(state: BidGraphState) -> Dict[str, Any]:
    """Submission node: executes actual marketplace submission if approved."""
    approval_status = state.get("approval_status", "pending")
    if approval_status in ["rejected", "skipped"]:
        return {
            "status": "rejected",
            "submission_result": {"status": "not_submitted", "reason": "Rejected by human reviewer"}
        }
        
    draft = state.get("proposal_draft") or {}
    price = state.get("price_quote") or {}
    job_id = state.get("job_id", "unknown")
    idempotency_key = f"submit-{job_id}-{uuid.uuid4().hex[:6]}"
    
    port = get_marketplace_port()
    try:
        res = port.submit_proposal(
            job_id=job_id,
            bid_amount_usd=price.get("bid_amount_usd", 500.0),
            cover_letter=draft.get("cover_letter", ""),
            screening_answers=draft.get("screening_answers", []),
            idempotency_key=idempotency_key,
            dry_run=False
        )
    except Exception as e:
        res = {"status": "error", "detail": str(e)}
        
    trace = {
        "node": "submission",
        "timestamp": time.time(),
        "result_status": res.get("status", "unknown")
    }
    
    return {
        "submission_result": res,
        "status": "completed",
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
