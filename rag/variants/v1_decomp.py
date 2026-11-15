from typing import List, Dict, Any
from rag.ingest.chunker import CorpusChunk
from rag.variants.v0_naive import V0NaiveRetriever, tokenize

class V1RequirementDecompositionRetriever:
    """V1: Requirement decomposition - decomposes query into separate requirements and merges."""
    def __init__(self, chunks: List[CorpusChunk]):
        self.base_retriever = V0NaiveRetriever(chunks)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # Split query by bullet points, sentences, or commas
        sub_queries = [s.strip() for s in query.replace('\n', ';').split(';') if len(s.strip()) > 5]
        if not sub_queries:
            sub_queries = [query]

        merged_scores: Dict[str, Dict[str, Any]] = {}
        for sub_q in sub_queries:
            hits = self.base_retriever.retrieve(sub_q, k=k)
            for h in hits:
                c_id = h["chunk_id"]
                if c_id not in merged_scores:
                    merged_scores[c_id] = h
                    merged_scores[c_id]["retrieval_score"] = h["retrieval_score"]
                else:
                    merged_scores[c_id]["retrieval_score"] += h["retrieval_score"]

        ranked = sorted(merged_scores.values(), key=lambda x: x["retrieval_score"], reverse=True)
        return ranked[:k]
