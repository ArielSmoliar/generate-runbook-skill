#!/usr/bin/env python3
"""Install this skill for Codex, Claude Code, or both."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


EXCLUDED = {"__pycache__", ".DS_Store"}


def copy_skill(source: Path, destination_root: Path, force: bool) -> Path:
    destination = destination_root / source.name
    if destination.exists():
        if not force:
            raise FileExistsError(
                f"{destination} already exists; rerun with --force to replace only this skill"
            )
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*EXCLUDED))
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("codex", "claude", "all"), default="all")
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex" / "skills")
    parser.add_argument("--claude-root", type=Path, default=Path.home() / ".claude" / "skills")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing generate-runbook installation",
    )
    args = parser.parse_args()

    source = Path(__file__).resolve().parent.parent
    targets: list[tuple[str, Path]] = []
    if args.target in {"codex", "all"}:
        targets.append(("Codex", args.codex_root.expanduser()))
    if args.target in {"claude", "all"}:
        targets.append(("Claude Code", args.claude_root.expanduser()))

    for label, root in targets:
        destination = root / source.name
        if args.dry_run:
            print(f"DRY RUN: install {source} -> {destination} for {label}")
            continue
        root.mkdir(parents=True, exist_ok=True)
        try:
            installed = copy_skill(source, root, args.force)
        except FileExistsError as error:
            print(f"ERROR: {error}")
            return 2
        print(f"INSTALLED: {label}: {installed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
