# Lesson 7: A Search Index in SQLite

## What you built
- `src/docmate/index.py`: an `Index` class backed by SQLite (in `.docmate/index.db`).
  - `documents` table: one row per file with its SHA-256 fingerprint.
  - `chunks` table: text, position and the embedding stored as a blob of 4-byte floats.
  - `add_folder()` adds new files, re-indexes changed files, skips unchanged ones and removes deleted ones.
  - `search()` embeds the question and returns the closest chunks.
- `docmate index FOLDER` and `docmate search "question"`.

## Try it
```bash
uv run docmate index samples
uv run docmate index samples        # second time: everything unchanged
uv run docmate search "Can my kids get a fine for returning books late?"
./check.sh
```

## Exercises
1. Add `docmate search --source FILE` to only search one document.
2. Store the indexing date per document and show it in a new `docmate documents` command.
3. Search compares every chunk. Time it with 10,000 fake chunks. When would you need something faster?
