import os
from typing import List, Dict, Any, Optional
from rag.ingest.chunker import load_all_chunks
from rag.variants.v0_naive import V0NaiveRetriever
from rag.variants.v1_decomp import V1RequirementDecompositionRetriever
from rag.variants.v2_hybrid import V2HybridRRFRetriever
from rag.variants.v3_rerank import V3CrossEncoderRerankRetriever
from rag.variants.v4_outcome import V4OutcomeAwareRetriever, V8SelfRAGRetriever

def get_retriever(variant_name: str = "v4_outcome", persona_id: str = "sample-ai-engineer"):
    chunks = load_all_chunks(persona_id)
    var = variant_name.lower()
    if var in ["v0", "v0_naive"]:
        return V0NaiveRetriever(chunks)
    elif var in ["v1", "v1_decomp"]:
        return V1RequirementDecompositionRetriever(chunks)
    elif var in ["v2", "v2_hybrid"]:
        return V2HybridRRFRetriever(chunks)
    elif var in ["v3", "v3_rerank"]:
        return V3CrossEncoderRerankRetriever(chunks)
    elif var in ["v8", "v8_self_rag"]:
        return V8SelfRAGRetriever(chunks)
    else:
        return V4OutcomeAwareRetriever(chunks)
