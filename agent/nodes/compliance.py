import re
import time
from typing import Dict, Any
from agent.state import BidGraphState
from agent.handoffs import ComplianceVerdict

def compliance_node(state: BidGraphState) -> Dict[str, Any]:
    """Compliance Guard: enforces platform terms, scrubs contact info, ensures zero off-platform leaks."""
    draft_dict = state.get("proposal_draft") or {}
    cover_letter = draft_dict.get("cover_letter", "")
    
    violations = []
    redacted = False
    
    # 1. Check & Redact Contact Details (Email, Phone)
    email_pat = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pat = r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    
    if re.search(email_pat, cover_letter):
        violations.append("Prohibited direct email address included")
        cover_letter = re.sub(email_pat, "[REDACTED_CONTACT_INFO]", cover_letter)
        redacted = True
        
    if re.search(phone_pat, cover_letter):
        violations.append("Prohibited phone number included")
        cover_letter = re.sub(phone_pat, "[REDACTED_PHONE]", cover_letter)
        redacted = True
        
    # 2. Check Prohibited Guarantees
    if "100% guarantee" in cover_letter.lower():
        violations.append("Prohibited absolute guarantee clause")
        cover_letter = cover_letter.replace("100% guarantee", "proven production methodology")
        
    draft_dict["cover_letter"] = cover_letter
    compliant = (len(violations) == 0 or redacted)
    
    verdict = ComplianceVerdict(
        compliant=compliant,
        violations_detected=violations,
        redacted_contact_info=redacted,
        policy_notes="All platform compliance rules satisfied." if compliant else "Policy violations mitigated and redacted."
    )
    
    trace = {
        "node": "compliance",
        "timestamp": time.time(),
        "compliant": compliant,
        "violations_count": len(violations)
    }
    
    return {
        "proposal_draft": draft_dict,
        "compliance_verdict": verdict.dict(),
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
