#!/usr/bin/env python3
"""Validate shared Codex and Claude plugin marketplace metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "generate-runbook"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    codex = load(PLUGIN / ".codex-plugin" / "plugin.json")
    claude = load(PLUGIN / ".claude-plugin" / "plugin.json")
    codex_market = load(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = load(ROOT / ".claude-plugin" / "marketplace.json")

    assert SEMVER.fullmatch(version), "VERSION must be strict semver"
    assert codex["name"] == claude["name"] == "generate-runbook"
    assert codex["version"] == claude["version"] == version
    assert (PLUGIN / "skills" / "generate-runbook" / "SKILL.md").is_file()
    assert codex["skills"] == "./skills/"
    assert codex_market["name"] == claude_market["name"] == "ariel-smoliar-tools"
    assert codex_market["plugins"][0]["name"] == "generate-runbook"
    assert claude_market["plugins"][0]["name"] == "generate-runbook"
    assert claude_market["plugins"][0]["version"] == version
    print("Plugin and marketplace manifests are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
