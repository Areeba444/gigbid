# GigBid Operations & Deployment Runbook

## 1. Quick Start Locally
To run the complete GigBid stack locally:

```bash
# 1. Setup virtual environment & dependencies
python -m pip install -r pyproject.toml

# 2. Configure environment
cp .env.example .env
# Ensure GROQ_API_KEY is populated

# 3. Build & generate all datasets and personas
python data/build_datasets.py

# 4. Start GigSim Marketplace Simulator (Port 8001)
python gigsim/server.py

# 5. Start GigBid API & Web Application (Port 8000)
python apps/api/main.py
```

Open `http://localhost:8000` in any web browser to access the full-stack dashboard.

## 2. Reviewer Login Credentials
- **Email**: `reviewer@gigbid.ai`
- **Password**: `gigbid2026!`
- **Preloaded Persona**: Alex Morgan (Senior AI/ML & LLM Systems Engineer)

## 3. Switching Between GigSim & Live Upwork
In `agent/config.yaml` or `.env`:
- To run against local simulator: set `MARKETPLACE_MODE=gigsim`
- To run in live Upwork mode: set `MARKETPLACE_MODE=upwork_live` and provide `UPWORK_ACCESS_TOKEN`
- *Note*: Live mode strictly generates unsubmitted drafts on Upwork; it never spends Connects or submits without explicit human confirmation.

## 4. Degraded Mode & Failure Recovery
- If the Marketplace MCP server is temporarily offline:
  1. The Web UI displays an alert banner: "Marketplace Port Degraded".
  2. In-flight proposal drafts are preserved in the Postgres/Memory checkpointer.
  3. Work is queued in background state; restarting the service immediately allows the reviewer to resume the thread without duplicate submission.
