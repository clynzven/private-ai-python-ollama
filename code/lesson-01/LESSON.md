# Lesson 1: Your First Private AI Call

## What you built
- A Python project managed by `uv`, with the `ollama` library.
- `src/docmate/llm.py`: `ask()` sends one prompt to a local model, `list_models()` lists downloaded models.
- `src/docmate/cli.py`: the `docmate ask` and `docmate models` commands, with friendly errors
  when Ollama is not running or a model is missing.
- Tests with a fake client (fast, no model needed) and one live test against the real model.

## Try it
```bash
ollama pull llama3.2:3b
uv run docmate models
uv run docmate ask "In one sentence, what is Python?"
./check.sh
```

## Exercises
1. Add a `--host` option so `docmate` can talk to Ollama on another computer.
2. Ask the same question to `llama3.2:3b` and `qwen3:4b`. Which is faster? Which answer is better?
3. Write a test for `docmate models` using `monkeypatch`.
