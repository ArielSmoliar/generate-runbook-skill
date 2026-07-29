# Safety gates

## Gate levels

### Gate 0 — Read-only

Proceed when the target is clear and inspection does not expose secrets or private content.

### Gate 1 — Reversible change

Require a verified target, current health check, recovery path, post-change verification, and bounded scope.

### Gate 2 — Production or external change

Require explicit authorization, named operator, blast-radius assessment, stop conditions, rollback owner, communication plan, and live monitoring.

### Gate 3 — Destructive or irreversible change

Require explicit approval immediately before execution, independently verified targets, recoverable backup when possible, dry run, precise exclusions, and a second-person check when the organization supports it.

## Mandatory stops

Stop immediately for:

- unexpected access to another user’s data
- data loss or corruption
- credential or secret exposure
- production outage outside the stated tolerance
- a target that differs from the approved scope
- recovery that requires an unapproved destructive action
- verification signals that are unavailable or contradictory

Do not convert a failed verification into an improvised repair. Contain, preserve evidence, and obtain a new decision.

## Command rules

- Resolve paths and identifiers with read-only checks.
- Avoid broad globs, unresolved variables, and recursive deletion.
- Never target a home directory, repository root, filesystem root, or shared production resource ambiguously.
- Prefer reversible operations and non-interactive commands.
- Redact secret values from commands and evidence.
