import os
import json
import time
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="GigBid Workspace MCP Server", version="1.0.0")

INTERVIEW_HOLDS: List[Dict[str, Any]] = []
EMAIL_DRAFTS: List[Dict[str, Any]] = []

@app.get("/tools")
def list_tools():
    return [
        {
            "name": "get_free_calendar_slots",
            "description": "Fetch upcoming available calendar slots for scheduling client interviews.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer", "default": 5},
                    "timezone": {"type": "string", "default": "UTC"}
                }
            },
            "annotations": {"readOnlyHint": True, "idempotentHint": True}
        },
        {
            "name": "create_tentative_interview_hold",
            "description": "Block a tentative interview slot on the calendar pending client confirmation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "slot_time": {"type": "string"},
                    "client_name": {"type": "string"},
                    "job_id": {"type": "string"}
                },
                "required": ["slot_time", "job_id"]
            },
            "annotations": {"destructiveHint": True, "idempotentHint": True}
        },
        {
            "name": "create_email_draft",
            "description": "Create a preliminary email draft for client follow-up.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "recipient_email": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["recipient_email", "subject", "body"]
            },
            "annotations": {"destructiveHint": False, "idempotentHint": True}
        }
    ]

@app.get("/get_free_calendar_slots")
def get_free_calendar_slots(days_ahead: int = 5, timezone: str = "UTC"):
    # Generate realistic open slots for the next 5 business days
    base_timestamp = time.time() + 86400  # tomorrow
    slots = []
    days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Monday"]
    times = ["10:00 AM", "2:00 PM", "4:30 PM"]
    
    for d_idx, day_name in enumerate(days[:days_ahead]):
        for t in times:
            slots.append({
                "slot_id": f"slot-{d_idx}-{t.replace(' ', '').replace(':', '')}",
                "day": day_name,
                "time": t,
                "timezone": timezone,
                "formatted": f"{day_name} at {t} {timezone}"
            })
    return {"timezone": timezone, "slots": slots}

class HoldModel(BaseModel):
    slot_time: str
    client_name: str = "Client"
    job_id: str

@app.post("/create_tentative_interview_hold")
def create_tentative_interview_hold(hold: HoldModel):
    record = {
        "hold_id": f"hold-{uuid.uuid4().hex[:6]}",
        "slot_time": hold.slot_time,
        "client_name": hold.client_name,
        "job_id": hold.job_id,
        "created_at": time.time(),
        "status": "tentative_hold"
    }
    INTERVIEW_HOLDS.append(record)
    return {"status": "hold_created", "hold": record}

class EmailDraftModel(BaseModel):
    recipient_email: str
    subject: str
    body: str

@app.post("/create_email_draft")
def create_email_draft(draft: EmailDraftModel):
    record = {
        "draft_id": f"draft-{uuid.uuid4().hex[:6]}",
        "recipient": draft.recipient_email,
        "subject": draft.subject,
        "body": draft.body,
        "created_at": time.time()
    }
    EMAIL_DRAFTS.append(record)
    return {"status": "draft_created", "draft": record}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_servers.workspace.server:app", host="0.0.0.0", port=8004, reload=False)
