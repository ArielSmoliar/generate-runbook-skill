# Execution, resumption and evidence

Read for Execute, interrupted work, handoffs, or any review relying on prior
results. Use `assets/execution-record-template.md` for a durable record; keep
short procedures proportionate by using explicit not-applicable explanations.
The record is an audit artifact, not an authorization service or budget enforcer.

## Resume from verified state

1. Read the runbook revision, current execution snapshot, authorization ledger,
   step ledger and cited evidence. Preserve failures and consumed grants.
2. Recheck target identity and volatile live state using authorized read-only
   inspection. Repository state, deployment, schema and external submission
   status are separate facts. A committed migration is not an applied migration.
3. Reconcile conflicts with timestamped authoritative observations. Update the
   current snapshot and mark earlier status superseded; do not silently delete
   history or choose whichever document permits progress.
4. Find the next incomplete step whose prerequisites and authorization hold.
   Do not repeat successful steps unless their evidence was invalidated. A
   handoff, new task, restart or elapsed time does not renew a consumed grant.
5. Continue authorized independent preparation while a dependent step is
   blocked. Report the concrete blocker and next permitted action.

## Entry and final decision

Before starting or reusing a consequential procedure, establish three things:
the entry signal is currently satisfied, the rollback/containment trigger is
observable, and a named person or accountable role owns the final go/no-go.
Record the entry check's result, timestamp and evidence, then the decision,
decision owner, scope and authorization reference in the execution snapshot.

A prepared procedure or passing linter cannot establish that its entry signal
is true. If the signal is false, stale or unknown, hold the affected operation
and use authorized read-only checks to resolve it. Do not invent a decision or
appoint yourself approver to fill a template. Continue safe independent
preparation. Reuse an existing go decision only while its evidence, target,
scope and authority still apply; this does not require a new approval on every
resume. Honor any explicit action-time approval gate.

## Authorization without repeated permission loops

Reuse valid authorization for the same action, target, scope and limits. Ask
again only for changed scope, exhausted/expired/revoked authority, or an explicit
action-time approval requirement. A runbook's Approved status is not a grant.
Finish authorized preparation before presenting an approval request: identify
the exact action and artifact, impact, verification and recovery procedure.

For paid or bounded operations, preserve used and reserved capacity across
restarts. Unknown outcomes retain their reservation until reconciled. Record
the actual units and where enforcement occurs. A Markdown counter is advisory;
do not claim a hard cap without verifying enforcement by the host or runner.
Do not infer authorization to send messages from a communications plan.

## Record before and after consequential actions

Before dispatch, record the stable step ID, attempt, exact target, authorization
reference and available operation/deduplication ID. Mark it in progress. After
dispatch, record the observed result and independent verification evidence.
An issued command or successful HTTP response is not sufficient if the required
system outcome has not been observed.

If the response is lost or the task stops during a mutation, mark the outcome
unknown. Inspect the authoritative operation/resource state before retrying.
Do not resubmit, repay, recreate or replay merely because the client timed out.
If reconciliation is unavailable, stop that action and retain the uncertainty.
Specify repeat safety, retry limits, timeouts and terminal-failure handling in
the procedure. Rollback is a separate action with its own authority and checks.

## Bind evidence to claims

Every gate-supporting result needs a stable ID, sanitized location, observation
time, collection method, exact artifact/environment, outcome, supported claim,
and limitations or invalidation conditions. For relevant evaluation work, also
record model/configuration, prompt, input/dataset and rubric versions or hashes.
Never invent missing provenance or replace raw failed outcomes with revised
grades. Preserve original and re-adjudicated results separately.

Keep these boundaries explicit:

- Source inspection does not establish deployment, applied schema or health.
- Simulation, scripted demonstrations and synthetic development results do not
  establish live behavior, independent validation or production accuracy.
- A successful older build or different account/device state does not prove
  the candidate passed the required path. State the observed version and limits.
- User reports remain user-reported unless independently verified.
- Missing telemetry and an unreproduced failure mean unknown, not passed/fixed.

An artifact, configuration or fixture change invalidates affected evidence;
rerun only the checks needed for those claims. Define freshness by the gate's
risk and observed state, not a universal time limit. Keep credentials in
protected fields and use synthetic fixtures where possible.

## Closeout

Declare completion only when required steps and current evidence satisfy the
runbook's measurable criteria. Record residual uncertainty, follow-up owner and
monitoring obligations. Submission, review acceptance, public release and
post-release observation are separate milestones. Do not erase blockers by
editing the completion criteria after the fact without a recorded decision.
