# Lesson 4: Structured Answers with Pydantic

## What you built
- `samples/`: four documents of a made-up library. The model cannot know them, which we use from now on.
- `src/docmate/extract.py`: `DocSummary` (a Pydantic model) and `extract()`, which sends the schema
  as Ollama's `format`, checks the answer with Pydantic, and retries with the error message.
- `docmate summarize FILE`: prints a document summary as JSON.

## Try it
```bash
uv run docmate summarize samples/borrowing-rules.md
./check.sh
```

## Exercises
1. Add a `contact_email: str | None` field to `DocSummary`. Which sample has one?
2. Write a new model `Event` (name, day, time, price) and extract all events from `samples/events-autumn.md`.
3. Summarize every file in `samples/` with one command.
