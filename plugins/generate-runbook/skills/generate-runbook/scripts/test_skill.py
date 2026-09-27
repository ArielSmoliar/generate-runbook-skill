#!/usr/bin/env python3
"""Unit tests for the portable runbook skill scripts."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module("runbook_validator", "validate_runbook.py")
installer = load_module("skill_installer", "install_skill.py")
target_inspector = load_module("repository_target_inspector", "inspect_repository_target.py")


READY_RUNBOOK = """# Disposable service inspection

## Metadata
- **Status:** Approved
- **Owner:** Test operator
- **Operator:** Test operator
- **Go/no-go owner:** Test operator
- **Last verified:** 2020-01-01
- **Environment:** Disposable local fixture
- **Expected duration:** Two minutes
- **Change/incident ID:** TEST-1
- **Runbook revision:** fixture-v1
- **Target artifact:** fixture-service-v1

## Objective
Inspect the disposable service and record its health.

## Scope
**Included**
- Local fixture service
**Excluded**
- All remote systems
**Must remain unchanged**
- Service configuration

## Preconditions
- **Entry signal:** The requested local health inspection concerns fixture-service-v1.
- **Entry verification:** Compare the operator request and running fixture identity; both must identify fixture-service-v1.
- [ ] Operator verifies the fixture is running locally.

## Risk and stop conditions
- **Risk:** Wrong fixture; verify the service identity before the check.
- **Stop immediately if:** Identity differs from fixture-service-v1.

## Evidence plan
- Record: Sanitized health result and service identity.
- Store in: Local test record.
- Never record: Credentials or request contents.
- Binding: Record fixture identity, environment and observation time; restart invalidates the result.

## Procedure
### Phase 1 — Inspect
1. **Action:** Inspect the disposable fixture health.
   - **Step ID:** S01
   - **Expected result:** Service reports healthy and fixture-service-v1.
   - **Verify:** Inspect both status and identity in the response.
   - **If verification fails:** Stop and record the observed failure.
   - **Approval required:** Not required because this is a local read-only fixture check.
   - **Retry safety:** Read-only; at most two attempts with a two-second timeout.

## Rollback
- **Trigger:** Wrong fixture identity.
- **Decision owner:** Test operator
- **Actions:** Stop inspection; no mutation to reverse.
- **Verification:** Confirm no service changes were made.
- **Limitations:** Not applicable because the procedure is read-only.

## Completion criteria
- [ ] Health and identity observations are recorded.

## Communications
- **Start:** Local operator record only.
- **Failure:** Record the mismatch locally.
- **Completion:** Report the verified observation to the requesting operator.

## Record
- **Execution record:** Local disposable record for TEST-1; operator reviews before execution.
- **Completed:**
"""


class ReadinessTests(unittest.TestCase):
    def check(self, text: str, mode: str = "ready"):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "runbook.md"
            path.write_text(text, encoding="utf-8")
            return validator.validate(path, mode)

    def test_populated_read_only_procedure_passes(self) -> None:
        self.assertEqual(self.check(READY_RUNBOOK), ([], []))

    def test_empty_approved_document_cannot_pass_ready(self) -> None:
        text = "# Empty\n" + "\n".join("## " + section for section in validator.REQUIRED_SECTIONS)
        text += "\nApproval. Excluded. Verify.\n"
        errors, _ = self.check(text)
        self.assertTrue(errors)
        self.assertTrue(any("Procedure requires" in error for error in errors))
        self.assertTrue(any("Owner" in error for error in errors))

    def test_each_operational_field_is_required(self) -> None:
        for field in ("Owner", "Operator", "Environment", "Target artifact", "Runbook revision"):
            with self.subTest(field=field):
                text = re.sub(r"(?m)^(- \*\*" + re.escape(field) + r":\*\*).*$", r"\1", READY_RUNBOOK)
                errors, _ = self.check(text)
                self.assertTrue(any(field in error for error in errors), errors)

    def test_entry_signal_and_check_required_beyond_generic_preconditions(self) -> None:
        for field in ("Entry signal", "Entry verification"):
            for replacement in ("", "- **" + field + ":**"):
                with self.subTest(field=field, replacement=replacement):
                    text = re.sub(r"(?m)^- \*\*" + re.escape(field) + r":\*\*.*$", replacement, READY_RUNBOOK)
                    # An unrelated generic prerequisite cannot fill the entry check.
                    errors, _ = self.check(text)
                    self.assertIn(f"missing populated field: Preconditions / {field}", errors)

    def test_final_decision_owner_required_even_when_owner_and_operator_exist(self) -> None:
        for replacement in ("", "- **Go/no-go owner:**"):
            text = re.sub(r"(?m)^- \*\*Go/no-go owner:\*\*.*$", replacement, READY_RUNBOOK)
            errors, _ = self.check(text)
            self.assertIn("missing populated field: Metadata / Go/no-go owner", errors)

    def test_rollback_trigger_cannot_be_replaced_by_recovery_actions(self) -> None:
        for replacement in ("", "- **Trigger:**"):
            text = re.sub(r"(?m)^- \*\*Trigger:\*\*.*$", replacement, READY_RUNBOOK)
            errors, _ = self.check(text)
            self.assertIn("missing populated field: Rollback / Trigger", errors)

    def test_each_step_needs_its_own_checks(self) -> None:
        step = READY_RUNBOOK.split("1. **Action:", 1)[1].split("## Rollback", 1)[0]
        for field in validator.STEP_FIELDS:
            with self.subTest(field=field):
                second = "2. **Action:" + step.replace("S01", "S02")
                second = re.sub(r"(?m)^([^\n]*\*\*" + re.escape(field) + r":\*\*).*$", r"\1", second)
                text = READY_RUNBOOK.replace("## Rollback", second + "\n## Rollback")
                errors, _ = self.check(text)
                self.assertTrue(any(f"step 2: missing populated {field}" in error for error in errors), errors)

    def test_duplicate_step_ids_fail(self) -> None:
        step = READY_RUNBOOK.split("1. **Action:", 1)[1].split("## Rollback", 1)[0]
        errors, _ = self.check(READY_RUNBOOK.replace("## Rollback", "2. **Action:" + step + "## Rollback"))
        self.assertIn("duplicate Step ID: S01", errors)

    def test_draft_template_is_not_ready(self) -> None:
        template = (SCRIPT_DIR.parent / "assets" / "runbook-template.md").read_text()
        self.assertEqual(self.check(template, "draft")[0], [])
        self.assertTrue(self.check(template)[0])

    def test_real_markdown_is_not_a_placeholder(self) -> None:
        links = "\n[Evidence](https://example.com) ![Chart](chart.png) [Report][r] [r] [^1]\n[r]: https://example.com\n[^1]: Local observation\n"
        self.assertEqual(self.check(READY_RUNBOOK + links), ([], []))

    def test_unresolved_prose_placeholder_blocks_ready(self) -> None:
        for marker in ("[Exact check]", "TBD", "UNSET"):
            errors, _ = self.check(READY_RUNBOOK.replace("Inspect both status and identity in the response.", marker))
            self.assertTrue(any("placeholder" in error for error in errors))

    def test_section_names_in_code_or_comments_do_not_count(self) -> None:
        for hidden in ("```md\n## Objective\n```", "<!--\n## Objective\n-->"):
            errors, _ = self.check(READY_RUNBOOK.replace("## Objective", hidden))
            self.assertIn("missing required section: Objective", errors)

    def test_invalid_status_and_date_block_ready(self) -> None:
        for value in ("Draft", "Complete", "Superseded"):
            self.assertTrue(self.check(READY_RUNBOOK.replace("**Status:** Approved", "**Status:** " + value))[0])
        for value in ("2020-02-30", "2999-01-01", "yesterday"):
            self.assertTrue(self.check(READY_RUNBOOK.replace("2020-01-01", value))[0])

    def test_secret_inside_code_still_fails(self) -> None:
        errors, _ = self.check(READY_RUNBOOK + "\n```\npassword=abcdefghijklmnop\n```\n")
        self.assertIn("possible secret or private key found", errors)

    def test_duplicate_sections_fail(self) -> None:
        errors, _ = self.check(READY_RUNBOOK + "\n## Objective\nDifferent objective\n")
        self.assertTrue(any("duplicate section" in error for error in errors))

    def test_blank_field_before_next_phase_stays_blank(self) -> None:
        text = READY_RUNBOOK.replace("Read-only; at most two attempts with a two-second timeout.", "\n### Phase 2 — Follow up")
        errors, _ = self.check(text)
        self.assertIn("step 1: missing populated Retry safety", errors)

    def test_cli_exit_codes_and_honest_success_message(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "runbook.md"
            command = [sys.executable, str(SCRIPT_DIR / "validate_runbook.py"), str(path), "--mode", "ready"]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            path.write_text(READY_RUNBOOK)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("structural checks passed", result.stdout)
            self.assertIn("Not authorization", result.stdout)
            path.write_text(READY_RUNBOOK.replace("**Owner:** Test operator", "**Owner:**"))
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)


class ValidateRunbookTests(unittest.TestCase):
    def test_template_passes_with_placeholder_warning(self) -> None:
        template = SCRIPT_DIR.parent / "assets" / "runbook-template.md"
        errors, warnings = validator.validate(template)
        self.assertEqual(errors, [])
        self.assertTrue(any("placeholder" in warning for warning in warnings))

    def test_incomplete_runbook_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.md"
            path.write_text("# Deploy\n\nRun the command.\n", encoding="utf-8")
            errors, _ = validator.validate(path)
        self.assertTrue(any("missing required section" in error for error in errors))
        self.assertIn("no explicit stop condition found", errors)
        self.assertIn("no verification instruction found", errors)

    def test_possible_secret_fails(self) -> None:
        template = (SCRIPT_DIR.parent / "assets" / "runbook-template.md").read_text(
            encoding="utf-8"
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "secret.md"
            path.write_text(
                template + "\npassword=abcdefghijklmnop\n",
                encoding="utf-8",
            )
            errors, _ = validator.validate(path)
        self.assertIn("possible secret or private key found", errors)


class InstallerTests(unittest.TestCase):
    def test_copy_requires_force_for_existing_installation(self) -> None:
        source = SCRIPT_DIR.parent
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed = installer.copy_skill(source, root, force=False)
            self.assertTrue((installed / "SKILL.md").is_file())
            with self.assertRaises(FileExistsError):
                installer.copy_skill(source, root, force=False)
            replaced = installer.copy_skill(source, root, force=True)
            self.assertTrue((replaced / "SKILL.md").is_file())


class RepositoryTargetTests(unittest.TestCase):
    def git(self, path: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(path), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def test_exact_branch_and_commit_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            self.git(repository, "init", "-b", "main")
            self.git(repository, "config", "user.email", "test@example.com")
            self.git(repository, "config", "user.name", "Test")
            (repository / "tracked.txt").write_text("same tree\n", encoding="utf-8")
            self.git(repository, "add", "tracked.txt")
            self.git(repository, "commit", "-m", "initial")
            head = self.git(repository, "rev-parse", "HEAD")

            report, passed = target_inspector.inspect(
                repository,
                target_ref="refs/heads/main",
                target_commit=head,
                require_clean=True,
            )

            self.assertTrue(passed)
            self.assertEqual(report["branch"], "main")
            self.assertTrue(report["head_matches_target"])
            self.assertFalse(report["dirty"])
            self.assertEqual(report["remote_freshness"], "not required; no fetch performed")

    def test_required_remote_freshness_blocks_without_network_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            self.git(repository, "init", "-b", "main")
            self.git(repository, "config", "user.email", "test@example.com")
            self.git(repository, "config", "user.name", "Test")
            self.git(repository, "commit", "--allow-empty", "-m", "initial")

            report, passed = target_inspector.inspect(
                repository,
                remote_freshness_required=True,
            )

            self.assertFalse(passed)
            self.assertEqual(
                report["remote_freshness"],
                "unknown and required; no fetch performed",
            )
            self.assertIn(
                "remote freshness is required but has not been verified",
                report["failures"],
            )

    def test_same_tree_wrong_branch_stops_and_finds_target_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            main_worktree = Path(temporary) / "main-worktree"
            repository.mkdir()
            self.git(repository, "init", "-b", "main")
            self.git(repository, "config", "user.email", "test@example.com")
            self.git(repository, "config", "user.name", "Test")
            (repository / "tracked.txt").write_text("same tree\n", encoding="utf-8")
            self.git(repository, "add", "tracked.txt")
            self.git(repository, "commit", "-m", "initial")
            self.git(repository, "switch", "-c", "feature")
            self.git(repository, "commit", "--allow-empty", "-m", "feature identity")
            feature_head = self.git(repository, "rev-parse", "HEAD")
            self.git(repository, "worktree", "add", str(main_worktree), "main")
            main_head = self.git(repository, "rev-parse", "main")

            report, passed = target_inspector.inspect(
                repository,
                target_ref="refs/heads/main",
                target_commit=main_head,
                require_clean=True,
            )

            self.assertFalse(passed)
            self.assertNotEqual(feature_head, main_head)
            self.assertTrue(report["tree_matches_target"])
            self.assertFalse(report["head_matches_target"])
            self.assertTrue(
                any(Path(item["path"]).resolve() == main_worktree.resolve() for item in report["matching_worktrees"])
            )
            self.assertIn("HEAD does not match requested target commit", report["failures"])
            self.assertIn("current branch is feature, not main", report["failures"])


if __name__ == "__main__":
    unittest.main()
