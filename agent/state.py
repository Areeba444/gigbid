import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from agent.handoffs import (
    JobSpec, RiskReport, FitReport, BidDecision,
    PriceQuote, ProposalDraft, Critique, ComplianceVerdict
)

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(a)
    res.update(b)
    return res

class BidGraphState(TypedDict, total=False):
    # Core Job Context
    job_id: str
    job_raw: Dict[str, Any]
    persona_id: str
    
    # Parallel Analysis Handoffs (written concurrently by analyst, risk, fit)
    job_spec: Optional[Dict[str, Any]]
    risk_report: Optional[Dict[str, Any]]
    fit_report: Optional[Dict[str, Any]]
    
    # Decisions & Strategy
    bid_decision: Optional[Dict[str, Any]]  # action: 'bid', 'skip', 'watch'
    price_quote: Optional[Dict[str, Any]]
    
    # Drafting & Evidence
    evidence_items: List[Dict[str, Any]]
    proposal_draft: Optional[Dict[str, Any]]
    claim_verification: Optional[Dict[str, Any]]
    
    # Critique & Compliance
    critique_history: Annotated[List[Dict[str, Any]], operator.add]
    critic_iteration: int
    compliance_verdict: Optional[Dict[str, Any]]
    
    # Human in the loop approval
    approval_status: str  # 'pending', 'approved', 'rejected', 'edited'
    human_feedback: Optional[str]
    human_edited_draft: Optional[str]
    
    # Submission result
    submission_result: Optional[Dict[str, Any]]
    
    # Observability & Tracing
    execution_trace: Annotated[List[Dict[str, Any]], operator.add]
    step_count: int
    total_tokens: int
    status: str  # 'running', 'interrupted', 'completed', 'skipped', 'failed'
    errors: Annotated[List[str], operator.add]

class ConversationGraphState(TypedDict, total=False):
    conversation_id: str
    job_id: str
    client_id: str
    incoming_message: str
    client_intent: str  # 'question', 'negotiation', 'interview_request', 'scam_signal'
    suggested_reply: Optional[str]
    selected_slots: List[Dict[str, Any]]
    approval_status: str
    sent_message_id: Optional[str]
    status: str
