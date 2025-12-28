#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

ALLOWED_TYPES = (
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore",
)

SCOPE_PATTERN = r"[a-zA-Z0-9._-]+"
COMMIT_PATTERN = re.compile(
    rf"^({'|'.join(ALLOWED_TYPES)})\({SCOPE_PATTERN}\): .+"
)


def _first_subject_line(message_path: Path) -> str:
    for line in message_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped
    return ""


def main() -> int:
    if os.getenv("CI"):
        return 0

    if len(sys.argv) < 2:
        print("Missing commit message file path.", file=sys.stderr)
        return 1

    message_path = Path(sys.argv[1])
    if not message_path.exists():
        print(f"Commit message file not found: {message_path}", file=sys.stderr)
        return 1

    subject = _first_subject_line(message_path)
    if not subject:
        print("Empty commit message.", file=sys.stderr)
        return 1

    if not COMMIT_PATTERN.match(subject):
        allowed = ", ".join(ALLOWED_TYPES)
        print(
            "Invalid commit message. Expected: type(scope): subject", file=sys.stderr
        )
        print(f"Allowed types: {allowed}", file=sys.stderr)
        print("Example: feat(auth): add login", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
