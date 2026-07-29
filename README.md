# Generate Runbook

A portable Codex and Claude Code skill for creating, reviewing, validating, dry-running, executing, and auditing operational runbooks.

It produces procedures with explicit preservation requirements, verification, approval gates, stop conditions, evidence rules, and rollback coverage.

Current version: `0.1.0`. Licensed under Apache 2.0.

## Install

Preview the destinations:

```bash
python3 generate-runbook/scripts/install_skill.py --target all --dry-run
```

Install for Codex, Claude Code, or both:

```bash
python3 generate-runbook/scripts/install_skill.py --target codex
python3 generate-runbook/scripts/install_skill.py --target claude
python3 generate-runbook/scripts/install_skill.py --target all
```

An existing installation is preserved unless the user explicitly passes `--force`:

```bash
python3 generate-runbook/scripts/install_skill.py --target all --force
```

The installer replaces only the `generate-runbook` directory at the selected destination. It does not modify other skills.

## Use

Invoke the skill explicitly:

```text
Use $generate-runbook to create a production deployment runbook for this service.
```

It also triggers for requests involving operational runbooks, playbooks, standard operating procedures, launch checklists, rollback plans, incident procedures, and operational handoffs.

## Validate

```bash
python3 generate-runbook/scripts/test_skill.py
python3 generate-runbook/scripts/validate_runbook.py generate-runbook/assets/runbook-template.md
python3 generate-runbook/scripts/install_skill.py --target all --dry-run
```

Codex users can additionally run the skill metadata validator distributed with Codex:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py generate-runbook
```

## Release

Build the deterministic standalone ZIP and SHA-256 checksum:

```bash
python3 scripts/build_release.py
```

Never add user profiles, credentials, private infrastructure identifiers, or generated operational evidence to this repository.
