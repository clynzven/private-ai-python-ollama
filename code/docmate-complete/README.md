# DocMate

A private AI assistant for your own documents. It runs entirely on your computer with
[Ollama](https://ollama.com): no account, no API key, and nothing you type leaves your machine.

- Chat with memory, answers that stream in word by word
- Answers from your documents (.txt, .md, .pdf) with the sources they came from
- Tools: search, today's date and a safe calculator
- A ChatGPT-style web app: past chats, Markdown, a Stop button, a model picker, drag-and-drop documents
- Evaluation: score DocMate on questions with known answers

## Quick start

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama pull qwen3:4b            # for docmate agent
uv sync
mkdir -p documents && cp samples/* documents/
uv run docmate serve            # open http://127.0.0.1:8000
```

## Commands

| Command | What it does |
|---|---|
| `docmate ask "question" [--docs]` | one answer, optionally from your documents |
| `docmate chat` | a conversation in the terminal |
| `docmate compare "prompt" --models a b` | speed and answers of several models |
| `docmate summarize FILE` | a JSON summary of a document |
| `docmate index FOLDER` / `docmate search "query"` | build and search the index |
| `docmate agent "question"` | answer with tools |
| `docmate serve` | the web app |
| `docmate eval` | score answers on `evals/questions.json` |

## Install as a command

```bash
uv build
uv tool install dist/docmate-1.0.0-py3-none-any.whl
docmate --help
```

## Tests

```bash
./check.sh                      # format, lint, all tests (live tests skip without Ollama)
uv run pytest -m "not live"     # only the fast tests
```
