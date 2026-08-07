# Repository target gate

Use this gate before drawing project-specific conclusions from a Git checkout. A clean checkout is not proof that it is the requested branch, commit, release, or freshest remote state.

## Resolve the target

Record the user's explicit target when provided:

- repository path or remote identity
- branch, tag, pull request, release, or commit
- whether a clean checkout is required
- whether remote freshness must be verified
- whether the task concerns source code, a deployed environment, or both

If no target is explicit, inspect the current checkout but label it as the current checkout only. Do not call it `latest`, `main`, merged, deployed, or production without evidence.

Run the bundled read-only inspector when Git is available:

```bash
python3 scripts/inspect_repository_target.py \
  --repository REPOSITORY_ROOT \
  --target-ref TARGET_REF \
  --target-commit TARGET_COMMIT \
  --require-clean
```

Add `--remote-freshness-required` only when the user requires a fresh remote comparison. The read-only inspector will then stop and report that freshness remains unverified; verify it separately with an approved fetch or remote API before rerunning the gate. Omit unknown target arguments. The script never fetches, switches branches, creates worktrees, or changes files.

## Gate decision

Proceed only when all user-required properties match. Stop and report the mismatch when:

- the inspected root is not the requested repository
- `HEAD` is not the requested commit
- the current branch is not the requested branch
- cleanliness is required and tracked or untracked changes exist
- remote freshness is required but was not verified, or the verified remote target differs

When another worktree contains the requested branch or commit, report its path. Do not silently move the task, fetch, checkout, switch, reset, or create a worktree.

Tree equality and commit identity are different evidence. Equal tree hashes mean the checked-out source content is equivalent at that instant; they do not prove the same history, merge identity, branch, release, deployment, or remote freshness. State both facts when relevant.

## Evidence stamp

Every repository-backed output must include:

- repository root and remote identity when available
- inspected worktree path
- current branch or detached state
- full `HEAD` commit and tree hash
- requested comparison ref/commit and whether it matched
- dirty state
- remote freshness status: verified with timestamp and ref, not required, or unknown
- any other worktree holding the requested target

Keep repository evidence separate from live-system evidence. Source inspection cannot prove that a migration ran, configuration is active, a deployment succeeded, or production is healthy. Cite the independent evidence for those claims or mark them unverified.

If the target advances after inspection, mark the report stale and repeat the gate before execution or release approval.
