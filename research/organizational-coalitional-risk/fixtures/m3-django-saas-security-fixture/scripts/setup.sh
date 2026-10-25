#!/usr/bin/env bash
# Create an isolated virtual environment with the exact tested dependencies.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

"$PYTHON" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --quiet --upgrade pip
"$ROOT/.venv/bin/python" -m pip install --quiet -r "$ROOT/requirements.lock.txt"

echo "Environment ready: $ROOT/.venv"
echo "Python: $("$ROOT/.venv/bin/python" --version)"
