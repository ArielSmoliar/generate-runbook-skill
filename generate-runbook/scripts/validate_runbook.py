#!/usr/bin/env python3
"""Validate the structural safety coverage of a Markdown runbook."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = (
    "Metadata",
    "Objective",
    "Scope",
    "Preconditions",
    "Risk and stop conditions",
    "Evidence plan",
    "Procedure",
    "Rollback",
    "Completion criteria",
    "Communications",
    "Record",
)

SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{12,}", re.I),
)


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def validate(path: Path) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    headings = {
        normalize_heading(match.group(1))
        for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
    }
    errors: list[str] = []
    warnings: list[str] = []

    for section in REQUIRED_SECTIONS:
        if normalize_heading(section) not in headings:
            errors.append(f"missing required section: {section}")

    if not re.search(r"\bstop\b", text, re.I):
        errors.append("no explicit stop condition found")
    if not re.search(r"\bverif(?:y|ication)\b", text, re.I):
        errors.append("no verification instruction found")
    if not re.search(r"\brollback\b", text, re.I):
        errors.append("no rollback coverage found")
    if not re.search(r"\bapproval\b", text, re.I):
        warnings.append("no approval gate mentioned")
    if not re.search(r"\bmust remain unchanged\b|\bexcluded\b", text, re.I):
        warnings.append("no preservation invariant or exclusion found")
    if not re.search(r"\bowner\b", text, re.I):
        warnings.append("no owner identified")

    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append("possible secret or private key found")
            break

    placeholders = re.findall(r"\[[^\]\n]{2,80}\]", text)
    if placeholders:
        warnings.append(f"{len(placeholders)} unresolved bracketed placeholder(s)")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runbook", type=Path)
    args = parser.parse_args()

    if not args.runbook.is_file():
        print(f"ERROR: runbook not found: {args.runbook}")
        return 2

    errors, warnings = validate(args.runbook)
    for issue in errors:
        print(f"ERROR: {issue}")
    for issue in warnings:
        print(f"WARNING: {issue}")
    if not errors:
        print(f"PASS: {args.runbook}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
