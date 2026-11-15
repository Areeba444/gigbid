import time
from typing import Dict, Any
from agent.state import BidGraphState
from agent.handoffs import Critique

def critic_node(state: BidGraphState) -> Dict[str, Any]:
    """Critic: audits draft proposal grounding, personalization and word count limits."""
    draft_dict = state.get("proposal_draft") or {}
    cover_letter = draft_dict.get("cover_letter", "")
    critique_history = state.get("critique_history") or []
    current_iteration = len(critique_history) + 1
    
    words = cover_letter.split()
    word_count = len(words)
    
    length_verdict = "optimal"
    if word_count < 60:
        length_verdict = "too_short"
    elif word_count > 300:
        length_verdict = "too_long"
        
    has_evidence_mention = "deployed" in cover_letter.lower() or "achieved" in cover_letter.lower()
    grounding_score = 0.95 if has_evidence_mention else 0.60
    personalization_score = 0.90 if len(words) > 50 else 0.50
    
    # Loop limit: at most 2 loops
    needs_revision = (length_verdict != "optimal" or grounding_score < 0.70) and current_iteration <= 2
    approved = not needs_revision
    
    feedback = "Draft is grounded, concise, and ready for compliance check."
    if not approved:
        feedback = f"Draft returned for revision {current_iteration}/2: improve grounding and adjust length ({word_count} words)."
        
    critique = Critique(
        approved=approved,
        grounding_score=grounding_score,
        personalization_score=personalization_score,
        length_verdict=length_verdict,
        feedback=feedback,
        iteration=current_iteration
    )
    
    trace = {
        "node": "critic",
        "timestamp": time.time(),
        "iteration": current_iteration,
        "approved": approved,
        "length_verdict": length_verdict
    }
    
    return {
        "critique_history": [critique.dict()],
        "critic_iteration": current_iteration,
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
