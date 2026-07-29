---
name: generate-runbook
description: Create, review, validate, dry-run, and audit operational runbooks for software releases, incidents, migrations, recurring procedures, and other high-consequence workflows. Use when a user asks for a runbook, playbook, standard operating procedure, launch checklist, rollback plan, incident procedure, operational handoff, or validation of an existing runbook.
---

# Generate Runbook

Turn operational intent into a procedure another operator or agent can execute safely.

## Workflow

1. Inspect the repository, system, existing documentation, and available tools before drafting.
2. Separate verified facts from assumptions. Resolve safe, read-only questions directly.
3. Identify the operator, environment, scope, prerequisites, expected duration, and completion signal.
4. Classify each action:
   - `read-only`: inspection with no state change
   - `reversible`: state change with a tested recovery path
   - `destructive`: deletion, replacement, irreversible migration, credential rotation, or broad external impact
5. Add explicit approval gates before destructive actions and material external changes.
6. Write the runbook using `assets/runbook-template.md`.
7. Include exact verification after every consequential phase, not only at the end.
8. Include rollback criteria and instructions that do not depend on the failed component.
9. Validate the result with `scripts/validate_runbook.py`.
10. Report unresolved assumptions, validation results, and the safest next action.

## Operating modes

- **Generate**: Create a new runbook from evidence and stated intent.
- **Review**: Find ambiguity, unsafe steps, missing verification, and weak rollback coverage.
- **Dry run**: Simulate decisions and commands without changing state. Never claim execution occurred.
- **Execute**: Follow an approved runbook one gated step at a time. Pause at approval gates and stop conditions.
- **Drift audit**: Compare a runbook with current code, infrastructure, interfaces, and ownership.

Read `references/runbook-schema.md` before generating or reviewing a runbook.
Read `references/safety-gates.md` for production, destructive, security-sensitive, or external-facing operations.
Read only the relevant platform adapter: `references/codex-adapter.md` or `references/claude-adapter.md`.

## Required qualities

- Make steps atomic, ordered, observable, and attributable.
- Use exact commands only after verifying paths, flags, environment, and scope.
- Never put secrets, tokens, private content, or reviewer credentials in the runbook.
- Prefer stable identifiers over UI position or screenshots.
- State what must remain unchanged.
- Define stop conditions for privacy leaks, data loss, security incidents, outages, and destructive recovery.
- Keep evidence sanitized and proportionate.
- Distinguish rollback from retry.
- Do not invent commands, dashboards, owners, URLs, or success criteria.

## Validation

Run:

```bash
python3 scripts/validate_runbook.py PATH_TO_RUNBOOK.md
```

Treat errors as blocking. Treat warnings as items requiring an explicit disposition.

For drift checks, run:

```bash
python3 scripts/check_runbook_drift.py PATH_TO_RUNBOOK.md REPOSITORY_ROOT
```

This is a heuristic check. Confirm reported paths and commands manually before execution.
