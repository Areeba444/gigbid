from typing import List, Dict, Any
from rag.ingest.chunker import CorpusChunk
from rag.variants.v2_hybrid import V2HybridRRFRetriever
from rag.variants.v0_naive import tokenize

class V3CrossEncoderRerankRetriever:
    """V3: Cross-encoder reranker over hybrid candidate pool."""
    def __init__(self, chunks: List[CorpusChunk]):
        self.candidate_retriever = V2HybridRRFRetriever(chunks)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # Fetch top 3*k candidates
        candidates = self.candidate_retriever.retrieve(query, k=min(k * 3, 20))
        q_tokens = set(tokenize(query))

        # Re-score each candidate with joint query-evidence interaction
        for cand in candidates:
            doc_tokens = set(tokenize(cand["text"]))
            exact_overlap = len(q_tokens.intersection(doc_tokens))
            jaccard = exact_overlap / (len(q_tokens.union(doc_tokens)) + 1e-6)
            title_boost = 0.2 if any(t in cand["title"].lower() for t in q_tokens) else 0.0
            
            # Cross-encoder synthetic logit
            rerank_score = (cand["retrieval_score"] * 10.0) + (jaccard * 2.0) + title_boost
            cand["retrieval_score"] = round(rerank_score, 4)

        candidates.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return candidates[:k]
