from fakes import FakeClient

from docmate.chat import SYSTEM_PROMPT, Chat


def test_reply_arrives_in_pieces():
    chat = Chat(client=FakeClient(reply="Hello there, friend"))
    pieces = list(chat.send("Hi"))
    assert len(pieces) > 1
    assert "".join(pieces) == "Hello there, friend"


def test_conversation_is_remembered():
    client = FakeClient(reply="Nice to meet you, Sam.")
    chat = Chat(client=client)
    list(chat.send("My name is Sam."))
    list(chat.send("What is my name?"))

    second_call = client.calls[1]["messages"]
    assert [m["role"] for m in second_call] == ["system", "user", "assistant", "user"]
    assert second_call[1]["content"] == "My name is Sam."
    assert second_call[2]["content"] == "Nice to meet you, Sam."


def test_nothing_happens_until_you_read_the_reply():
    client = FakeClient()
    chat = Chat(client=client)
    reply = chat.send("Hi")  # a generator: no request yet
    assert client.calls == []
    list(reply)
    assert len(client.calls) == 1


def test_reset_keeps_only_the_system_prompt():
    chat = Chat(client=FakeClient())
    list(chat.send("Hi"))
    chat.reset()
    assert chat.messages == [{"role": "system", "content": SYSTEM_PROMPT}]
