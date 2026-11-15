import os
import json
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAS_DIR = os.path.join(BASE_DIR, "data", "personas")

class CorpusChunk:
    def __init__(self, chunk_id: str, persona_id: str, doc_type: str, title: str, text: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.persona_id = persona_id
        self.doc_type = doc_type  # 'case_study', 'proposal', 'review', 'cv'
        self.title = title
        self.text = text
        self.metadata = metadata

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "persona_id": self.persona_id,
            "doc_type": self.doc_type,
            "title": self.title,
            "text": self.text,
            "metadata": self.metadata
        }

def load_all_chunks(persona_id: str = "sample-ai-engineer") -> List[CorpusChunk]:
    chunks = []
    p_dir = os.path.join(PERSONAS_DIR, persona_id)
    if not os.path.exists(p_dir):
        p_dir = os.path.join(PERSONAS_DIR, "sample-ai-engineer")

    # 1. Ingest Case Studies
    cs_file = os.path.join(p_dir, "case_studies.json")
    if os.path.exists(cs_file):
        with open(cs_file, "r", encoding="utf-8") as f:
            studies = json.load(f)
            for cs in studies:
                full_text = f"Title: {cs['title']}\nIndustry: {cs['client_industry']}\nSkills: {', '.join(cs['skills'])}\nProblem: {cs['problem']}\nSolution: {cs['solution']}\nMetrics: {cs['outcome_metrics']}"
                chunks.append(CorpusChunk(
                    chunk_id=cs["id"],
                    persona_id=persona_id,
                    doc_type="case_study",
                    title=cs["title"],
                    text=full_text,
                    metadata={
                        "skills": cs["skills"],
                        "industry": cs["client_industry"],
                        "date": cs["date"],
                        "outcome": "completed",
                        "metrics": cs["outcome_metrics"]
                    }
                ))

    # 2. Ingest Past Proposals
    pr_file = os.path.join(p_dir, "past_proposals.json")
    if os.path.exists(pr_file):
        with open(pr_file, "r", encoding="utf-8") as f:
            proposals = json.load(f)
            for pr in proposals:
                full_text = f"Proposal for {pr['job_title']}: {pr['cover_letter']}"
                chunks.append(CorpusChunk(
                    chunk_id=pr["proposal_id"],
                    persona_id=persona_id,
                    doc_type="proposal",
                    title=pr["job_title"],
                    text=full_text,
                    metadata={
                        "skills": pr["relevance_skills"],
                        "outcome": pr["outcome"],
                        "bid_amount": pr["bid_amount_usd"],
                        "date": pr["date"]
                    }
                ))

    # 3. Ingest Reviews
    rev_file = os.path.join(p_dir, "reviews.json")
    if os.path.exists(rev_file):
        with open(rev_file, "r", encoding="utf-8") as f:
            reviews = json.load(f)
            for rev in reviews:
                full_text = f"Client Review ({rev['rating']}/5.0) on {rev['project_name']}: {rev['comment']}"
                chunks.append(CorpusChunk(
                    chunk_id=rev["review_id"],
                    persona_id=persona_id,
                    doc_type="review",
                    title=rev["project_name"],
                    text=full_text,
                    metadata={"rating": rev["rating"], "date": rev["date"]}
                ))

    return chunks
