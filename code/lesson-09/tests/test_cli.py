import ollama
from fakes import FakeClient

from docmate import cli


def test_ask_prints_the_answer(monkeypatch, capsys):
    monkeypatch.setattr(cli, "ask", lambda prompt, model, settings: f"echo: {prompt}")
    assert cli.main(["ask", "hello"]) == 0
    assert capsys.readouterr().out == "echo: hello\n"


def test_friendly_message_when_ollama_is_not_running(monkeypatch, capsys):
    def down(prompt, model, settings):
        raise ConnectionError("connection refused")

    monkeypatch.setattr(cli, "ask", down)
    assert cli.main(["ask", "hello"]) == 1
    assert "Is it running?" in capsys.readouterr().err


def test_friendly_message_for_a_missing_model(monkeypatch, capsys):
    def missing(prompt, model, settings):
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


def test_settings_reach_the_model(monkeypatch, capsys):
    seen = {}

    def fake_ask(prompt, model, settings):
        seen["settings"] = settings
        return "ok"

    monkeypatch.setattr(cli, "ask", fake_ask)
    cli.main(["ask", "hi", "--temperature", "0", "--seed", "42"])
    assert seen["settings"].options() == {"temperature": 0.0, "seed": 42}


def test_compare_prints_one_row_per_model(monkeypatch, capsys):
    client = FakeClient(reply="Four.")
    monkeypatch.setattr("docmate.llm.make_client", lambda: client)
    cli.main(["compare", "2+2?", "--models", "a:1b", "b:2b"])
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("model")
    assert [line.split()[0] for line in out[1:]] == ["a:1b", "b:2b"]
    assert "6.0" in out[1]  # 12 tokens in 2 seconds
