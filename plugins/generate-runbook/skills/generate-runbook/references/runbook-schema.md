# Runbook schema

Use these sections in this order. A section may say `Not applicable` only when the reason is explicit.

## Metadata

- Title
- Status: Draft, Approved, In progress, Complete, or Superseded
- Owner and operator
- Go/no-go owner: the person or accountable role with final authority to proceed
- Last verified date
- Target environment
- Expected duration
- Change or incident identifier
- Immutable runbook revision and exact target artifact/resource identity

Use the field labels in `assets/runbook-template.md` for ready-mode linting.
Put a value on the same line as each required field label; further details can
follow on later lines. The three Scope labels also accept the template's block
bullet lists. Unrelated checklists cannot fill an empty labeled field.
Use ISO `YYYY-MM-DD` for Last verified. Ready mode accepts Approved or In progress
status, but independently check the authorization source before execution.
The owner maintains the runbook; the operator performs it; the go/no-go owner
decides whether the consequential operation may proceed. One person can hold
all three roles, but identify the final decision authority explicitly.

## Objective

State the outcome and why the procedure exists in two or three sentences.

## Scope

List included systems, excluded systems, and invariants that must remain unchanged.

## Preconditions

List access, backups, approvals, health checks, maintenance windows, dependencies, and required isolated test data.

Also require **Entry signal**, the observable condition that makes the procedure
applicable now, and **Entry verification**, the exact check and acceptance
criterion for that signal. Preconditions describe what must be available or
true; they do not replace the reason to start. For an incident the signal may
be a verified alert; for a release, a specific approved candidate and window;
for QA or a beta launch, a specified candidate or cohort ready for that procedure.
Recheck applicability before reuse or resuming a consequential operation.

## Risk and stop conditions

Name the important failure modes. State conditions requiring an immediate pause or abort.

## Evidence plan

Define what may be recorded, where it belongs, retention expectations, and prohibited sensitive content.

## Procedure

Use numbered phases. For each consequential step include:

- **Action**
- **Step ID**: unique and stable across resumptions
- **Expected result**
- **Verify**
- **If verification fails**
- **Approval required**: existing grant, new gate, or not required with reason
- **Retry safety**: repeat-safety/reconciliation check, attempt limit and timeout

Commands must be copyable, scoped, and preceded by context when the working directory or environment matters.

## Rollback

Define the trigger, decision owner, exact recovery procedure, verification, and limits. If rollback is impossible, state that before execution and provide containment steps.
Use an observable condition or threshold for **Trigger**, not merely "if needed".
For a read-only procedure, explain the no-change recovery limit and name the
condition that requires stopping or containment instead of inventing a rollback.

## Completion criteria

List measurable signals that prove the objective is achieved and preserved systems remain healthy.

## Communications

Define who is notified at start, at failure, at completion, and through which approved channel. Do not embed private contact data unless the runbook is access controlled.

## Record

Capture sanitized timestamps, operator, approvals, outcome, deviations, follow-up work, and the next verification date.

Link a durable execution record using **Execution record**. Use
`assets/execution-record-template.md` and `references/execution-and-evidence.md`
for its current snapshot, authorization and step ledgers, evidence register and
append-only decision history. Completed timestamps may remain empty before work
finishes; do not invent outcomes to make a document look complete.
