# Lesson 11: A Chat Web Page

## What you built
- `src/docmate/static/`: a ChatGPT-style chat page in plain HTML, CSS and JavaScript (no build tools,
  nothing loaded from the internet):
  - `index.html`: sidebar (new chat, past chats, documents), header (model picker, "Use my documents"),
    messages and the input box.
  - `app.js`: reads the NDJSON stream with `fetch` + `getReader()`, a Stop button with
    `AbortController`, saved chats, document upload with a button or drag-and-drop.
  - Errors are shown, not hidden: a failed answer or upload shows a short message.
  - `markdown.js`: a tiny, safe Markdown renderer (escapes HTML first), with Copy buttons on code.
  - `style.css`: the dark theme.
- `web.py` serves the page with `StaticFiles`, and now indexes the documents folder when the app
  starts (a bug the browser test found: the page showed no documents).
- `tests/test_browser.py`: Playwright clicks through the real page with the fake model.

## Try it
```bash
uv run playwright install chromium      # once, for the browser tests
mkdir -p documents && cp samples/* documents/
uv run docmate serve
```
Open http://127.0.0.1:8000, ask "How long can I borrow a DVD?", then drop a file on the page.

## Exercises
1. Add a "Regenerate" button under the last answer.
2. Show the score of each source in a tooltip on its chip.
3. Add a light theme that follows the computer's setting (`prefers-color-scheme`).
