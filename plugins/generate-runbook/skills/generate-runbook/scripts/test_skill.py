#!/usr/bin/env python3
"""Unit tests for the portable runbook skill scripts."""

from __future__ import annotations

import importlib.util
import subprocess
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
