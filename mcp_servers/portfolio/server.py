import os
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "personas")

app = FastAPI(title="GigBid Portfolio MCP Server", version="1.0.0")

def load_persona_data(persona_id: str):
    p_dir = os.path.join(DATA_DIR, persona_id)
    if not os.path.exists(p_dir):
        p_dir = os.path.join(DATA_DIR, "sample-ai-engineer")
        
    case_studies = []
    proposals = []
    reviews = []
    persona = {}
    
    if os.path.exists(os.path.join(p_dir, "case_studies.json")):
        with open(os.path.join(p_dir, "case_studies.json"), "r", encoding="utf-8") as f:
            case_studies = json.load(f)
    if os.path.exists(os.path.join(p_dir, "past_proposals.json")):
        with open(os.path.join(p_dir, "past_proposals.json"), "r", encoding="utf-8") as f:
            proposals = json.load(f)
    if os.path.exists(os.path.join(p_dir, "reviews.json")):
        with open(os.path.join(p_dir, "reviews.json"), "r", encoding="utf-8") as f:
            reviews = json.load(f)
    if os.path.exists(os.path.join(p_dir, "persona.json")):
        with open(os.path.join(p_dir, "persona.json"), "r", encoding="utf-8") as f:
            persona = json.load(f)
            
    return persona, case_studies, proposals, reviews

@app.get("/tools")
def list_tools():
    """Declares the MCP tool schemas for standard MCP clients."""
    return [
        {
            "name": "search_evidence",
            "description": "Search portfolio case studies, proposals, and reviews for grounded evidence matching a job requirement.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "requirement": {"type": "string", "description": "Specific technical or domain requirement to match"},
                    "k": {"type": "integer", "default": 5, "description": "Number of evidence items to return"},
                    "filters": {"type": "object", "description": "Optional filters such as type ('case_study', 'proposal') or min_outcome"}
                },
                "required": ["requirement"]
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "get_case_study",
            "description": "Fetch the full technical details of a portfolio case study by its unique ID.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Case study identifier (e.g. sample-ai-engineer-case-001)"}
                },
                "required": ["id"]
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "list_skills",
            "description": "List all verified technical skills and proficiencies for the active freelancer persona.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "persona_id": {"type": "string", "default": "sample-ai-engineer"}
                }
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        }
    ]

@app.get("/resources")
def list_resources():
    return [
        {"uri": "portfolio://case/{id}", "name": "Full Case Study Item", "mimeType": "application/json"},
        {"uri": "portfolio://proposal/{id}", "name": "Full Proposal Item with Outcome", "mimeType": "application/json"}
    ]

@app.get("/prompts")
def list_prompts():
    return [
        {
            "name": "screening_question_answer",
            "description": "Answer a client screening question grounded purely in portfolio evidence.",
            "arguments": [
                {"name": "question", "description": "The client screening question", "required": True},
                {"name": "persona_id", "description": "Persona ID", "required": False}
            ]
        }
    ]

# Core Tool Implementations
@app.get("/search_evidence")
def search_evidence(
    requirement: str,
    k: int = Query(default=5, ge=1, le=20),
    persona_id: str = "sample-ai-engineer"
):
    persona, case_studies, proposals, reviews = load_persona_data(persona_id)
    req_terms = set(requirement.lower().split())
    
    scored_items = []
    
    # Search Case Studies
    for cs in case_studies:
        text = f"{cs['title']} {cs['client_industry']} {' '.join(cs['skills'])} {cs['problem']} {cs['solution']} {cs['outcome_metrics']}".lower()
        overlap = sum(1 for term in req_terms if term in text)
        score = overlap / (len(req_terms) + 1e-5)
        scored_items.append({
            "id": cs["id"],
            "type": "case_study",
            "title": cs["title"],
            "industry": cs["client_industry"],
            "skills": cs["skills"],
            "summary": cs["solution"][:200],
            "metrics": cs["outcome_metrics"],
            "date": cs["date"],
            "score": round(score, 3)
        })
        
    # Search Past Proposals (won or replied have higher priority)
    for pr in proposals:
        text = f"{pr['job_title']} {' '.join(pr['relevance_skills'])} {pr['cover_letter']}".lower()
        overlap = sum(1 for term in req_terms if term in text)
        outcome_bonus = 0.2 if pr["outcome"] == "won" else (0.1 if pr["outcome"] == "replied" else 0.0)
        score = (overlap / (len(req_terms) + 1e-5)) + outcome_bonus
        scored_items.append({
            "id": pr["proposal_id"],
            "type": "proposal",
            "title": pr["job_title"],
            "skills": pr["relevance_skills"],
            "summary": pr["cover_letter"][:200],
            "outcome": pr["outcome"],
            "date": pr["date"],
            "score": round(score, 3)
        })
        
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    return scored_items[:k]

@app.get("/get_case_study")
def get_case_study(id: str, persona_id: str = "sample-ai-engineer"):
    persona, case_studies, proposals, reviews = load_persona_data(persona_id)
    for cs in case_studies:
        if cs["id"] == id:
            return cs
    raise HTTPException(status_code=404, detail="Case study not found")

@app.get("/list_skills")
def list_skills(persona_id: str = "sample-ai-engineer"):
    persona, _, _, _ = load_persona_data(persona_id)
    return {
        "persona_id": persona_id,
        "display_name": persona.get("display_name", "Freelancer"),
        "skills": persona.get("skills", []),
        "hourly_rate_usd": persona.get("hourly_rate_usd", 50)
    }

# Resource resolver
@app.get("/resource")
def get_resource(uri: str, persona_id: str = "sample-ai-engineer"):
    persona, case_studies, proposals, reviews = load_persona_data(persona_id)
    if uri.startswith("portfolio://case/"):
        cs_id = uri.replace("portfolio://case/", "")
        for cs in case_studies:
            if cs["id"] == cs_id:
                return cs
        raise HTTPException(status_code=404, detail="Case study resource not found")
    elif uri.startswith("portfolio://proposal/"):
        pr_id = uri.replace("portfolio://proposal/", "")
        for pr in proposals:
            if pr["proposal_id"] == pr_id:
                return pr
        raise HTTPException(status_code=404, detail="Proposal resource not found")
    raise HTTPException(status_code=400, detail="Invalid resource URI")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_servers.portfolio.server:app", host="0.0.0.0", port=8002, reload=False)
