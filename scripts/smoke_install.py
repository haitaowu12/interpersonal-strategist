#!/usr/bin/env python3
"""Smoke-test a clean user-scoped installation in a temporary Codex home."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILL = PROJECT_ROOT / "skill" / "interpersonal-strategist"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import validate_skill_dir  # noqa: E402


def safe_extract(archive: Path, target: Path) -> None:
    target_resolved = target.resolve()
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            destination = (target / member.filename).resolve()
            if target_resolved not in destination.parents and destination != target_resolved:
                raise ValueError(f"archive path escapes destination: {member.filename}")
            if member.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(zf.read(member))


def run_smoke(archive: Path | None = None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="interpersonal-strategist-smoke-") as raw:
        temp_root = Path(raw)
        user_skills = temp_root / ".agents" / "skills"
        user_skills.mkdir(parents=True)

        if archive:
            safe_extract(archive, user_skills)
        else:
            shutil.copytree(SOURCE_SKILL, user_skills / "interpersonal-strategist")

        installed = user_skills / "interpersonal-strategist"
        errors = validate_skill_dir(installed)
        discovered = installed.is_dir() and (installed / "SKILL.md").is_file()
        return {
            "status": "pass" if discovered and not errors else "fail",
            "discovery_root": ".agents/skills",
            "skill": "interpersonal-strategist",
            "explicit_invocation": "$interpersonal-strategist",
            "errors": errors,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    result = run_smoke(args.archive)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
