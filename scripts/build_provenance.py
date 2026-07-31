#!/usr/bin/env python3
"""Record machine-readable identity for a qualification-candidate build."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHA_PATTERN_LENGTH = 40


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(project_root: Path, expression: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", expression],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def build_provenance(
    output: Path,
    *,
    project_root: Path = PROJECT_ROOT,
    environment: Mapping[str, str] | None = None,
) -> dict[str, object]:
    env = os.environ if environment is None else environment
    checkout_sha = git_value(project_root, "HEAD")
    checkout_tree_sha = git_value(project_root, "HEAD^{tree}")
    candidate_sha = env.get("CANDIDATE_SHA", checkout_sha)
    if len(candidate_sha) != SHA_PATTERN_LENGTH or candidate_sha != checkout_sha:
        raise ValueError(
            f"candidate SHA does not match checked-out HEAD: {candidate_sha!r} != {checkout_sha!r}"
        )

    version = (project_root / "VERSION").read_text(encoding="utf-8").strip()
    archive = project_root / "dist" / f"interpersonal-strategist-{version}.zip"
    manifest = (
        project_root / "dist" / f"interpersonal-strategist-{version}.manifest.json"
    )
    workflow = project_root / ".github" / "workflows" / "ci.yml"
    for required in (archive, manifest, workflow):
        if not required.is_file():
            raise ValueError(f"missing build-provenance input: {required}")

    payload: dict[str, object] = {
        "schema_version": "1.0",
        "candidate_sha": candidate_sha,
        "checkout_sha": checkout_sha,
        "checkout_tree_sha": checkout_tree_sha,
        "event_sha": env.get("GITHUB_SHA", checkout_sha),
        "event_name": env.get("GITHUB_EVENT_NAME", "local"),
        "run_id": env.get("GITHUB_RUN_ID"),
        "release": version,
        "release_zip": str(archive.relative_to(project_root)),
        "release_zip_sha256": sha256_file(archive),
        "release_manifest_sha256": sha256_file(manifest),
        "workflow_sha256": sha256_file(workflow),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build_provenance(args.output)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"status": "pass", "provenance": payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
