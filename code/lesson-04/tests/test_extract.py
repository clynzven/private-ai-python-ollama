import json

import pytest
from fakes import FakeClient

from docmate.extract import DocSummary, ExtractionError, extract

GOOD = json.dumps(
    {"title": "Hours", "summary": "When we are open.", "topics": ["hours"], "audience": "everyone"}
)
BAD = '{"title": "Hours", "audience": "aliens"}'


def test_valid_json_becomes_a_pydantic_object():
    result = extract("some text", DocSummary, client=FakeClient(reply=GOOD))
    assert result.title == "Hours"
    assert result.audience == "everyone"


def test_the_schema_is_sent_as_the_format():
    client = FakeClient(reply=GOOD)
    extract("some text", DocSummary, client=client)
    assert client.calls[0]["format"]["properties"]["audience"]["enum"] == [
        "everyone",
        "adults",
        "children",
        "staff",
    ]


def test_a_bad_answer_is_retried_with_the_error():
    client = FakeClient(replies=[BAD, GOOD])
    result = extract("some text", DocSummary, client=client)
    assert result.title == "Hours"
    retry = client.calls[1]["messages"]
    assert retry[-1]["content"].startswith("That was not valid")


def test_give_up_after_the_retries():
    client = FakeClient(replies=[BAD, BAD, BAD])
    with pytest.raises(ExtractionError):
        extract("some text", DocSummary, client=client, retries=2)
    assert len(client.calls) == 3
