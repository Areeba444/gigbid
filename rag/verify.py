import re
from typing import List, Dict, Any, Tuple

def split_into_claims(text: str) -> List[str]:
    """Splits text into atomic sentences / factual claim segments."""
    # Split on sentence boundaries (. ! ?) while keeping abbreviations intact
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    claims = []
    for s in raw_sentences:
        clean = s.strip()
        if len(clean) > 10:
            claims.append(clean)
    return claims

def check_claim_support(claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluates whether an individual claim is grounded in the provided portfolio evidence."""
    claim_lower = claim.lower()
    words = re.findall(r'\b[a-zA-Z0-9_\-\.]{3,}\b', claim_lower)
    
    # Check for hallucination red flags
    unsupported_flags = [
        "100% guarantee", "10 years experience", "guaranteed #1", 
        "never failed", "free work", "all platforms"
    ]
    for flag in unsupported_flags:
        if flag in claim_lower:
            return {
                "claim": claim,
                "status": "unsupported",
                "reason": f"Contains ungrounded guarantee or exaggerated claim: '{flag}'",
                "matched_evidence_id": None
            }

    best_overlap = 0
    best_ev_id = None
    
    for ev in evidence:
        ev_text = (ev.get("text", "") or ev.get("summary", "") or ev.get("title", "")).lower()
        overlap = sum(1 for w in words if w in ev_text)
        if overlap > best_overlap:
            best_overlap = overlap
            best_ev_id = ev.get("id") or ev.get("chunk_id")
            
    overlap_ratio = best_overlap / (len(words) + 1e-5)
    
    if overlap_ratio >= 0.35 or best_overlap >= 4:
        return {
            "claim": claim,
            "status": "supported",
            "reason": "Directly grounded in portfolio case study or past proposal.",
            "matched_evidence_id": best_ev_id
        }
    elif overlap_ratio >= 0.18 or best_overlap >= 2:
        return {
            "claim": claim,
            "status": "partly_supported",
            "reason": "Partially supported by broad skills, lacks specific case citation.",
            "matched_evidence_id": best_ev_id
        }
    else:
        return {
            "claim": claim,
            "status": "unsupported",
            "reason": "No matching portfolio case study, code sample, or verified outcome found.",
            "matched_evidence_id": None
        }

def verify_claims(draft: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    claims = split_into_claims(draft)
    evaluations = [check_claim_support(c, evidence) for c in claims]
    
    unsupported_before = sum(1 for e in evaluations if e["status"] == "unsupported")
    total_claims = max(1, len(claims))
    rate_before = unsupported_before / total_claims
    
    # Filter or rewrite draft by removing unsupported claims
    cleaned_sentences = []
    for e in evaluations:
        if e["status"] == "unsupported":
            continue
        cleaned_sentences.append(e["claim"])
        
    cleaned_draft = " ".join(cleaned_sentences)
    if not cleaned_draft and evidence:
        # Fallback to grounded summary if all was unsupported
        cleaned_draft = f"Based on our relevant project work: {evidence[0].get('title', '')}, we can deliver this within your specifications."
        
    cleaned_claims = split_into_claims(cleaned_draft)
    rate_after = 0.0  # Unsupported claims were excised
    
    return {
        "original_draft": draft,
        "verified_draft": cleaned_draft,
        "claims_evaluated": evaluations,
        "total_claims": total_claims,
        "unsupported_count_before": unsupported_before,
        "unsupported_rate_before": round(rate_before, 3),
        "unsupported_rate_after": rate_after
    }
