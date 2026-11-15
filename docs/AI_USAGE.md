# AI Usage Disclosure (AI-4016 Compliance)

In accordance with course academic integrity guidelines, this document records the usage of AI coding assistants during the development of GigBid.

## 1. Tools & Models Used
- **Antigravity / Claude Code**: Architecture scaffolding, drafting state schemas, test specs, and dataset synthesis scripts.
- **Groq Hosted Open Models**: `openai/gpt-oss-20b` (fast router, classifier, and verifier) and `qwen/qwen3.8-27b` (proposal writer and critic).

## 2. Files Generated & Assisted
- `agent/graphs/bid_graph.py` & `conversation_graph.py`: StateGraph wiring and interrupt handling.
- `rag/variants/`: Hybrid BM25, RRF rank fusion, and outcome-aware retrieval.
- `apps/api/main.py`: FastAPI routes, SSE streaming bridge, and OpenAPI contracts.
- `apps/web/public/index.html`: Responsive full-stack dashboard with evidence hover and Kanban board.

## 3. Discrepancy Caught & Corrected
During initial graph assembly, the Critic node was configured with a hard retry threshold that caused an infinite oscillation loop on drafts exceeding word count limits by less than 10 words. We caught this failure in `evals/results/failure_taxonomy.json` (Item `FAIL-010`) and corrected it by bounding the conditional edge to a maximum of 2 revision passes before forcing the proposal through the compliance and human approval gates.
