# Generate Runbook

A portable Codex and Claude Code plugin for creating, reviewing, validating, dry-running, executing, and auditing operational runbooks.

It produces procedures with explicit preservation requirements, verification, approval gates, stop conditions, evidence rules, and rollback coverage.

Development version: `0.4.0` (release pending). Licensed under Apache 2.0.

Version 0.4 adds draft/ready structural validation, a durable execution record,
authorization reuse across resumptions, explicit retry reconciliation, and
evidence bound to exact artifacts and supported claims. These checks do not
authorize actions or replace live verification.

[Privacy](docs/privacy.md) · [Terms](docs/terms.md) · [Support](docs/support.md)

## Codex marketplace

Add the public marketplace and install the plugin:

```bash
codex plugin marketplace add ArielSmoliar/generate-runbook-skill --ref main
codex plugin add generate-runbook@ariel-smoliar-tools
```

Start a new Codex task, then use:

```text
Use $generate-runbook to create a production deployment runbook for this service.
```

## Claude Code marketplace

Inside Claude Code:

```text
/plugin marketplace add ArielSmoliar/generate-runbook-skill
/plugin install generate-runbook@ariel-smoliar-tools
/reload-plugins
```

The skill is namespaced as:

```text
/generate-runbook:generate-runbook
```

Claude can also load it automatically for runbook, playbook, SOP, launch checklist, rollback plan, incident procedure, and operational-handoff requests.

## Direct skill installation

Users who prefer the standalone skill can still install it without the plugin layer.

Clone the published release source (the 0.4.0 development changes are not yet tagged):

```bash
git clone --branch v0.3.0 --depth 1 \
  https://github.com/ArielSmoliar/generate-runbook-skill.git
cd generate-runbook-skill
```

Install for Codex, Claude Code, or both:

```bash
python3 plugins/generate-runbook/skills/generate-runbook/scripts/install_skill.py --target codex
python3 plugins/generate-runbook/skills/generate-runbook/scripts/install_skill.py --target claude
python3 plugins/generate-runbook/skills/generate-runbook/scripts/install_skill.py --target all
```

An existing direct installation is preserved unless the user explicitly passes `--force`.
If both standalone and plugin copies are installed, compare their contents before
upgrading. Back up local changes and align them to the same verified version;
do not edit a managed plugin cache to simulate a marketplace update.

## Validate

```bash
python3 plugins/generate-runbook/skills/generate-runbook/scripts/test_skill.py
python3 plugins/generate-runbook/skills/generate-runbook/scripts/validate_runbook.py \
  plugins/generate-runbook/skills/generate-runbook/assets/runbook-template.md
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/generate-runbook
claude plugin validate .
```

For a completed procedure in the bundled Markdown format:

```bash
python3 plugins/generate-runbook/skills/generate-runbook/scripts/validate_runbook.py \
  path/to/runbook.md --mode ready
```

Draft mode is the default and reports incomplete fields as warnings. Ready mode
rejects missing operational fields and per-step verification, failure handling,
approval disposition or retry safety. Neither mode proves semantic correctness,
authorization or live readiness. Execution records are operator-reviewed, not
automatically enforced. The drift script checks referenced paths only; live
deployment, schema and external workflow drift require independent inspection.

## Release

Build the deterministic standalone ZIP and SHA-256 checksum:

```bash
python3 scripts/build_release.py
```

Never add user profiles, credentials, private infrastructure identifiers, or generated operational evidence to this repository.
