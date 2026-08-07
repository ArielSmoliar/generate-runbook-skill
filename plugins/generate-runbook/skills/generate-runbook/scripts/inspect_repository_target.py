#!/usr/bin/env python3
"""Read-only Git worktree and target identity inspection."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def git(repository: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def resolve(repository: Path, ref: str) -> str | None:
    value = git(repository, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
    return value or None


def parse_worktrees(raw: str) -> list[dict[str, str]]:
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in [*raw.splitlines(), ""]:
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return worktrees


def inspect(
    repository: Path,
    target_ref: str | None = None,
    target_commit: str | None = None,
    require_clean: bool = False,
    remote_freshness_required: bool = False,
) -> tuple[dict[str, object], bool]:
    root = Path(git(repository, "rev-parse", "--show-toplevel")).resolve()
    head = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    branch = git(root, "branch", "--show-current") or None
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    remote = git(root, "remote", "get-url", "origin", check=False) or None
    resolved_ref = resolve(root, target_ref) if target_ref else None
    resolved_commit = resolve(root, target_commit) if target_commit else None
    expected = resolved_commit or resolved_ref
    expected_tree = git(root, "rev-parse", f"{expected}^{{tree}}") if expected else None

    worktrees = parse_worktrees(git(root, "worktree", "list", "--porcelain"))
    candidates = [
        {
            "path": item.get("worktree", ""),
            "head": item.get("HEAD", ""),
            "branch": item.get("branch", "").removeprefix("refs/heads/") or None,
        }
        for item in worktrees
        if expected and item.get("HEAD") == expected
    ]

    failures: list[str] = []
    if target_ref and resolved_ref is None:
        failures.append(f"target ref does not resolve locally: {target_ref}")
    if target_commit and resolved_commit is None:
        failures.append(f"target commit does not resolve locally: {target_commit}")
    if resolved_ref and resolved_commit and resolved_ref != resolved_commit:
        failures.append("target ref and target commit resolve to different commits")
    if expected and head != expected:
        failures.append("HEAD does not match requested target commit")
    local_branch_ref = (
        git(root, "show-ref", "--verify", f"refs/heads/{target_ref}", check=False)
        if target_ref and not target_ref.startswith("refs/")
        else ""
    )
    requested_branch = None
    if target_ref and target_ref.startswith("refs/heads/"):
        requested_branch = target_ref.removeprefix("refs/heads/")
    elif target_ref and local_branch_ref:
        requested_branch = target_ref
    if requested_branch:
        if branch != requested_branch:
            failures.append(f"current branch is {branch or 'detached'}, not {requested_branch}")
    if require_clean and status:
        failures.append("worktree is not clean")
    if remote_freshness_required:
        failures.append("remote freshness is required but has not been verified")

    report: dict[str, object] = {
        "repository_root": str(root),
        "remote_origin": remote,
        "worktree": str(root),
        "branch": branch,
        "head": head,
        "tree": tree,
        "dirty": bool(status),
        "target_ref": target_ref,
        "target_ref_commit": resolved_ref,
        "target_commit": target_commit,
        "target_commit_resolved": resolved_commit,
        "target_tree": expected_tree,
        "head_matches_target": bool(expected and head == expected) if expected else None,
        "tree_matches_target": bool(expected_tree and tree == expected_tree) if expected else None,
        "matching_worktrees": candidates,
        "remote_freshness": (
            "unknown and required; no fetch performed"
            if remote_freshness_required
            else "not required; no fetch performed"
        ),
        "failures": failures,
    }
    return report, not failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--target-ref")
    parser.add_argument("--target-commit")
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--remote-freshness-required", action="store_true")
    args = parser.parse_args()
    try:
        report, passed = inspect(
            args.repository,
            target_ref=args.target_ref,
            target_commit=args.target_commit,
            require_clean=args.require_clean,
            remote_freshness_required=args.remote_freshness_required,
        )
    except RuntimeError as error:
        print(json.dumps({"failures": [str(error)]}, indent=2))
        return 2
    print(json.dumps(report, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
