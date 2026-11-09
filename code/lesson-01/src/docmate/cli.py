"""The docmate command line."""

import argparse
import sys

import ollama

from docmate.llm import DEFAULT_MODEL, ask, list_models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docmate",
        description="A private AI assistant that runs on your computer.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    ask_cmd = commands.add_parser("ask", help="ask the model one question")
    ask_cmd.add_argument("prompt", help="what you want to ask")
    ask_cmd.add_argument("--model", default=DEFAULT_MODEL, help="which model to use")

    commands.add_parser("models", help="list the models on this computer")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ask":
            print(ask(args.prompt, model=args.model))
        elif args.command == "models":
            for name in list_models():
                print(name)
    except ConnectionError:
        print("Cannot reach Ollama. Is it running? Start it with: ollama serve", file=sys.stderr)
        return 1
    except ollama.ResponseError as err:
        print(f"Ollama error: {err.error}", file=sys.stderr)
        return 1
    return 0
