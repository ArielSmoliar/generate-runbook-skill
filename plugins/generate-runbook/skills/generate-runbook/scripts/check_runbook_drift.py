#!/usr/bin/env python3
"""Heuristically flag repository paths named in a runbook that no longer exist."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PATH_TOKEN = re.compile(r"`((?:\./)?(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+)`")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runbook", type=Path)
    parser.add_argument("repository", type=Path)
    args = parser.parse_args()

    if not args.runbook.is_file() or not args.repository.is_dir():
        print("ERROR: provide an existing runbook and repository directory")
        return 2

    text = args.runbook.read_text(encoding="utf-8")
    candidates = sorted(set(PATH_TOKEN.findall(text)))
    missing: list[str] = []
    for token in candidates:
        relative = token[2:] if token.startswith("./") else token
        if not (args.repository / relative).exists():
            missing.append(token)

    for token in missing:
        print(f"WARNING: referenced path not found: {token}")
    print(f"CHECKED: {len(candidates)} path reference(s); {len(missing)} missing")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
