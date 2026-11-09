# Lesson 12: Testing, Evaluation and Packaging

## What you built
- `evals/questions.json`: 10 questions with the file that holds the answer and words the answer must contain.
- `src/docmate/evaluate.py` and `docmate eval [-k N] [--model M]`: checks two things per question:
  did the search find the right file, and did the answer contain the facts?
- A `live` pytest marker: `uv run pytest -m "not live"` runs only the fast tests (for CI without Ollama).
- Version 1.0.0, a README, and a wheel built with `uv build` that includes the web page.

## Try it
```bash
uv run docmate index samples
uv run docmate eval
uv run pytest -m "not live"
uv build
uv tool install dist/docmate-1.0.0-py3-none-any.whl
```

## Exercises
1. The fine question with a maximum fails. Make `docmate eval --agent` use the tools from lesson 9. Does it pass now?
2. Add five questions of your own, including one that is not in the documents.
3. Save every eval run to a CSV file with the date, so you can see if a change made DocMate better or worse.
