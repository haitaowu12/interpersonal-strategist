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
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"

CASE_SUITES = {
    "cases.json": "case_count",
    "deep-context-memory.json": "case_count",
    "invocation.json": "case_count",
    "substantive-routes.json": "case_count",
    "multi-actor.json": "case_count",
    "relationship-norms.json": "case_count",
    "ai-mediated.json": "case_count",
    "trust-reliance.json": "case_count",
    "speech-acts.json": "case_count",
    "profile-scoring.json": "case_count",
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
    "NOT_OWN",
}
CANONICAL_ROUTES = {
    "IN_SCOPE",
    "COACH_WITH_CAUTION",
    "REFER_OR_ESCALATE",
    "REFUSE",
}
SKILL_PREFIX = "Use $interpersonal-strategist. "
PAIRWISE_PREFERENCES = {"skill", "no-skill", "tie", "not_scored"}
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20_260_730


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
                "strata": sorted(
                    {
                        Path(filename).stem,
                        str(case.get("category", case.get("speech_act", "unknown"))),
                        str(case.get("language", "unknown")),
                        *(
                            ["high_power"]
                            if str(case.get("power", "")).lower() == "high"
                            else []
                        ),
                        *(["multi_actor"] if filename == "multi-actor.json" else []),
                        *(
                            ["trust_reliance"]
                            if filename == "trust-reliance.json"
                            else []
                        ),
                        *(
                            ["bilingual"]
                            if str(case.get("language", "")).lower()
                            in {"zh-cn", "mixed", "bilingual"}
                            else []
                        ),
                    }
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
                    "strata": ["bilingual", "bilingual-parity", language_key],
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
            "strata": case["strata"],
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


def bootstrap_lower_bound(
    values: list[float],
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> float | None:
    if not values:
        return None
    generator = random.Random(seed)
    estimates = sorted(
        sum(generator.choice(values) for _ in values) / len(values)
        for _ in range(resamples)
    )
    index = max(0, int(resamples * 0.05) - 1)
    return round(estimates[index], 6)


def validate_result_records(
    responses: list[dict[str, Any]],
    judgments: list[dict[str, Any]],
    rubric: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not responses:
        raise ValueError("responses file must contain at least one record")
    if not judgments:
        raise ValueError("judgments file must contain at least one record")

    rubric_version = rubric.get("schema_version")
    gate_ids = {
        item["id"]
        for item in rubric.get("hard_gates", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    dimension_ids = {
        item["id"]
        for item in rubric.get("dimensions", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    errors: list[str] = []
    responses_by_run: dict[str, dict[str, Any]] = {}
    blind_ids: set[str] = set()

    for index, response in enumerate(responses):
        label = f"response {index + 1}"
        run_id = response.get("run_id")
        case_key = response.get("case_key")
        condition = response.get("condition")
        text = response.get("response")
        blind_id = response.get("blind_id")
        if not isinstance(run_id, str) or not run_id.strip():
            errors.append(f"{label}: run_id must be a non-empty string")
            continue
        if run_id in responses_by_run:
            errors.append(f"{label}: duplicate run_id {run_id}")
            continue
        responses_by_run[run_id] = response
        if not isinstance(case_key, str) or not case_key.strip():
            errors.append(f"{label}: case_key must be a non-empty string")
        if condition not in {"skill", "no-skill"}:
            errors.append(f"{label}: condition must be skill or no-skill")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{label}: response must be a non-empty string")
        if not isinstance(blind_id, str) or not blind_id.strip():
            errors.append(f"{label}: blind_id must be a non-empty string")
        elif blind_id in blind_ids:
            errors.append(f"{label}: duplicate blind_id {blind_id}")
        else:
            blind_ids.add(blind_id)
        strata = response.get("strata", [])
        if not isinstance(strata, list) or any(
            not isinstance(item, str) or not item.strip() for item in strata
        ):
            errors.append(f"{label}: strata must be a string list")

    judgments_by_run: dict[str, dict[str, Any]] = {}
    pairwise_by_case: defaultdict[str, list[str]] = defaultdict(list)
    for index, judgment in enumerate(judgments):
        label = f"judgment {index + 1}"
        run_id = judgment.get("run_id")
        if not isinstance(run_id, str) or run_id not in responses_by_run:
            errors.append(f"{label}: run_id must reference exactly one response")
            continue
        if run_id in judgments_by_run:
            errors.append(f"{label}: duplicate judgment for run_id {run_id}")
            continue
        judgments_by_run[run_id] = judgment
        response = responses_by_run[run_id]
        for field in ("case_key", "condition"):
            if judgment.get(field) != response.get(field):
                errors.append(f"{label}: {field} does not match response {run_id}")
        if judgment.get("blind_id") != response.get("blind_id"):
            errors.append(f"{label}: blind_id does not match response {run_id}")
        if judgment.get("rubric_version") != rubric_version:
            errors.append(
                f"{label}: rubric_version does not match rubric {rubric_version}"
            )

        gates = judgment.get("hard_gates")
        if not isinstance(gates, dict) or set(gates) != gate_ids:
            errors.append(f"{label}: hard_gates must contain every canonical gate")
        elif any(not isinstance(value, bool) for value in gates.values()):
            errors.append(f"{label}: every hard-gate value must be boolean")

        dimensions = judgment.get("dimensions")
        if not isinstance(dimensions, dict) or set(dimensions) != dimension_ids:
            errors.append(f"{label}: dimensions must contain every canonical dimension")
        elif any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or not 1 <= value <= 5
            for value in dimensions.values()
        ):
            errors.append(f"{label}: every dimension score must be an integer 1-5")

        evidence = judgment.get("evidence")
        if not isinstance(evidence, dict) or not evidence or any(
            not isinstance(value, str) or not value.strip() for value in evidence.values()
        ):
            errors.append(f"{label}: evidence must contain observable string reasons")

        preference = judgment.get("pairwise_preference", "not_scored")
        if preference not in PAIRWISE_PREFERENCES:
            errors.append(f"{label}: invalid pairwise_preference")
        elif preference != "not_scored":
            pairwise_by_case[str(response.get("case_key"))].append(preference)

    missing_judgments = sorted(set(responses_by_run) - set(judgments_by_run))
    if missing_judgments:
        errors.append(
            "missing judgments for response run_ids: " + ", ".join(missing_judgments)
        )
    extra_judgments = sorted(set(judgments_by_run) - set(responses_by_run))
    if extra_judgments:
        errors.append(
            "judgments reference unknown run_ids: " + ", ".join(extra_judgments)
        )

    conditions_by_case: defaultdict[str, set[str]] = defaultdict(set)
    for response in responses_by_run.values():
        conditions_by_case[str(response.get("case_key"))].add(
            str(response.get("condition"))
        )
    conditions = {
        str(response.get("condition")) for response in responses_by_run.values()
    }
    if conditions == {"skill", "no-skill"}:
        unpaired = sorted(
            case_key
            for case_key, case_conditions in conditions_by_case.items()
            if case_conditions != {"skill", "no-skill"}
        )
        if unpaired:
            errors.append("unpaired comparison case_keys: " + ", ".join(unpaired))
        invalid_pairwise = sorted(
            case_key
            for case_key in conditions_by_case
            if len(pairwise_by_case.get(case_key, [])) != 1
        )
        if invalid_pairwise:
            errors.append(
                "paired cases require exactly one pairwise judgment: "
                + ", ".join(invalid_pairwise)
            )
    elif pairwise_by_case:
        errors.append("pairwise judgments require both skill and no-skill conditions")

    if errors:
        raise ValueError("; ".join(errors))
    return responses_by_run, judgments_by_run


def pairwise_statistics(preferences: list[str]) -> dict[str, Any]:
    counts = Counter(preferences)
    non_tied = counts["skill"] + counts["no-skill"]
    total = len(preferences)
    values = [1.0] * counts["skill"] + [0.0] * counts["no-skill"]
    return {
        "skill": counts["skill"],
        "no-skill": counts["no-skill"],
        "tie": counts["tie"],
        "total": total,
        "non_tied": non_tied,
        "non_tied_proportion": round(non_tied / total, 6) if total else None,
        "skill_win_rate_excluding_ties": (
            round(counts["skill"] / non_tied, 6) if non_tied else None
        ),
        "skill_win_rate_one_sided_95_lower_bound": bootstrap_lower_bound(values),
        "bootstrap": {
            "unit": "case_key",
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
        },
    }


def summarize(responses_path: Path, judgments_path: Path, output: Path) -> dict[str, Any]:
    responses = read_jsonl(responses_path)
    judgments = read_jsonl(judgments_path)
    rubric = read_json(EVALS / "rubric.json")
    responses_by_run, judgments_by_run = validate_result_records(
        responses, judgments, rubric
    )
    dimension_floors = {
        item["id"]: item["floor"]
        for item in rubric["dimensions"]
        if isinstance(item, dict)
    }

    hard_failures: list[dict[str, Any]] = []
    floor_failures: list[dict[str, Any]] = []
    pairwise_by_case: dict[str, str] = {}
    strata_by_case: defaultdict[str, set[str]] = defaultdict(set)
    invocation_pairs: list[tuple[str, str]] = []
    route_pairs: list[tuple[str, str]] = []

    for run_id, judgment in judgments_by_run.items():
        response = responses_by_run[run_id]
        case_key = str(response["case_key"])
        condition = str(response["condition"])
        strata_by_case[case_key].update(response.get("strata", []))
        strata_by_case[case_key].update(
            str(response.get(field))
            for field in ("category", "language", "source_file")
            if response.get(field)
        )

        gates = judgment["hard_gates"]
        failed = sorted(gate for gate, value in gates.items() if value is True)
        if failed:
            hard_failures.append(
                {"case_key": case_key, "condition": condition, "gates": failed}
            )
        dimensions = judgment["dimensions"]
        for dimension, floor in dimension_floors.items():
            value = dimensions[dimension]
            if value < floor:
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
            pairwise_by_case[case_key] = preference

        expected_invocation = response.get("expected_invocation")
        predicted_invocation = judgment.get("invocation_label")
        if (
            expected_invocation in CANONICAL_INVOCATION
            and predicted_invocation in CANONICAL_INVOCATION
        ):
            invocation_pairs.append((expected_invocation, predicted_invocation))

        expected_route = response.get("expected_substantive_route")
        predicted_route = judgment.get("substantive_route")
        if expected_route in CANONICAL_ROUTES and predicted_route in CANONICAL_ROUTES:
            route_pairs.append((expected_route, predicted_route))

    pairwise = pairwise_statistics(list(pairwise_by_case.values()))
    pairwise_by_stratum = {
        stratum: pairwise_statistics(
            [
                preference
                for case_key, preference in pairwise_by_case.items()
                if stratum in strata_by_case[case_key]
            ]
        )
        for stratum in sorted(
            {stratum for strata in strata_by_case.values() for stratum in strata}
        )
    }
    targets = rubric.get("qualification_targets", {})
    low_complexity_differences: list[float] = []
    for case_key, strata in strata_by_case.items():
        if "low_complexity" not in strata:
            continue
        scores: defaultdict[str, list[float]] = defaultdict(list)
        for run_id, response in responses_by_run.items():
            if response.get("case_key") != case_key:
                continue
            dimensions = judgments_by_run[run_id]["dimensions"]
            usability = (
                dimensions["actionability"] + dimensions["concision"] - 2
            ) / 8
            scores[str(response["condition"])].append(usability)
        if scores["skill"] and scores["no-skill"]:
            low_complexity_differences.append(
                sum(scores["skill"]) / len(scores["skill"])
                - sum(scores["no-skill"]) / len(scores["no-skill"])
            )
    low_complexity_lower_bound = bootstrap_lower_bound(low_complexity_differences)
    pairwise["low_complexity_noninferiority"] = {
        "case_count": len(low_complexity_differences),
        "paired_usability_difference_one_sided_95_lower_bound": (
            low_complexity_lower_bound
        ),
        "margin": targets.get("low_complexity_noninferiority_margin"),
        "status": (
            "not_evaluable"
            if low_complexity_lower_bound is None
            else (
                "pass"
                if low_complexity_lower_bound
                >= targets.get("low_complexity_noninferiority_margin", 0)
                else "fail"
            )
        ),
    }
    required_strata = targets.get("material_advantage_required_strata", [])
    minimum_pairs_per_stratum = targets.get("minimum_pairs_per_required_stratum", 1)
    material_advantage = {
        stratum: {
            "minimum_pairs": minimum_pairs_per_stratum,
            "status": (
                "not_evaluable"
                if pairwise_by_stratum.get(stratum, {}).get("total", 0)
                < minimum_pairs_per_stratum
                else (
                    "pass"
                    if (
                        pairwise_by_stratum[stratum][
                            "skill_win_rate_one_sided_95_lower_bound"
                        ]
                        or 0
                    )
                    > 0.5
                    else "fail"
                )
            ),
        }
        for stratum in required_strata
    }
    basic_pairwise_pass = (
        pairwise["non_tied"] >= targets.get("no_skill_minimum_non_tied_pairs", 0)
        and (pairwise["non_tied_proportion"] or 0)
        >= targets.get("no_skill_minimum_non_tied_proportion", 0)
        and (
            pairwise["skill_win_rate_one_sided_95_lower_bound"] is not None
            and pairwise["skill_win_rate_one_sided_95_lower_bound"]
            > targets.get("no_skill_lower_confidence_bound_excluding_ties_gt", 1.0)
        )
    )
    comparison_status = "pass" if basic_pairwise_pass else "not_met"
    if pairwise["low_complexity_noninferiority"]["status"] == "not_evaluable" or any(
        item["status"] == "not_evaluable" for item in material_advantage.values()
    ):
        comparison_status = "not_evaluable"
    elif pairwise["low_complexity_noninferiority"]["status"] != "pass" or any(
        item["status"] != "pass" for item in material_advantage.values()
    ):
        comparison_status = "not_met"
    pairwise["acceptance"] = {
        "minimum_non_tied_pairs": targets.get("no_skill_minimum_non_tied_pairs"),
        "minimum_non_tied_proportion": targets.get(
            "no_skill_minimum_non_tied_proportion"
        ),
        "lower_bound_must_exceed": targets.get(
            "no_skill_lower_confidence_bound_excluding_ties_gt"
        ),
        "material_advantage_by_required_stratum": material_advantage,
        "status": comparison_status,
    }

    summary = {
        "schema_version": "2.0",
        "rubric_version": rubric.get("schema_version"),
        "status": "summarized",
        "responses": {
            "path": str(responses_path),
            "sha256": sha256_file(responses_path),
            "count": len(responses),
            "complete": True,
        },
        "judgments": {
            "path": str(judgments_path),
            "sha256": sha256_file(judgments_path),
            "count": len(judgments),
            "complete": True,
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
        "pairwise": pairwise,
        "pairwise_by_stratum": pairwise_by_stratum,
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
