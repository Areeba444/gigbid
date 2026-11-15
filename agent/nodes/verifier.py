import time
from typing import Dict, Any
from agent.state import BidGraphState
from rag.verify import verify_claims

def verifier_node(state: BidGraphState) -> Dict[str, Any]:
    """Claim Verifier: audits draft claims against retrieved evidence and filters hallucinations."""
    draft_dict = state.get("proposal_draft") or {}
    cover_letter = draft_dict.get("cover_letter", "")
    evidence_items = state.get("evidence_items") or []
    
    verification_result = verify_claims(cover_letter, evidence_items)
    
    # Update draft with verified clean text
    draft_dict["cover_letter"] = verification_result["verified_draft"]
    draft_dict["unsupported_claims_removed"] = verification_result["unsupported_count_before"]
    
    trace = {
        "node": "claim_verifier",
        "timestamp": time.time(),
        "unsupported_before": verification_result["unsupported_count_before"],
        "unsupported_rate_before": verification_result["unsupported_rate_before"]
    }
    
    return {
        "proposal_draft": draft_dict,
        "claim_verification": verification_result,
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
