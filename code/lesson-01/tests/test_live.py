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
