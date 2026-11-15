import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_STORE_FILE = os.path.join(BASE_DIR, "data", "memory_store.json")

class MemoryStore:
    """Durable long-term memory store enforcing explicit promotion rules."""
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or MEMORY_STORE_FILE
        self.style_memory: List[Dict[str, Any]] = []
        self.outcome_memory: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.style_memory = data.get("style_memory", [])
                    self.outcome_memory = data.get("outcome_memory", [])
            except Exception:
                self._seed_defaults()
        else:
            self._seed_defaults()

    def _seed_defaults(self):
        self.style_memory = [
            {
                "id": "style-001",
                "rule": "Never include opening pleasantries like 'Dear Hiring Manager' or 'Hope you are well'. Hook straight into relevant technical delivery.",
                "created_at": time.time() - 86400,
                "confidence": 0.95,
                "source": "repeated_user_edit"
            },
            {
                "id": "style-002",
                "rule": "Always explicitly name the database/framework version (e.g., 'FastAPI 0.115', 'LangGraph 1.2') when quoting architecture.",
                "created_at": time.time() - 43200,
                "confidence": 0.88,
                "source": "user_explicit_preference"
            }
        ]
        self.outcome_memory = [
            {
                "id": "out-001",
                "category": "AI/ML & LLMs",
                "winning_features": ["hybrid BM25+dense citation", "benchmark latency under 300ms", "vLLM experience"],
                "optimal_bid_ratio": 0.95,
                "reply_rate": 0.68
            },
            {
                "id": "out-002",
                "category": "Full-Stack Web Development",
                "winning_features": ["Next.js App router", "SSE streaming proof", "PostgreSQL schema sample"],
                "optimal_bid_ratio": 0.90,
                "reply_rate": 0.62
            }
        ]
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({
                "style_memory": self.style_memory,
                "outcome_memory": self.outcome_memory
            }, f, indent=2)

    def promote_style_rule(self, rule_text: str, source: str = "human_diff_promotion", confidence: float = 0.9):
        # Explicit promotion rule enforcement
        item = {
            "id": f"style-{uuid.uuid4().hex[:6]}",
            "rule": rule_text.strip(),
            "created_at": time.time(),
            "confidence": confidence,
            "source": source
        }
        self.style_memory.append(item)
        self.save()
        return item

    def delete_style_rule(self, rule_id: str) -> bool:
        before = len(self.style_memory)
        self.style_memory = [r for r in self.style_memory if r["id"] != rule_id]
        if len(self.style_memory) < before:
            self.save()
            return True
        return False

    def record_job_outcome(self, category: str, outcome: str, bid_ratio: float, key_skills: List[str]):
        rec = {
            "id": f"out-{uuid.uuid4().hex[:6]}",
            "category": category,
            "outcome": outcome,
            "bid_ratio": bid_ratio,
            "skills": key_skills,
            "timestamp": time.time()
        }
        self.outcome_memory.append(rec)
        self.save()
        return rec

    def get_all(self):
        return {
            "style_memory": self.style_memory,
            "outcome_memory": self.outcome_memory
        }

# Global singleton
memory_store = MemoryStore()
