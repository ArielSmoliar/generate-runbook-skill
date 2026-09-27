# Execution record — [Run ID]

This is the canonical maintained summary for this run. Reconcile it with newer
authoritative observations before acting. Keep dated history below; older
handoffs link here and must not override verified current state. Store privately
when targets or approval references are sensitive. Do not store credentials.

## Current snapshot

- Updated at: [ISO timestamp with timezone]
- Runbook location and immutable revision: [Path and revision/digest]
- Target artifact and environment: [Exact identity]
- Run status: [Not started / In progress / Blocked / Complete / Aborted]
- Last verified step and evidence: [Stable step ID and evidence ID, or Not started]
- Next authorized action: [Step ID and scoped action, or None with reason]
- Blockers and required reconciliation: [Facts, owner and next read-only check]
- Live state checked at and source: [Timestamp and authoritative query or interface]
- Supersedes: [Earlier snapshot/handoff or Initial record]

## Authorization ledger

Record existing user authorization before asking again. A row does not grant
authority. Confirm its source, scope and remaining allowance before use.
Use explicit units; do not equate tokens, calls, dollars or scheduling weights.

| Grant ID | Authorization source and time | Allowed actions and exact target | Limits and expiry | Used/reserved/remaining | Status | Enforcement location |
|---|---|---|---|---|---|---|
| [ID] | [Decision reference, no private transcript] | [Scope] | [Units and expiry or no stated expiry] | [Counts, including uncertain in-flight usage] | [Active / Exhausted / Expired / Revoked] | [Host/runner/operator/advisory; verified mechanism or unknown] |

## Step ledger

Allowed states: `pending`, `in_progress`, `succeeded`, `failed`, `unknown`,
`blocked`, `skipped`. Skipped requires a reason and cannot satisfy a required
completion criterion. Unknown requires reconciliation before retry.

| Step ID | State | Attempt and timestamp | Target | Grant ID or reason not required | Operation/deduplication ID | Evidence IDs | Next action or failure disposition |
|---|---|---|---|---|---|---|---|
| [ID] | pending | [Attempt] | [Identity] | [Grant] | [Sanitized stable ID or not applicable with reason] | [IDs] | [Action] |

## Evidence register

Register observations, not just links. Scope each supported claim narrowly.
Different-build evidence remains useful context but does not pass an exact-build
gate. An unknown or stale result cannot be promoted to passed.

| Evidence ID | Location | Observed at and collector | Artifact and environment | Method/type | Result and supported claim | Limitations and invalidation rule |
|---|---|---|---|---|---|---|
| [ID] | [Sanitized reference] | [Time and operator/tool] | [Exact identity] | [Source inspection / automated / live / simulated / user-reported] | [Pass/fail/unknown and claim] | [Expiry or changes requiring recheck] |

## History and handoff

Append dated decisions, failed attempts, deviations, reconciliations and
superseded evidence without erasing the original result. Update the current
snapshot at each consequential checkpoint and before handoff. Record which
facts the next operator must refresh and which completed work must not repeat.
