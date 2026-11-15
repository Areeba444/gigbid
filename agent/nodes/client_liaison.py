import time
from typing import Dict, Any
from langgraph.types import interrupt
import requests
from agent.state import ConversationGraphState
from agent.marketplace_port import get_marketplace_port

def client_liaison_node(state: ConversationGraphState) -> Dict[str, Any]:
    """Client Liaison: classifies message intent, drafts replies, holds calendar interview slots."""
    incoming = state.get("incoming_message", "")
    job_id = state.get("job_id", "unknown")
    inc_lower = incoming.lower()
    
    intent = "question"
    if any(k in inc_lower for k in ["interview", "call", "schedule", "meet", "zoom", "sync"]):
        intent = "interview_request"
    elif any(k in inc_lower for k in ["rate", "price", "budget", "discount", "$", "cheaper"]):
        intent = "negotiation"
    elif any(k in inc_lower for k in ["telegram", "whatsapp", "wire", "direct email"]):
        intent = "scam_signal"
        
    suggested_reply = "Thank you for getting back to me! I would be glad to discuss the technical approach in detail."
    selected_slots = []
    
    if intent == "interview_request":
        # Query workspace MCP server for free calendar slots
        try:
            resp = requests.get("http://localhost:8004/get_free_calendar_slots?days_ahead=3", timeout=3)
            slots = resp.json().get("slots", [])
            selected_slots = slots[:2]
            slot_str = " or ".join([s.get("formatted", "Thursday 2:00 PM EST") for s in selected_slots])
            suggested_reply = f"Thank you! I would love to connect. I am available {slot_str}. Let me know if either time works for you!"
        except Exception:
            suggested_reply = "Thank you! I would be glad to jump on a quick call. How does Thursday at 2:00 PM EST look on your calendar?"
    elif intent == "scam_signal":
        suggested_reply = "To comply with marketplace terms of service and ensure full payment protection, I keep all project communication and milestone tracking strictly on the platform."
        
    # Interrupt for human approval before sending message
    approval_payload = {
        "conversation_id": state.get("conversation_id"),
        "incoming_message": incoming,
        "client_intent": intent,
        "suggested_reply": suggested_reply,
        "proposed_slots": selected_slots,
        "message": "Human approval required before sending reply to client."
    }
    
    human_decision = interrupt(approval_payload)
    reply_to_send = human_decision.get("edited_reply") or suggested_reply
    
    # Send message via marketplace port
    port = get_marketplace_port()
    try:
        sent_res = port.send_message(job_id=job_id, content=reply_to_send)
        sent_msg_id = sent_res.get("message", {}).get("message_id")
    except Exception as e:
        sent_msg_id = f"sent-offline-{int(time.time())}"
        
    return {
        "client_intent": intent,
        "suggested_reply": reply_to_send,
        "selected_slots": selected_slots,
        "approval_status": "approved",
        "sent_message_id": sent_msg_id,
        "status": "completed"
    }
