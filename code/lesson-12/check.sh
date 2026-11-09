#!/usr/bin/env bash
# Run before every commit: formatting, lint and all tests must pass.
set -euo pipefail
uv run ruff format --check .
uv run ruff check .
uv run pytest -q
