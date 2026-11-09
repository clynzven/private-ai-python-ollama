"""The docmate command line."""

import argparse
import sys

import ollama

from docmate.chat import Chat
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
    return parser


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
    except ConnectionError:
        print("Cannot reach Ollama. Is it running? Start it with: ollama serve", file=sys.stderr)
        return 1
    except ollama.ResponseError as err:
        print(f"Ollama error: {err.error}", file=sys.stderr)
        return 1
    return 0
