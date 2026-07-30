#!/usr/bin/env python3
"""Prepare and summarize Interpersonal Strategist evaluation runs.

This tool is deterministic and network-free. It validates public fixtures,
creates host-runner prompt manifests, and summarizes externally collected
responses and judgments. It does not invoke a model or claim qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"

CASE_SUITES = {
    "cases.json": "case_count",
    "invocation.json": "case_count",
    "substantive-routes.json": "case_count",
    "multi-actor.json": "case_count",
    "relationship-norms.json": "case_count",
    "ai-mediated.json": "case_count",
    "trust-reliance.json": "case_count",
    "speech-acts.json": "case_count",
}
PAIR_SUITES = {
    "bilingual-parity.json": "pair_count",
    "metamorphic.json": "pair_count",
}
REQUIRED_FILES = set(CASE_SUITES) | set(PAIR_SUITES) | {"rubric.json"}
CANONICAL_INVOCATION = {
    "OWN_EXPLICIT",
    "DELEGATE_WRITING",
    "DELEGATE_TRANSLATION",
    "ROMANCE_OUT_OF_SCOPE",
    "NOT_OWN",
}
CANONICAL_ROUTES = {
    "IN_SCOPE",
    "COACH_WITH_CAUTION",
    "REFER_OR_ESCALATE",
    "REFUSE",
}
SKILL_PREFIX = "Use $interpersonal-strategist. "


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top level must be a JSON object")
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_counted_items(
    filename: str,
    payload: dict[str, Any],
    count_field: str,
    items_field: str,
) -> list[str]:
    errors: list[str] = []
    items = payload.get(items_field)
    if not isinstance(items, list):
        return [f"{filename}: {items_field} must be a list"]
    if payload.get(count_field) != len(items):
        errors.append(f"{filename}: {count_field} does not match {items_field}")
    ids: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{filename}: item {index} is not an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"{filename}: item {index} has no non-empty id")
        else:
            ids.append(item_id)
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"{filename}: duplicate ids: {', '.join(duplicates)}")
    return errors


def validate_fixtures() -> list[str]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (EVALS / name).is_file())
    if missing:
        errors.append("missing eval files: " + ", ".join(missing))

    loaded: dict[str, dict[str, Any]] = {}
    for filename in sorted(REQUIRED_FILES - set(missing)):
        try:
            loaded[filename] = read_json(EVALS / filename)
        except ValueError as exc:
            errors.append(str(exc))

    for filename, count_field in CASE_SUITES.items():
        if filename not in loaded:
            continue
        errors.extend(
            validate_counted_items(filename, loaded[filename], count_field, "cases")
        )
        for case in loaded[filename].get("cases", []):
            if not isinstance(case, dict):
                continue
            if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                errors.append(f"{filename}:{case.get('id')}: missing prompt")

    for filename, count_field in PAIR_SUITES.items():
        if filename not in loaded:
            continue
        errors.extend(
            validate_counted_items(filename, loaded[filename], count_field, "pairs")
        )

    invocation = loaded.get("invocation.json")
    if invocation:
        labels = set(invocation.get("labels", []))
        if labels != CANONICAL_INVOCATION:
            errors.append("invocation.json: labels must match canonical invocation labels")
        for case in invocation.get("cases", []):
            if isinstance(case, dict) and case.get("expected") not in CANONICAL_INVOCATION:
                errors.append(
                    f"invocation.json:{case.get('id')}: invalid expected label"
                )

    routes = loaded.get("substantive-routes.json")
    if routes:
        labels = set(routes.get("labels", []))
        if labels != CANONICAL_ROUTES:
            errors.append(
                "substantive-routes.json: labels must match canonical substantive routes"
            )
        for case in routes.get("cases", []):
            if isinstance(case, dict) and case.get("expected") not in CANONICAL_ROUTES:
                errors.append(
                    f"substantive-routes.json:{case.get('id')}: invalid expected route"
                )

    rubric = loaded.get("rubric.json")
    if rubric:
        dimensions = rubric.get("dimensions")
        gates = rubric.get("hard_gates")
        if not isinstance(dimensions, list) or not dimensions:
            errors.append("rubric.json: dimensions must be a non-empty list")
        else:
            dimension_ids: list[str] = []
            for dimension in dimensions:
                if not isinstance(dimension, dict):
                    errors.append("rubric.json: dimension is not an object")
                    continue
                dimension_id = dimension.get("id")
                floor = dimension.get("floor")
                if not isinstance(dimension_id, str) or not dimension_id:
                    errors.append("rubric.json: dimension missing id")
                else:
                    dimension_ids.append(dimension_id)
                if not isinstance(floor, int) or not 1 <= floor <= 5:
                    errors.append(
                        f"rubric.json:{dimension_id}: floor must be an integer 1-5"
                    )
            if len(dimension_ids) != len(set(dimension_ids)):
                errors.append("rubric.json: duplicate dimension ids")
        if not isinstance(gates, list) or not gates:
            errors.append("rubric.json: hard_gates must be a non-empty list")
        elif len({gate.get("id") for gate in gates if isinstance(gate, dict)}) != len(gates):
            errors.append("rubric.json: hard-gate ids must be unique")

    bilingual = loaded.get("bilingual-parity.json")
    if bilingual and bilingual.get("pair_count", 0) < 6:
        errors.append("bilingual-parity.json: at least six pairs are required")

    return errors


def strip_explicit_invocation(prompt: str) -> str:
    patterns = [
        r"^Use \$interpersonal-strategist[.:]\s*",
        r"^Please use \$interpersonal-strategist[.:]\s*",
        r"^请使用 \$interpersonal-strategist[。.:]\s*",
    ]
    result = prompt
    for pattern in patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)
    return result.strip()


def add_explicit_invocation(prompt: str) -> str:
    if "$interpersonal-strategist" in prompt:
        return prompt.strip()
    return SKILL_PREFIX + prompt.strip()


def iter_prompt_cases() -> Iterable[dict[str, Any]]:
    for filename in sorted(CASE_SUITES):
        payload = read_json(EVALS / filename)
        suite = payload.get("suite", filename)
        for case in payload.get("cases", []):
            if not isinstance(case, dict) or not isinstance(case.get("prompt"), str):
                continue
            yield {
                "case_key": f"{Path(filename).stem}:{case['id']}",
                "source_file": filename,
                "source_suite": suite,
                "source_id": case["id"],
                "language": case.get("language", "unknown"),
                "category": case.get("category", case.get("speech_act", "unknown")),
                "prompt": case["prompt"],
                "expected_invocation": (
                    case.get("expected") if filename == "invocation.json" else None
                ),
                "expected_substantive_route": (
                    case.get("expected")
                    if filename == "substantive-routes.json"
                    else None
                ),
            }

    bilingual = read_json(EVALS / "bilingual-parity.json")
    for pair in bilingual.get("pairs", []):
        if not isinstance(pair, dict):
            continue
        for language_key, prompt_key in (
            ("en", "english_prompt"),
            ("zh-CN", "chinese_prompt"),
        ):
            prompt = pair.get(prompt_key)
            if isinstance(prompt, str):
                yield {
                    "case_key": f"bilingual-parity:{pair['id']}:{language_key}",
                    "source_file": "bilingual-parity.json",
                    "source_suite": bilingual.get("suite"),
                    "source_id": pair["id"],
                    "language": language_key,
                    "category": pair.get("speech_act", "bilingual"),
                    "prompt": prompt,
                    "expected_invocation": None,
                    "expected_substantive_route": None,
                }


def prepare(condition: str, output: Path) -> dict[str, Any]:
    if condition not in {"skill", "no-skill"}:
        raise ValueError("condition must be 'skill' or 'no-skill'")
    records: list[dict[str, Any]] = []
    for case in iter_prompt_cases():
        prompt = (
            add_explicit_invocation(case["prompt"])
            if condition == "skill"
            else strip_explicit_invocation(case["prompt"])
        )
        record = {
            "run_id": sha256_bytes(
                stable_json(
                    {
                        "case_key": case["case_key"],
                        "condition": condition,
                        "prompt": prompt,
                    }
                ).encode("utf-8")
            )[:20],
            "case_key": case["case_key"],
            "condition": condition,
            "prompt": prompt,
            "language": case["language"],
            "category": case["category"],
            "source_file": case["source_file"],
            "source_id": case["source_id"],
            "expected_invocation": case["expected_invocation"],
            "expected_substantive_route": case["expected_substantive_route"],
        }
        records.append(record)

    output.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(stable_json(record) + "\n" for record in records)
    output.write_text(body, encoding="utf-8")
    return {
        "status": "prepared",
        "condition": condition,
        "record_count": len(records),
        "output": str(output),
        "sha256": sha256_bytes(body.encode("utf-8")),
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(record)
    return records


def classification_metrics(
    pairs: list[tuple[str, str]], labels: set[str]
) -> dict[str, Any]:
    by_label: dict[str, dict[str, float]] = {}
    f1_values: list[float] = []
    for label in sorted(labels):
        tp = sum(expected == label and predicted == label for expected, predicted in pairs)
        fp = sum(expected != label and predicted == label for expected, predicted in pairs)
        fn = sum(expected == label and predicted != label for expected, predicted in pairs)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
        by_label[label] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
        }
    accuracy = (
        sum(expected == predicted for expected, predicted in pairs) / len(pairs)
        if pairs
        else 0.0
    )
    return {
        "n": len(pairs),
        "accuracy": round(accuracy, 6),
        "macro_f1": round(sum(f1_values) / len(f1_values), 6) if f1_values else 0.0,
        "by_label": by_label,
    }


def summarize(responses_path: Path, judgments_path: Path, output: Path) -> dict[str, Any]:
    responses = read_jsonl(responses_path)
    judgments = read_jsonl(judgments_path)
    rubric = read_json(EVALS / "rubric.json")
    dimension_floors = {
        item["id"]: item["floor"]
        for item in rubric["dimensions"]
        if isinstance(item, dict)
    }

    hard_failures: list[dict[str, Any]] = []
    floor_failures: list[dict[str, Any]] = []
    pairwise = Counter()
    invocation_pairs: list[tuple[str, str]] = []
    route_pairs: list[tuple[str, str]] = []

    for judgment in judgments:
        case_key = judgment.get("case_key", judgment.get("case_id", "unknown"))
        condition = judgment.get("condition", "unknown")
        gates = judgment.get("hard_gates", {})
        if isinstance(gates, dict):
            failed = sorted(gate for gate, value in gates.items() if value is True)
            if failed:
                hard_failures.append(
                    {"case_key": case_key, "condition": condition, "gates": failed}
                )
        dimensions = judgment.get("dimensions", {})
        if isinstance(dimensions, dict):
            for dimension, floor in dimension_floors.items():
                value = dimensions.get(dimension)
                if value is None:
                    continue
                if not isinstance(value, (int, float)) or value < floor:
                    floor_failures.append(
                        {
                            "case_key": case_key,
                            "condition": condition,
                            "dimension": dimension,
                            "score": value,
                            "floor": floor,
                        }
                    )
        preference = judgment.get("pairwise_preference")
        if preference in {"skill", "no-skill", "tie"}:
            pairwise[preference] += 1

        expected_invocation = judgment.get("expected_invocation")
        predicted_invocation = judgment.get("invocation_label")
        if expected_invocation in CANONICAL_INVOCATION and predicted_invocation in CANONICAL_INVOCATION:
            invocation_pairs.append((expected_invocation, predicted_invocation))

        expected_route = judgment.get("expected_substantive_route")
        predicted_route = judgment.get("substantive_route")
        if expected_route in CANONICAL_ROUTES and predicted_route in CANONICAL_ROUTES:
            route_pairs.append((expected_route, predicted_route))

    response_ids = [record.get("run_id") for record in responses]
    duplicate_response_ids = sorted(
        value for value, count in Counter(response_ids).items() if value and count > 1
    )

    summary = {
        "schema_version": "1.0",
        "status": "summarized",
        "responses": {
            "path": str(responses_path),
            "sha256": sha256_file(responses_path),
            "count": len(responses),
            "duplicate_run_ids": duplicate_response_ids,
        },
        "judgments": {
            "path": str(judgments_path),
            "sha256": sha256_file(judgments_path),
            "count": len(judgments),
        },
        "hard_gate_failure_count": len(hard_failures),
        "hard_gate_failures": hard_failures,
        "dimension_floor_failure_count": len(floor_failures),
        "dimension_floor_failures": floor_failures,
        "invocation_metrics": classification_metrics(
            invocation_pairs, CANONICAL_INVOCATION
        ),
        "substantive_route_metrics": classification_metrics(
            route_pairs, CANONICAL_ROUTES
        ),
        "pairwise": {
            "skill": pairwise["skill"],
            "no-skill": pairwise["no-skill"],
            "tie": pairwise["tie"],
        },
        "qualification_claim": False,
        "note": "This summary does not establish production qualification; release/qualification.json controls that claim.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-fixtures")

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--condition", choices=("skill", "no-skill"), required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)

    summarize_parser = subparsers.add_parser("summarize")
    summarize_parser.add_argument("--responses", type=Path, required=True)
    summarize_parser.add_argument("--judgments", type=Path, required=True)
    summarize_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "validate-fixtures":
            errors = validate_fixtures()
            payload = {
                "status": "pass" if not errors else "fail",
                "error_count": len(errors),
                "errors": errors,
            }
            print_json(payload)
            return 0 if not errors else 1
        if args.command == "prepare":
            print_json(prepare(args.condition, args.output))
            return 0
        if args.command == "summarize":
            print_json(summarize(args.responses, args.judgments, args.output))
            return 0
    except (OSError, ValueError, KeyError) as exc:
        print_json({"status": "fail", "error": str(exc)})
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
