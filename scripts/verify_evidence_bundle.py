#!/usr/bin/env python3
"""Verify actual qualification bytes and recompute the planned comparison.

The private bundle stays outside the skill/package. Hashes establish identity,
not truth, reviewer competence, independence, or research efficacy.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROLES = {
    "package", "package_manifest", "build_provenance", "run_plan",
    "skill_prompt_manifest", "no_skill_prompt_manifest", "blinding_manifest",
    "responses", "judgments", "source_resolution", "holdout_set", "holdout_results",
    "bilingual_review", "pilot_evidence", "independent_release_review", "judge_calibration",
    "host_receipt", "reference_trace",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_file(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("artifact path must be a relative POSIX path")
    parts = PurePosixPath(name)
    if parts.is_absolute() or ".." in parts.parts or ":" in name:
        raise ValueError("artifact path escapes bundle")
    path = root
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("artifact symlinks are not permitted")
    if not path.is_file():
        raise ValueError(f"missing artifact: {name}")
    path.resolve().relative_to(root.resolve())
    return path


def verify_artifacts(index_path: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    index = read_json(index_path)
    if index.get("schema_version") != "1.0":
        raise ValueError("unsupported evidence-index schema")
    entries = index.get("artifacts")
    if not isinstance(entries, dict) or not entries:
        raise ValueError("evidence index requires artifacts")
    paths = {}
    for role, entry in entries.items():
        if not isinstance(entry, dict):
            raise ValueError(f"invalid artifact descriptor: {role}")
        path = safe_file(index_path.parent, entry.get("path"))
        actual = sha256(path)
        if actual != entry.get("sha256"):
            raise ValueError(f"artifact hash mismatch: {role}")
        paths[role] = path
    return index, paths


def verify_package(package: Path, manifest_path: Path, project_root: Path) -> None:
    manifest = read_json(manifest_path)
    if manifest.get("archive_sha256") != sha256(package):
        raise ValueError("package manifest archive hash mismatch")
    expected = {}
    for item in manifest.get("files", []):
        if not isinstance(item, dict) or item.get("path") in expected:
            raise ValueError("invalid or duplicate package manifest member")
        expected[item["path"]] = item
    if not expected:
        raise ValueError("empty package manifest")
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected) | {"interpersonal-strategist/PACKAGE_MANIFEST.json"}:
            raise ValueError("package contents do not match manifest")
        if sum(i.file_size for i in archive.infolist()) > 10_000_000:
            raise ValueError("unexpected package size")
        for name, item in expected.items():
            if not name.startswith("interpersonal-strategist/") or ".." in PurePosixPath(name).parts:
                raise ValueError("unsafe package member")
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != item.get("sha256") or len(data) != item.get("bytes"):
                raise ValueError("package member hash/size mismatch")
            relative = name.removeprefix("interpersonal-strategist/")
            source = safe_file(project_root / "skill/interpersonal-strategist", relative)
            if source.read_bytes() != data:
                raise ValueError(f"package does not match current runtime: {relative}")
        internal = json.loads(archive.read("interpersonal-strategist/PACKAGE_MANIFEST.json"))
        if internal.get("files") != manifest.get("files") or internal.get("version") != manifest.get("version"):
            raise ValueError("internal package manifest mismatch")
    root = project_root / "skill/interpersonal-strategist"
    source_names = {"interpersonal-strategist/" + p.relative_to(root).as_posix()
                    for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                    and p.suffix not in {".pyc", ".pyo"} and p.name != "PACKAGE_MANIFEST.json"}
    if source_names != set(expected):
        raise ValueError("package omits or adds runtime files")


def verify_bundle(index_path: Path, qualification: dict[str, Any], *, project_root: Path = ROOT) -> dict[str, Any]:
    index, paths = verify_artifacts(index_path)
    missing = REQUIRED_ROLES - set(paths)
    if missing:
        raise ValueError("missing required artifact roles: " + ", ".join(sorted(missing)))
    if qualification.get("status") != "qualified" or qualification.get("production_claim_allowed") is not True:
        raise ValueError("production verification requires a qualified candidate declaration; pending gates remain blocked")
    subject = index.get("subject", {})
    expected_subject = {"commit": qualification.get("qualification_commit"),
        "package_sha256": qualification.get("package_sha256"),
        "model_snapshot": qualification.get("model_snapshot"), "host_version": qualification.get("host_version"),
        "rubric_version": qualification.get("rubric_version")}
    if any(not value or subject.get(key) != value for key, value in expected_subject.items()):
        raise ValueError("evidence index subject does not match qualification")
    if sha256(paths["package"]) != subject["package_sha256"]:
        raise ValueError("subject package hash mismatch")
    declared = qualification.get("evidence_bundle")
    if not isinstance(declared, dict):
        raise ValueError("qualification requires evidence_bundle")
    for field, value in declared.items():
        if field.endswith("_sha256") and field.removesuffix("_sha256") in paths:
            if value != sha256(paths[field.removesuffix("_sha256")]):
                raise ValueError(f"declared evidence hash differs from actual bytes: {field}")
    verify_package(paths["package"], paths["package_manifest"], project_root)
    build = read_json(paths["build_provenance"])
    if (build.get("candidate_sha") != subject["commit"] or build.get("checkout_sha") != subject["commit"]
            or build.get("release_zip_sha256") != subject["package_sha256"]
            or build.get("release_manifest_sha256") != sha256(paths["package_manifest"])
            or build.get("checkout_tree_sha") != qualification.get("qualification_tree_sha")
            or build.get("working_tree_clean") is not True):
        raise ValueError("build provenance does not bind a clean candidate tree and package")
    plan = read_json(paths["run_plan"])
    if plan.get("purpose") != "qualification" or plan.get("subject") != expected_subject:
        raise ValueError("comparison plan must bind the exact qualification subject")
    for role in ("skill_prompt_manifest", "no_skill_prompt_manifest"):
        if sha256(paths[role]) not in {m["sha256"] for m in plan.get("manifests", [])}:
            raise ValueError(f"run plan does not bind {role}")
    spec = importlib.util.spec_from_file_location("bundle_eval_runner", project_root / "evals/run.py")
    if spec is None or spec.loader is None:
        raise ValueError("evaluation runner cannot be loaded")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    with tempfile.TemporaryDirectory(prefix="interpersonal-verify-") as temporary:
        rebuilt = runner.make_plan([paths["skill_prompt_manifest"], paths["no_skill_prompt_manifest"]],
            Path(temporary) / "rebuilt.json", subject=expected_subject, purpose="qualification",
            seed=plan.get("execution_order_seed", 20260907))
        by_id = lambda rows: {r["run_id"]: r for r in rows}
        if by_id(rebuilt["planned_runs"]) != by_id(plan["planned_runs"]):
            raise ValueError("run plan does not match actual prompt manifests")
        mapping = read_json(paths["blinding_manifest"])
        if (mapping.get("plan_sha256") != sha256(paths["run_plan"])
                or mapping.get("canonical_responses_sha256") != sha256(paths["responses"])):
            raise ValueError("blinding map does not bind plan and canonical responses")
        response_ids = {r["blind_id"]: r["run_id"] for r in runner.read_jsonl(paths["responses"])}
        mapped_ids = {r["blind_id"]: r["run_id"] for r in mapping.get("rows", [])}
        if response_ids != mapped_ids or len(mapped_ids) != len(mapping.get("rows", [])):
            raise ValueError("blinding identity coverage mismatch")
        summary = runner.summarize(paths["responses"], paths["judgments"], Path(temporary) / "summary.json", plan_path=paths["run_plan"])
    if (not summary["coverage"]["complete"] or not summary["judgments"]["complete"]
            or summary["pairwise"]["acceptance"]["status"] != "pass"):
        raise ValueError("recomputed planned comparison does not meet acceptance")

    source_report = read_json(paths["source_resolution"])
    registry = read_json(project_root / "provenance/evidence-sources.json")
    source_ids = {s["id"] for s in registry["sources"]}
    observed = source_report.get("sources", [])
    if (source_report.get("mode") != "online" or source_report.get("status") != "pass"
            or source_report.get("registry_errors") != []
            or source_report.get("registry_sha256") != sha256(project_root / "provenance/evidence-sources.json")
            or len(observed) != len(source_ids) or {s.get("id") for s in observed} != source_ids
            or any(s.get("status") != "pass" for s in observed)):
        raise ValueError("online source-resolution evidence is incomplete or stale")
    host = read_json(paths["host_receipt"])
    required_operations = {"discovery", "explicit_invocation", "reference_reads", "quick_mode", "ask_wait_update", "stop"}
    capabilities = read_json(project_root / "release/host-capabilities.json")
    if capabilities.get("persistent_adapter_enabled"):
        required_operations.update({"scoped_read", "scoped_write", "inspect", "correct", "expire", "export", "delete"})
    observations = host.get("observations", [])
    if host.get("subject") != expected_subject or not isinstance(observations, list):
        raise ValueError("host observation subject mismatch")
    by_operation = {o["operation"]: o for o in observations}
    if len(by_operation) != len(observations) or not required_operations <= set(by_operation):
        raise ValueError("host operation coverage is incomplete")
    if any(by_operation[o].get("status") != "pass" or not by_operation[o].get("evidence") for o in required_operations):
        raise ValueError("host operations require observed passing evidence")
    reference_trace = read_json(paths["reference_trace"])
    if reference_trace.get("subject") != expected_subject or not reference_trace.get("observations"):
        raise ValueError("reference trace requires exact-subject observations")
    gate_support = {
        "static_repository_ci": {"build_provenance"},
        "deterministic_package_and_layout": {"package", "package_manifest"},
        "evidence_registry_parity": {"source_resolution"},
        "online_source_resolution": {"source_resolution"},
        "clean_host_discovery_and_invocation": {"host_receipt"},
        "reference_selection_and_compound_overlays": {"reference_trace"},
        "calibrated_no_skill_comparison": {"run_plan", "responses", "judgments", "blinding_manifest"},
        "independent_untouched_holdouts": {"holdout_set", "holdout_results"},
        "adversarial_safety_holdouts": {"holdout_set", "holdout_results"},
        "bilingual_fluent_review": {"bilingual_review"},
        "judge_calibration": {"judge_calibration"},
        "privacy_safe_controlled_pilot": {"pilot_evidence"},
        "independent_release_review": {"independent_release_review"},
    }
    gate_roles = index.get("gate_receipts")
    if not isinstance(gate_roles, dict) or set(gate_roles) != set(qualification.get("gates", {})):
        raise ValueError("one bound receipt is required for every qualification gate")
    for gate_id, gate in qualification["gates"].items():
        role = gate_roles[gate_id]
        if gate.get("status") != "passed" or role not in paths:
            raise ValueError(f"gate not passed or receipt unavailable: {gate_id}")
        receipt = read_json(paths[role])
        if receipt.get("gate_id") != gate_id or receipt.get("subject") != expected_subject or receipt.get("result") != "pass":
            raise ValueError(f"gate receipt identity/result mismatch: {gate_id}")
        evidence = gate.get("evidence", {})
        if evidence.get("artifact_sha256") != sha256(paths[role]):
            raise ValueError(f"gate receipt bytes differ from declared evidence: {gate_id}")
        for field in ("counts", "metrics", "protocol_version"):
            if receipt.get(field) != evidence.get(field):
                raise ValueError(f"gate receipt {field} differs from declaration: {gate_id}")
        supporting = receipt.get("supporting_artifacts")
        if not isinstance(supporting, dict) or not gate_support[gate_id] <= set(supporting):
            raise ValueError(f"gate receipt needs supporting artifacts: {gate_id}")
        for support_role, expected_hash in supporting.items():
            if support_role not in paths or sha256(paths[support_role]) != expected_hash:
                raise ValueError(f"unbound supporting evidence for {gate_id}")
        if not receipt.get("reviewer_role") or not receipt.get("reviewed_at"):
            raise ValueError(f"gate receipt requires reviewer role and date: {gate_id}")
    sys.path.insert(0, str(project_root / "scripts"))
    from evidence_metrics import recompute_reviews
    review_metrics = recompute_reviews(paths, qualification, expected_subject,
                                      read_json(project_root / "evals/rubric.json"))
    for gate_id, computed in review_metrics.items():
        evidence = qualification["gates"][gate_id]["evidence"]
        for field, values in computed.items():
            if any(evidence.get(field, {}).get(key) != value for key, value in values.items()):
                raise ValueError(f"declared {gate_id} {field} differ from raw-review recomputation")
    comparison = qualification["gates"]["calibrated_no_skill_comparison"]["evidence"]
    pw = summary["pairwise"]
    actual_counts = {"non_tied_pairs": pw["non_tied"], "total_pairs": pw["total"],
                     "hard_failures": sum(f["condition"] == "skill" for f in summary["hard_gate_failures"])}
    actual_metrics = {"non_tied_proportion": pw["non_tied_proportion"],
                      "skill_win_rate_lower_bound": pw["skill_win_rate_one_sided_95_lower_bound"],
                      "low_complexity_lower_bound": pw["low_complexity_noninferiority"]["paired_usability_difference_one_sided_95_lower_bound"]}
    if any(comparison["counts"].get(k) != v for k, v in actual_counts.items()) or any(comparison["metrics"].get(k) != v for k, v in actual_metrics.items()):
        raise ValueError("declared comparative counts/metrics differ from recomputation")
    return {"status": "pass", "artifact_count": len(paths), "subject": expected_subject,
        "comparison": actual_counts, "evidence_index_sha256": sha256(index_path),
        "nonclaim": "Verified bytes, planned-run coverage, package parity, receipt consistency, comparative calculations, and review-record counts/metrics. Human review must establish source truth, reviewer independence, and applicability; this script cannot establish them."}


def qualification_bundle_errors(project_root: Path, qualification: dict[str, Any]) -> list[str]:
    if qualification.get("status") != "qualified":
        return []
    location = os.environ.get("INTERPERSONAL_EVIDENCE_INDEX")
    if not location:
        return ["qualified release requires actual evidence bytes via INTERPERSONAL_EVIDENCE_INDEX; hash declarations alone do not qualify"]
    try:
        verify_bundle(Path(location), qualification, project_root=project_root)
        return []
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        return [f"evidence bundle verification failed: {exc}"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, default=ROOT / "release/qualification.json")
    args = parser.parse_args()
    try:
        result = verify_bundle(args.index, read_json(args.qualification))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)})); return 1
    print(json.dumps(result, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
