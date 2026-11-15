# GigBid Tool Catalog & MCP Surface

Every agent capability in GigBid is exposed strictly through Model Context Protocol (MCP) servers with explicit Pydantic schemas, declared input/output boundaries, and annotations.

## 1. Tool Surface Summary Table

| Tool Name | Server | Read / Write | Annotations | Authentication | Trust & Security Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `search_evidence` | `portfolio` (:8002) | Read | `readOnlyHint`, `idempotentHint` | Local Session | Read-only semantic search over verified local persona corpus. |
| `get_case_study` | `portfolio` (:8002) | Read | `readOnlyHint`, `idempotentHint` | Local Session | Returns verified historical project metrics. |
| `list_skills` | `portfolio` (:8002) | Read | `readOnlyHint`, `idempotentHint` | Local Session | Reads freelancer skill list without external egress. |
| `search_jobs` | `marketplace` (:8003)| Read | `readOnlyHint`, `idempotentHint` | Bearer Token | Reads jobs stream from GigSim or Upwork adapter with rate limiting. |
| `get_job` | `marketplace` (:8003)| Read | `readOnlyHint`, `idempotentHint` | Bearer Token | Fetches single job spec. |
| `get_client_history`| `marketplace` (:8003)| Read | `readOnlyHint`, `idempotentHint` | Bearer Token | Inspects verified client spend and feedback. |
| `get_connects_balance`| `marketplace` (:8003)| Read | `readOnlyHint`, `idempotentHint` | Bearer Token | Checks wallet balance. |
| `submit_proposal` | `marketplace` (:8003)| Write | `destructiveHint`, `idempotentHint` | Bearer + Human Gate | Requires idempotency key; supports `dry_run=True`; only called after human approval. |
| `send_message` | `marketplace` (:8003)| Write | `destructiveHint` | Bearer + Human Gate | Sends approved client replies; bounded rate limits. |
| `get_free_calendar_slots`| `workspace` (:8004)| Read | `readOnlyHint`, `idempotentHint` | Local / OAuth | Reads mock or official Google Calendar availability. |
| `create_tentative_interview_hold`| `workspace` (:8004)| Write | `destructiveHint`, `idempotentHint` | Local / OAuth | Temporarily blocks slot on calendar pending confirmation. |
| `create_email_draft`| `workspace` (:8004)| Write | `idempotentHint` | Local / OAuth | Creates draft email without auto-sending. |

## 2. Third-Party Servers Trust Rationale
1. **Official Upwork MCP Server (`https://mcp.upwork.com/mcp`)**:
   - *Trust Rationale*: Upwork's official OAuth 2.1 protected server. Never receives raw platform credentials; tokens are encrypted at rest per tenant; write actions only produce unsubmitted drafts on Upwork.
2. **GitHub MCP Server (`github.com/modelcontextprotocol/servers/tree/main/src/github`)**:
   - *Trust Rationale*: Official MCP reference server for ingesting open-source repository READMEs and code chunks. Read-only scope is enforced (`repo:read`); no write or administrative permissions granted.
