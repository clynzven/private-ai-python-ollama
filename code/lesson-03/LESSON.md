# Lesson 3: Model Settings and Choosing a Model

## What you built
- `Settings` in `src/docmate/llm.py`: temperature, seed and context size, sent as Ollama `options`.
- `timed_ask()` and `Timing`: how long a model took and how many tokens per second it wrote.
- `docmate compare`: ask several models the same question and compare speed and answers.
- `strip_thinking()`: some models (qwen3) write their reasoning before `</think>`; we keep only the answer.
- `--temperature` and `--seed` on `docmate ask` and `docmate chat`.

## Try it
```bash
uv run docmate ask "Name one fruit. One word." --temperature 0 --seed 42
uv run docmate ask "Invent a name for a cat. One word." --temperature 1.5
uv run docmate compare "In one sentence, what is a CPU?" --models llama3.2:3b qwen3:4b
./check.sh
```

## Exercises
1. Add a `--num-ctx` option and try a bigger context window. Does it get slower?
2. Run `docmate compare` with three prompts of your own. Which model would you pick for DocMate, and why?
3. Add a `--json` flag to `docmate compare` that prints the results as JSON.
