import math
from typing import List, Dict, Any
from collections import Counter
from rank_bm25 import BM25Okapi
from rag.ingest.chunker import CorpusChunk
from rag.variants.v0_naive import V0NaiveRetriever, tokenize

class V2HybridRRFRetriever:
    """V2: Hybrid BM25 + Dense with Reciprocal Rank Fusion (RRF)."""
    def __init__(self, chunks: List[CorpusChunk]):
        self.chunks = chunks
        self.corpus_tokens = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        self.dense = V0NaiveRetriever(chunks)

    def retrieve(self, query: str, k: int = 5, rrf_k: int = 60) -> List[Dict[str, Any]]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return self.dense.retrieve(query, k=k)

        # 1. BM25 ranking
        bm25_scores = self.bm25.get_scores(q_tokens)
        bm25_ranked_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)

        # 2. Dense ranking
        dense_hits = self.dense.retrieve(query, k=len(self.chunks))
        dense_chunk_to_rank = {h["chunk_id"]: rank for rank, h in enumerate(dense_hits)}

        # 3. Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}
        for rank_bm25, idx in enumerate(bm25_ranked_indices):
            c_id = self.chunks[idx].chunk_id
            rank_dense = dense_chunk_to_rank.get(c_id, len(self.chunks))
            rrf_scores[c_id] = (1.0 / (rrf_k + rank_bm25 + 1)) + (1.0 / (rrf_k + rank_dense + 1))

        # Build output
        id_to_chunk = {c.chunk_id: c.to_dict() for c in self.chunks}
        sorted_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        results = []
        for cid in sorted_ids[:k]:
            item = id_to_chunk[cid]
            item["retrieval_score"] = round(rrf_scores[cid], 5)
            results.append(item)
        return results
