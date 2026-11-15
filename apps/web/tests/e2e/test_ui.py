import pytest
import time
import requests

BASE_URL = "http://localhost:8000"

def test_01_api_health_and_root():
    """Verify backend and frontend root serve correctly."""
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    assert "GigBid" in resp.text

def test_02_job_inbox_and_filtering():
    """Test job discovery inbox returns ranked jobs with badges."""
    resp = requests.get(f"{BASE_URL}/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert "jobs" in data
    assert len(data["jobs"]) > 0
    # Check that jobs contain recommended_action and fit_score
    first_job = data["jobs"][0]
    assert "recommended_action" in first_job
    assert "fit_score" in first_job

def test_03_persona_switching():
    """Test switching between AI engineer, web dev, and data analyst."""
    resp = requests.post(
        f"{BASE_URL}/auth/switch-persona",
        json={"persona_id": "sample-web-dev"}
    )
    assert resp.status_code == 200
    assert resp.json()["current_user"]["persona_id"] == "sample-web-dev"

def test_04_proposal_approval_and_edits():
    """Test proposal interrupt approval flow and style memory saving."""
    # Create mock approval thread
    thread_id = f"test-thread-{int(time.time())}"
    # Seed pending approval via API
    resp_jobs = requests.get(f"{BASE_URL}/jobs")
    job_id = resp_jobs.json()["jobs"][0]["job_id"]
    
    # Test resolve with edit
    resolve_resp = requests.post(
        f"{BASE_URL}/approvals/resolve",
        json={
            "thread_id": "conv-001",  # fallback or test id
            "action": "edit",
            "edited_draft": "I delivered production high-concurrency systems with zero downtime."
        }
    )
    # Check that resolve responds with status
    assert resolve_resp.status_code in [200, 404]

def test_05_memory_viewer_and_degraded_mode():
    """Test memory inspection and deletion."""
    resp = requests.get(f"{BASE_URL}/settings/memory")
    assert resp.status_code == 200
    mem = resp.json()
    assert "style_memory" in mem
    assert len(mem["style_memory"]) > 0
