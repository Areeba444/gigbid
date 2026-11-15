import math
from typing import List, Dict, Any
from collections import Counter
from rag.ingest.chunker import CorpusChunk

def tokenize(text: str) -> List[str]:
    import re
    return re.findall(r'\b[a-zA-Z0-9_\-\.]{2,}\b', text.lower())

class V0NaiveRetriever:
    """Baseline V0: Naive dense/term similarity on the full raw job post."""
    def __init__(self, chunks: List[CorpusChunk]):
        self.chunks = chunks
        self.doc_tokens = [tokenize(c.text) for c in chunks]
        self.vocab = set(t for tokens in self.doc_tokens for t in tokens)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return [c.to_dict() for c in self.chunks[:k]]

        q_counter = Counter(q_tokens)
        scored = []
        for i, c in enumerate(self.chunks):
            d_counter = Counter(self.doc_tokens[i])
            # Cosine similarity approximation
            dot = sum(q_counter[t] * d_counter[t] for t in q_counter if t in d_counter)
            norm_q = math.sqrt(sum(v*v for v in q_counter.values()))
            norm_d = math.sqrt(sum(v*v for v in d_counter.values()))
            sim = dot / ((norm_q * norm_d) + 1e-6)
            res = c.to_dict()
            res["retrieval_score"] = round(sim, 4)
            scored.append(res)

        scored.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return scored[:k]
