from fakes import FakeClient

from docmate.index import Index, from_blob, to_blob


def make_docs(folder):
    folder.mkdir()
    (folder / "hours.md").write_text("We are open from nine. Open every weekday.")
    (folder / "print.txt").write_text("Print a page for ten cents. Print in colour too.")
    return folder


def test_vectors_survive_the_database():
    assert from_blob(to_blob([0.5, -1.0, 2.0])) == [0.5, -1.0, 2.0]


def test_index_a_folder(tmp_path):
    index = Index(tmp_path / "test.db", client=FakeClient())
    counts = index.add_folder(make_docs(tmp_path / "docs"))
    assert counts["added"] == 2
    assert index.stats() == (2, 2)


def test_unchanged_files_are_skipped(tmp_path):
    docs = make_docs(tmp_path / "docs")
    client = FakeClient()
    index = Index(tmp_path / "test.db", client=client)
    index.add_folder(docs)
    calls = len(client.calls)
    assert index.add_folder(docs)["unchanged"] == 2
    assert len(client.calls) == calls  # no new embeddings were made


def test_changed_and_deleted_files(tmp_path):
    docs = make_docs(tmp_path / "docs")
    index = Index(tmp_path / "test.db", client=FakeClient())
    index.add_folder(docs)
    (docs / "hours.md").write_text("Now we open at ten.")
    (docs / "print.txt").unlink()
    counts = index.add_folder(docs)
    assert counts["updated"] == 1 and counts["removed"] == 1
    assert index.stats() == (1, 1)


def test_search_finds_the_best_chunk(tmp_path):
    index = Index(tmp_path / "test.db", client=FakeClient())
    index.add_folder(make_docs(tmp_path / "docs"))
    best = index.search("when do you open?", k=1)[0]
    assert best.source == "hours.md"


def test_an_unreadable_file_is_skipped(tmp_path):
    docs = make_docs(tmp_path / "docs")
    (docs / "broken.pdf").write_bytes(b"this is not really a PDF")
    index = Index(tmp_path / "test.db", client=FakeClient())
    counts = index.add_folder(docs)
    assert counts["added"] == 2
    assert index.failed[0].startswith("broken.pdf:")
