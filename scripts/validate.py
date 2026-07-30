#!/usr/bin/env python3
"""Validate the standalone Interpersonal Strategist skill and repository."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tomllib
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
    "method-contracts.md",
    "power-and-workplace.md",
    "pragmatics-and-digital-channels.md",
    "practice-and-after-action-learning.md",
    "reciprocity-and-relationship-maintenance.md",
    "safety-and-referral.md",
    "scene-playbooks.md",
    "situation-classification-and-calibration.md",
}
REQUIRED_EVALS = {
    "ai-mediated.json",
    "bilingual-parity.json",
    "cases.json",
    "invocation.json",
    "metamorphic.json",
    "multi-actor.json",
    "relationship-norms.json",
    "rubric.json",
    "speech-acts.json",
    "substantive-routes.json",
    "trust-reliance.json",
}
REQUIRED_EVAL_DOCS = {
    "README.md",
    "holdout-protocol.md",
    "judge-protocol.md",
    "no-skill-protocol.md",
    "run.py",
}
REQUIRED_DISTRIBUTABLE_FILES = {"LICENSE", "NOTICE.md", "SKILL.md"}
REQUIRED_METHOD_CONTRACTS = set("ABCDEFGHIJKL")
REQUIRED_QUALIFICATION_GATES = {
    "static_repository_ci",
    "deterministic_package_and_layout",
    "evidence_registry_parity",
    "online_source_resolution",
    "clean_host_discovery_and_invocation",
    "reference_selection_and_compound_overlays",
    "calibrated_no_skill_comparison",
    "independent_untouched_holdouts",
    "adversarial_safety_holdouts",
    "bilingual_fluent_review",
    "judge_calibration",
    "privacy_safe_controlled_pilot",
    "independent_release_review",
}
CANONICAL_INVOCATION_LABELS = {
    "OWN_EXPLICIT",
    "DELEGATE_WRITING",
    "DELEGATE_TRANSLATION",
    "ROMANCE_OUT_OF_SCOPE",
    "NOT_OWN",
}
CANONICAL_SUBSTANTIVE_ROUTES = {
    "IN_SCOPE",
    "COACH_WITH_CAUTION",
    "REFER_OR_ESCALATE",
    "REFUSE",
}
EVIDENCE_REQUIRED_FIELDS = {
    "id",
    "first_author",
    "year",
    "title",
    "stable_identity",
    "evidence_type",
    "permitted_claim",
    "limitation",
    "runtime_rule",
    "last_verified",
    "license_note",
}
MINIMUM_SCENE_PLAYBOOKS = 20
MINIMUM_DEVELOPMENT_CASES = 36
MINIMUM_BILINGUAL_PAIRS = 6
FORBIDDEN_PORTABILITY_PATTERNS = {
    "/Users/tony": "machine-specific user path",
    "Second Brain": "private vault dependency",
    ".agent/": "private control-plane dependency",
    ".codex/skills": "legacy or environment-specific install dependency",
}
VERSION_PATTERN = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<pre>alpha|beta|rc)\.(?P<num>\d+))?$"
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EVIDENCE_ID_PATTERN = re.compile(r"^[A-Z]+(?:-[A-Z]+)?-\d+$")


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


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top level must be an object")
    return payload


def version_to_pep440(version: str) -> str:
    match = VERSION_PATTERN.fullmatch(version)
    if not match:
        raise ValueError(f"invalid VERSION: {version!r}")
    base = f"{match['major']}.{match['minor']}.{match['patch']}"
    pre = match["pre"]
    if not pre:
        return base
    marker = {"alpha": "a", "beta": "b", "rc": "rc"}[pre]
    return f"{base}{marker}{match['num']}"


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

    skill_text = skill_md.read_text(encoding="utf-8")
    if "[TODO" in skill_text:
        errors.append("SKILL.md contains unresolved TODO text")
    if len(skill_text.splitlines()) >= 500:
        errors.append("SKILL.md must remain under 500 lines")
    if len(skill_text) > 15_000:
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
            "distributable must contain exactly one case-insensitive SKILL.md; "
            f"found {len(skill_files)}"
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


def validate_version_parity(project_root: Path, version: str) -> list[str]:
    errors: list[str] = []
    text_requirements = {
        "CHANGELOG.md": f"## {version}",
        "README.md": version,
        "skill/interpersonal-strategist/NOTICE.md": version,
        "provenance/PROVENANCE.md": version,
    }
    for relative, required in text_requirements.items():
        path = project_root / relative
        if not path.is_file():
            errors.append(f"missing release metadata file: {relative}")
            continue
        if required not in path.read_text(encoding="utf-8"):
            errors.append(f"{relative} does not contain current VERSION {version}")

    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        errors.append("missing pyproject.toml")
    else:
        try:
            pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"invalid pyproject.toml: {exc}")
        else:
            expected = version_to_pep440(version)
            actual = pyproject.get("project", {}).get("version")
            if actual != expected:
                errors.append(
                    f"pyproject.toml version does not match VERSION: {actual!r} != {expected!r}"
                )

    source_manifest_path = project_root / "provenance" / "SOURCE_MANIFEST.json"
    if not source_manifest_path.is_file():
        errors.append("missing provenance/SOURCE_MANIFEST.json")
    else:
        try:
            manifest = read_json(source_manifest_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if manifest.get("release") != version:
                errors.append("provenance/SOURCE_MANIFEST.json release mismatch")
            if manifest.get("historical_v05a_status") != "unavailable_not_reconstructed":
                errors.append("provenance must preserve unavailable v0.5a status")

    qualification_path = project_root / "release" / "qualification.json"
    if not qualification_path.is_file():
        errors.append("missing release/qualification.json")
    else:
        try:
            qualification = read_json(qualification_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if qualification.get("release") != version:
                errors.append("release/qualification.json release mismatch")

    return errors


def validate_counted_file(
    path: Path, count_field: str, items_field: str
) -> tuple[list[str], dict[str, Any] | None]:
    errors: list[str] = []
    try:
        payload = read_json(path)
    except ValueError as exc:
        return [str(exc)], None
    items = payload.get(items_field)
    if not isinstance(items, list):
        return [f"{path}: {items_field} must be a list"], payload
    if payload.get(count_field) != len(items):
        errors.append(f"{path}: {count_field} does not match {items_field}")
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if len(ids) != len(items):
        errors.append(f"{path}: every item must be an object with an id")
    if any(not isinstance(item_id, str) or not item_id for item_id in ids):
        errors.append(f"{path}: every item id must be a non-empty string")
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: duplicate ids")
    return errors, payload


def load_eval_runner_errors(project_root: Path) -> list[str]:
    runner_path = project_root / "evals" / "run.py"
    if not runner_path.is_file():
        return ["missing evals/run.py"]
    spec = importlib.util.spec_from_file_location("interpersonal_eval_runner", runner_path)
    if spec is None or spec.loader is None:
        return ["unable to load evals/run.py"]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        result = module.validate_fixtures()
    except Exception as exc:  # validation must surface runner defects
        return [f"evals/run.py validation failed: {exc}"]
    if not isinstance(result, list):
        return ["evals/run.py validate_fixtures must return a list"]
    return [f"eval fixture: {item}" for item in result]


def validate_evidence(project_root: Path) -> list[str]:
    errors: list[str] = []
    registry_path = project_root / "provenance" / "evidence-sources.json"
    ledger_path = (
        project_root
        / "skill"
        / EXPECTED_SKILL_NAME
        / "references"
        / "evidence-ledger.md"
    )
    if not registry_path.is_file():
        return ["missing provenance/evidence-sources.json"]
    if not ledger_path.is_file():
        return ["missing evidence ledger"]

    try:
        registry = read_json(registry_path)
    except ValueError as exc:
        return [str(exc)]
    sources = registry.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["evidence registry sources must be a non-empty list"]

    source_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"evidence source {index} is not an object")
            continue
        missing = EVIDENCE_REQUIRED_FIELDS - set(source)
        if missing:
            errors.append(
                f"evidence source {source.get('id', index)!r} missing: "
                + ", ".join(sorted(missing))
            )
            continue
        source_id = source["id"]
        if not isinstance(source_id, str) or not EVIDENCE_ID_PATTERN.fullmatch(source_id):
            errors.append(f"invalid evidence id: {source_id!r}")
            continue
        if source_id in source_by_id:
            errors.append(f"duplicate evidence id: {source_id}")
            continue
        source_by_id[source_id] = source
        if not isinstance(source.get("year"), int):
            errors.append(f"{source_id}: year must be an integer")
        for field in EVIDENCE_REQUIRED_FIELDS - {"year"}:
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{source_id}: {field} must be a non-empty string")
        if not DATE_PATTERN.fullmatch(str(source.get("last_verified", ""))):
            errors.append(f"{source_id}: last_verified must use YYYY-MM-DD")
        stable_identity = str(source.get("stable_identity", ""))
        if not any(marker in stable_identity for marker in ("DOI ", "PMID ", "NIST ", "official guide")):
            errors.append(f"{source_id}: stable_identity lacks a recognized identity")

    ledger_text = ledger_path.read_text(encoding="utf-8")
    ledger_rows: dict[str, str] = {}
    for match in re.finditer(r"^\| ([A-Z]+(?:-[A-Z]+)?-\d+) \| (.+?) \|", ledger_text, re.MULTILINE):
        ledger_rows[match.group(1)] = match.group(2)

    registry_ids = set(source_by_id)
    ledger_ids = set(ledger_rows)
    if registry_ids != ledger_ids:
        missing_rows = registry_ids - ledger_ids
        unknown_rows = ledger_ids - registry_ids
        if missing_rows:
            errors.append("evidence ledger missing registry ids: " + ", ".join(sorted(missing_rows)))
        if unknown_rows:
            errors.append("evidence ledger contains unregistered ids: " + ", ".join(sorted(unknown_rows)))

    for source_id in sorted(registry_ids & ledger_ids):
        source = source_by_id[source_id]
        row = ledger_rows[source_id]
        if source["first_author"].casefold() not in row.casefold():
            errors.append(
                f"{source_id}: ledger source does not contain first author or issuer {source['first_author']!r}"
            )
        identity_tokens = re.findall(
            r"(?:PMID \d+|DOI [^;]+|NIST AI 600-1)", source["stable_identity"]
        )
        for token in identity_tokens:
            if token not in row:
                errors.append(f"{source_id}: ledger row missing stable identity {token!r}")

    if "## Practitioner-framework quarantine" not in ledger_text:
        errors.append("evidence ledger missing practitioner-framework quarantine")
    if "## Original product safeguards" not in ledger_text:
        errors.append("evidence ledger missing original-product safeguard boundary")
    return errors


def validate_qualification(project_root: Path) -> list[str]:
    errors: list[str] = []
    path = project_root / "release" / "qualification.json"
    try:
        payload = read_json(path)
    except ValueError as exc:
        return [str(exc)]

    status = payload.get("status")
    production_allowed = payload.get("production_claim_allowed")
    if status not in {"blocked", "qualified"}:
        errors.append("qualification status must be blocked or qualified")
    if not isinstance(production_allowed, bool):
        errors.append("production_claim_allowed must be boolean")

    gates = payload.get("gates")
    if not isinstance(gates, dict):
        return errors + ["qualification gates must be an object"]
    missing_gates = REQUIRED_QUALIFICATION_GATES - set(gates)
    if missing_gates:
        errors.append("qualification missing gates: " + ", ".join(sorted(missing_gates)))
    unknown_gates = set(gates) - REQUIRED_QUALIFICATION_GATES
    if unknown_gates:
        errors.append("qualification contains unknown gates: " + ", ".join(sorted(unknown_gates)))

    for gate_id, gate in gates.items():
        if not isinstance(gate, dict):
            errors.append(f"qualification gate {gate_id} must be an object")
            continue
        if gate.get("required") is not True:
            errors.append(f"qualification gate {gate_id} must remain required")
        if gate.get("status") not in {"pending", "passed", "failed", "blocked"}:
            errors.append(f"qualification gate {gate_id} has invalid status")

    if status == "blocked":
        if production_allowed:
            errors.append("blocked qualification cannot allow a production claim")
    elif status == "qualified":
        if production_allowed is not True:
            errors.append("qualified status must allow production claim")
        failed = [
            gate_id
            for gate_id, gate in gates.items()
            if not isinstance(gate, dict) or gate.get("status") != "passed"
        ]
        if failed:
            errors.append("qualified status has non-passing gates: " + ", ".join(sorted(failed)))
        qualification_commit = payload.get("qualification_commit")
        package_sha = payload.get("package_sha256")
        if not isinstance(qualification_commit, str) or not COMMIT_PATTERN.fullmatch(qualification_commit):
            errors.append("qualified status requires a 40-character qualification_commit")
        if not isinstance(package_sha, str) or not SHA256_PATTERN.fullmatch(package_sha):
            errors.append("qualified status requires package_sha256")
        for field in ("model_snapshot", "host_version"):
            if not isinstance(payload.get(field), str) or not payload[field].strip():
                errors.append(f"qualified status requires {field}")
        for gate_id, gate in gates.items():
            if isinstance(gate, dict) and not gate.get("evidence"):
                errors.append(f"qualified gate {gate_id} requires evidence")

    return errors


def validate_repository(project_root: Path = PROJECT_ROOT) -> list[str]:
    errors = validate_skill_dir(project_root / "skill" / EXPECTED_SKILL_NAME)

    version_path = project_root / "VERSION"
    if not version_path.is_file():
        errors.append("missing VERSION")
        version = ""
    else:
        version = version_path.read_text(encoding="utf-8").strip()
        try:
            version_to_pep440(version)
        except ValueError as exc:
            errors.append(str(exc))

    if version:
        errors.extend(validate_version_parity(project_root, version))

    evals_dir = project_root / "evals"
    for filename in sorted(REQUIRED_EVALS | REQUIRED_EVAL_DOCS):
        if not (evals_dir / filename).is_file():
            errors.append(f"missing eval file: evals/{filename}")
    if (evals_dir / "routing.json").exists():
        errors.append("evals/routing.json is retired; use invocation.json and substantive-routes.json")

    cases_path = evals_dir / "cases.json"
    if cases_path.is_file():
        case_errors, payload = validate_counted_file(cases_path, "case_count", "cases")
        errors.extend(case_errors)
        if payload and len(payload.get("cases", [])) < MINIMUM_DEVELOPMENT_CASES:
            errors.append(
                f"evals/cases.json must retain at least {MINIMUM_DEVELOPMENT_CASES} cases"
            )

    bilingual_path = evals_dir / "bilingual-parity.json"
    if bilingual_path.is_file():
        pair_errors, payload = validate_counted_file(
            bilingual_path, "pair_count", "pairs"
        )
        errors.extend(pair_errors)
        if payload and len(payload.get("pairs", [])) < MINIMUM_BILINGUAL_PAIRS:
            errors.append(
                f"bilingual parity must retain at least {MINIMUM_BILINGUAL_PAIRS} pairs"
            )

    invocation_path = evals_dir / "invocation.json"
    if invocation_path.is_file():
        try:
            invocation = read_json(invocation_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if set(invocation.get("labels", [])) != CANONICAL_INVOCATION_LABELS:
                errors.append("invocation labels do not match canonical set")

    routes_path = evals_dir / "substantive-routes.json"
    if routes_path.is_file():
        try:
            routes = read_json(routes_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if set(routes.get("labels", [])) != CANONICAL_SUBSTANTIVE_ROUTES:
                errors.append("substantive routes do not match canonical set")

    references_dir = project_root / "skill" / EXPECTED_SKILL_NAME / "references"
    playbooks_path = references_dir / "scene-playbooks.md"
    if playbooks_path.is_file():
        playbook_numbers = re.findall(
            r"^## (\d+)\. ", playbooks_path.read_text(encoding="utf-8"), re.MULTILINE
        )
        if len(playbook_numbers) < MINIMUM_SCENE_PLAYBOOKS:
            errors.append(
                f"scene playbooks must retain at least {MINIMUM_SCENE_PLAYBOOKS} entries"
            )
        if len(playbook_numbers) != len(set(playbook_numbers)):
            errors.append("scene playbooks contain duplicate numbered entries")

    contracts_path = references_dir / "method-contracts.md"
    if contracts_path.is_file():
        contract_ids = set(
            re.findall(
                r"^## ([A-L])\. ",
                contracts_path.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
        )
        missing_contracts = REQUIRED_METHOD_CONTRACTS - contract_ids
        if missing_contracts:
            errors.append("method contracts missing: " + ", ".join(sorted(missing_contracts)))

    errors.extend(validate_evidence(project_root))
    errors.extend(validate_qualification(project_root))
    errors.extend(load_eval_runner_errors(project_root))

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
