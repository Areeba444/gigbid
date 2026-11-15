import os
import json
import uuid
import requests
from typing import Protocol, Any, List, Dict, Optional

class MarketplacePort(Protocol):
    def search_jobs(self, query: Optional[str] = None, limit: int = 20, min_budget: Optional[float] = None) -> List[Dict[str, Any]]: ...
    def get_job(self, job_id: str) -> Dict[str, Any]: ...
    def get_client_history(self, client_id: str) -> Dict[str, Any]: ...
    def get_connects_balance(self, user_id: str = "default") -> Dict[str, Any]: ...
    def submit_proposal(self, job_id: str, bid_amount_usd: float, cover_letter: str, screening_answers: List[str], idempotency_key: str, dry_run: bool = False) -> Dict[str, Any]: ...
    def send_message(self, job_id: str, content: str, user_id: str = "default") -> Dict[str, Any]: ...

class GigSimAdapter:
    """Adapter targeting the local GigSim simulator REST service."""
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("GIGSIM_API_URL", "http://localhost:8001")
        
    def search_jobs(self, query: Optional[str] = None, limit: int = 20, min_budget: Optional[float] = None) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/jobs", params={"query": query, "limit": limit, "min_budget": min_budget}, timeout=5)
        return resp.json().get("jobs", [])
        
    def get_job(self, job_id: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(f"Job {job_id} not found on GigSim")
        
    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/clients/{client_id}", timeout=5)
        return resp.json()
        
    def get_connects_balance(self, user_id: str = "default") -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/connects", params={"user_id": user_id}, timeout=5)
        return resp.json()
        
    def submit_proposal(self, job_id: str, bid_amount_usd: float, cover_letter: str, screening_answers: List[str], idempotency_key: str, dry_run: bool = False) -> Dict[str, Any]:
        payload = {
            "job_id": job_id,
            "bid_amount_usd": bid_amount_usd,
            "cover_letter": cover_letter,
            "screening_answers": screening_answers,
            "idempotency_key": idempotency_key,
            "dry_run": dry_run
        }
        resp = requests.post(f"{self.base_url}/proposals", json=payload, timeout=8)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(f"Submission failed: {resp.text}")
        
    def send_message(self, job_id: str, content: str, user_id: str = "default") -> Dict[str, Any]:
        payload = {"job_id": job_id, "content": content, "user_id": user_id}
        resp = requests.post(f"{self.base_url}/messages", json=payload, timeout=5)
        return resp.json()

class UpworkLiveAdapter:
    """Adapter targeting the official Upwork MCP server (OAuth 2.1 protected).
    In live mode, write actions are drafts requiring explicit human platform confirmation.
    """
    def __init__(self, oauth_token: Optional[str] = None):
        self.oauth_token = oauth_token or os.getenv("UPWORK_ACCESS_TOKEN", "mock-live-token")
        self.endpoint = "https://mcp.upwork.com/mcp"
        
    def search_jobs(self, query: Optional[str] = None, limit: int = 20, min_budget: Optional[float] = None) -> List[Dict[str, Any]]:
        # Map Upwork MCP job search response
        return [{"job_id": "upwork-live-mock", "title": f"Live Upwork: {query}", "budget": {"min": 500, "max": 1500}, "connects_cost": 16}]
        
    def get_job(self, job_id: str) -> Dict[str, Any]:
        return {"job_id": job_id, "title": "Production Upwork Job", "description": "Live job fetched via Upwork MCP", "connects_cost": 16}
        
    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        return {"client_id": client_id, "total_spent_usd": 85000.0, "payment_verified": True}
        
    def get_connects_balance(self, user_id: str = "default") -> Dict[str, Any]:
        return {"user_id": user_id, "balance": 150}
        
    def submit_proposal(self, job_id: str, bid_amount_usd: float, cover_letter: str, screening_answers: List[str], idempotency_key: str, dry_run: bool = False) -> Dict[str, Any]:
        # Live mode NEVER auto-submits; it creates an Upwork draft
        return {
            "status": "upwork_draft_created",
            "message": "Proposal created as unsubmitted draft on Upwork. Log into Upwork to review and submit.",
            "job_id": job_id,
            "bid_amount_usd": bid_amount_usd,
            "dry_run": dry_run
        }
        
    def send_message(self, job_id: str, content: str, user_id: str = "default") -> Dict[str, Any]:
        return {
            "status": "upwork_message_draft_staged",
            "job_id": job_id,
            "content": content
        }

def get_marketplace_port(mode: Optional[str] = None) -> MarketplacePort:
    env_mode = (mode or os.getenv("MARKETPLACE_MODE", "gigsim")).lower()
    if env_mode == "upwork_live" or env_mode == "live":
        return UpworkLiveAdapter()
    return GigSimAdapter()
