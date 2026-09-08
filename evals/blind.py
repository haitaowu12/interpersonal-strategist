#!/usr/bin/env python3
"""Prepare shuffled judge packets and reconcile human/adapter judgments.

Keep the mapping and canonical responses private. Masked labels are not proof
that a judge cannot infer a condition from prose. Evaluate order/verbosity bias.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from eval_integrity import digest, jsonl, reconcile


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def prepare(plan_path: Path, responses_path: Path, destination: Path, seed: int = 20260907) -> dict:
    plan = json.loads(plan_path.read_text())
    rows, coverage = reconcile(plan, jsonl(responses_path))
    if not coverage["complete"]:
        raise ValueError("blinding requires complete planned responses, with no failed or excluded runs")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("blinding destination must be empty; do not overwrite an issued mapping")
    destination.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    rng.shuffle(rows)
    canonical, packets, groups = [], [], defaultdict(list)
    for number, row in enumerate(rows, 1):
        blind_id = f"B{number:05d}"
        canonical.append({**row, "blind_id": blind_id})
        packets.append({"blind_id": blind_id, "prompt": row.get("judge_prompt", ""), "response": row["response"]})
        groups[(row["case_key"], row.get("replicate_id", 1))].append(blind_id)
    pairs = []
    for number, (_, ids) in enumerate(sorted(groups.items()), 1):
        if len(ids) != 2:
            raise ValueError("prepare one two-condition comparison lane at a time")
        rng.shuffle(ids)
        pairs.append({"pair_id": f"P{number:05d}", "left": ids[0], "right": ids[1]})
    rng.shuffle(pairs)
    write_jsonl(destination / "judge-packets.jsonl", packets)
    write_jsonl(destination / "judge-pairs.jsonl", pairs)
    write_jsonl(destination / "canonical-responses.jsonl", canonical)
    mapping = {"schema_version": "1.0", "seed": seed, "plan_sha256": digest(plan_path),
               "input_responses_sha256": digest(responses_path),
               "canonical_responses_sha256": digest(destination / "canonical-responses.jsonl"),
               "pairs": pairs, "rows": [{k: r[k] for k in ("blind_id", "run_id", "case_key", "condition", "replicate_id")} for r in canonical],
               "nonclaim": "Randomized labels and order, not guaranteed semantic blinding or judge calibration."}
    (destination / "mapping-private.json").write_text(json.dumps(mapping, indent=2) + "\n")
    return {"status": "prepared", "responses": len(rows), "pairs": len(pairs), "seed": seed}


def unblind(mapping_path: Path, pointwise_path: Path, pairwise_path: Path, output: Path,
            rubric_version: str, trace_audit_path: Path | None = None) -> dict:
    mapping = json.loads(mapping_path.read_text())
    if mapping.get("schema_version") != "1.0" or not isinstance(mapping.get("rows"), list):
        raise ValueError("unsupported blinding mapping")
    by_blind = {r["blind_id"]: r for r in mapping["rows"]}
    if len(by_blind) != len(mapping["rows"]) or len({r["run_id"] for r in mapping["rows"]}) != len(by_blind):
        raise ValueError("duplicate blinding identity")
    traces = {}
    for audit in jsonl(trace_audit_path) if trace_audit_path else []:
        rid = audit.get("run_id")
        if rid in traces or rid not in {r["run_id"] for r in mapping["rows"]}:
            raise ValueError("duplicate or unknown trace audit run")
        if not audit.get("evidence") or audit.get("invocation_label") not in {"OWN_EXPLICIT", "NOT_OWN", "DELEGATE_WRITING", "DELEGATE_TRANSLATION"}:
            raise ValueError("trace audit requires label and observable evidence")
        traces[rid] = audit
    pointwise = jsonl(pointwise_path)
    judgments = {}
    for row in pointwise:
        blind_id = row.get("blind_id")
        if blind_id not in by_blind or blind_id in judgments:
            raise ValueError("unknown or duplicate pointwise blind_id")
        if row.get("rubric_version") != rubric_version:
            raise ValueError("pointwise judgment rubric version mismatch")
        # Identity is reconstructed only from the private map, never judge guesses.
        judgments[blind_id] = {**row, **by_blind[blind_id], "rubric_version": rubric_version,
                               "pairwise_preference": "not_scored"}
    if set(judgments) != set(by_blind):
        raise ValueError("missing pointwise judgments")
    for blind_id, judgment in judgments.items():
        audit = traces.get(judgment["run_id"])
        if audit:
            judgment["invocation_label"] = audit["invocation_label"]
            judgment.setdefault("evidence", {})["invocation_trace"] = audit["evidence"]
    pairs = {r["pair_id"]: r for r in mapping["pairs"]}
    members = [p[key] for p in pairs.values() for key in ("left", "right")]
    if len(pairs) != len(mapping["pairs"]) or len(members) != len(set(members)) or set(members) != set(by_blind):
        raise ValueError("blinding pairs must cover each response exactly once")
    for pair in pairs.values():
        a, b = by_blind[pair["left"]], by_blind[pair["right"]]
        if a["case_key"] != b["case_key"] or a["condition"] == b["condition"] or a["replicate_id"] != b["replicate_id"]:
            raise ValueError("blinding pairs must compare matching cases across conditions")
    seen = set()
    for row in jsonl(pairwise_path):
        pid, winner = row.get("pair_id"), row.get("winner")
        if pid not in pairs or pid in seen or winner not in {"left", "right", "tie"}:
            raise ValueError("unknown, duplicate, or invalid pairwise judgment")
        seen.add(pid); pair = pairs[pid]
        preference = "tie" if winner == "tie" else by_blind[pair[winner]]["condition"]
        judgments[pair["left"]]["pairwise_preference"] = preference
    if seen != set(pairs):
        raise ValueError("missing pairwise judgments")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output, list(judgments.values()))
    return {"status": "reconciled", "judgments": len(judgments), "output_sha256": digest(output)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--plan", type=Path, required=True)
    prep.add_argument("--responses", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--seed", type=int, default=20260907)
    undo = sub.add_parser("unblind")
    undo.add_argument("--mapping", type=Path, required=True)
    undo.add_argument("--pointwise", type=Path, required=True)
    undo.add_argument("--pairwise", type=Path, required=True)
    undo.add_argument("--output", type=Path, required=True)
    undo.add_argument("--rubric-version", required=True)
    undo.add_argument("--trace-audit", type=Path)
    args = parser.parse_args()
    try:
        report = (prepare(args.plan, args.responses, args.output, args.seed) if args.command == "prepare"
                  else unblind(args.mapping, args.pointwise, args.pairwise, args.output, args.rubric_version, args.trace_audit))
        print(json.dumps(report, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)})); return 1


if __name__ == "__main__":
    raise SystemExit(main())
