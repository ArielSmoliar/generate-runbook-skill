# Generate Runbook

A portable Codex and Claude Code plugin for creating, reviewing, validating, dry-running, executing, and auditing operational runbooks.

Create a procedure another operator or agent can follow, verify, and resume.
Each runbook defines its target, preservation requirements, approval boundaries,
stop conditions, verification steps, and recovery path.

**Release status:** `0.3.0` is the published version. This branch prepares
`0.4.0`; it is not yet released. The new validation modes and execution-record
workflow below require the 0.4.0 candidate. Licensed under Apache 2.0.

[Privacy](docs/privacy.md) · [Terms](docs/terms.md) · [Support](docs/support.md)

## What's new in 0.4.0

| Improvement | What it changes |
|---|---|
| Entry and decision ownership | Require an observable entry signal, its verification check, a rollback/containment trigger, and an explicit final go/no-go owner before reuse. |
| Draft and ready validation | Drafts report incomplete fields as warnings. Ready checks reject missing operational details, per-step checks, duplicate step IDs, and unresolved prose placeholders. Ordinary Markdown links are no longer mistaken for placeholders. |
| Durable execution records | Preserve the current snapshot, completed steps, failed or unknown outcomes, consumed authorizations, and next authorized action across sessions. |
| Authorization reuse | Continue within existing valid authority. A restart does not replenish spent calls or budget, and an Approved document is not itself an authorization. |
| Retry reconciliation | Check whether an uncertain external action succeeded before repeating it. Record repeat safety, attempt limits, timeouts, and operation IDs where available. |
| Evidence tied to claims | Record the exact artifact, environment, observation time, method, supported claim, and limitations. Older-build or simulated evidence cannot silently satisfy a live candidate gate. |

Repository targeting remains part of the workflow: verify the intended checkout,
branch or commit before drawing repository-backed conclusions. Keep source
inspection separate from deployed state, applied migrations, and production health.

## Use the skill

| Mode | Example request |
|---|---|
| Generate | “Create a deployment runbook for this service using the current checkout. Do not deploy.” |
| Review | “Review this migration runbook for missing verification, unsafe retries, and recovery gaps.” |
| Dry run | “Walk through the procedure and its failure branches without changing state.” |
| Execute / Resume | “Resume this runbook from its execution record. Recheck current state and continue the next authorized step.” |
| Drift audit | “Compare this runbook with the specified release and report what needs re-verification.” |

The skill resolves safe read-only questions before asking for missing information.
At an approval boundary, it prepares the exact action, target, impact, verification,
and recovery plan. Independent authorized preparation can continue while a
dependent action is blocked.

### Runbook and execution record

Use the [runbook template](plugins/generate-runbook/skills/generate-runbook/assets/runbook-template.md)
for the procedure and the [execution-record template](plugins/generate-runbook/skills/generate-runbook/assets/execution-record-template.md)
for a specific run. The record contains:

- A current snapshot linked to the runbook revision and exact target.
- The observed entry signal and the go/no-go decision, with its owner and evidence.
- An authorization ledger with scope, limits, used/reserved capacity, and enforcement location.
- A step ledger with stable IDs, attempts, outcomes, and evidence references.
- An evidence register and dated decision history.

Before resuming, reconcile the snapshot with newer authoritative observations.
Preserve completed work and consumed grants. If an action's response was lost,
retain the unknown outcome until it can be reconciled. For example, a verified
submission receipt can prevent a duplicate submission; a recording from build 41
does not establish that build 42 passed the same device test.

See [execution and evidence guidance](plugins/generate-runbook/skills/generate-runbook/references/execution-and-evidence.md)
for the detailed workflow. Keep operational records in an appropriate private
location, outside this public skill repository.

## Codex marketplace

Add the public marketplace and install the plugin from `main`:

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

An existing direct installation is preserved unless the user explicitly passes
`--force`. To install development changes, run the installer from the verified
candidate checkout instead of the published-tag checkout above.

### Keep installed copies consistent

The standalone skill and marketplace plugin are separate installations. Updating
one does not update the other. If both are present, compare their contents and
align them to the same verified version before relying on either copy.

Back up local customizations before replacing a standalone installation. Update
the marketplace copy through its plugin manager; do not edit a managed plugin
cache to simulate an update. Installing the published tag above does not install
the unreleased 0.4.0 changes.

## Validate a runbook

From a 0.4.0 candidate checkout, use the mode appropriate to the document:

```bash
python3 plugins/generate-runbook/skills/generate-runbook/scripts/validate_runbook.py \
  path/to/runbook.md --mode draft

python3 plugins/generate-runbook/skills/generate-runbook/scripts/validate_runbook.py \
  path/to/runbook.md --mode ready
```

| Mode | Checks and result |
|---|---|
| `draft` (default) | Checks required structure and possible secrets; reports incomplete operational fields and prose placeholders as warnings. |
| `ready` | Also requires populated metadata including a final go/no-go owner; an entry signal and verification check; scope, risk, evidence, recovery (including a rollback trigger) and communication fields; a linked execution record; and numbered actions with unique step IDs, expected results, verification, failure handling, approval disposition, and retry safety. Declared status must be Approved or In progress. |

Use the bundled Markdown format; update older runbooks to that format before
using ready mode. Required fields need a value on the same line as their label;
the three Scope labels also accept the template's block bullet lists. Exit codes
are `0` for structural success, `1` for validation
errors, and `2` when the input cannot be read. Resolve errors and explicitly
disposition warnings before proceeding.

**A structural pass does not authorize execution or prove operational readiness.**
The linter does not establish command safety, valid approvals, evidence validity,
live state, or the correctness of execution-record ledgers. Those require operator
review and independent verification. The record does not enforce budgets or
deduplication; identify the actual enforcement mechanism.

For a heuristic check of referenced repository paths:

```bash
python3 plugins/generate-runbook/skills/generate-runbook/scripts/check_runbook_drift.py \
  path/to/runbook.md path/to/repository
```

This checks path existence only. Deployment, database schema, external workflow
status, and evidence freshness require separate inspection.

## Development and verification

Run the portable checks from the repository root:

```bash
python3 plugins/generate-runbook/skills/generate-runbook/scripts/test_skill.py
python3 scripts/test_release.py
python3 scripts/validate_manifests.py
python3 plugins/generate-runbook/skills/generate-runbook/scripts/validate_runbook.py \
  plugins/generate-runbook/skills/generate-runbook/assets/runbook-template.md --mode draft
python3 plugins/generate-runbook/skills/generate-runbook/scripts/install_skill.py \
  --target all --dry-run
```

When the corresponding platform tools are installed:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/generate-runbook
claude plugin validate .
```

The 0.4.0 candidate passed 24 skill-script tests, three release-package tests,
and three independent synthetic forward-test requests. Release tests verify
checksums, reproducibility, packaged README links, and clean standalone installs
into isolated Codex and Claude directories, including the installed test suite
and preservation of existing copies. They do not test live discovery or model
behavior inside either host application. The [evaluation catalog](evals/evals.json) contains 15
scenarios; it is not an automated end-to-end agent test runner. Read the
[candidate evaluation report](evals/results-execution-readiness.md) for observed
behavior and limits. These results do not establish production safety.

## Release

Build the deterministic standalone ZIP and SHA-256 checksum:

```bash
python3 scripts/build_release.py
```

Never add user profiles, credentials, private infrastructure identifiers, or generated operational evidence to this repository.
