"""Plan reconciliation and boundary-safe statistics; no model or network access."""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

CONDITIONS = {"skill", "no-skill", "short-prompt", "context-only", "context-playbook"}
PLAN_FIELDS = ("case_key", "condition", "replicate_id", "cluster_id", "strata",
               "expected_invocation", "expected_substantive_route", "prompt_sha256", "judge_prompt")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line, parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: expected object")
        rows.append(value)
    return rows


def cluster_id(row: dict[str, Any]) -> str:
    explicit = row.get("cluster_id")
    if explicit is not None:
        if not isinstance(explicit, str) or not explicit.strip():
            raise ValueError("cluster_id must be non-empty text")
        return explicit
    # Language variants of the same public source case are not independent draws.
    if row.get("source_file") and row.get("source_id"):
        return f"{row['source_file']}:{row['source_id']}"
    return str(row["case_key"])


def make_plan(manifests: list[Path], output: Path, *, subject: dict[str, str] | None = None,
              purpose: str = "development", seed: int = 20260907) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in manifests:
        for item in jsonl(path):
            prompt = item.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("planned prompt must be non-empty")
            rows.append({
                "run_id": item["run_id"], "case_key": item["case_key"],
                "condition": item["condition"], "replicate_id": item.get("replicate_id", 1),
                "cluster_id": cluster_id(item), "strata": item.get("strata", []),
                "expected_invocation": item.get("expected_invocation"),
                "expected_substantive_route": item.get("expected_substantive_route"),
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "judge_prompt": item.get("judge_prompt", prompt.removeprefix("Use $interpersonal-strategist. ")),
            })
    random.Random(seed).shuffle(rows)
    plan = {"execution_order_seed": seed, "schema_version": "1.0", "purpose": purpose, "subject": subject or {},
            "manifests": [{"name": p.name, "sha256": digest(p)} for p in manifests],
            "planned_runs": rows,
            "nonclaim": "Frozen run accounting; this does not attest independent authorship, host identity, or untouched holdouts."}
    validate_plan(plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return plan


def validate_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != "1.0" or plan.get("purpose") not in {"development", "qualification"}:
        raise ValueError("unsupported plan schema or purpose")
    if not isinstance(plan.get("subject"), dict):
        raise ValueError("plan requires a subject object")
    if plan["purpose"] == "qualification":
        for name in ("commit", "package_sha256", "model_snapshot", "host_version", "rubric_version"):
            if not isinstance(plan["subject"].get(name), str) or not plan["subject"][name].strip():
                raise ValueError(f"qualification plan requires subject.{name}")
    for name, length in (("commit", 40), ("package_sha256", 64)):
        value = plan["subject"].get(name)
        if plan["purpose"] == "qualification" and not re.fullmatch(r"[0-9a-f]{%d}" % length, str(value)):
            raise ValueError(f"invalid qualification subject.{name}")
    rows = plan.get("planned_runs")
    if not isinstance(rows, list) or not rows:
        raise ValueError("planned_runs must be a non-empty list")
    ids, identities = set(), set()
    families: dict[str, tuple[Any, ...]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("planned run must be an object")
        for name in ("run_id", "case_key", "cluster_id", "prompt_sha256"):
            if not isinstance(row.get(name), str) or not row[name].strip():
                raise ValueError(f"planned run requires {name}")
        if row.get("condition") not in CONDITIONS:
            raise ValueError("unknown planned condition")
        rep = row.get("replicate_id")
        if type(rep) is not int or rep < 1:
            raise ValueError("replicate_id must be a positive integer")
        if not isinstance(row.get("strata"), list) or any(not isinstance(s, str) or not s for s in row["strata"]):
            raise ValueError("planned strata must be a string list")
        sha = row["prompt_sha256"]
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("invalid prompt_sha256")
        if not isinstance(row.get("judge_prompt"), str) or not row["judge_prompt"].strip():
            raise ValueError("planned run requires neutral judge_prompt")
        for field, labels in (("expected_invocation", {"OWN_EXPLICIT", "NOT_OWN", "DELEGATE_WRITING", "DELEGATE_TRANSLATION"}),
                              ("expected_substantive_route", {"IN_SCOPE", "COACH_WITH_CAUTION", "REFER_OR_ESCALATE", "REFUSE"})):
            label = row.get(field)
            if label is not None and (not isinstance(label, str) or label not in labels):
                raise ValueError(f"invalid planned {field}")
        identity = (row["case_key"], row["condition"], rep)
        if row["run_id"] in ids or identity in identities:
            raise ValueError("duplicate planned run identity")
        ids.add(row["run_id"]); identities.add(identity)
        family = (row["cluster_id"], tuple(sorted(row["strata"])), row.get("expected_substantive_route"), row.get("judge_prompt"))
        if row["case_key"] in families and families[row["case_key"]] != family:
            raise ValueError("case family/strata/route must agree across conditions and replicates")
        families[row["case_key"]] = family


def reconcile(plan: dict[str, Any] | None, responses: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if plan is None:
        return responses, {"status": "unknown", "complete": False, "expected": None,
                           "observed": len(responses), "reason": "No frozen run plan supplied."}
    validate_plan(plan)
    planned = {r["run_id"]: r for r in plan["planned_runs"]}
    observed: dict[str, dict[str, Any]] = {}
    completed = []
    failures, exclusions = [], []
    for response in responses:
        run_id = response.get("run_id")
        if not isinstance(run_id, str) or run_id not in planned:
            raise ValueError(f"unplanned run_id: {run_id}")
        if run_id in observed:
            raise ValueError(f"duplicate response run_id: {run_id}")
        expected = planned[run_id]
        for name in PLAN_FIELDS:
            if name in response and response[name] != expected.get(name):
                raise ValueError(f"response {run_id}: {name} contradicts the frozen plan")
        row = {**expected, **response}
        observed[run_id] = row
        status = row.get("status", "completed")
        if status == "completed":
            completed.append(row)
        elif status in {"failed", "excluded"}:
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                raise ValueError(f"{status} run requires reason")
            (failures if status == "failed" else exclusions).append({"run_id": run_id, "reason": row["reason"]})
        else:
            raise ValueError(f"invalid run status: {status}")
    missing = sorted(set(planned) - set(observed))
    complete = not (missing or failures or exclusions)
    return completed, {"status": "complete" if complete else "incomplete", "complete": complete,
        "expected": len(planned), "observed": len(observed), "completed": len(completed),
        "missing_run_ids": missing, "failed": failures, "excluded": exclusions,
        "all_accounted_for": not missing,
        "nonclaim": "Explained failures/exclusions remain in the denominator and block automatic acceptance."}


def exact_binomial_lower(successes: int, trials: int, alpha: float = 0.05) -> float | None:
    """One-sided Clopper–Pearson lower bound, via binomial-tail inversion."""
    if type(successes) is not int or type(trials) is not int or not 0 <= successes <= trials:
        raise ValueError("expected integer 0 <= successes <= trials")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if trials == 0:
        return None
    if successes == 0:
        return 0.0
    if successes == trials:
        return alpha ** (1 / trials)
    coefficients = [(i, math.lgamma(trials + 1) - math.lgamma(i + 1) - math.lgamma(trials - i + 1))
                    for i in range(successes, trials + 1)]
    lo, hi = 0.0, 1.0
    for _ in range(64):
        p = (lo + hi) / 2
        lp, lq = math.log(p), math.log1p(-p)
        terms = [c + i * lp + (trials - i) * lq for i, c in coefficients]
        maximum = max(terms)
        tail = math.exp(maximum) * sum(math.exp(t - maximum) for t in terms)
        if tail < alpha:
            lo = p
        else:
            hi = p
    return (lo + hi) / 2


def preference_statistics(preferences: list[str], clusters: list[str] | None = None,
                          baseline: str = "no-skill") -> dict[str, Any]:
    if clusters is None:
        clusters = [str(i) for i in range(len(preferences))]
    if len(preferences) != len(clusters):
        raise ValueError("one cluster id is required per preference")
    by_cluster: dict[str, list[int]] = defaultdict(list)
    for preference, cluster in zip(preferences, clusters):
        if preference not in {"skill", baseline, "tie"}:
            raise ValueError("unknown pairwise preference")
        by_cluster[cluster].append(1 if preference == "skill" else -1 if preference == baseline else 0)
    # One predeclared family vote: language variants and repeated runs are not extra trials.
    votes = ["skill" if sum(v) > 0 else baseline if sum(v) < 0 else "tie" for v in by_cluster.values()]
    counts = Counter(votes)
    non_tied, total = counts["skill"] + counts[baseline], len(votes)
    bound = exact_binomial_lower(counts["skill"], non_tied)
    return {"skill": counts["skill"], baseline: counts[baseline], "tie": counts["tie"],
        "total": total, "non_tied": non_tied,
        "non_tied_proportion": round(non_tied / total, 6) if total else None,
        "skill_win_rate_excluding_ties": round(counts["skill"] / non_tied, 6) if non_tied else None,
        "skill_win_rate_one_sided_95_lower_bound": round(bound, 6) if bound is not None else None,
        "raw_pair_counts": dict(Counter(preferences)), "raw_pairs": len(preferences),
        "interval": {"method": "one-sided Clopper-Pearson", "confidence_level": 0.95,
                     "unit": "predeclared_cluster", "cluster_reduction": "majority of pairwise outcomes; net zero is tie",
                     "assumption": "independent sampled scenario families; excludes ties and is not a population efficacy claim"}}
