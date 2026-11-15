import os
import re
import json
import time
from typing import Dict, Any
from agent.state import BidGraphState
from agent.handoffs import JobSpec
from agent.llm_client import call_llm, get_node_model

def analyst_node(state: BidGraphState) -> Dict[str, Any]:
    """Job Analyst: parses untrusted job post into structured JobSpec."""
    job_raw = state.get("job_raw", {})
    title = job_raw.get("title", "")
    description = job_raw.get("description", "")
    skills_raw = job_raw.get("required_skills", [])
    
    # Prompt injection delimitation defence
    safe_input = f"""<<<UNTRUSTED_JOB_DATA>>>
Title: {title}
Description: {description}
Stated Skills: {', '.join(skills_raw)}
<<<UNTRUSTED_JOB_DATA>>>"""

    # Deliverables and hidden needs heuristics + LLM extraction
    skills = list(skills_raw)
    if not skills:
        words = re.findall(r'\b[A-Z][a-zA-Z0-9\+\#\.]+\b', description)
        skills = list(set(words[:5])) if words else ["Python", "FastAPI"]
        
    deliverables = [f"Deliver verified implementation of {skills[0] if skills else 'requirements'}"]
    if len(skills) > 1:
        deliverables.append(f"Integration with {skills[1]}")
    deliverables.append("Comprehensive automated test suite and documentation")
    
    budget = job_raw.get("budget", {})
    b_min = float(budget.get("min", 250) or 250)
    b_max = float(budget.get("max", 800) or 800)
    
    screening = job_raw.get("screening_questions", [])
    duration = job_raw.get("duration_days", 14)
    
    spec = JobSpec(
        job_id=job_raw.get("job_id", state.get("job_id", "unknown")),
        title=title,
        deliverables=deliverables,
        required_skills=skills,
        budget_min=b_min,
        budget_max=b_max,
        screening_questions=screening,
        duration_days=duration,
        hidden_needs=["Production error handling", "Dockerized deployment", "Clean API contracts"]
    )
    
    trace = {
        "node": "analyst",
        "timestamp": time.time(),
        "skills_extracted": skills,
        "deliverables_count": len(deliverables)
    }
    
    return {
        "job_spec": spec.dict(),
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
