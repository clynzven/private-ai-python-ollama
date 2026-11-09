"""Saved conversations, so the web app can show a list of past chats."""

import json
import sqlite3
from pathlib import Path

SCHEMA = """
create table if not exists chats (
    id integer primary key,
    title text not null,
    created text not null default current_timestamp
);
create table if not exists messages (
    id integer primary key,
    chat_id integer not null references chats(id) on delete cascade,
    role text not null,          -- user or assistant
    content text not null,
    sources text                 -- JSON list of sources, for answers from documents
);
"""


class ChatStore:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30)  # wait for other writers
        self.db.execute("pragma foreign_keys = on")
        self.db.executescript(SCHEMA)

    def new_chat(self, title: str = "New chat") -> int:
        with self.db:
            return self.db.execute("insert into chats (title) values (?)", (title,)).lastrowid

    def chats(self) -> list[dict]:
        rows = self.db.execute("select id, title from chats order by id desc").fetchall()
        return [{"id": i, "title": t} for i, t in rows]

    def exists(self, chat_id: int) -> bool:
        return (
            self.db.execute("select 1 from chats where id = ?", (chat_id,)).fetchone() is not None
        )

    def rename(self, chat_id: int, title: str) -> None:
        with self.db:
            self.db.execute("update chats set title = ? where id = ?", (title, chat_id))

    def delete(self, chat_id: int) -> None:
        with self.db:
            self.db.execute("delete from chats where id = ?", (chat_id,))

    def add_message(self, chat_id: int, role: str, content: str, sources=None) -> None:
        with self.db:
            self.db.execute(
                "insert into messages (chat_id, role, content, sources) values (?, ?, ?, ?)",
                (chat_id, role, content, json.dumps(sources) if sources else None),
            )

    def messages(self, chat_id: int) -> list[dict]:
        rows = self.db.execute(
            "select role, content, sources from messages where chat_id = ? order by id", (chat_id,)
        ).fetchall()
        return [
            {"role": r, "content": c, "sources": json.loads(s) if s else []} for r, c, s in rows
        ]
