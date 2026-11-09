# Build Private AI Apps in Python with Ollama

The code for the 12-lesson course by **ClynzVen Code Academy**. You build **DocMate**, a private AI
assistant for your own documents. Everything runs on your own computer with [Ollama](https://ollama.com):
no account, no API key, and nothing you type leaves your machine.

![CI](https://github.com/clynzven/private-ai-python-ollama/actions/workflows/ci.yml/badge.svg)

## What you build

- Chat with memory, and answers that stream in word by word
- Model settings (temperature, seed) and measuring models against each other
- Structured answers checked by Pydantic
- Reading .txt, .md and .pdf files, chunking, embeddings and a SQLite search index
- Answers from your documents with sources, or an honest "I don't know"
- Tools: search, today's date and a safe calculator
- A FastAPI streaming API and a chat web page: saved chats, Markdown, a Stop button,
  a model picker and drag-and-drop documents
- An evaluation set, fast and live tests, and an installable package

## How this repository works

| Folder | What is inside |
|---|---|
| `code/lesson-01` … `code/lesson-12` | The whole project **as it is at the end of that lesson** |
| `code/docmate-complete` | The finished app |

- Every folder runs and passes its tests on its own.
- Every folder has a `LESSON.md` with a summary of the lesson, commands to try, and exercises.
- To see exactly what a lesson changed, compare two folders:

  ```bash
  diff -ru code/lesson-07 code/lesson-08
  ```

## 1. Install the tools (once)

1. **Ollama**: download it from [ollama.com](https://ollama.com) (macOS, Windows, Linux),
   or on a Mac with Homebrew: `brew install ollama`. The desktop app starts the server for you;
   otherwise run `ollama serve` in a terminal and leave it open.
2. **uv**: see [docs.astral.sh/uv](https://docs.astral.sh/uv/), or `brew install uv`.
   uv installs the right Python version (3.12) for you.
3. **The models** (about 5 GB together):

   ```bash
   ollama pull llama3.2:3b         # chat and answers (lessons 1-12)
   ollama pull nomic-embed-text    # embeddings (lesson 6 onwards)
   ollama pull qwen3:4b            # tools (lesson 3 and lesson 9)
   ```

About 8 GB of memory is enough.

## 2. Get the code

```bash
git clone https://github.com/clynzven/private-ai-python-ollama.git
cd private-ai-python-ollama
```

## 3. Follow along with a lesson

Pick the folder of the lesson you are watching, install its packages, and try it:

```bash
cd code/lesson-01
uv sync                                   # installs everything for this lesson
uv run docmate ask "In one sentence, what is Python?"
```

`LESSON.md` in each folder lists the commands for that lesson. A few examples:

```bash
uv run docmate chat                                            # lesson 2
uv run docmate compare "What is a CPU?" --models llama3.2:3b qwen3:4b   # lesson 3
uv run docmate index samples                                   # lesson 7
uv run docmate ask --docs "How long can I borrow a DVD?"       # lesson 8
uv run docmate agent "Is the library open today?"              # lesson 9
```

The `samples/` folder holds the documents of a made-up library, so you can check that DocMate
really answers from the documents.

## 4. Run the finished chat app

```bash
cd code/docmate-complete
uv sync
mkdir -p documents && cp samples/* documents/
uv run docmate serve
```

Open http://127.0.0.1:8000. Ask "How long can I borrow a DVD?", then drop one of your own
.txt, .md or .pdf files on the page and ask about it. The app only accepts requests from your own
computer.

### Use your own documents

Put your files in the `documents/` folder (or drop them on the page) and ask away. From the terminal:

```bash
uv run docmate index path/to/your/folder
uv run docmate ask --docs "your question"
```

### Install DocMate as a normal command

```bash
cd code/docmate-complete
uv build
uv tool install dist/docmate-1.0.0-py3-none-any.whl
docmate --help
```

## All commands

| Command | What it does |
|---|---|
| `docmate ask "question" [--docs]` | one answer, optionally from your documents |
| `docmate chat` | a conversation in the terminal (`/reset`, `/quit`) |
| `docmate models` | the models on this computer |
| `docmate compare "prompt" --models a b` | speed and answers of several models |
| `docmate summarize FILE` | a JSON summary of a document |
| `docmate chunks FOLDER` | how documents are cut into chunks |
| `docmate similar "query" "text" ...` | score texts by meaning |
| `docmate index FOLDER` / `docmate search "query"` | build and search the index |
| `docmate agent "question"` | answer with tools |
| `docmate serve` | the web app |
| `docmate eval` | score answers on `evals/questions.json` |

## Run the tests

```bash
./check.sh                     # formatting, lint and all tests (live tests skip without Ollama)
uv run pytest -m "not live"    # only the fast tests, no model needed
```

From lesson 11 on, the browser tests need Chromium once: `uv run playwright install chromium`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot reach Ollama. Is it running?` | Start the Ollama app, or run `ollama serve` |
| `model 'llama3.2:3b' not found` | `ollama pull llama3.2:3b` (and the other models above) |
| The first answer is slow | Normal: Ollama loads the model into memory first, then keeps it for 5 minutes |
| `docmate ask --docs` says "I don't know" for everything | Run `uv run docmate index samples` first |
| Browser tests are skipped | `uv run playwright install chromium` |

## License

MIT. The sample documents describe a made-up library.
