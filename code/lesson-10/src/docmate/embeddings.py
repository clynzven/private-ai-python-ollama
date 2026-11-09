"""Embeddings: turn text into a list of numbers that captures its meaning."""

import math

from docmate.llm import make_client

EMBED_MODEL = "nomic-embed-text"

# nomic-embed-text was trained with these prefixes: one for questions, one for documents.
PREFIX = {"query": "search_query: ", "document": "search_document: "}


def embed(texts: list[str], kind: str = "document", model: str = EMBED_MODEL, client=None):
    """Return one vector (a list of floats) per text."""
    client = client or make_client()
    response = client.embed(model=model, input=[PREFIX[kind] + t for t in texts])
    return [list(v) for v in response.embeddings]


def cosine(a: list[float], b: list[float]) -> float:
    """How alike two vectors point: 1 = same direction, 0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def rank(query: list[float], vectors: list[list[float]]) -> list[tuple[int, float]]:
    """(position, score) for every vector, best match first."""
    scores = [(i, cosine(query, v)) for i, v in enumerate(vectors)]
    return sorted(scores, key=lambda pair: pair[1], reverse=True)
