# Worktree target gate evaluation

Status: candidate evaluation, not a published release

## Scenario

A clean feature-branch checkout and a separate `main` worktree contain different commits with equal tree hashes. The user requests production release review of the `main` merge commit without mutations.

## Comparison

| Criterion | Published 0.2.1 | Candidate | Result |
| --- | --- | --- | --- |
| Stops on wrong checkout | Inferred from generic safety guidance | Mandatory target gate | Improved determinism |
| Distinguishes tree from commit identity | Possible but not required | Explicitly required | Pass |
| Finds and reports target worktree | Not standardized | Required and script-supported | Pass |
| Evidence stamp | Not standardized | Mandatory fields | Pass |
| Silent repository mutation | Discouraged generally | Explicitly forbidden in read-only inspection | Pass |
| Remote freshness | Unspecified | `not required` or blocking `unknown and required` | Pass |

The published-skill evaluator reached the safe conclusion in about two minutes, but reported that the behavior was under-specified and could vary. The candidate evaluator reached the required stop in about one minute and produced the complete target evidence stamp. Agent activity is not treated as quality evidence; the candidate also passed deterministic unit, manifest, plugin-package, and diff checks.

## Product and orchestration observations

- Agents need a structured target contract, not only a path in natural language.
- “Clean” should be displayed independently from branch, commit, tree, and remote freshness.
- Worktree discovery should surface the checkout containing the requested target.
- Reports should be automatically marked stale when the target ref advances.
- The orchestrator should preserve the resolved target metadata and pass it unchanged to specialist agents.
