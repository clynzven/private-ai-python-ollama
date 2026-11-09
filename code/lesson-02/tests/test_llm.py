from fakes import FakeClient

from docmate.llm import DEFAULT_MODEL, ask, list_models


def test_ask_returns_the_model_reply():
    client = FakeClient(reply="Paris")
    assert ask("What is the capital of France?", client=client) == "Paris"


def test_ask_sends_the_prompt_as_a_user_message():
    client = FakeClient()
    ask("Hi there", client=client)
    call = client.calls[0]
    assert call["model"] == DEFAULT_MODEL
    assert call["messages"] == [{"role": "user", "content": "Hi there"}]


def test_ask_can_use_another_model():
    client = FakeClient()
    ask("Hi", model="qwen3:4b", client=client)
    assert client.calls[0]["model"] == "qwen3:4b"


def test_list_models_is_sorted():
    client = FakeClient(models=["qwen3:4b", "llama3.2:3b"])
    assert list_models(client=client) == ["llama3.2:3b", "qwen3:4b"]
