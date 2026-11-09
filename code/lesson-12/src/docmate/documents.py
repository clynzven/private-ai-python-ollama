"""Read documents from a folder and cut them into small chunks."""

import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

SUPPORTED = {".txt", ".md", ".pdf"}


@dataclass
class Chunk:
    source: str  # the file name, so we can show where an answer came from
    index: int  # which piece of that file: 0, 1, 2, ...
    text: str


def load_text(path: Path) -> str:
    """Return the plain text of a .txt, .md or .pdf file."""
    if path.suffix.lower() == ".pdf":
        text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    else:
        # errors="replace": a broken byte becomes "�" instead of crashing everything.
        text = path.read_text(encoding="utf-8", errors="replace")
    # PDFs often use special characters such as the "ﬁ" ligature; NFKC turns them into "fi".
    return unicodedata.normalize("NFKC", text)


def find_documents(folder: Path) -> list[Path]:
    """All supported files in a folder and its subfolders, in a stable order."""
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)


def chunk_text(text: str, size: int = 100, overlap: int = 20) -> list[str]:
    """Cut text into pieces of `size` words. Neighbours share `overlap` words."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    words = text.split()
    step = size - overlap
    return [" ".join(words[i : i + size]) for i in range(0, max(len(words) - overlap, 1), step)]


def load_chunks(folder: Path, size: int = 100, overlap: int = 20) -> list[Chunk]:
    chunks = []
    for path in find_documents(folder):
        name = str(path.relative_to(folder))
        for i, text in enumerate(chunk_text(load_text(path), size, overlap)):
            if text:
                chunks.append(Chunk(source=name, index=i, text=text))
    return chunks
