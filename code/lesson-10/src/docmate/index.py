"""A search index in SQLite: chunks, their source file and their embedding."""

import hashlib
import sqlite3
from array import array
from dataclasses import dataclass
from pathlib import Path

from docmate.documents import chunk_text, find_documents, load_text
from docmate.embeddings import cosine, embed

DEFAULT_DB = Path(".docmate") / "index.db"

SCHEMA = """
create table if not exists documents (
    source text primary key,   -- file name, relative to the indexed folder
    sha256 text not null       -- fingerprint of the file, to skip unchanged files
);
create table if not exists chunks (
    id integer primary key,
    source text not null references documents(source) on delete cascade,
    position integer not null,
    text text not null,
    vector blob not null       -- the embedding, stored as 4-byte floats
);
"""


@dataclass
class Hit:
    source: str
    position: int
    text: str
    score: float


def to_blob(vector: list[float]) -> bytes:
    return array("f", vector).tobytes()


def from_blob(blob: bytes) -> list[float]:
    return array("f", blob).tolist()


class Index:
    def __init__(self, path: Path = DEFAULT_DB, client=None):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30)  # wait for other writers
        self.db.execute("pragma foreign_keys = on")
        self.db.executescript(SCHEMA)
        self.client = client

    def add_folder(self, folder: Path) -> dict:
        """Index every document in `folder`. Unchanged files are skipped."""
        counts = {"added": 0, "updated": 0, "unchanged": 0, "removed": 0}
        self.failed = []  # files we could not read, with the reason
        seen = set()
        with self.db:  # one transaction: all or nothing
            for path in find_documents(folder):
                source = str(path.relative_to(folder))
                seen.add(source)
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                row = self.db.execute(
                    "select sha256 from documents where source = ?", (source,)
                ).fetchone()
                if row and row[0] == digest:
                    counts["unchanged"] += 1
                    continue
                try:
                    texts = chunk_text(load_text(path))
                except Exception as err:  # a broken PDF: skip it, index the rest
                    self.failed.append(f"{source}: {err}")
                    continue
                self.db.execute("delete from documents where source = ?", (source,))
                self._add(source, digest, texts)
                counts["updated" if row else "added"] += 1
            for (source,) in self.db.execute("select source from documents").fetchall():
                if source not in seen:  # the file was deleted
                    self.db.execute("delete from documents where source = ?", (source,))
                    counts["removed"] += 1
        return counts

    def _add(self, source: str, digest: str, texts: list[str]) -> None:
        self.db.execute("insert into documents (source, sha256) values (?, ?)", (source, digest))
        vectors = embed(texts, client=self.client) if texts else []
        self.db.executemany(
            "insert into chunks (source, position, text, vector) values (?, ?, ?, ?)",
            [
                (source, i, t, to_blob(v))
                for i, (t, v) in enumerate(zip(texts, vectors, strict=True))
            ],
        )

    def search(self, query: str, k: int = 4) -> list[Hit]:
        """The k chunks whose meaning is closest to the query."""
        [q] = embed([query], kind="query", client=self.client)
        rows = self.db.execute("select source, position, text, vector from chunks").fetchall()
        hits = [Hit(s, p, t, cosine(q, from_blob(v))) for s, p, t, v in rows]
        return sorted(hits, key=lambda h: h.score, reverse=True)[:k]

    def stats(self) -> tuple[int, int]:
        documents = self.db.execute("select count(*) from documents").fetchone()[0]
        chunks = self.db.execute("select count(*) from chunks").fetchone()[0]
        return documents, chunks
