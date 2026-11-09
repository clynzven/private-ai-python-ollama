import datetime

import pytest
from fakes import FakeClient

from docmate.index import Hit
from docmate.tools import make_tools, run_agent, safe_math


class FakeIndex:
    def search(self, query, k):
        return [Hit("borrowing-rules.md", 0, "Adults pay 20 cents per item per day.", 0.9)]


def test_safe_math_does_arithmetic():
    assert safe_math("3 * 4 * 0.20") == pytest.approx(2.4)
    assert safe_math("-2 + 10 / 4") == 0.5


def test_safe_math_refuses_code():
    with pytest.raises(ValueError):
        safe_math("__import__('os').remove('important.txt')")


def test_tools_have_names_and_results():
    tools = make_tools(FakeIndex(), now=lambda: datetime.date(2026, 11, 9))
    assert tools["today"]() == "Monday 09 November 2026"
    assert tools["calculate"]("3 * 4 * 0.20") == "2.40"
    assert "20 cents" in tools["search_documents"]("late fees")


def test_the_agent_runs_the_tools_the_model_asks_for():
    client = FakeClient(
        replies=[
            {"tool": "search_documents", "args": {"query": "late fees"}},
            {"tool": "calculate", "args": {"expression": "3 * 4 * 0.20"}},
            "You pay 2.40 euros.",
        ]
    )
    seen = []
    answer = run_agent(
        "How much?",
        make_tools(FakeIndex()),
        client=client,
        on_tool=lambda name, args, result: seen.append((name, result)),
    )
    assert answer == "You pay 2.40 euros."
    assert seen[1] == ("calculate", "2.40")
    last_messages = client.calls[-1]["messages"]
    assert last_messages[-1] == {"role": "tool", "tool_name": "calculate", "content": "2.40"}


def test_a_broken_tool_call_is_reported_to_the_model():
    client = FakeClient(
        replies=[{"tool": "calculate", "args": {"expression": "open('x')"}}, "Sorry."]
    )
    run_agent("?", make_tools(FakeIndex()), client=client)
    assert client.calls[1]["messages"][-1]["content"].startswith("error:")


def test_a_tool_call_written_as_text_still_runs():
    client = FakeClient(replies=['{"name": "today", "arguments": {}}', "It is Monday."])
    seen = []
    answer = run_agent(
        "Which day is it?",
        make_tools(FakeIndex(), now=lambda: datetime.date(2026, 11, 9)),
        client=client,
        on_tool=lambda name, args, result: seen.append(result),
    )
    assert seen == ["Monday 09 November 2026"]
    assert answer == "It is Monday."
