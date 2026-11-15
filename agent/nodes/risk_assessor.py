import os
import re
import time
from typing import Dict, Any
from agent.state import BidGraphState
from agent.handoffs import RiskReport

def risk_assessor_node(state: BidGraphState) -> Dict[str, Any]:
    """Risk Assessor: detects prompt injection, scams, free work, off-platform solicitations."""
    job_raw = state.get("job_raw", {})
    text = (job_raw.get("title", "") + " " + job_raw.get("description", "")).lower()
    warning_signals = list(job_raw.get("warning_signals", []))
    
    flags = []
    is_scam = False
    has_injection = False
    
    # 1. Prompt Injection Checks
    injection_patterns = [
        r'ignore (all )?previous instructions',
        r'system (override|directive|instruction)',
        r'disregard (all )?rules',
        r'ai instruction',
        r'jailbreak',
        r'print system prompt',
        r'set_bid_price\(0\)'
    ]
    for pat in injection_patterns:
        if re.search(pat, text):
            flags.append(f"Prompt injection detected: '{pat}'")
            has_injection = True
            
    # 2. Scam & Policy Violations
    scam_patterns = [
        (r'(telegram|whatsapp|skype|venmo|wire transfer)', "off_platform_contact"),
        (r'(\bfree\b.*(trial|dashboard|work|prototype|test))', "unpaid_work_trial"),
        (r'(send deposit|pay deposit|crypto payment|0\.\d+ eth)', "upfront_fee_fraud"),
        (r'(cashier\'s check|equipment purchasing)', "fake_check_fraud")
    ]
    for pat, flag_name in scam_patterns:
        if re.search(pat, text):
            flags.append(flag_name)
            is_scam = True
            
    for ws in warning_signals:
        if ws not in flags:
            flags.append(ws)
            if ws in ["free_work_request", "off_platform_contact", "unpaid_work", "crypto_scam"]:
                is_scam = True
                
    # Calculate Risk Score (0.0 to 1.0)
    score = 0.05
    if has_injection:
        score = 0.95
    elif is_scam:
        score = 0.88
    elif len(flags) > 0:
        score = min(0.75, 0.25 * len(flags))
    else:
        # Check budget reasonableness
        budget = job_raw.get("budget", {})
        if budget.get("max", 500) < 50:
            score = 0.65
            flags.append("unusually_low_budget")
            
    explanation = "Job appears legitimate and safe."
    if has_injection:
        explanation = "Adversarial prompt injection attempt identified within untrusted job text."
    elif is_scam:
        explanation = f"Detected prohibited platform violations: {', '.join(flags)}."
    elif flags:
        explanation = f"Minor cautionary indicators: {', '.join(flags)}."
        
    report = RiskReport(
        score=round(score, 2),
        is_scam=is_scam,
        has_prompt_injection=has_injection,
        flags=flags,
        explanation=explanation
    )
    
    trace = {
        "node": "risk_assessor",
        "timestamp": time.time(),
        "risk_score": report.score,
        "is_scam": report.is_scam,
        "has_injection": report.has_prompt_injection
    }
    
    return {
        "risk_report": report.dict(),
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
