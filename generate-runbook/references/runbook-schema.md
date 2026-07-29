# Runbook schema

Use these sections in this order. A section may say `Not applicable` only when the reason is explicit.

## Metadata

- Title
- Status: Draft, Approved, In progress, Complete, or Superseded
- Owner and operator
- Last verified date
- Target environment
- Expected duration
- Change or incident identifier

## Objective

State the outcome and why the procedure exists in two or three sentences.

## Scope

List included systems, excluded systems, and invariants that must remain unchanged.

## Preconditions

List access, backups, approvals, health checks, maintenance windows, dependencies, and required isolated test data.

## Risk and stop conditions

Name the important failure modes. State conditions requiring an immediate pause or abort.

## Evidence plan

Define what may be recorded, where it belongs, retention expectations, and prohibited sensitive content.

## Procedure

Use numbered phases. For each consequential step include:

- **Action**
- **Expected result**
- **Verify**
- **If verification fails**
- **Approval required**, when applicable

Commands must be copyable, scoped, and preceded by context when the working directory or environment matters.

## Rollback

Define the trigger, decision owner, exact recovery procedure, verification, and limits. If rollback is impossible, state that before execution and provide containment steps.

## Completion criteria

List measurable signals that prove the objective is achieved and preserved systems remain healthy.

## Communications

Define who is notified at start, at failure, at completion, and through which approved channel. Do not embed private contact data unless the runbook is access controlled.

## Record

Capture sanitized timestamps, operator, approvals, outcome, deviations, follow-up work, and the next verification date.
