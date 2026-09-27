#!/usr/bin/env python3
"""Exercise the built archive and isolated installs without touching user skills."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

import build_release


class ReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="runbook-release-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive, self.checksum = build_release.build(self.root / "release")
        self.unpacked = self.root / "unpacked"
        with zipfile.ZipFile(self.archive) as bundle:
            bundle.extractall(self.unpacked)

    def run_cli(self, *args: str | Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", *(str(arg) for arg in args)],
            cwd=self.unpacked,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            timeout=60,
        )

    def test_checksum_and_reproducible_archive(self) -> None:
        digest, filename = self.checksum.read_text().split()
        self.assertEqual(filename, self.archive.name)
        self.assertEqual(digest, hashlib.sha256(self.archive.read_bytes()).hexdigest())
        other, _ = build_release.build(self.root / "second-release")
        self.assertEqual(self.archive.read_bytes(), other.read_bytes())

    def test_readme_links_and_manifests_survive_packaging(self) -> None:
        readme = (self.unpacked / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
        for link in links:
            if "://" not in link and not link.startswith("#"):
                with self.subTest(link=link):
                    self.assertTrue((self.unpacked / link.split("#")[0]).is_file(), link)
        result = self.run_cli("scripts/validate_manifests.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(self.archive) as bundle:
            for name in bundle.namelist():
                self.assertFalse({".git", "__pycache__", ".DS_Store"}.intersection(Path(name).parts))
                self.assertFalse(name.endswith(".pyc"))

    def test_clean_installs_run_and_preserve_existing_copies(self) -> None:
        skill = self.unpacked / "plugins/generate-runbook/skills/generate-runbook"
        command = (
            skill / "scripts/install_skill.py", "--target", "all",
            "--codex-root", self.root / "codex",
            "--claude-root", self.root / "claude",
        )
        result = self.run_cli(*command)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for platform in ("codex", "claude"):
            with self.subTest(platform=platform):
                installed = self.root / platform / "generate-runbook"
                for source in skill.rglob("*"):
                    if source.is_file():
                        self.assertEqual((installed / source.relative_to(skill)).read_bytes(), source.read_bytes())
                # Exercise the installed scripts, not the repository source.
                result = self.run_cli(installed / "scripts/test_skill.py")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                result = self.run_cli(
                    installed / "scripts/validate_runbook.py",
                    installed / "assets/runbook-template.md", "--mode", "ready",
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        marker = self.root / "codex/generate-runbook/local-customization.txt"
        marker.write_text("preserve this local customization\n", encoding="utf-8")
        result = self.run_cli(*command)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(marker.read_text(), "preserve this local customization\n")


if __name__ == "__main__":
    unittest.main()
