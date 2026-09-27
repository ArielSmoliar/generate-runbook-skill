#!/usr/bin/env python3
"""Lint the bundled Markdown format; never authorize or execute a procedure."""

from __future__ import annotations

import argparse
from datetime import date
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = (
    "Metadata", "Objective", "Scope", "Preconditions", "Risk and stop conditions",
    "Evidence plan", "Procedure", "Rollback", "Completion criteria",
    "Communications", "Record",
)
REQUIRED_FIELDS = {
    "Metadata": ("Status", "Owner", "Operator", "Go/no-go owner", "Last verified", "Environment",
                 "Expected duration", "Change/incident ID", "Runbook revision", "Target artifact"),
    "Scope": ("Included", "Excluded", "Must remain unchanged"),
    "Preconditions": ("Entry signal", "Entry verification"),
    "Risk and stop conditions": ("Risk", "Stop immediately if"),
    "Evidence plan": ("Record", "Store in", "Never record", "Binding"),
    "Rollback": ("Trigger", "Decision owner", "Actions", "Verification", "Limitations"),
    "Communications": ("Start", "Failure", "Completion"),
    "Record": ("Execution record",),
}
STEP_FIELDS = (
    "Step ID", "Action", "Expected result", "Verify", "If verification fails",
    "Approval required", "Retry safety",
)
SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{12,}", re.I),
)


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def prose(text: str) -> str:
    """Exclude comments and fenced code from structural checks."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.fullmatch(r"\s{0,3}" + re.escape(fence[0]) + r"{" + str(len(fence)) + r",}\s*", line):
                fence = None
        elif marker:
            fence = marker.group(1)
        else:
            lines.append(line)
    return "\n".join(lines)


def field_values(body: str) -> dict[str, str]:
    """Read inline template values and the three Scope block labels."""
    pattern = re.compile(
        r"^[ \t]*(?:(?:[-*]|\d+\.)[ \t]+)?(?:\*\*)?"
        r"([A-Za-z][A-Za-z /-]*?)(?::(?:\*\*)?|\*\*:?)[ \t]*(.*)$", re.M
    )
    matches = list(pattern.finditer(body))
    values = {}
    for i, match in enumerate(matches):
        name = normalize_heading(match.group(1))
        if name not in {"included", "excluded", "must remain unchanged"}:
            # A generic checklist after a blank field is not that field's value.
            values[name] = match.group(2).strip()
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        # A phase heading must not supply the value of an empty preceding field.
        value = re.split(r"^#{1,6}\s", body[match.start(2):end], maxsplit=1, flags=re.M)[0]
        values[name] = value.strip()
    return values


def placeholders(text: str) -> list[str]:
    # Links, images, reference links/definitions, footnotes, checkboxes and
    # inline code are not template placeholders. This is not a Markdown parser.
    definitions = set(re.findall(r"^\s*\[([^\]\n]+)\]:", text, re.M))
    text = re.sub(r"`+[^`\n]*`+", "", text)
    text = re.sub(r"^\s*\[[^\]\n]+\]:.*$", "", text, flags=re.M)
    text = re.sub(r"!?\[[^\]\n]*\](?:\([^\n]*?\)|\[[^\]\n]*\])", "", text)
    text = re.sub(r"\[\^[^\]\n]+\]|\[[ xX]\]", "", text)
    found = re.findall(r"\[[^\]\n]{2,80}\]|\b(?:TODO|TBD|UNSET|YYYY-MM-DD)\b", text)
    return [item for item in found if item.strip("[]") not in definitions]


def populated(value: str) -> bool:
    value = re.sub(r"^[\s*#\-\[\]]+", "", value).strip()
    return bool(value) and value.casefold() not in {"none", "n/a", "not applicable"}


def validate(path: Path, mode: str = "draft") -> tuple[list[str], list[str]]:
    if mode not in {"draft", "ready"}:
        raise ValueError("mode must be draft or ready")
    text = path.read_text(encoding="utf-8")
    body = prose(text)
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, re.M))
    sections = {}
    errors: list[str] = []
    warnings: list[str] = []
    readiness = errors if mode == "ready" else warnings
    for i, match in enumerate(matches):
        name = normalize_heading(match.group(1))
        if name in sections:
            errors.append(f"duplicate section: {match.group(1)}")
        sections[name] = body[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(body)].strip()

    for section in REQUIRED_SECTIONS:
        key = normalize_heading(section)
        if key not in sections:
            errors.append(f"missing required section: {section}")
        elif not populated(sections[key]):
            readiness.append(f"empty section or unexplained not-applicable value: {section}")

    for word, message in ((r"\bstop\b", "no explicit stop condition found"),
                          (r"\bverif(?:y|ication)\b", "no verification instruction found"),
                          (r"\brollback\b", "no rollback coverage found")):
        if not re.search(word, body, re.I):
            errors.append(message)

    fields = {name: field_values(sections.get(normalize_heading(name), ""))
              for name in REQUIRED_FIELDS}
    for section, labels in REQUIRED_FIELDS.items():
        for label in labels:
            if not populated(fields[section].get(normalize_heading(label), "")):
                readiness.append(f"missing populated field: {section} / {label}")

    status = fields["Metadata"].get("status", "").casefold()
    if mode == "ready" and status not in {"approved", "in progress"}:
        errors.append("ready mode requires Status: Approved or In progress; this is a declaration, not proof of approval")
    if mode == "draft" and status in {"approved", "in progress"}:
        warnings.append("execution status declared; run --mode ready before execution")
    verified = fields["Metadata"].get("last verified", "")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified):
            raise ValueError
        if date.fromisoformat(verified) > date.today():
            raise ValueError
    except ValueError:
        readiness.append("Last verified must be a real, non-future YYYY-MM-DD date")

    procedure = sections.get("procedure", "")
    actions = list(re.finditer(r"^\s*\d+\.\s+\*\*Action:\*\*", procedure, re.M))
    if not actions:
        readiness.append("Procedure requires numbered **Action:** steps in the bundled format")
    seen_ids = set()
    for i, action in enumerate(actions):
        step = field_values(procedure[action.start():actions[i + 1].start() if i + 1 < len(actions) else len(procedure)])
        for label in STEP_FIELDS:
            if not populated(step.get(normalize_heading(label), "")):
                readiness.append(f"step {i + 1}: missing populated {label}")
        step_id = step.get("step id", "").strip("`")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", step_id):
            readiness.append(f"step {i + 1}: Step ID must be a stable identifier")
        elif step_id in seen_ids:
            readiness.append(f"duplicate Step ID: {step_id}")
        seen_ids.add(step_id)

    unresolved = placeholders(body)
    if unresolved:
        readiness.append(f"{len(unresolved)} unresolved template placeholder(s)")
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append("possible secret or private key found")
            break
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runbook", type=Path)
    parser.add_argument("--mode", choices=("draft", "ready"), default="draft")
    args = parser.parse_args()
    try:
        errors, warnings = validate(args.runbook, args.mode)
    except (OSError, UnicodeError) as error:
        print(f"ERROR: cannot read runbook: {error}")
        return 2
    for issue in errors:
        print(f"ERROR: {issue}")
    for issue in warnings:
        print(f"WARNING: {issue}")
    if not errors:
        print(f"PASS: {args.mode} structural checks passed: {args.runbook}")
        print("Not authorization or proof of live state, evidence validity, command safety, or operational readiness.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
