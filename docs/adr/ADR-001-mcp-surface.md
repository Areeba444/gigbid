# ADR 001: Separation of Concerns Across Three MCP Servers

## Status: Accepted

## Context:
Agents need access to portfolio evidence, marketplace actions (GigSim/Upwork), and calendar/email tools. Direct integration in agent nodes couples reasoning with external I/O and violates least-privilege security.

## Decision:
We partitioned capabilities into three distinct MCP servers:
1. `portfolio` (:8002): Strictly read-only access to CVs, case studies, and past proposals.
2. `marketplace` (:8003): Single port adapter wrapping GigSim and Upwork Live with idempotency keys and dry-run preview.
3. `workspace` (:8004): Calendar free slots and draft email holds.

## Consequences:
- High modularity: external tools like Claude Desktop can reuse the Portfolio server independently.
- Clean degraded mode: if Marketplace server is killed, Portfolio and Workspace remain operational.
