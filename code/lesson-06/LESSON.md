# Lesson 6: Embeddings: Meaning as Numbers

## What you built
- `src/docmate/embeddings.py`:
  - `embed()` turns texts into vectors with `nomic-embed-text` (768 numbers each), adding the
    `search_query:` / `search_document:` prefixes the model was trained with.
  - `cosine()` measures how alike two vectors are; `rank()` sorts vectors by score.
- `docmate similar QUERY TEXT...`: score texts by meaning.
- A fake `embed()` in `tests/fakes.py`, so tests don't need the embedding model.

## Try it
```bash
ollama pull nomic-embed-text
uv run docmate similar "When can I visit on Saturday?" "The library is open from 10 to 4 on weekends." "Saturday football training starts at 9."
./check.sh
```

## Exercises
1. Remove the prefixes and compare the scores. Do they change the ranking for your own examples?
2. Find a query where a keyword match beats the right meaning. Why does it happen?
3. Time `embed()` for 1, 10 and 100 texts. Is sending a list faster than one text at a time?
