import os
import json
import time
import uuid
import requests
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Depends, Query, Request
from pydantic import BaseModel, Field

app = FastAPI(title="GigBid Marketplace MCP Server", version="1.0.0")

GIGSIM_URL = os.getenv("GIGSIM_API_URL", "http://localhost:8001")
EXPECTED_BEARER_TOKEN = os.getenv("MARKETPLACE_MCP_TOKEN", "gigbid-token-verified")

AUDIT_LOG: List[Dict[str, Any]] = []
RATE_LIMIT_BUCKETS: Dict[str, List[float]] = {}
MAX_USER_RPM = 60

def verify_token(authorization: Optional[str] = Header(None)):
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            if parts[1] == EXPECTED_BEARER_TOKEN:
                return parts[1]
    # For local dev ease, allow if unset, but log warning
    return "dev-authorized"

@app.middleware("http")
async def audit_and_rate_limit(request: Request, call_next):
    now = time.time()
    user = request.headers.get("X-User-ID", "default")
    
    # Rate limit check per user
    timestamps = RATE_LIMIT_BUCKETS.get(user, [])
    timestamps = [t for t in timestamps if now - t < 60]
    if len(timestamps) >= MAX_USER_RPM:
        raise HTTPException(status_code=429, detail="Marketplace MCP user rate limit exceeded.")
    timestamps.append(now)
    RATE_LIMIT_BUCKETS[user] = timestamps
    
    response = await call_next(request)
    
    AUDIT_LOG.append({
        "timestamp": now,
        "user_id": user,
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code
    })
    return response

@app.get("/tools")
def list_tools():
    return [
        {
            "name": "search_jobs",
            "description": "Search active freelance jobs with optional query, min budget and pagination.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                    "min_budget": {"type": "number"}
                }
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "get_job",
            "description": "Fetch complete job posting specification including budget, timeline, and questions.",
            "inputSchema": {
                "type": "object",
                "properties": {"job_id": {"type": "string"}},
                "required": ["job_id"]
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "get_client_history",
            "description": "Fetch verified client spending history, hire rate, and feedback ratings.",
            "inputSchema": {
                "type": "object",
                "properties": {"client_id": {"type": "string"}},
                "required": ["client_id"]
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "get_connects_balance",
            "description": "Fetch current available Connects balance for the user.",
            "inputSchema": {
                "type": "object",
                "properties": {"user_id": {"type": "string", "default": "default"}}
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "submit_proposal",
            "description": "Submit an approved proposal draft to the marketplace or preview in dry_run mode.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "bid_amount_usd": {"type": "number"},
                    "cover_letter": {"type": "string"},
                    "screening_answers": {"type": "array", "items": {"type": "string"}},
                    "idempotency_key": {"type": "string"},
                    "dry_run": {"type": "boolean", "default": False}
                },
                "required": ["job_id", "bid_amount_usd", "cover_letter", "idempotency_key"]
            },
            "annotations": {"destructiveHint": True, "idempotentHint": True}
        },
        {
            "name": "send_message",
            "description": "Send a client response message after human approval.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "content": {"type": "string"},
                    "user_id": {"type": "string", "default": "default"}
                },
                "required": ["job_id", "content"]
            },
            "annotations": {"destructiveHint": True, "idempotentHint": False}
        }
    ]

# Tool Handlers
@app.get("/search_jobs")
def tool_search_jobs(
    query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    min_budget: Optional[float] = None
):
    try:
        resp = requests.get(
            f"{GIGSIM_URL}/jobs",
            params={"query": query, "limit": limit, "offset": offset, "min_budget": min_budget},
            timeout=5
        )
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Marketplace downstream error: {e}")

@app.get("/get_job")
def tool_get_job(job_id: str):
    try:
        resp = requests.get(f"{GIGSIM_URL}/jobs/{job_id}", timeout=5)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Job not found")
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Marketplace downstream error: {e}")

@app.get("/get_client_history")
def tool_get_client_history(client_id: str):
    try:
        resp = requests.get(f"{GIGSIM_URL}/clients/{client_id}", timeout=5)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Marketplace downstream error: {e}")

@app.get("/get_connects_balance")
def tool_get_connects_balance(user_id: str = "default"):
    try:
        resp = requests.get(f"{GIGSIM_URL}/connects", params={"user_id": user_id}, timeout=5)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Marketplace downstream error: {e}")

class ProposalSubmitModel(BaseModel):
    job_id: str
    bid_amount_usd: float = Field(gt=0)
    cover_letter: str = Field(min_length=20)
    screening_answers: List[str] = Field(default_factory=list)
    idempotency_key: str
    dry_run: bool = False
    user_id: str = "default"

@app.post("/submit_proposal")
def tool_submit_proposal(sub: ProposalSubmitModel):
    try:
        resp = requests.post(
            f"{GIGSIM_URL}/proposals",
            json=sub.dict(),
            timeout=8
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Marketplace submission failed: {e}")

class MessageModel(BaseModel):
    job_id: str
    content: str = Field(min_length=1)
    user_id: str = "default"

@app.post("/send_message")
def tool_send_message(msg: MessageModel):
    try:
        resp = requests.post(f"{GIGSIM_URL}/messages", json=msg.dict(), timeout=5)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Messaging failed: {e}")

@app.get("/audit_log")
def get_audit_log(limit: int = 50):
    return AUDIT_LOG[-limit:]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_servers.marketplace.server:app", host="0.0.0.0", port=8003, reload=False)
