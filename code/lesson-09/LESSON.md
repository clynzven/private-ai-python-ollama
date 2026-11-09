# Lesson 9: Tools: Let the Model Call Python

## What you built
- `src/docmate/tools.py`:
  - three tools: `today()`, `search_documents(query)` and `calculate(expression)`. Their docstrings
    tell the model what they do.
  - `safe_math()`: arithmetic without `eval()`, because the expression comes from a model.
  - `run_agent()`: the tool loop. The model asks for a tool, we run it, send back the result, repeat.
  - `tool_call_in_text()`: catches a tool call the model wrote as JSON text instead of making it.
- `docmate agent "question"` shows every tool call. It uses `qwen3:4b`, which handled tools far
  better than `llama3.2:3b` in our tests.

## Try it
```bash
uv run docmate index samples
uv run docmate agent "I returned 3 books 4 days late. As an adult, how much do I pay?"
uv run docmate agent "I returned 3 books 4 days late. As an adult, how much do I pay?" --model llama3.2:3b
uv run docmate agent "Is the library open today?"
./check.sh
```

## Exercises
1. Add a tool `list_documents()` that returns the names of the indexed files.
2. The fee has a maximum of 5 euros per item. Ask about 2 books 30 days late. Is the answer right?
3. Count the steps: add a `--max-steps` option and print how many steps each question needed.
