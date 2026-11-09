import pytest
from fakes import FakeClient

from docmate.embeddings import cosine, embed, rank


def test_cosine_of_the_same_direction_is_one():
    assert cosine([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)


def test_cosine_of_unrelated_vectors_is_zero():
    assert cosine([1, 0], [0, 1]) == 0.0


def test_queries_and_documents_get_their_prefix():
    client = FakeClient()
    embed(["hello"], kind="query", client=client)
    embed(["hello"], client=client)
    assert client.calls[0]["input"] == ["search_query: hello"]
    assert client.calls[1]["input"] == ["search_document: hello"]


def test_rank_puts_the_best_match_first():
    client = FakeClient()
    [query] = embed(["when are you open?"], kind="query", client=client)
    docs = embed(["printing prices", "we are open at nine", "wifi password"], client=client)
    assert rank(query, docs)[0][0] == 1
