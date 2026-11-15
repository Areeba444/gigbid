import time
from typing import Dict, Any, List
from agent.state import BidGraphState
from agent.marketplace_port import get_marketplace_port

def scout_node(state: BidGraphState) -> Dict[str, Any]:
    """Scout node: fetches job details or queues a new job from marketplace."""
    job_raw = state.get("job_raw", {})
    job_id = state.get("job_id")
    
    if not job_raw and job_id:
        port = get_marketplace_port()
        try:
            job_raw = port.get_job(job_id)
        except Exception:
            job_raw = {"job_id": job_id, "title": "Freelance Project", "description": "General requirements"}
            
    trace_entry = {
        "node": "scout",
        "timestamp": time.time(),
        "job_id": job_raw.get("job_id", "unknown"),
        "title": job_raw.get("title", "")
    }
    
    return {
        "job_raw": job_raw,
        "job_id": job_raw.get("job_id", job_id),
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1
    }
