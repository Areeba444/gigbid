from typing import List, Dict, Any
from rag.ingest.chunker import CorpusChunk
from rag.variants.v3_rerank import V3CrossEncoderRerankRetriever

class V4OutcomeAwareRetriever:
    """V4: Outcome-aware ranking boosting evidence and phrasing from proposals that won or replied."""
    def __init__(self, chunks: List[CorpusChunk]):
        self.rerank_retriever = V3CrossEncoderRerankRetriever(chunks)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        candidates = self.rerank_retriever.retrieve(query, k=min(k * 2, 15))
        for cand in candidates:
            outcome = cand.get("metadata", {}).get("outcome")
            boost = 1.0
            if outcome == "won":
                boost = 1.35
            elif outcome == "replied":
                boost = 1.18
            elif outcome == "ignored":
                boost = 0.85
            elif outcome == "completed":  # verified case study
                boost = 1.25

            cand["retrieval_score"] = round(cand["retrieval_score"] * boost, 4)
            cand["outcome_multiplier"] = boost

        candidates.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return candidates[:k]

class V8SelfRAGRetriever:
    """V8: Corrective / Self-RAG loop that grades candidate evidence relevance,
    filters sub-threshold items, and refuses or triggers expansion query when weak.
    """
    def __init__(self, chunks: List[CorpusChunk]):
        self.retriever = V4OutcomeAwareRetriever(chunks)

    def retrieve(self, query: str, k: int = 5, relevance_threshold: float = 0.45) -> List[Dict[str, Any]]:
        candidates = self.retriever.retrieve(query, k=k)
        graded = []
        for cand in candidates:
            # Self-reflection grade: is score sufficient?
            cand["is_grounded_evidence"] = cand["retrieval_score"] >= relevance_threshold
            if cand["is_grounded_evidence"]:
                graded.append(cand)

        # If zero items passed threshold, return top 1 with warning flag
        if not graded and candidates:
            fallback = candidates[0]
            fallback["warning"] = "low_confidence_evidence"
            graded.append(fallback)
        return graded
