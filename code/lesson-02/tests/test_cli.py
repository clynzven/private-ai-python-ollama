import ollama
from fakes import FakeClient

from docmate import cli


def test_ask_prints_the_answer(monkeypatch, capsys):
    monkeypatch.setattr(cli, "ask", lambda prompt, model: f"echo: {prompt}")
    assert cli.main(["ask", "hello"]) == 0
    assert capsys.readouterr().out == "echo: hello\n"


def test_friendly_message_when_ollama_is_not_running(monkeypatch, capsys):
    def down(prompt, model):
        raise ConnectionError("connection refused")

    monkeypatch.setattr(cli, "ask", down)
    assert cli.main(["ask", "hello"]) == 1
    assert "Is it running?" in capsys.readouterr().err


def test_friendly_message_for_a_missing_model(monkeypatch, capsys):
    def missing(prompt, model):
        raise ollama.ResponseError("model 'nope' not found", 404)

    monkeypatch.setattr(cli, "ask", missing)
    assert cli.main(["ask", "hello", "--model", "nope"]) == 1
    assert "model 'nope' not found" in capsys.readouterr().err


def test_chat_loop_reset_and_quit(monkeypatch, capsys):
    client = FakeClient(reply="Hi!")
    monkeypatch.setattr("docmate.chat.make_client", lambda: client)
    lines = iter(["hello", "/reset", "/quit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(lines))

    assert cli.main(["chat"]) == 0
    out = capsys.readouterr().out
    assert "docmate> Hi!" in out
    assert "(conversation cleared)" in out
