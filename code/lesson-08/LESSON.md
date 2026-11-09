# Lesson 8: Answers with Sources (RAG)

## What you built
- `src/docmate/rag.py`:
  - `RAG_RULES`: answer only from the numbered sources, cite them like [1], or say "I don't know".
  - `build_prompt()`: the question plus the best chunks, numbered, with their file names.
  - `ask_docs()`: search the index, then stream the answer (temperature 0).
  - `cited()`: which sources the answer really used.
- `docmate ask --docs "question"`: answers from your documents and lists the sources.

## Try it
```bash
uv run docmate index samples
uv run docmate ask "How long can I borrow a DVD at the Maple Grove library?"
uv run docmate ask --docs "How long can I borrow a DVD at the Maple Grove library?"
uv run docmate ask --docs "Does the library have a café?"
./check.sh
```

## Exercises
1. Add `--k` to `docmate ask --docs`. What happens to the answers with k=1 and k=7?
2. Skip sources with a score below 0.5. Does "I don't know" come faster?
3. Print the full prompt with a `--show-prompt` flag, so you can see exactly what the model reads.
