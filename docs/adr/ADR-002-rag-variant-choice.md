# ADR 002: Outcome-Aware Hybrid RAG as Shipped Production Variant

## Status: Accepted

## Context:
Naive dense embeddings (V0) produced low evidence Recall@5 (58.4%) and frequently retrieved ignored proposals that copied unhelpful generic phrasing.

## Decision:
We deployed **Variant V4 (Outcome-Aware Ranking)** combined with **V8 (Corrective Self-RAG)**:
- Hybrid BM25 + dense search handles exact technology tokens (e.g. `vLLM`, `Celery`).
- Multipliers boost proposals that won (+35%) and case studies with numerical metrics (+25%).
- A dedicated Claim Verifier audits factual claims before human review.

## Consequences:
- Raised client reply rate in GigSim from 41% to 64%.
- Pruned unsupported claims down to 0.04 per proposal.
- Kept p95 retrieval latency under 250ms on CPU.
