---
name: generate-runbook
description: Create, review, validate, dry-run, and audit operational runbooks for software releases, incidents, migrations, recurring procedures, and other high-consequence workflows. Use when a user asks for a runbook, playbook, standard operating procedure, launch checklist, rollback plan, incident procedure, operational handoff, or validation of an existing runbook.
---

# Generate Runbook

Turn operational intent into a procedure another operator or agent can execute safely.

## Workflow

1. When using repository evidence, resolve and verify the intended target before inspection. Read `references/repository-targeting.md` and treat a required repository, branch, commit, cleanliness, or freshness mismatch as a stop condition unless the user explicitly accepts it. For supplied artifacts or non-repository operations, record their identity and limits without inventing a checkout or claiming live verification.
2. Inspect the verified repository, system, existing documentation, and available tools before drafting.
3. Separate verified facts from assumptions. Resolve safe, read-only questions directly.
4. Identify the operator, environment, scope, prerequisites, expected duration, and completion signal.
5. Classify each action:
   - `read-only`: inspection with no state change
   - `reversible`: state change with a tested recovery path
   - `destructive`: deletion, replacement, irreversible migration, credential rotation, or broad external impact
6. Add explicit approval gates before destructive actions and material external changes.
7. Write the runbook using `assets/runbook-template.md`.
8. Include exact verification after every consequential phase, not only at the end.
9. Include rollback criteria and instructions that do not depend on the failed component.
10. Validate drafts with `scripts/validate_runbook.py --mode draft`. Before execution, run `--mode ready` and independently verify live prerequisites, evidence and authorization.
11. For execution or handoff, maintain `assets/execution-record-template.md`: current state, consumed authorizations, step outcomes and evidence bound to the exact artifact.
12. Report the verified target identity, unresolved assumptions, validation results, and the next authorized action.

## Operating modes

- **Generate**: Create a new runbook from evidence and stated intent.
- **Review**: Find ambiguity, unsafe steps, missing verification, and weak rollback coverage.
- **Dry run**: Simulate decisions and commands without changing state. Never claim execution occurred.
- **Execute / Resume**: Reconcile the durable execution record with live state, then follow the next authorized incomplete step. Preserve completed work and consumed grants; reconcile unknown outcomes before retrying.
- **Drift audit**: Compare a runbook with current code, infrastructure, interfaces, and ownership.

Read `references/runbook-schema.md` before generating or reviewing a runbook.
Read `references/repository-targeting.md` before using repository evidence.
Read `references/safety-gates.md` for production, destructive, security-sensitive, or external-facing operations.
Read only the relevant platform adapter: `references/codex-adapter.md` or `references/claude-adapter.md`.
Read `references/execution-and-evidence.md` for execution, resumption, handoff, or review of prior results. It defines authorization reuse, uncertain outcomes and the evidence needed to support a claim.

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
python3 scripts/validate_runbook.py PATH_TO_RUNBOOK.md --mode draft
python3 scripts/validate_runbook.py PATH_TO_RUNBOOK.md --mode ready
```

Treat errors as blocking. Treat warnings as items requiring an explicit disposition.
Draft mode allows incomplete fields with warnings. Ready mode requires the bundled
Markdown format, populated operational fields, stable step IDs, verification,
failure handling, approval disposition and retry safety. Update older runbooks to
the template before using ready mode. Execution records are reviewed by the
operator; the linter does not parse or validate their ledgers.

A structural pass is not authorization or proof of command safety, evidence
validity, current system state or operational readiness. Check these separately.

For drift checks, run:

```bash
python3 scripts/check_runbook_drift.py PATH_TO_RUNBOOK.md REPOSITORY_ROOT
```

This is a heuristic check. Confirm reported paths and commands manually before execution.
