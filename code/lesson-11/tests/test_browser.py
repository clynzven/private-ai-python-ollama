"""Click through the real chat page in a browser (Chromium), with the fake model behind it."""

import socket
import threading
import time

import pytest
import uvicorn
from fakes import FakeClient

from docmate.web import create_app

playwright = pytest.importorskip("playwright.sync_api")


class SlowFake(FakeClient):
    """Streams slowly, so we can press Stop in the middle of an answer."""

    fail = False  # set to True to pretend Ollama is not running

    def chat(self, model, messages, stream=False, **kwargs):
        if self.fail:
            raise ConnectionError("Failed to connect to Ollama")
        result = super().chat(model, messages, stream=stream, **kwargs)
        if not stream:
            return result

        def slow():
            for chunk in result:
                time.sleep(0.05)
                yield chunk

        return slow()


@pytest.fixture
def site(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "hours.md").write_text("We are open from nine.")
    fake = SlowFake(
        reply="Hours\n=====\nWe open at **nine** [1].\n\n- Monday\n- Tuesday",
        models=["llama3.2:3b"],
    )
    app = create_app(db=tmp_path / "test.db", docs=docs, client=fake)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}", fake, docs
    server.should_exit = True
    thread.join()


@pytest.fixture
def page(site):
    try:
        with playwright.sync_playwright() as p:
            browser = p.chromium.launch()
            yield browser.new_page()
            browser.close()
    except playwright.Error as err:  # Chromium not installed: `uv run playwright install chromium`
        pytest.skip(str(err))


def test_ask_and_see_the_answer_with_sources(site, page):
    url, _, _ = site
    page.goto(url)
    page.fill("#input", "When do you open?")
    page.keyboard.press("Enter")
    answer = page.locator(".msg.assistant")
    answer.locator(".source").wait_for()
    assert answer.locator("strong").inner_text() == "nine"  # Markdown was rendered
    assert answer.locator("li").count() == 2
    assert answer.locator("hr").count() == 1  # the ===== line is not shown as text
    assert answer.locator(".source").inner_text() == "[1] hours.md"
    assert page.locator(".chat-item.active").inner_text().startswith("When do you open?")


def test_models_and_documents_are_listed(site, page):
    url, _, _ = site
    page.goto(url)
    page.locator("#doc-list li").first.wait_for()
    assert page.locator("#model option").all_inner_texts() == ["llama3.2:3b"]
    assert page.locator("#doc-list li").all_inner_texts() == ["hours.md"]


def test_upload_a_document(site, page, tmp_path):
    url, _, docs = site
    page.goto(url)
    new_file = tmp_path / "printing.txt"
    new_file.write_text("Printing costs ten cents.")
    page.set_input_files("#file", str(new_file))
    page.locator("#doc-list li", has_text="printing.txt").wait_for()
    assert (docs / "printing.txt").exists()


def test_stop_ends_the_answer_early(site, page):
    url, _, _ = site
    page.goto(url)
    page.fill("#input", "Tell me everything")
    page.keyboard.press("Enter")
    page.locator("#stop").click()
    page.locator("#send").wait_for()
    shown = page.locator(".msg.assistant .body").inner_text()
    assert len(shown) < len("Hours We open at nine [1]. Monday Tuesday")


def test_a_saved_chat_opens_again(site, page):
    url, _, _ = site
    page.goto(url)
    page.fill("#input", "Hello there")
    page.keyboard.press("Enter")
    page.locator(".msg.assistant .source").wait_for()
    page.click("#new-chat")
    assert page.locator(".msg").count() == 0
    page.click(".chat-item")
    page.locator(".msg.user", has_text="Hello there").wait_for()


def test_a_model_error_is_shown(site, page):
    url, fake, _ = site
    fake.fail = True
    page.goto(url)
    page.fill("#input", "Hello?")
    page.keyboard.press("Enter")
    page.locator("#toast", has_text="DocMate could not answer").wait_for()


def test_a_broken_upload_is_explained(site, page, tmp_path):
    url, _, docs = site
    page.goto(url)
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"not a PDF")
    page.set_input_files("#file", str(broken))
    page.locator("#toast", has_text="Could not add broken.pdf").wait_for()
    assert not (docs / "broken.pdf").exists()
