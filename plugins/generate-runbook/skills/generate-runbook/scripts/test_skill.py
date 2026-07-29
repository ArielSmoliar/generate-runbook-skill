#!/usr/bin/env python3
"""Unit tests for the portable runbook skill scripts."""

from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
