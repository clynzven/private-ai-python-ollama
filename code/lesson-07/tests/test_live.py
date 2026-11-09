"""Tests that talk to the real model. They are skipped when Ollama is not running."""

import pytest

from docmate.llm import DEFAULT_MODEL, ask, list_models, make_client


def ollama_ready() -> bool:
    try:
        return DEFAULT_MODEL in list_models(make_client())
    except ConnectionError:
        return False


pytestmark = pytest.mark.skipif(not ollama_ready(), reason="Ollama or the model is not available")


def test_the_real_model_answers():
    answer = ask("Reply with only the word: pong")
    assert "pong" in answer.lower()


def test_the_real_model_remembers_the_conversation():
    from docmate.chat import Chat

    chat = Chat()
    list(chat.send("My favourite colour is green. Just say OK."))
    answer = "".join(chat.send("What is my favourite colour? Answer in one word."))
    assert "green" in answer.lower()


def test_temperature_zero_with_a_seed_repeats_itself():
    from docmate.llm import Settings

    fixed = Settings(temperature=0, seed=42)
    first = ask("Name one fruit. One word.", settings=fixed)
    second = ask("Name one fruit. One word.", settings=fixed)
    assert first == second


def test_the_real_model_fills_in_a_summary():
    from pathlib import Path

    from docmate.extract import DocSummary, extract

    text = (Path(__file__).parent.parent / "samples" / "opening-hours.md").read_text()
    summary = extract(text, DocSummary)
    assert summary.title
    assert len(summary.topics) <= 5


def test_real_embeddings_find_the_right_meaning():
    from docmate.embeddings import embed, rank

    [query] = embed(["How much does it cost to print a page?"], kind="query")
    docs = embed(["Black and white costs 10 cents per page.", "Story time is on Tuesday."])
    assert rank(query, docs)[0][0] == 0
