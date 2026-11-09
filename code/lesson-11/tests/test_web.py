import json

import pytest
from fakes import FakeClient
from fastapi.testclient import TestClient

from docmate.web import create_app


@pytest.fixture
def web(tmp_path):
    fake = FakeClient(reply="We open at nine [1].", models=["llama3.2:3b"])
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "hours.md").write_text("We are open from nine.")
    app = create_app(db=tmp_path / "test.db", docs=docs, client=fake)
    with TestClient(app, base_url="http://127.0.0.1") as client:
        client.post("/api/documents", files={"file": ("print.txt", b"Print for ten cents.")})
        yield client, fake


def events(response):
    return [json.loads(line) for line in response.text.splitlines()]


def test_models(web):
    client, _ = web
    assert client.get("/api/models").json() == ["llama3.2:3b"]


def test_upload_indexes_the_folder(web):
    client, _ = web
    assert client.get("/api/documents").json() == ["hours.md", "print.txt"]


def test_a_chat_streams_tokens_then_sources(web):
    client, _ = web
    chat_id = client.post("/api/chats").json()["id"]
    response = client.post(f"/api/chats/{chat_id}/messages", json={"content": "When do you open?"})
    lines = events(response)
    assert "".join(e["text"] for e in lines if e["type"] == "token") == "We open at nine [1]."
    sources = next(e for e in lines if e["type"] == "sources")["sources"]
    assert sources[0]["n"] == 1
    assert lines[-1] == {"type": "done"}


def test_chats_are_saved_with_a_title(web):
    client, _ = web
    chat_id = client.post("/api/chats").json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "When do you open?"})
    assert client.get("/api/chats").json() == [{"id": chat_id, "title": "When do you open?"}]
    roles = [m["role"] for m in client.get(f"/api/chats/{chat_id}").json()]
    assert roles == ["user", "assistant"]


def test_history_is_sent_to_the_model(web):
    client, fake = web
    chat_id = client.post("/api/chats").json()["id"]
    for text in ("Hi!", "And again?"):
        client.post(f"/api/chats/{chat_id}/messages", json={"content": text, "use_docs": False})
    sent = [m["role"] for m in fake.calls[-1]["messages"]]
    assert sent == ["system", "user", "assistant", "user"]


def test_unknown_chat_is_404(web):
    client, _ = web
    assert client.get("/api/chats/999").status_code == 404


def test_delete_a_chat(web):
    client, _ = web
    chat_id = client.post("/api/chats").json()["id"]
    client.delete(f"/api/chats/{chat_id}")
    assert client.get("/api/chats").json() == []


class BrokenClient(FakeClient):
    def chat(self, model, messages, stream=False, **kwargs):
        raise ConnectionError("Failed to connect to Ollama")


def test_a_model_error_becomes_an_error_event(tmp_path):
    app = create_app(db=tmp_path / "test.db", docs=tmp_path / "docs", client=BrokenClient())
    with TestClient(app, base_url="http://127.0.0.1") as client:
        chat_id = client.post("/api/chats").json()["id"]
        lines = events(client.post(f"/api/chats/{chat_id}/messages", json={"content": "Hi"}))
        assert lines == [{"type": "error", "message": "Failed to connect to Ollama"}]
        roles = [m["role"] for m in client.get(f"/api/chats/{chat_id}").json()]
        assert roles == ["user"]  # no empty answer was saved


def test_uploads_must_be_documents(web):
    client, _ = web
    assert client.post("/api/documents", files={"file": ("..", b"x")}).status_code == 415
    assert client.post("/api/documents", files={"file": ("photo.jpg", b"x")}).status_code == 415


def test_an_unreadable_upload_is_refused_and_not_kept(web, tmp_path):
    client, _ = web
    response = client.post("/api/documents", files={"file": ("broken.pdf", b"not a PDF")})
    assert response.status_code == 422
    assert not (tmp_path / "docs" / "broken.pdf").exists()


def test_other_websites_cannot_upload(web):
    client, _ = web
    response = client.post(
        "/api/documents",
        files={"file": ("hours.md", b"Closed forever.")},
        headers={"Origin": "https://evil.example"},
    )
    assert response.status_code == 403


def test_other_host_names_are_refused(web):
    client, _ = web
    assert client.get("/api/chats", headers={"Host": "attacker.example"}).status_code == 400
