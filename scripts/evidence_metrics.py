"""Recompute qualification counts from private, adjudicated review records.

These checks validate accounting, not whether a reviewer is truthful, independent,
or competent. The evidence bundle and human release review must establish that.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any


def load(path: Path, subject: dict) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise ValueError(f"invalid review record: {path.name}")
    if data.get("subject") != subject:
        raise ValueError(f"review subject mismatch: {path.name}")
    return data


def unique(rows: Any, key: str) -> dict:
    if not isinstance(rows, list) or not rows:
        raise ValueError("review records must be a non-empty list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"review record requires {key}")
        if row[key] in result:
            raise ValueError(f"duplicate {key}")
        result[row[key]] = row
    return result


def kappa(pairs: list[tuple[Any, Any]]) -> float:
    if not pairs:
        raise ValueError("empty calibration stratum")
    a, b = Counter(x for x, y in pairs), Counter(y for x, y in pairs)
    n = len(pairs)
    observed = sum(x == y for x, y in pairs) / n
    chance = sum(a[x] * b[x] for x in set(a) | set(b)) / n ** 2
    if chance == 1:
        raise ValueError("constant calibration labels cannot establish chance-corrected agreement")
    return round((observed - chance) / (1 - chance), 6)


def recompute_reviews(paths: dict[str, Path], qualification: dict, subject: dict, rubric: dict) -> dict:
    gates = qualification["gates"]
    expected = unique(load(paths["holdout_set"], subject).get("cases"), "case_id")
    results = unique(load(paths["holdout_results"], subject).get("results"), "case_id")
    if set(expected) != set(results):
        raise ValueError("holdout expected/result coverage mismatch")
    hard_gates = {g["id"] for g in rubric["hard_gates"]}
    failure_count = 0
    for row in results.values():
        flags = row.get("hard_gates")
        if row.get("status") != "completed" or not row.get("reviewer_id"):
            raise ValueError("holdout result missing completion or reviewer")
        if not isinstance(flags, dict) or set(flags) != hard_gates or any(type(x) is not bool for x in flags.values()):
            raise ValueError("holdout result requires every canonical hard gate")
        failure_count += any(flags.values())
    for row in expected.values():
        strata = row.get("strata")
        if not isinstance(strata, list) or len(strata) != len(set(strata)) or any(not isinstance(s, str) for s in strata):
            raise ValueError("holdout strata must be unique strings")
    families = defaultdict(set)
    family_failed = defaultdict(bool)
    for key, row in expected.items():
        family = row.get("family_id")
        if not isinstance(family, str) or not family.strip():
            raise ValueError("holdout requires predeclared family_id")
        families[family].update(row["strata"])
        family_failed[family] |= any(results[key]["hard_gates"].values())
    general = {key: sum(key in labels for labels in families.values())
               for key in ("general", "multi_actor", "bilingual_mixed")}
    general["hard_failures"] = failure_count
    safety_strata = set(gates["adversarial_safety_holdouts"]["required_strata"])
    safety = {key: labels & safety_strata for key, labels in families.items() if labels & safety_strata}
    safety_counts = {"unique_cases": len(safety), "compound_cases": sum(len(s) >= 2 for s in safety.values()),
        "hard_failures": sum(family_failed[key] for key in safety),
        "maximum_strata_credit_observed": max(map(len, safety.values()), default=0),
        "strata": {s: sum(s in labels for labels in safety.values()) for s in sorted(safety_strata)}}

    bilingual = load(paths["bilingual_review"], subject)
    expected_items = bilingual.get("expected_item_ids")
    if not isinstance(expected_items, list) or not expected_items or len(expected_items) != len(set(expected_items)):
        raise ValueError("bilingual review requires unique expected items")
    ratings = bilingual.get("ratings", [])
    seen, reviewers, values = set(), set(), []
    for row in ratings:
        key = (row.get("item_id"), row.get("reviewer_id"))
        score = row.get("naturalness")
        if key in seen or key[0] not in expected_items or not isinstance(key[1], str) or not key[1]:
            raise ValueError("duplicate or unplanned bilingual rating")
        if type(score) is not int or not 1 <= score <= 5:
            raise ValueError("naturalness must be an integer 1–5")
        seen.add(key); reviewers.add(key[1]); values.append(score)
    if any(sum(key[0] == item for key in seen) < 2 for item in expected_items):
        raise ValueError("every planned bilingual item requires two reviewers")

    pilot = load(paths["pilot_evidence"], subject)
    episodes = unique(pilot.get("episodes"), "episode_id")
    planned_episodes = pilot.get("expected_episode_ids")
    if not isinstance(planned_episodes, list) or len(planned_episodes) != len(set(planned_episodes)) or set(planned_episodes) != set(episodes):
        raise ValueError("pilot expected/observed coverage mismatch")
    for row in episodes.values():
        if row.get("consented") is not True or row.get("eligible_adult") is not True or row.get("status") != "completed":
            raise ValueError("pilot episode lacks consent, eligibility, or completion")
        if row.get("followup_status") not in {"completed", "declined", "unreachable"}:
            raise ValueError("pilot must preserve follow-up missingness")
        if row.get("unresolved_adverse_event") is not False:
            raise ValueError("pilot has an unreviewed adverse event")

    calibration = load(paths["judge_calibration"], subject)
    rows = unique(calibration.get("ratings"), "rating_id")
    groups = {"route": [], "hard_gate": [], "subjective": []}
    positive, false_negative = 0, 0
    for row in rows.values():
        kind, a, b = row.get("kind"), row.get("human_a"), row.get("human_b")
        if kind not in groups:
            raise ValueError("unknown calibration kind")
        if kind == "route" and (a not in {"IN_SCOPE", "COACH_WITH_CAUTION", "REFER_OR_ESCALATE", "REFUSE"} or b not in {"IN_SCOPE", "COACH_WITH_CAUTION", "REFER_OR_ESCALATE", "REFUSE"}):
            raise ValueError("invalid calibration route")
        if kind == "hard_gate":
            if any(type(row.get(k)) is not bool for k in ("human_a", "human_b", "adjudicated_failure", "automated_failure")):
                raise ValueError("hard-gate calibration requires binary judgments")
            positive += row["adjudicated_failure"]
            false_negative += row["adjudicated_failure"] and not row["automated_failure"]
            if a != b and row.get("adjudicated") is not True:
                raise ValueError("hard-gate disagreement needs human adjudication")
        if kind == "subjective" and any(type(x) is not int or not 1 <= x <= 5 for x in (a, b)):
            raise ValueError("subjective calibration ratings must be 1–5")
        groups[kind].append((a, b))
    if not positive:
        raise ValueError("calibration contains no positive hard failures")
    metrics = {"route_and_hard_gate_agreement": min(kappa(groups["route"]), kappa(groups["hard_gate"])),
               "subjective_agreement": kappa(groups["subjective"]),
               "hard_failure_false_negative_rate": round(false_negative / positive, 6)}
    return {
        "independent_untouched_holdouts": {"counts": general},
        "adversarial_safety_holdouts": {"counts": safety_counts},
        "bilingual_fluent_review": {"counts": {"reviewers": len(reviewers)}, "metrics": {"median_naturalness": median(values)}},
        "privacy_safe_controlled_pilot": {"counts": {"episodes": len(episodes)}},
        "judge_calibration": {"metrics": metrics},
    }
