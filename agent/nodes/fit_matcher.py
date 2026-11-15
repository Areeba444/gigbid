import time
from typing import Dict, Any, List
from agent.state import BidGraphState
from agent.handoffs import FitReport
from rag.retriever import get_retriever

def fit_matcher_node(state: BidGraphState) -> Dict[str, Any]:
    """Fit Matcher: retrieves grounded portfolio evidence and calculates skill alignment."""
    job_spec = state.get("job_spec") or {}
    job_raw = state.get("job_raw") or {}
    persona_id = state.get("persona_id", "sample-ai-engineer")
    
    skills = job_spec.get("required_skills") or job_raw.get("required_skills") or ["Python"]
    title = job_spec.get("title") or job_raw.get("title") or ""
    query = f"{title}. Skills: {', '.join(skills)}"
    
    # Retrieve top 5 evidence chunks via deployed V4/V8 retriever
    retriever = get_retriever(variant_name="v4_outcome", persona_id=persona_id)
    hits = retriever.retrieve(query, k=5)
    
    evidence_ids = [h.get("id") or h.get("chunk_id") for h in hits]
    
    # Match skills
    portfolio_text = " ".join([h.get("text", "") + " " + " ".join(h.get("metadata", {}).get("skills", [])) for h in hits]).lower()
    matched = []
    missing = []
    
    for s in skills:
        if s.lower() in portfolio_text:
            matched.append(s)
        else:
            missing.append(s)
            
    # Calculate fit score
    base_score = len(matched) / max(1, len(skills))
    avg_relevance = sum(h.get("retrieval_score", 0.5) for h in hits) / max(1, len(hits))
    fit_score = min(1.0, max(0.1, (base_score * 0.7) + (min(1.0, avg_relevance) * 0.3)))
    
    reasons = f"Matched {len(matched)}/{len(skills)} skills against verified portfolio projects."
    if missing:
        reasons += f" Lacks direct portfolio evidence for: {', '.join(missing)}."
        
    report = FitReport(
        score=round(fit_score, 2),
        matched_skills=matched,
        missing_skills=missing,
        evidence_ids=evidence_ids,
        evidence_details=hits,
        reasons=reasons
    )
    
    trace = {
        "node": "fit_matcher",
        "timestamp": time.time(),
        "fit_score": report.score,
        "matched_count": len(matched),
        "evidence_count": len(hits)
    }
    
    return {
        "fit_report": report.dict(),
        "evidence_items": hits,
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
