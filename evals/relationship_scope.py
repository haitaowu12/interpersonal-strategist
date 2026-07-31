#!/usr/bin/env python3
"""Validate and prepare the public inclusive-relationship regression lane.

This deterministic adapter does not invoke a model, create untouched holdouts,
or authorize a production claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals" / "relationship-scope.json"
SKILL_PREFIX = "Use $interpersonal-strategist. "
LANGUAGES = {"en", "zh-CN", "mixed"}
ROUTES = {"IN_SCOPE", "COACH_WITH_CAUTION", "REFER_OR_ESCALATE", "REFUSE"}
REQUIRED_CATEGORIES = {
    "invitation",
    "ambiguous_interest",
    "relationship_definition",
    "consent_and_intimacy",
    "jealousy_and_third_parties",
    "breakup_and_contact",
    "reconciliation",
    "workplace_romance",
    "inclusive_relationship_structure",
    "typology_lens",
    "safety_referral",
    "privacy_and_intimate_media",
    "minors_incapacity",
    "refusal_and_manipulation",
    "bilingual_function",
}
CANONICAL_HARD_GATES = {
    "route",
    "fabrication",
    "harmful_tactic",
    "authority_boundary",
    "unsafe_exposure",
    "memory_abuse",
    "cultural_prediction",
    "nonverbal_inference",
    "bilingual_drift",
    "ai_authorization",
    "covert_test",
    "simulation_leakage",
    "control_failure",
}
ID_PATTERN = re.compile(r"^RS\d{2}$")


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_fixture() -> dict[str, Any]:
    try:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{FIXTURE}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{FIXTURE}: top level must be an object")
    return payload


def string_list(value: Any, *, permit_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (permit_empty or bool(value))
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def validate_fixture() -> list[str]:
    try:
        payload = read_fixture()
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    if payload.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if payload.get("status") != "public_development_only_not_qualification_holdout":
        errors.append("status must preserve the public-development nonclaim")

    cases = payload.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    if payload.get("case_count") != len(cases):
        errors.append("case_count does not match cases")
    if len(cases) < 30:
        errors.append("at least 30 relationship-scope cases are required")

    ids: list[str] = []
    prompts: list[str] = []
    categories: set[str] = set()
    languages: set[str] = set()
    routes: Counter[str] = Counter()
    gates: Counter[str] = Counter()

    for index, case in enumerate(cases, 1):
        label = f"case {index}"
        if not isinstance(case, dict):
            errors.append(f"{label}: case must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not ID_PATTERN.fullmatch(case_id):
            errors.append(f"{label}: id must match RS##")
        else:
            ids.append(case_id)
            label = case_id
        language = case.get("language")
        if language not in LANGUAGES:
            errors.append(f"{label}: invalid language {language!r}")
        else:
            languages.add(language)
        category = case.get("category")
        if not isinstance(category, str) or not category.strip():
            errors.append(f"{label}: category must be a non-empty string")
        else:
            categories.add(category)
        route = case.get("expected_route")
        if route not in ROUTES:
            errors.append(f"{label}: invalid expected_route {route!r}")
        else:
            routes[route] += 1
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{label}: prompt must be a non-empty string")
        else:
            prompts.append(prompt.strip())
        if not string_list(case.get("expected_features")):
            errors.append(f"{label}: expected_features must be a non-empty string list")
        if not string_list(case.get("prohibited")):
            errors.append(f"{label}: prohibited must be a non-empty string list")
        hard_gates = case.get("hard_gates")
        if not string_list(hard_gates, permit_empty=True):
            errors.append(f"{label}: hard_gates must be a string list")
        else:
            unknown = sorted(set(hard_gates) - CANONICAL_HARD_GATES)
            if unknown:
                errors.append(f"{label}: unknown hard gates: {', '.join(unknown)}")
            gates.update(hard_gates)

    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append("duplicate ids: " + ", ".join(duplicates))
    if len(prompts) != len(set(prompts)):
        errors.append("duplicate prompts")
    if languages != LANGUAGES:
        errors.append("languages must cover en, zh-CN, and mixed")
    missing = sorted(REQUIRED_CATEGORIES - categories)
    if missing:
        errors.append("missing required categories: " + ", ".join(missing))
    for route in ROUTES:
        if routes[route] < 2:
            errors.append(f"route {route} requires at least two cases")
    for gate in ("harmful_tactic", "authority_boundary", "bilingual_drift"):
        if gates[gate] < 2:
            errors.append(f"hard gate {gate} requires at least two cases")
    return errors


def strip_explicit_invocation(prompt: str) -> str:
    result = prompt.strip()
    for pattern in (
        r"^Use \$interpersonal-strategist[.:]\s*",
        r"^Please use \$interpersonal-strategist[.:]\s*",
        r"^请使用 \$interpersonal-strategist[。.:]\s*",
    ):
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)
    return result.strip()


def add_explicit_invocation(prompt: str) -> str:
    prompt = prompt.strip()
    return prompt if "$interpersonal-strategist" in prompt else SKILL_PREFIX + prompt


def prepare(condition: str, output: Path) -> dict[str, Any]:
    if condition not in {"skill", "no-skill"}:
        raise ValueError("condition must be skill or no-skill")
    errors = validate_fixture()
    if errors:
        raise ValueError("; ".join(errors))

    records: list[dict[str, Any]] = []
    for case in read_fixture()["cases"]:
        prompt = (
            add_explicit_invocation(case["prompt"])
            if condition == "skill"
            else strip_explicit_invocation(case["prompt"])
        )
        case_key = f"relationship-scope:{case['id']}"
        run_id = hashlib.sha256(
            stable_json(
                {"case_key": case_key, "condition": condition, "prompt": prompt}
            ).encode("utf-8")
        ).hexdigest()[:20]
        records.append(
            {
                "run_id": run_id,
                "case_key": case_key,
                "condition": condition,
                "prompt": prompt,
                "language": case["language"],
                "category": case["category"],
                "source_file": FIXTURE.name,
                "source_id": case["id"],
                "expected_invocation": None,
                "expected_substantive_route": case["expected_route"],
                "strata": sorted(
                    {
                        "relationship_scope",
                        "romance",
                        case["language"],
                        case["category"],
                        case["expected_route"].lower(),
                        *("consent" for _ in [0] if case["category"] in {"consent_and_intimacy", "minors_incapacity"}),
                        *case["hard_gates"],
                    }
                ),
                "expected_features": case["expected_features"],
                "prohibited": case["prohibited"],
                "expected_hard_gates": case["hard_gates"],
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(stable_json(record) + "\n" for record in records)
    output.write_text(body, encoding="utf-8")
    return {
        "status": "prepared",
        "condition": condition,
        "record_count": len(records),
        "output": str(output),
        "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "qualification_claim": False,
    }


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--condition", choices=("skill", "no-skill"), required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            errors = validate_fixture()
            print_json(
                {
                    "status": "pass" if not errors else "fail",
                    "error_count": len(errors),
                    "errors": errors,
                    "qualification_claim": False,
                }
            )
            return 0 if not errors else 1
        print_json(prepare(args.condition, args.output))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print_json({"status": "fail", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
