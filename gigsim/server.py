import os
import json
import uuid
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="GigSim Marketplace Simulator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# In-memory stores initialized from disk
JOBS: List[Dict[str, Any]] = []
CLIENTS: Dict[str, Dict[str, Any]] = {}
PROPOSALS: Dict[str, Dict[str, Any]] = {}
IDEMPOTENCY_STORE: Dict[str, Dict[str, Any]] = {}
MESSAGES: List[Dict[str, Any]] = []
USER_CONNECTS: Dict[str, int] = {"default": 120}

# Rate limiting & audit
AUDIT_LOG: List[Dict[str, Any]] = []
RATE_LIMIT_BUCKETS: Dict[str, List[float]] = {}
MAX_REQUESTS_PER_MINUTE = 60

# Dynamic policy config (supports change request)
POLICY_CONFIG = {
    "connects_multiplier": 1.0,
    "min_bid_floor": 20.0,
    "prohibit_direct_contact": True,
    "require_two_factor_verified": False
}

def load_data():
    global JOBS, CLIENTS
    jobs_path = os.path.join(DATA_DIR, "jobs.json")
    clients_path = os.path.join(DATA_DIR, "clients.json")
    if os.path.exists(jobs_path):
        with open(jobs_path, "r", encoding="utf-8") as f:
            JOBS = json.load(f)
    if os.path.exists(clients_path):
        with open(clients_path, "r", encoding="utf-8") as f:
            client_list = json.load(f)
            CLIENTS = {c["client_id"]: c for c in client_list}

load_data()

@app.middleware("http")
async def rate_limit_and_audit(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    
    # Rate limit check
    timestamps = RATE_LIMIT_BUCKETS.get(client_ip, [])
    timestamps = [t for t in timestamps if now - t < 60]
    if len(timestamps) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(status_code=429, detail="GigSim rate limit exceeded. Max 60 req/min.")
    timestamps.append(now)
    RATE_LIMIT_BUCKETS[client_ip] = timestamps
    
    response = await call_next(request)
    
    AUDIT_LOG.append({
        "timestamp": now,
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "client_ip": client_ip
    })
    return response

@app.get("/health")
def health():
    return {"status": "ok", "service": "GigSim Marketplace Simulator", "jobs_count": len(JOBS)}

@app.get("/policy")
def get_policy():
    return POLICY_CONFIG

@app.post("/admin/policy-update")
def update_policy(update: Dict[str, Any]):
    """Change request endpoint: update platform fee, rules, or Connects cost"""
    POLICY_CONFIG.update(update)
    return {"status": "policy_updated", "current_policy": POLICY_CONFIG}

@app.get("/jobs")
def search_jobs(
    query: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    min_budget: Optional[float] = None
):
    results = JOBS
    if query:
        q = query.lower()
        results = [j for j in results if q in j.get("title", "").lower() or q in j.get("description", "").lower()]
    if min_budget is not None:
        results = [j for j in results if j.get("budget", {}).get("max", 0) >= min_budget]
        
    paged = results[offset : offset + limit]
    return {
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "jobs": paged
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    for j in JOBS:
        if j["job_id"] == job_id:
            return j
    raise HTTPException(status_code=404, detail="Job not found")

@app.get("/clients/{client_id}")
def get_client(client_id: str):
    if client_id in CLIENTS:
        client = CLIENTS[client_id].copy()
        # Do not expose raw hidden preferences to cheating, provide public profile
        public_view = {
            "client_id": client["client_id"],
            "name": client["name"],
            "company": client["company"],
            "total_spent_usd": client["total_spent_usd"],
            "hires_count": client["hires_count"],
            "average_rating": client["average_rating"],
            "payment_verified": client["payment_verified"]
        }
        return public_view
    # Fallback default client
    return {
        "client_id": client_id,
        "name": "Verified Client",
        "company": "Enterprise Tech Partners",
        "total_spent_usd": 25000.0,
        "hires_count": 14,
        "average_rating": 4.92,
        "payment_verified": True
    }

@app.get("/connects")
def get_connects(user_id: str = "default"):
    return {"user_id": user_id, "balance": USER_CONNECTS.get(user_id, 120)}

class ProposalSubmission(BaseModel):
    job_id: str
    user_id: str = "default"
    bid_amount_usd: float
    cover_letter: str
    screening_answers: List[str] = Field(default_factory=list)
    idempotency_key: str
    dry_run: bool = False

@app.post("/proposals")
def submit_proposal(sub: ProposalSubmission):
    # Check idempotency
    if sub.idempotency_key in IDEMPOTENCY_STORE:
        return IDEMPOTENCY_STORE[sub.idempotency_key]
        
    job = None
    for j in JOBS:
        if j["job_id"] == sub.job_id:
            job = j
            break
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    connects_required = int(job.get("connects_cost", 8) * POLICY_CONFIG["connects_multiplier"])
    
    if sub.dry_run:
        return {
            "status": "dry_run_preview",
            "job_id": sub.job_id,
            "bid_amount_usd": sub.bid_amount_usd,
            "connects_cost": connects_required,
            "current_connects_balance": USER_CONNECTS.get(sub.user_id, 120),
            "will_succeed": USER_CONNECTS.get(sub.user_id, 120) >= connects_required,
            "proposal_preview": {
                "cover_letter_snippet": sub.cover_letter[:150] + "...",
                "screening_answers_count": len(sub.screening_answers)
            }
        }
        
    # Check balance
    curr_balance = USER_CONNECTS.get(sub.user_id, 120)
    if curr_balance < connects_required:
        raise HTTPException(status_code=400, detail=f"Insufficient connects. Required: {connects_required}, Available: {curr_balance}")
        
    # Deduct connects
    USER_CONNECTS[sub.user_id] = curr_balance - connects_required
    
    # Simulate Client Evaluation Heuristic / Decision
    outcome = "viewed"
    reply_message = None
    
    # Generic opening penalty check
    is_generic = any(sub.cover_letter.lower().startswith(g) for g in ["dear hiring manager", "hello sir", "i am an expert", "hi, i have 10 years"])
    has_evidence = bool(re.search(r'(case study|benchmark|deployed|reduced|increased|\d+%)', sub.cover_letter, re.IGNORECASE))
    
    # Decide outcome
    if not is_generic and has_evidence and sub.bid_amount_usd <= job.get("budget", {}).get("max", 1000) * 1.15:
        outcome = "replied"
        reply_message = f"Hi! Thanks for your detailed proposal on '{job['title']}'. We were impressed by your referenced experience. Could we schedule an introductory call to discuss timeline and specifics?"
    elif is_generic:
        outcome = "ignored"
    else:
        outcome = "viewed"
        
    proposal_record = {
        "proposal_id": f"prop-{uuid.uuid4().hex[:8]}",
        "job_id": sub.job_id,
        "user_id": sub.user_id,
        "bid_amount_usd": sub.bid_amount_usd,
        "connects_spent": connects_required,
        "remaining_connects": USER_CONNECTS[sub.user_id],
        "cover_letter": sub.cover_letter,
        "screening_answers": sub.screening_answers,
        "status": outcome,
        "created_at": time.time(),
        "client_reply": reply_message
    }
    
    PROPOSALS[proposal_record["proposal_id"]] = proposal_record
    IDEMPOTENCY_STORE[sub.idempotency_key] = proposal_record
    
    if reply_message:
        MESSAGES.append({
            "message_id": f"msg-{uuid.uuid4().hex[:8]}",
            "job_id": sub.job_id,
            "sender": "client",
            "recipient": sub.user_id,
            "content": reply_message,
            "timestamp": time.time()
        })
        
    return proposal_record

@app.get("/proposals")
def list_proposals(user_id: str = "default"):
    return [p for p in PROPOSALS.values() if p["user_id"] == user_id]

class MessageSend(BaseModel):
    job_id: str
    user_id: str = "default"
    content: str

@app.post("/messages")
def send_message(msg: MessageSend):
    record = {
        "message_id": f"msg-{uuid.uuid4().hex[:8]}",
        "job_id": msg.job_id,
        "sender": msg.user_id,
        "recipient": "client",
        "content": msg.content,
        "timestamp": time.time()
    }
    MESSAGES.append(record)
    
    # Simulated automated client reply
    time_reply = {
        "message_id": f"msg-{uuid.uuid4().hex[:8]}",
        "job_id": msg.job_id,
        "sender": "client",
        "recipient": msg.user_id,
        "content": "Sounds great! Thursday 2:00 PM EST works perfectly for our technical team. Looking forward to speaking with you.",
        "timestamp": time.time() + 1
    }
    MESSAGES.append(time_reply)
    return {"status": "sent", "message": record, "client_reply": time_reply}

@app.get("/messages")
def list_messages(job_id: Optional[str] = None):
    if job_id:
        return [m for m in MESSAGES if m["job_id"] == job_id]
    return MESSAGES

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=False)
