#!/usr/bin/env python3
"""Validate the standalone Interpersonal Strategist skill and repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_DIR = PROJECT_ROOT / "skill" / "interpersonal-strategist"

EXPECTED_SKILL_NAME = "interpersonal-strategist"
REQUIRED_REFERENCES = {
    "bilingual-pragmatics.md",
    "communication-and-control.md",
    "conflict-and-trust-repair.md",
    "evidence-ledger.md",
    "evidence-and-readiness.md",
    "negotiation-and-commitments.md",
    "power-and-workplace.md",
    "safety-and-referral.md",
    "scene-playbooks.md",
    "situation-classification-and-calibration.md",
}
REQUIRED_EVALS = {
    "bilingual-parity.json",
    "cases.json",
    "routing.json",
    "rubric.json",
}
REQUIRED_DISTRIBUTABLE_FILES = {"LICENSE", "NOTICE.md", "SKILL.md"}
FORBIDDEN_PORTABILITY_PATTERNS = {
    "/Users/tony": "machine-specific user path",
    "Second Brain": "private vault dependency",
    ".agent/": "private control-plane dependency",
    ".codex/skills": "legacy or environment-specific install dependency",
}


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError("SKILL.md frontmatter is not closed")
    raw_frontmatter = parts[0][4:]
    body = parts[1]
    parsed: dict[str, str] = {}
    for line_number, line in enumerate(raw_frontmatter.splitlines(), start=2):
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line {line_number}: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise ValueError(f"empty frontmatter key/value on line {line_number}")
        parsed[key] = value
    return parsed, body


def validate_skill_dir(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_dir = skill_dir.resolve()
    skill_md = skill_dir / "SKILL.md"
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    references_dir = skill_dir / "references"

    if not skill_md.is_file():
        return [f"missing required file: {skill_md}"]
    if not openai_yaml.is_file():
        errors.append("missing agents/openai.yaml")
    if not references_dir.is_dir():
        errors.append("missing references directory")

    try:
        frontmatter, body = parse_frontmatter(skill_md)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        frontmatter, body = {}, ""

    if set(frontmatter) != {"name", "description"}:
        errors.append("SKILL.md frontmatter must contain only name and description")
    if frontmatter.get("name") != EXPECTED_SKILL_NAME:
        errors.append(f"skill name must be {EXPECTED_SKILL_NAME!r}")
    description = frontmatter.get("description", "")
    if len(description) < 80:
        errors.append("description is too short to express triggers and boundaries")
    if len(description) > 1200:
        errors.append("description exceeds the 1200-character portability budget")
    if "[TODO" in skill_md.read_text(encoding="utf-8"):
        errors.append("SKILL.md contains unresolved TODO text")
    if len(skill_md.read_text(encoding="utf-8").splitlines()) >= 500:
        errors.append("SKILL.md must remain under 500 lines")
    if len(skill_md.read_text(encoding="utf-8")) > 15_000:
        errors.append("SKILL.md exceeds the 15,000-character context budget")

    linked_references = set(
        re.findall(r"\(references/([a-z0-9-]+\.md)\)", body)
    )
    missing_links = REQUIRED_REFERENCES - linked_references
    if missing_links:
        errors.append(
            "SKILL.md does not link required references: "
            + ", ".join(sorted(missing_links))
        )

    if references_dir.is_dir():
        actual_references = {
            path.name for path in references_dir.iterdir() if path.is_file()
        }
        missing_references = REQUIRED_REFERENCES - actual_references
        if missing_references:
            errors.append(
                "missing reference files: " + ", ".join(sorted(missing_references))
            )
        unlinked = actual_references - linked_references
        if unlinked:
            errors.append(
                "reference files are not linked from SKILL.md: "
                + ", ".join(sorted(unlinked))
            )

    if openai_yaml.is_file():
        metadata = openai_yaml.read_text(encoding="utf-8")
        for required in (
            'display_name: "Interpersonal Strategist"',
            'default_prompt: "Use $interpersonal-strategist',
            "allow_implicit_invocation: false",
        ):
            if required not in metadata:
                errors.append(f"agents/openai.yaml missing: {required}")

    actual_top_level = {child.name for child in skill_dir.iterdir()}
    missing_top_level = REQUIRED_DISTRIBUTABLE_FILES - actual_top_level
    if missing_top_level:
        errors.append(
            "missing distributable legal/runtime files: "
            + ", ".join(sorted(missing_top_level))
        )

    allowed_top_level = {
        "LICENSE",
        "NOTICE.md",
        "PACKAGE_MANIFEST.json",
        "SKILL.md",
        "agents",
        "references",
    }
    for child in skill_dir.iterdir():
        if child.name not in allowed_top_level:
            errors.append(f"unexpected distributable entry: {child.name}")

    skill_files = [
        path
        for path in skill_dir.rglob("*")
        if path.is_file() and path.name.lower() == "skill.md"
    ]
    if len(skill_files) != 1:
        errors.append(
            f"distributable must contain exactly one case-insensitive SKILL.md; found {len(skill_files)}"
        )

    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if path.is_symlink():
            errors.append(f"symlinks are not allowed: {relative}")
            continue
        if not path.is_file():
            continue
        if path.stat().st_size > 200_000:
            errors.append(f"file exceeds 200 KB portability limit: {relative}")
        if path.stat().st_mode & 0o111:
            errors.append(f"executable files are not allowed: {relative}")
        raw = path.read_bytes()
        if b"\r\n" in raw:
            errors.append(f"CRLF line endings are not allowed: {relative}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 file in distributable: {relative}")
            continue
        for pattern, reason in FORBIDDEN_PORTABILITY_PATTERNS.items():
            if pattern in text:
                errors.append(f"{relative}: contains {reason}: {pattern!r}")

    return errors


def validate_repository(project_root: Path = PROJECT_ROOT) -> list[str]:
    errors = validate_skill_dir(project_root / "skill" / EXPECTED_SKILL_NAME)

    version_path = project_root / "VERSION"
    if not version_path.is_file():
        errors.append("missing VERSION")
    else:
        version = version_path.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
            errors.append(f"invalid VERSION: {version!r}")
        changelog = (project_root / "CHANGELOG.md").read_text(encoding="utf-8")
        if f"## {version}" not in changelog:
            errors.append("CHANGELOG.md does not contain the current VERSION")

    evals_dir = project_root / "evals"
    for filename in sorted(REQUIRED_EVALS):
        path = evals_dir / filename
        if not path.is_file():
            errors.append(f"missing eval file: evals/{filename}")
            continue
        try:
            payload: Any = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON in evals/{filename}: {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"evals/{filename} must contain a JSON object")

    manifest_path = project_root / "provenance" / "SOURCE_MANIFEST.json"
    if not manifest_path.is_file():
        errors.append("missing provenance/SOURCE_MANIFEST.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid provenance manifest: {exc}")
        else:
            if manifest.get("historical_v05a_status") != (
                "unavailable_not_reconstructed"
            ):
                errors.append("provenance must preserve unavailable v0.5a status")

    return errors


def report(errors: list[str], scope: str) -> int:
    payload = {
        "status": "pass" if not errors else "fail",
        "scope": scope,
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skill-dir",
        type=Path,
        help="Validate only this extracted skill directory.",
    )
    args = parser.parse_args()
    if args.skill_dir:
        return report(validate_skill_dir(args.skill_dir), str(args.skill_dir))
    return report(validate_repository(), str(PROJECT_ROOT))


if __name__ == "__main__":
    sys.exit(main())
