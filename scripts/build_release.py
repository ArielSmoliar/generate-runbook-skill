#!/usr/bin/env python3
"""Build a deterministic release archive for the generate-runbook skill."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "generate-runbook"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
EXCLUDED_PARTS = {"__pycache__", ".DS_Store"}


def included_files() -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = [
        (ROOT / "README.md", "README.md"),
        (ROOT / "LICENSE", "LICENSE"),
        (ROOT / "VERSION", "VERSION"),
    ]
    for path in sorted(SKILL.rglob("*")):
        if path.is_file() and not EXCLUDED_PARTS.intersection(path.parts):
            files.append((path, str(Path("generate-runbook") / path.relative_to(SKILL))))
    return files


def build(output_directory: Path) -> tuple[Path, Path]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"generate-runbook-v{version}.zip"

    with tempfile.NamedTemporaryFile(
        dir=output_directory, prefix=".generate-runbook-", suffix=".zip", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)

    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as bundle:
            for source, archive_name in included_files():
                info = zipfile.ZipInfo(archive_name, FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o755 if source.suffix == ".py" else 0o644) << 16
                bundle.writestr(info, source.read_bytes())
        shutil.move(temporary_path, archive)
    finally:
        temporary_path.unlink(missing_ok=True)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive, checksum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    archive, checksum = build(args.output.resolve())
    print(f"BUILT: {archive}")
    print(f"SHA256: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
