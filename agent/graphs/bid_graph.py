from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent.state import BidGraphState
from agent.nodes.scout import scout_node
from agent.nodes.analyst import analyst_node
from agent.nodes.risk_assessor import risk_assessor_node
from agent.nodes.fit_matcher import fit_matcher_node
from agent.nodes.decision import decision_node
from agent.nodes.pricing import pricing_node
from agent.nodes.writer import writer_node
from agent.nodes.verifier import verifier_node
from agent.nodes.critic import critic_node
from agent.nodes.compliance import compliance_node
from agent.nodes.approval import approval_gate_node, submission_node

def route_after_decision(state: BidGraphState) -> str:
    decision = state.get("bid_decision") or {}
    action = decision.get("action", "skip")
    if action == "bid":
        return "pricing"
    return END

def route_after_critic(state: BidGraphState) -> str:
    critique_history = state.get("critique_history") or []
    if not critique_history:
        return "compliance"
    latest = critique_history[-1]
    iteration = state.get("critic_iteration", 1)
    
    # Loop back at most twice
    if not latest.get("approved", True) and iteration <= 2:
        return "writer"
    return "compliance"

def build_bid_graph(checkpointer=None):
    """Assembles the hand-built LangGraph Bid Graph with parallel branches,
    bounded critique loops, and human-in-the-loop approval interrupts.
    """
    builder = StateGraph(BidGraphState)
    
    # Add Nodes
    builder.add_node("scout", scout_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("risk_assessor", risk_assessor_node)
    builder.add_node("fit_matcher", fit_matcher_node)
    builder.add_node("decision", decision_node)
    builder.add_node("pricing", pricing_node)
    builder.add_node("writer", writer_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("critic", critic_node)
    builder.add_node("compliance", compliance_node)
    builder.add_node("approval_gate", approval_gate_node)
    builder.add_node("submission", submission_node)
    
    # Start -> Scout
    builder.add_edge(START, "scout")
    
    # Scout -> Parallel Analysis Branches
    builder.add_edge("scout", "analyst")
    builder.add_edge("scout", "risk_assessor")
    builder.add_edge("scout", "fit_matcher")
    
    # Parallel Branches Join -> Decision Node
    builder.add_edge("analyst", "decision")
    builder.add_edge("risk_assessor", "decision")
    builder.add_edge("fit_matcher", "decision")
    
    # Decision Router: bid -> pricing, skip/watch -> END
    builder.add_conditional_edges(
        "decision",
        route_after_decision,
        {"pricing": "pricing", END: END}
    )
    
    # Linear proposal flow
    builder.add_edge("pricing", "writer")
    builder.add_edge("writer", "verifier")
    builder.add_edge("verifier", "critic")
    
    # Critic loop (at most 2 revisions)
    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {"writer": "writer", "compliance": "compliance"}
    )
    
    # Compliance -> Approval Interrupt -> Submission -> END
    builder.add_edge("compliance", "approval_gate")
    builder.add_edge("approval_gate", "submission")
    builder.add_edge("submission", END)
    
    saver = checkpointer or MemorySaver()
    return builder.compile(checkpointer=saver)

# Default compiled graph
bid_graph = build_bid_graph()
