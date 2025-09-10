from __future__ import annotations

"""Embeddings generation utilities (LLM-backed).

Uses text-embedding-3-large by default. Returns list of vectors.
"""

from typing import List

from openai import OpenAI

from ..config import settings
from ..utils import get_json_logger, retry_with_backoff


log = get_json_logger("reddit_pipeline.llm.embeddings")

@retry_with_backoff()
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Create embeddings for a batch of texts.

    Trims empty strings and preserves order for non-empty inputs.
    """

    log.info("Embedding texts", extra={"count": len(texts)})
    if not texts:
        return []
    client = OpenAI(api_key=settings.openai_api_key)
    # Filter empty strings to avoid API errors; keep indices to restore order
    indexed = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
    if not indexed:
        return [[] for _ in texts]
    _, non_empty_texts = zip(*indexed)
    resp = client.embeddings.create(model=settings.embeddings_model, input=list(non_empty_texts))
    vectors = [d.embedding for d in resp.data]
    dim = settings.embeddings_dim
    # Map back to original order, pad/truncate to configured dim for safety
    result: List[List[float]] = [[ ] for _ in texts]
    for (orig_idx, _), vec in zip(indexed, vectors):
        if len(vec) > dim:
            vec = vec[:dim]
        elif len(vec) < dim:
            vec = vec + [0.0] * (dim - len(vec))
        result[orig_idx] = vec
    # Ensure any empty inputs have empty vectors for clarity
    for i, t in enumerate(texts):
        if not t or not t.strip():
            result[i] = []
    return result


