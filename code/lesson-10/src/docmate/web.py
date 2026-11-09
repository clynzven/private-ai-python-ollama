"""The DocMate web API: chats, streaming answers, documents."""

import json
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from starlette.middleware.trustedhost import TrustedHostMiddleware

from docmate.chat import SYSTEM_PROMPT
from docmate.documents import SUPPORTED, load_text
from docmate.index import DEFAULT_DB, Index
from docmate.llm import DEFAULT_MODEL, list_models, make_client
from docmate.rag import RAG_RULES, build_prompt, cited

LOCAL = {"127.0.0.1", "localhost"}


class NewMessage(BaseModel):
    content: str
    model: str = DEFAULT_MODEL
    use_docs: bool = True


def create_app(db: Path = DEFAULT_DB, docs: Path = Path("documents"), client=None) -> FastAPI:
    app = FastAPI(title="DocMate")
    # Only this computer may use the API. TrustedHost stops "DNS rebinding" tricks, and
    # same_origin_only stops other websites from sending changes, like uploads.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=sorted(LOCAL))

    @app.middleware("http")
    async def same_origin_only(request: Request, call_next):
        origin = request.headers.get("origin")
        if request.method != "GET" and origin and urlparse(origin).hostname not in LOCAL:
            return JSONResponse({"detail": "other websites may not use DocMate"}, 403)
        return await call_next(request)

    docs.mkdir(parents=True, exist_ok=True)
    llm = client or make_client()

    # A new SQLite connection per request: simple, and safe with FastAPI's threads.
    def store():
        from docmate.store import ChatStore

        return ChatStore(db)

    def index():
        return Index(db, client=llm)

    @app.get("/api/models")
    def models():
        return list_models(llm)

    @app.get("/api/chats")
    def chats():
        return store().chats()

    @app.post("/api/chats")
    def new_chat():
        return {"id": store().new_chat()}

    @app.get("/api/chats/{chat_id}")
    def chat_messages(chat_id: int):
        if not store().exists(chat_id):
            raise HTTPException(404, "chat not found")
        return store().messages(chat_id)

    @app.delete("/api/chats/{chat_id}")
    def delete_chat(chat_id: int):
        store().delete(chat_id)
        return {"deleted": chat_id}

    @app.post("/api/chats/{chat_id}/messages")
    def send(chat_id: int, message: NewMessage):
        s = store()
        if not s.exists(chat_id):
            raise HTTPException(404, "chat not found")
        history = s.messages(chat_id)
        if not history:  # the first question becomes the chat's title
            s.rename(chat_id, message.content[:40])
        s.add_message(chat_id, "user", message.content)

        hits = index().search(message.content, 4) if message.use_docs else []
        system = RAG_RULES if hits else SYSTEM_PROMPT
        last = build_prompt(message.content, hits) if hits else message.content
        messages = [{"role": "system", "content": system}]
        messages += [{"role": m["role"], "content": m["content"]} for m in history]
        messages.append({"role": "user", "content": last})

        def events():
            # One JSON object per line (NDJSON): easy to read while it streams.
            answer, sources = "", None
            try:
                stream = llm.chat(model=message.model, messages=messages, stream=True)
                for chunk in stream:
                    answer += chunk.message.content
                    yield json.dumps({"type": "token", "text": chunk.message.content}) + "\n"
                sources = [
                    {"n": n, "source": h.source, "chunk": h.position, "score": round(h.score, 2)}
                    for n, h in cited(answer, hits)
                ]
                yield json.dumps({"type": "sources", "sources": sources}) + "\n"
                yield json.dumps({"type": "done"}) + "\n"
            except Exception as err:  # Ollama stopped, unknown model, ...
                yield json.dumps({"type": "error", "message": str(err)}) + "\n"
            finally:
                # Runs even if the user presses Stop: keep what we have so far.
                if answer:
                    store().add_message(chat_id, "assistant", answer, sources)

        return StreamingResponse(events(), media_type="application/x-ndjson")

    @app.get("/api/documents")
    def documents():
        rows = index().db.execute("select source from documents order by source").fetchall()
        return [r[0] for r in rows]

    @app.post("/api/documents")
    def upload(file: UploadFile):
        name = Path(file.filename or "").name  # never trust a path from the browser
        if Path(name).suffix.lower() not in SUPPORTED:
            raise HTTPException(415, "only .txt, .md and .pdf files")
        with tempfile.TemporaryDirectory() as tmp:  # check it before it joins the others
            temp = Path(tmp) / name
            with temp.open("wb") as out:
                shutil.copyfileobj(file.file, out)
            try:
                load_text(temp)
            except Exception:
                raise HTTPException(422, f"could not read {name}") from None
            shutil.move(temp, docs / name)
        return index().add_folder(docs)

    return app
