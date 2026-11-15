from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent.state import ConversationGraphState
from agent.nodes.client_liaison import client_liaison_node

def build_conversation_graph(checkpointer=None):
    """Conversation graph: Client Liaison handles client replies, intent classification,
    interview slot selection, and interrupts for human approval before sending.
    """
    builder = StateGraph(ConversationGraphState)
    builder.add_node("client_liaison", client_liaison_node)
    
    builder.add_edge(START, "client_liaison")
    builder.add_edge("client_liaison", END)
    
    saver = checkpointer or MemorySaver()
    return builder.compile(checkpointer=saver)

conversation_graph = build_conversation_graph()
