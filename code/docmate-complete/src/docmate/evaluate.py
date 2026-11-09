"""Evaluation: measure how well DocMate answers questions we know the answers to."""

import json
from dataclasses import dataclass
from pathlib import Path

from docmate.llm import DEFAULT_MODEL
from docmate.rag import ask_docs


@dataclass
class Result:
    question: str
    found_source: bool  # did the search bring back the right file?
    right_answer: bool  # does the answer contain the words we expect?
    answer: str


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def run_eval(cases: list[dict], index, model: str = DEFAULT_MODEL, client=None, k: int = 4):
    results = []
    for case in cases:
        hits, pieces = ask_docs(case["question"], index, model=model, client=client, k=k)
        answer = "".join(pieces)
        sources = [hit.source for hit in hits]
        expected = case["source"]
        results.append(
            Result(
                question=case["question"],
                # For questions with no answer in the documents, any search result is fine.
                found_source=expected is None or expected in sources,
                right_answer=all(
                    w.lower() in answer.lower().replace("’", "'") for w in case["words"]
                ),
                answer=answer,
            )
        )
    return results


def summary(results: list[Result]) -> str:
    total = len(results)
    found = sum(r.found_source for r in results)
    right = sum(r.right_answer for r in results)
    return f"search found the right file: {found}/{total}   answer had the facts: {right}/{total}"
