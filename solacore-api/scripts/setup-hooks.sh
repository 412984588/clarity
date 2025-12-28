#!/usr/bin/env bash
set -euo pipefail

if [ -n "${CI:-}" ]; then
  echo "CI environment detected; skipping git hook installation."
  exit 0
fi

if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit is not installed. Install dev dependencies first." >&2
  echo "Example: poetry install --with dev" >&2
  exit 1
fi

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

pre-commit install --install-hooks
pre-commit install --hook-type commit-msg --install-hooks
pre-commit install --hook-type pre-push --install-hooks

echo "Git hooks installed via pre-commit."
