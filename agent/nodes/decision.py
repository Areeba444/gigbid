import time
from typing import Dict, Any
from agent.state import BidGraphState
from agent.handoffs import BidDecision

def decision_node(state: BidGraphState) -> Dict[str, Any]:
    """Decision node: evaluates RiskReport and FitReport to choose bid, skip, or watch."""
    risk = state.get("risk_report", {})
    fit = state.get("fit_report", {})
    
    risk_score = risk.get("score", 0.0)
    fit_score = fit.get("score", 0.0)
    is_scam = risk.get("is_scam", False)
    has_injection = risk.get("has_prompt_injection", False)
    
    if is_scam or has_injection or risk_score >= 0.70:
        action = "skip"
        reasoning = f"Skipping job due to elevated risk (score: {risk_score}): {risk.get('explanation')}"
        confidence = 0.95
    elif fit_score < 0.40:
        action = "skip"
        reasoning = f"Skipping job due to low portfolio fit ({fit_score * 100:.0f}%): {fit.get('reasons')}"
        confidence = 0.85
    elif fit_score < 0.60:
        action = "watch"
        reasoning = f"Borderline fit ({fit_score * 100:.0f}%). Saved to watch list."
        confidence = 0.70
    else:
        action = "bid"
        reasoning = f"High fit ({fit_score * 100:.0f}%) and low risk ({risk_score * 100:.0f}%). Strong match for proposal."
        confidence = 0.90
        
    decision = BidDecision(
        action=action,
        confidence=confidence,
        reasoning=reasoning
    )
    
    trace = {
        "node": "bid_decision",
        "timestamp": time.time(),
        "action": action,
        "confidence": confidence
    }
    
    return {
        "bid_decision": decision.dict(),
        "status": "bidding" if action == "bid" else "skipped",
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
