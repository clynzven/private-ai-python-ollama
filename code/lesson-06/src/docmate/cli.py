"""The docmate command line."""

import argparse
import sys
from pathlib import Path

import ollama

from docmate.chat import Chat
from docmate.documents import find_documents, load_chunks, load_text
from docmate.embeddings import embed, rank
from docmate.extract import DocSummary, ExtractionError, extract
from docmate.llm import DEFAULT_MODEL, Settings, ask, list_models, timed_ask


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docmate",
        description="A private AI assistant that runs on your computer.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    ask_cmd = commands.add_parser("ask", help="ask the model one question")
    ask_cmd.add_argument("prompt", help="what you want to ask")
    ask_cmd.add_argument("--model", default=DEFAULT_MODEL, help="which model to use")
    add_settings(ask_cmd)

    commands.add_parser("models", help="list the models on this computer")

    chat_cmd = commands.add_parser("chat", help="have a conversation with the model")
    chat_cmd.add_argument("--model", default=DEFAULT_MODEL, help="which model to use")
    add_settings(chat_cmd)

    compare_cmd = commands.add_parser("compare", help="ask several models and compare speed")
    compare_cmd.add_argument("prompt")
    compare_cmd.add_argument("--models", nargs="+", default=[DEFAULT_MODEL])
    add_settings(compare_cmd)

    summarize_cmd = commands.add_parser("summarize", help="summarize a document as JSON")
    summarize_cmd.add_argument("file", type=Path)
    summarize_cmd.add_argument("--model", default=DEFAULT_MODEL)

    chunks_cmd = commands.add_parser("chunks", help="show how documents are cut into chunks")
    chunks_cmd.add_argument("folder", type=Path)
    chunks_cmd.add_argument("--show", help="print the chunks of this file")

    similar_cmd = commands.add_parser("similar", help="score texts by meaning against a query")
    similar_cmd.add_argument("query")
    similar_cmd.add_argument("texts", nargs="+")
    return parser


def run_similar(query: str, texts: list[str]) -> None:
    [query_vector] = embed([query], kind="query")
    vectors = embed(texts)
    print(f"vectors have {len(query_vector)} numbers")
    for i, score in rank(query_vector, vectors):
        print(f"{score:.3f}  {texts[i]}")


def run_chunks(folder: Path, show: str | None) -> None:
    chunks = load_chunks(folder)
    if show:
        for c in chunks:
            if c.source == show:
                print(f"--- {c.source} #{c.index} ({len(c.text.split())} words)\n{c.text}")
        return
    for path in find_documents(folder):
        name = str(path.relative_to(folder))
        mine = [c for c in chunks if c.source == name]
        words = sum(len(c.text.split()) for c in mine)
        label = "chunk " if len(mine) == 1 else "chunks"
        print(f"{name:<26} {len(mine)} {label}  {words:>4} words")
    print(f"total: {len(chunks)} chunks")


def add_settings(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument("--temperature", type=float, help="0 = focused, 1 = creative")
    cmd.add_argument("--seed", type=int, help="fix the randomness to repeat an answer")


def settings_from(args) -> Settings:
    return Settings(temperature=args.temperature, seed=args.seed)


def run_compare(prompt: str, models: list[str], settings: Settings) -> None:
    print(f"{'model':<14} {'seconds':>7} {'tokens':>6} {'tok/s':>6}  answer")
    for model in models:
        answer, t = timed_ask(prompt, model=model, settings=settings)
        short = answer.replace("\n", " ")
        short = short if len(short) <= 60 else short[:57] + "..."
        print(f"{model:<14} {t.seconds:>7.1f} {t.tokens:>6} {t.tokens_per_second:>6.1f}  {short}")


def run_chat(model: str, settings: Settings | None = None) -> None:
    chat = Chat(model=model, settings=settings)
    print(f"Chatting with {model}. Type /reset to start over, /quit to leave.")
    while True:
        try:
            text = input("you> ").strip()
        except EOFError:
            break
        if not sys.stdin.isatty():
            print(text)  # echo piped input so the transcript reads naturally
        if text == "/quit":
            break
        if text == "/reset":
            chat.reset()
            print("(conversation cleared)")
            continue
        if not text:
            continue
        print("docmate> ", end="", flush=True)
        for piece in chat.send(text):
            print(piece, end="", flush=True)
        print()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ask":
            print(ask(args.prompt, model=args.model, settings=settings_from(args)))
        elif args.command == "models":
            for name in list_models():
                print(name)
        elif args.command == "chat":
            run_chat(args.model, settings_from(args))
        elif args.command == "compare":
            run_compare(args.prompt, args.models, settings_from(args))
        elif args.command == "summarize":
            summary = extract(load_text(args.file), DocSummary, model=args.model)
            print(summary.model_dump_json(indent=2))
        elif args.command == "chunks":
            run_chunks(args.folder, args.show)
        elif args.command == "similar":
            run_similar(args.query, args.texts)
    except ConnectionError:
        print("Cannot reach Ollama. Is it running? Start it with: ollama serve", file=sys.stderr)
        return 1
    except ollama.ResponseError as err:
        print(f"Ollama error: {err.error}", file=sys.stderr)
        return 1
    except ExtractionError as err:
        print(f"Sorry: {err}", file=sys.stderr)
        return 1
    return 0
