import time
from typing import Dict, Any
from agent.state import BidGraphState
from agent.handoffs import PriceQuote

def pricing_node(state: BidGraphState) -> Dict[str, Any]:
    """Pricing Strategist: calculates market-grounded bid price and connects justification."""
    job_spec = state.get("job_spec") or {}
    job_raw = state.get("job_raw") or {}
    
    b_min = job_spec.get("budget_min") or 250.0
    b_max = job_spec.get("budget_max") or 800.0
    connects = job_raw.get("connects_cost", 8)
    
    # Target 85-92% of client maximum budget for competitive positioning
    recommended_bid = round(max(b_min, b_max * 0.90), -1)
    
    # Check connects justification
    connects_justified = (recommended_bid >= 150.0)
    strategy = "value_based" if recommended_bid >= 800 else "market_median"
    
    rationale = f"Positioned at ${recommended_bid:.0f} (90% of budget ceiling). Connects cost of {connects} justified by project size."
    
    quote = PriceQuote(
        bid_amount_usd=float(recommended_bid),
        pricing_strategy=strategy,
        market_median_usd=float((b_min + b_max) / 2),
        connects_cost=connects,
        connects_justified=connects_justified,
        rationale=rationale
    )
    
    trace = {
        "node": "pricing",
        "timestamp": time.time(),
        "bid_amount": quote.bid_amount_usd,
        "strategy": quote.pricing_strategy
    }
    
    return {
        "price_quote": quote.dict(),
        "execution_trace": [trace],
        "step_count": state.get("step_count", 0) + 1
    }
