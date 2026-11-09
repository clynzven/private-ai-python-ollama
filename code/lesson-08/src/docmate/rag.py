"""Answers with sources: search the index, then let the model answer from what it found."""

import re
from collections.abc import Iterator

from docmate.index import Hit
from docmate.llm import DEFAULT_MODEL, make_client

RAG_RULES = (
    "You are DocMate. Answer the question using ONLY the numbered sources. "
    "After each fact, cite its source like [1]. "
    "If the sources do not contain the answer, say: I don't know, that is not in your documents."
)


def build_prompt(question: str, hits: list[Hit]) -> str:
    sources = "\n\n".join(f"[{n}] ({hit.source})\n{hit.text}" for n, hit in enumerate(hits, 1))
    return f"Sources:\n\n{sources}\n\nQuestion: {question}"


def ask_docs(question: str, index, model: str = DEFAULT_MODEL, client=None, k: int = 4):
    """Return (the hits we found, a stream of answer pieces)."""
    hits = index.search(question, k)
    client = client or make_client()
    messages = [
        {"role": "system", "content": RAG_RULES},
        {"role": "user", "content": build_prompt(question, hits)},
    ]

    def pieces() -> Iterator[str]:
        stream = client.chat(
            model=model, messages=messages, stream=True, options={"temperature": 0}
        )
        for chunk in stream:
            yield chunk.message.content

    return hits, pieces()


def cited(answer: str, hits: list[Hit]) -> list[tuple[int, Hit]]:
    """The sources the answer actually mentions, like [2], in order."""
    # Matches [2], and also grouped citations like [1, 3].
    groups = re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", answer)
    numbers = sorted({int(n) for group in groups for n in group.split(",")})
    return [(n, hits[n - 1]) for n in numbers if 1 <= n <= len(hits)]
