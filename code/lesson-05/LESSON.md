# Lesson 5: Reading Your Documents

## What you built
- `samples/makerspace-safety.pdf`: a PDF, so DocMate can read more than plain text.
- `src/docmate/documents.py`:
  - `load_text()` reads .txt, .md and .pdf (with `pypdf`) and fixes PDF ligatures such as "ﬁ" with NFKC.
  - `find_documents()` finds supported files in a folder.
  - `chunk_text()` cuts text into 100-word chunks that overlap by 20 words.
  - `load_chunks()` returns `Chunk` objects that remember their source file.
- `docmate chunks FOLDER [--show FILE]`.

## Try it
```bash
uv run docmate chunks samples
uv run docmate chunks samples --show borrowing-rules.md
./check.sh
```

## Exercises
1. Try `size=50, overlap=10`. How many chunks do you get now?
2. Add support for `.html` files: strip the tags before chunking.
3. Make chunks follow paragraphs: never cut in the middle of a paragraph if it fits.
