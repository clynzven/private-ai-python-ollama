from fakes import FakeClient

from docmate.index import Hit
from docmate.rag import RAG_RULES, ask_docs, build_prompt, cited

HITS = [
    Hit("hours.md", 0, "Open from nine.", 0.8),
    Hit("print.txt", 0, "Ten cents a page.", 0.5),
]


class FakeIndex:
    def search(self, query, k):
        return HITS[:k]


def test_sources_are_numbered_with_their_file():
    prompt = build_prompt("When?", HITS)
    assert "[1] (hours.md)\nOpen from nine." in prompt
    assert "[2] (print.txt)" in prompt
    assert prompt.endswith("Question: When?")


def test_the_model_gets_the_rules_and_the_sources():
    client = FakeClient(reply="At nine [1].")
    hits, pieces = ask_docs("When do you open?", FakeIndex(), client=client)
    assert "".join(pieces) == "At nine [1]."
    messages = client.calls[0]["messages"]
    assert messages[0] == {"role": "system", "content": RAG_RULES}
    assert "Open from nine." in messages[1]["content"]


def test_only_cited_sources_are_listed():
    assert cited("At nine [1]. Also [1].", HITS) == [(1, HITS[0])]
    assert cited("I don't know.", HITS) == []
    assert cited("Made up [7].", HITS) == []  # a number we never gave it


def test_grouped_citations_count_too():
    assert cited("Open at nine [1, 2].", HITS) == [(1, HITS[0]), (2, HITS[1])]
