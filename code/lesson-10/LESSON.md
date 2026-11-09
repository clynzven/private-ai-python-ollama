# Lesson 10: A Web API with FastAPI

## What you built
- `src/docmate/store.py`: `ChatStore` saves chats and messages in SQLite (the sidebar of past chats).
- `src/docmate/web.py`: `create_app()` builds the API:
  - `GET /api/models`, `GET/POST /api/chats`, `GET/DELETE /api/chats/{id}`
  - `POST /api/chats/{id}/messages`: streams the answer as NDJSON (one JSON object per line):
    `token` events, then `sources`, then `done`. It uses the chat history and, if asked, your documents.
    A `finally:` block saves the answer even when the user stops it early, and an `error`
    event tells the page when the model fails.
  - Security: only `127.0.0.1`/`localhost` may use the API (Host check), and other websites
    may not send changes (Origin check). Uploads must be readable .txt, .md or .pdf files.
  - `GET/POST /api/documents`: list documents, upload a new one (it is indexed right away).
- `docmate serve --docs FOLDER`: runs the API with uvicorn on http://127.0.0.1:8000.
- Tests with FastAPI's `TestClient` and the fake model.

## Try it
```bash
mkdir -p documents && cp samples/* documents/
uv run docmate serve
# in a second terminal:
curl -s -X POST localhost:8000/api/chats
curl -sN -X POST localhost:8000/api/chats/1/messages -H 'content-type: application/json' \
     -d '{"content": "How long can I borrow a DVD?"}'
```
Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

## Exercises
1. Fix the follow-up: search with the last two user messages, so "And a board game?" finds the rule.
2. Add `PATCH /api/chats/{id}` to rename a chat.
3. Refuse uploads bigger than 20 MB with status 413.
