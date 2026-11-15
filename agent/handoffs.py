from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobSpec(BaseModel):
    job_id: str
    title: str
    deliverables: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    screening_questions: List[str] = Field(default_factory=list)
    duration_days: Optional[int] = None
    hidden_needs: List[str] = Field(default_factory=list)

class RiskReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="0=safe, 1=extreme risk")
    is_scam: bool = False
    has_prompt_injection: bool = False
    flags: List[str] = Field(default_factory=list)
    explanation: str

class FitReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="0=unfit, 1=perfect fit")
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    evidence_details: List[Dict[str, Any]] = Field(default_factory=list)
    reasons: str = Field(default="Matched skills")

class BidDecision(BaseModel):
    action: str = Field(description="'bid', 'skip', or 'watch'")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

class PriceQuote(BaseModel):
    bid_amount_usd: float
    pricing_strategy: str  # 'value_based', 'market_median', 'floor_rate'
    market_median_usd: Optional[float] = None
    connects_cost: int = 8
    connects_justified: bool = True
    rationale: str

class ProposalDraft(BaseModel):
    job_id: str
    cover_letter: str
    screening_answers: List[str] = Field(default_factory=list)
    evidence_citations: List[Dict[str, Any]] = Field(default_factory=list)
    unsupported_claims_removed: int = 0
    version: int = 1

class Critique(BaseModel):
    approved: bool
    grounding_score: float = Field(ge=0.0, le=1.0)
    personalization_score: float = Field(ge=0.0, le=1.0)
    length_verdict: str  # 'optimal', 'too_short', 'too_long'
    feedback: str
    iteration: int = 1

class ComplianceVerdict(BaseModel):
    compliant: bool
    violations_detected: List[str] = Field(default_factory=list)
    redacted_contact_info: bool = False
    policy_notes: str
