from pathlib import Path

import pytest

from docmate.documents import chunk_text, find_documents, load_chunks, load_text

SAMPLES = Path(__file__).parent.parent / "samples"


def test_short_text_is_one_chunk():
    assert chunk_text("one two three", size=10, overlap=2) == ["one two three"]


def test_chunks_overlap():
    words = " ".join(str(n) for n in range(25))
    chunks = chunk_text(words, size=10, overlap=3)
    assert chunks[0].split()[-3:] == chunks[1].split()[:3]
    assert chunks[-1].split()[-1] == "24"  # nothing is lost at the end


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("a b c", size=5, overlap=5)


def test_finds_all_supported_files(tmp_path):
    (tmp_path / "a.md").write_text("hi")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("hi")
    (tmp_path / "photo.jpg").write_bytes(b"not text")
    assert [p.name for p in find_documents(tmp_path)] == ["a.md", "b.txt"]


def test_pdf_ligatures_become_normal_letters():
    text = load_text(SAMPLES / "makerspace-safety.pdf")
    assert "first floor" in text
    assert "ﬁ" not in text  # the single-character "fi" ligature


def test_chunks_remember_their_source():
    chunks = load_chunks(SAMPLES)
    sources = {c.source for c in chunks}
    assert "makerspace-safety.pdf" in sources
    assert all(c.text for c in chunks)


def test_a_file_that_is_not_utf8_is_still_read(tmp_path):
    path = tmp_path / "menu.txt"
    path.write_bytes(b"caf\xe9 menu")  # saved by an old editor, not as UTF-8
    assert load_text(path) == "caf\ufffd menu"
