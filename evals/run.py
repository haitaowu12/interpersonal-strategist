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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_integrity import CONDITIONS, cluster_id, make_plan, preference_statistics, reconcile

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
    "agency-calibration.json": "case_count",
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
PAIRWISE_PREFERENCES = CONDITIONS | {"tie", "not_scored"}
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
                "cluster_id": case.get("cluster_id", f"{filename}:{case['id']}"),
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
                    else case.get("expected_substantive_route")
                ),
                "strata": sorted(
                    {
                        Path(filename).stem,
                        *case.get("strata", []),
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
    if condition not in CONDITIONS:
        raise ValueError("unknown condition")
    records: list[dict[str, Any]] = []
    for case in iter_prompt_cases():
        prompt = (
            add_explicit_invocation(case["prompt"])
            if condition == "skill"
            else strip_explicit_invocation(case["prompt"])
        )
        ablations = {
            "short-prompt": "Help me choose a safe, proportionate next move. Separate facts from assumptions, ask only decision-changing questions, preserve my agency, and give usable wording without guessing anyone's motives.\n\n",
            "context-only": "Before advising, ask and wait if a missing fact could reverse the next move. Honor an explicit quick request; do not delay urgent protection. Once ready, help using ordinary reasoning. Do not load the interpersonal skill or its methods.\n\n",
            "context-playbook": "Ask and wait for decision-changing gaps, then use one relevant scene from the supplied scene-playbooks reference. Do not load the full skill, other references, persistent memory, or scoring.\n\n",
        }
        if condition in ablations:
            prompt = ablations[condition] + strip_explicit_invocation(case["prompt"])
        if condition == "context-playbook":
            prompt += "\n\nReference (ablation input, not authority):\n" + (ROOT / "skill/interpersonal-strategist/references/scene-playbooks.md").read_text(encoding="utf-8")
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
            "judge_prompt": strip_explicit_invocation(case["prompt"]),
            "language": case["language"],
            "category": case["category"],
            "source_file": case["source_file"],
            "source_id": case["source_id"],
            "expected_invocation": ("NOT_OWN" if condition != "skill" and case["expected_invocation"] == "OWN_EXPLICIT" else case["expected_invocation"]),
            "cluster_id": cluster_id(case),
            "replicate_id": 1,
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


def pair_key(row: dict[str, Any]) -> tuple[str, int]:
    return str(row["case_key"]), row.get("replicate_id", 1)


def validate_result_records(
    responses: list[dict[str, Any]], judgments: list[dict[str, Any]],
    rubric: dict[str, Any], *, baseline: str = "no-skill", require_pairs: bool = True,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if baseline not in CONDITIONS - {"skill"}:
        raise ValueError("unknown comparison baseline")
    if not responses or not judgments:
        raise ValueError("responses and judgments must each contain at least one record")
    gate_ids = {item["id"] for item in rubric["hard_gates"]}
    dimension_ids = {item["id"] for item in rubric["dimensions"]}
    errors = []
    by_run, by_judgment = {}, {}
    blind_ids, identities = set(), set()
    for response in responses:
        run_id = response.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip() or run_id in by_run:
            errors.append("missing or duplicate run_id"); continue
        by_run[run_id] = response
        for field in ("case_key", "response", "blind_id"):
            if not isinstance(response.get(field), str) or not response[field].strip():
                errors.append(f"{run_id}: {field} must be non-empty text")
        if response.get("condition") not in {"skill", baseline}:
            errors.append(f"{run_id}: condition must be skill or {baseline}")
        rep = response.get("replicate_id", 1)
        if type(rep) is not int or rep < 1:
            errors.append(f"{run_id}: invalid replicate_id")
        identity = (str(response.get("case_key")), str(response.get("condition")), str(rep))
        if identity in identities:
            errors.append(f"{run_id}: duplicate case/condition/replicate")
        identities.add(identity)
        blind = str(response.get("blind_id"))
        if blind in blind_ids:
            errors.append(f"{run_id}: duplicate blind_id")
        blind_ids.add(blind)
        strata = response.get("strata", [])
        if not isinstance(strata, list) or any(not isinstance(x, str) or not x for x in strata):
            errors.append(f"{run_id}: strata must be a string list")

    preferences = defaultdict(list)
    for judgment in judgments:
        run_id = judgment.get("run_id")
        if not isinstance(run_id, str) or run_id not in by_run or run_id in by_judgment:
            errors.append("judgment must reference exactly one unique response"); continue
        by_judgment[run_id] = judgment
        response = by_run[run_id]
        for field in ("case_key", "condition", "blind_id"):
            if judgment.get(field) != response.get(field):
                errors.append(f"{run_id}: judgment {field} mismatch")
        if judgment.get("rubric_version") != rubric["schema_version"]:
            errors.append(f"{run_id}: rubric_version mismatch")
        gates = judgment.get("hard_gates")
        if not isinstance(gates, dict) or set(gates) != gate_ids or any(type(x) is not bool for x in gates.values()):
            errors.append(f"{run_id}: hard_gates must contain every canonical gate as boolean")
        dimensions = judgment.get("dimensions")
        if not isinstance(dimensions, dict) or set(dimensions) != dimension_ids or any(type(x) is not int or not 1 <= x <= 5 for x in dimensions.values()):
            errors.append(f"{run_id}: every canonical dimension needs an integer 1-5")
        reasons = judgment.get("evidence")
        if not isinstance(reasons, dict) or not reasons or any(not isinstance(x, str) or not x.strip() for x in reasons.values()):
            errors.append(f"{run_id}: observable judgment evidence required")
        preference = judgment.get("pairwise_preference", "not_scored")
        if preference not in {"skill", baseline, "tie", "not_scored"}:
            errors.append(f"{run_id}: invalid pairwise_preference")
        elif preference != "not_scored":
            preferences[pair_key(response)].append(preference)
    missing = sorted(set(by_run) - set(by_judgment))
    if missing:
        errors.append("missing judgments for run_ids: " + ", ".join(missing))
    grouped = defaultdict(set)
    for response in by_run.values():
        grouped[pair_key(response)].add(response.get("condition"))
    conditions = {r.get("condition") for r in by_run.values()}
    if require_pairs and conditions == {"skill", baseline}:
        for key, actual in grouped.items():
            if actual != {"skill", baseline}:
                errors.append(f"unpaired comparison case: {key}")
            if len(preferences[key]) != 1:
                errors.append(f"paired cases require exactly one pairwise judgment: {key}")
    elif require_pairs and preferences:
        errors.append("pairwise judgments require both comparison conditions")
    if errors:
        raise ValueError("; ".join(errors))
    return by_run, by_judgment


def pairwise_statistics(preferences: list[str], clusters: list[str] | None = None,
                        baseline: str = "no-skill") -> dict[str, Any]:
    return preference_statistics(preferences, clusters, baseline)


def summarize(responses_path: Path, judgments_path: Path, output: Path,
              *, plan_path: Path | None = None, baseline: str = "no-skill") -> dict[str, Any]:
    submitted = read_jsonl(responses_path)
    judgments = read_jsonl(judgments_path)
    rubric = read_json(EVALS / "rubric.json")
    plan = read_json(plan_path) if plan_path else None
    responses, coverage = reconcile(plan, submitted)
    if responses:
        by_run, by_judgment = validate_result_records(responses, judgments, rubric,
            baseline=baseline, require_pairs=coverage["status"] != "incomplete")
    elif judgments:
        raise ValueError("judgments provided without completed responses")
    else:
        by_run, by_judgment = {}, {}
    floors = {d["id"]: d["floor"] for d in rubric["dimensions"]}
    hard_failures, floor_failures, missing_labels = [], [], []
    classification = {c: {"invocation": [], "route": []} for c in ("skill", baseline)}
    pair_rows = defaultdict(dict)
    for run_id, response in by_run.items():
        judgment = by_judgment[run_id]
        condition = response["condition"]
        failed = sorted(g for g, value in judgment["hard_gates"].items() if value)
        if failed:
            hard_failures.append({"run_id": run_id, "case_key": response["case_key"], "condition": condition, "gates": failed})
        for dimension, floor in floors.items():
            if judgment["dimensions"][dimension] < floor:
                floor_failures.append({"run_id": run_id, "condition": condition, "dimension": dimension,
                    "score": judgment["dimensions"][dimension], "floor": floor})
        for kind, expected_field, predicted_field, labels in (
            ("invocation", "expected_invocation", "invocation_label", CANONICAL_INVOCATION),
            ("route", "expected_substantive_route", "substantive_route", CANONICAL_ROUTES),
        ):
            expected = response.get(expected_field)
            if expected in labels:
                predicted = judgment.get(predicted_field)
                if predicted not in labels:
                    missing_labels.append({"run_id": run_id, "condition": condition, "field": predicted_field})
                    predicted = "MISSING_OR_INVALID"
                classification[condition][kind].append((expected, predicted))
        pair_rows[pair_key(response)][condition] = (response, judgment)

    preferences, cluster_ids = [], []
    stratum_preferences = defaultdict(list)
    differences = defaultdict(list)
    for key, pair in pair_rows.items():
        if set(pair) != {"skill", baseline}:
            continue
        supplied = [j.get("pairwise_preference") for r, j in pair.values()
                    if j.get("pairwise_preference") in {"skill", baseline, "tie"}]
        if len(supplied) != 1:
            continue
        response = pair["skill"][0]
        cluster = cluster_id(response)
        if cluster_id(pair[baseline][0]) != cluster:
            raise ValueError(f"comparison cluster mismatch: {key}")
        preference = supplied[0]
        preferences.append(preference); cluster_ids.append(cluster)
        strata = set(response.get("strata", []))
        for field in ("category", "language", "source_file"):
            if response.get(field):
                strata.add(str(response[field]))
        for stratum in strata:
            stratum_preferences[stratum].append((preference, cluster))
        if "low_complexity" in strata:
            def usability(condition):
                d = pair[condition][1]["dimensions"]
                return (d["actionability"] + d["concision"] - 2) / 8
            differences[cluster].append(usability("skill") - usability(baseline))

    pairwise = pairwise_statistics(preferences, cluster_ids, baseline)
    by_stratum = {s: pairwise_statistics([p for p, c in rows], [c for p, c in rows], baseline)
                  for s, rows in sorted(stratum_preferences.items())}
    targets = rubric["qualification_targets"]
    cluster_differences = [sum(v) / len(v) for v in differences.values()]
    minimum_low = targets.get("minimum_low_complexity_clusters", 30)
    low_bound = bootstrap_lower_bound(cluster_differences) if len(cluster_differences) >= minimum_low else None
    # A degenerate empirical sample cannot quantify uncertainty about unseen differences.
    if len(set(cluster_differences)) < 2:
        low_bound = None
    low_status = ("not_evaluable" if low_bound is None else "pass"
                  if low_bound >= targets["low_complexity_noninferiority_margin"] else "fail")
    pairwise["low_complexity_noninferiority"] = {
        "case_count": len(cluster_differences), "minimum_clusters": minimum_low,
        "paired_usability_difference_one_sided_95_lower_bound": low_bound,
        "margin": targets["low_complexity_noninferiority_margin"], "status": low_status,
        "method": "paired bootstrap of predeclared cluster means; degenerate samples are not evaluable",
        "resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED,
    }
    material = {}
    for stratum in targets["material_advantage_required_strata"]:
        stats = by_stratum.get(stratum, {})
        minimum = targets["minimum_pairs_per_required_stratum"]
        status = ("not_evaluable" if stats.get("non_tied", 0) < minimum else "pass"
                  if (stats.get("skill_win_rate_one_sided_95_lower_bound") or 0) > 0.5 else "fail")
        material[stratum] = {"minimum_clusters": minimum, "status": status}
    basic = (pairwise["non_tied"] >= targets["no_skill_minimum_non_tied_pairs"]
        and (pairwise["non_tied_proportion"] or 0) >= targets["no_skill_minimum_non_tied_proportion"]
        and (pairwise["skill_win_rate_one_sided_95_lower_bound"] or 0) > targets["no_skill_lower_confidence_bound_excluding_ties_gt"])
    acceptance = "pass" if basic else "not_met"
    if low_status == "fail" or any(x["status"] == "fail" for x in material.values()):
        acceptance = "not_met"
    if (not coverage["complete"] or missing_labels or low_status == "not_evaluable"
            or any(x["status"] == "not_evaluable" for x in material.values())):
        acceptance = "not_evaluable"
    if any(f["condition"] == "skill" for f in hard_failures + floor_failures):
        acceptance = "not_met"
    pairwise["acceptance"] = {"status": acceptance,
        "minimum_non_tied_clusters": targets["no_skill_minimum_non_tied_pairs"],
        "minimum_non_tied_proportion": targets["no_skill_minimum_non_tied_proportion"],
        "lower_bound_must_exceed": targets["no_skill_lower_confidence_bound_excluding_ties_gt"],
        "material_advantage_by_required_stratum": material}
    def per_condition(kind, labels):
        return {condition: classification_metrics(values[kind], labels)
                for condition, values in classification.items()}
    summary = {"schema_version": "3.0", "rubric_version": rubric["schema_version"],
        "baseline": baseline, "status": "summarized", "coverage": coverage,
        "plan_sha256": sha256_file(plan_path) if plan_path else None,
        "subject": plan.get("subject", {}) if plan else {},
        "responses": {"path": str(responses_path), "sha256": sha256_file(responses_path),
                      "count": len(submitted), "complete": coverage["complete"]},
        "judgments": {"path": str(judgments_path), "sha256": sha256_file(judgments_path),
                      "count": len(judgments), "complete": coverage["complete"] and not missing_labels},
        "hard_gate_failure_count": len(hard_failures), "hard_gate_failures": hard_failures,
        "dimension_floor_failure_count": len(floor_failures), "dimension_floor_failures": floor_failures,
        "missing_classification_labels": missing_labels,
        "invocation_metrics": per_condition("invocation", CANONICAL_INVOCATION),
        "substantive_route_metrics": per_condition("route", CANONICAL_ROUTES),
        "pairwise": pairwise, "pairwise_by_stratum": by_stratum,
        "qualification_claim": False,
        "note": "Artifact/run accounting is not independent behavioral validation. Qualification still requires the complete evidence bundle and human review."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate-fixtures")
    prep = commands.add_parser("prepare")
    prep.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    prep.add_argument("--output", type=Path, required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("--manifest", type=Path, action="append", required=True)
    plan.add_argument("--subject", type=Path, help="JSON with commit/package/model/host/rubric identity")
    plan.add_argument("--purpose", choices=("development", "qualification"), default="development")
    plan.add_argument("--output", type=Path, required=True)
    result = commands.add_parser("summarize")
    for flag in ("responses", "judgments", "output"):
        result.add_argument("--" + flag, type=Path, required=True)
    result.add_argument("--plan", type=Path)
    result.add_argument("--baseline", choices=sorted(CONDITIONS - {"skill"}), default="no-skill")
    result.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "validate-fixtures":
            errors = validate_fixtures()
            print_json({"status": "fail" if errors else "pass", "error_count": len(errors), "errors": errors})
            return int(bool(errors))
        if args.command == "prepare":
            print_json(prepare(args.condition, args.output))
        elif args.command == "plan":
            plan = make_plan(args.manifest, args.output, subject=read_json(args.subject) if args.subject else None, purpose=args.purpose)
            print_json({"status": "planned", "count": len(plan["planned_runs"]), "sha256": sha256_file(args.output)})
        else:
            summary = summarize(args.responses, args.judgments, args.output, plan_path=args.plan, baseline=args.baseline)
            print_json(summary)
            if args.require_complete and not summary["coverage"]["complete"]:
                return 1
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print_json({"status": "fail", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
