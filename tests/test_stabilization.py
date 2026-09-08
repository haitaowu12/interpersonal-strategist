"""Synthetic infrastructure regressions. None is a model or human outcome test."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
sys.path.insert(0, str(ROOT / "scripts"))
import eval_integrity as integrity
import execute
import blind
import evidence_metrics
import verify_evidence_bundle as bundle
from test_profile_scoring import payload, dimension, load_module


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


runner = module("stabilization_runner", ROOT / "evals/run.py")
RUBRIC = json.loads((ROOT / "evals/rubric.json").read_text())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return path


def write_lines(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def manifests(directory, n=2, baseline="no-skill"):
    files = []
    for condition in ("skill", baseline):
        rows = []
        for i in range(n):
            rows.append({"run_id": f"{condition}-{i}", "case_key": f"case-{i}", "condition": condition,
                "prompt": f"{'Use $interpersonal-strategist. ' if condition == 'skill' else ''}Synthetic request {i}",
                "judge_prompt": f"Synthetic request {i}", "replicate_id": 1, "cluster_id": f"family-{i}",
                "strata": ["low_complexity", *RUBRIC["qualification_targets"]["material_advantage_required_strata"]],
                "expected_invocation": "OWN_EXPLICIT" if condition == "skill" else "NOT_OWN",
                "expected_substantive_route": "IN_SCOPE"})
        files.append(write_lines(directory / f"{condition}.jsonl", rows))
    return files


def records(plan):
    responses, judgments = [], []
    for row in plan["planned_runs"]:
        index = int(row["case_key"].split("-")[-1])
        response = {**row, "response": "Synthetic plumbing response only", "blind_id": row["run_id"]}
        responses.append(response)
        judgments.append({"run_id": row["run_id"], "case_key": row["case_key"], "condition": row["condition"],
            "blind_id": row["run_id"], "rubric_version": RUBRIC["schema_version"],
            "hard_gates": {g["id"]: False for g in RUBRIC["hard_gates"]},
            "dimensions": {d["id"]: 5 if row["condition"] == "skill" else 3 + index % 2 for d in RUBRIC["dimensions"]},
            "evidence": {"reason": "Synthetic test assertion; no semantic evaluation was run."},
            "invocation_label": row["expected_invocation"], "substantive_route": row["expected_substantive_route"],
            "pairwise_preference": "skill" if row["condition"] == "skill" else "not_scored"})
    return responses, judgments


class ScoreSafetyTests(unittest.TestCase):
    def setUp(self):
        self.score = load_module()

    def test_one_of_eight_cannot_be_a_100_headline(self):
        data = payload()
        data["dimensions"] = [dimension(f"dim{i}", weight=1, rating=5 if i == 0 else None,
                                      confidence="high" if i == 0 else "unknown") for i in range(8)]
        result = self.score.calculate(data)
        self.assertIsNone(result["decision_fit_score"])
        self.assertEqual(result["coverage_percent"], 12.5)
        self.assertEqual(result["arithmetic_only"]["scored_dimensions_score"], 100)
        self.assertEqual(result["arithmetic_only"]["full_model_bounds"], [12.5, 100])
        self.assertNotIn("strong current fit", result["interpretation"])

    def test_flag_blocks_even_full_coverage(self):
        data = payload(); data["dimensions"] = [dimension("a", weight=1, rating=5, confidence="high")]
        data["flags"] = [{"type": "safety", "status": "active", "description": "Synthetic blocker"}]
        result = self.score.calculate(data)
        self.assertEqual(result["decision_status"], "gated")
        self.assertIsNone(result["decision_fit_score"])
        self.assertEqual(result["coverage_percent"], 100)

    def test_rated_critical_unknown_still_withholds_score(self):
        data = payload(); data["dimensions"] = [dimension("a", weight=1, rating=4, confidence="low")]
        data["dimensions"][0]["unknowns"] = ["Critical condition unconfirmed"]
        self.assertEqual(self.score.calculate(data)["decision_status"], "insufficient_evidence")

    def test_noncritical_missing_remains_partial(self):
        data = payload(); data["dimensions"][-1]["decision_critical"] = False
        result = self.score.calculate(data)
        self.assertEqual(result["decision_status"], "partial")
        self.assertIsNone(result["decision_fit_score"])

    def test_complete_arithmetic_is_not_a_validated_recommendation(self):
        data = payload(); data["dimensions"] = [dimension("a", weight=1, rating=3, confidence="high")]
        result = self.score.calculate(data)
        self.assertEqual(result["decision_fit_score"], 60)
        self.assertEqual(result["arithmetic_only"]["full_model_bounds"], [60, 60])
        self.assertIn("not a prediction or recommendation", result["interpretation"])

    def test_invalid_json_types_fail_without_membership_crash(self):
        for key in ("schema_version", "mode"):
            data = payload(); data[key] = []
            with self.assertRaises(ValueError): self.score.calculate(data)
        data = payload(); data["dimensions"][0]["confidence"] = {}
        with self.assertRaises(ValueError): self.score.calculate(data)

    def test_non_boolean_criticality_and_compact_date_are_rejected(self):
        data = payload(); data["dimensions"][0]["decision_critical"] = "false"
        with self.assertRaises(ValueError): self.score.calculate(data)
        data = payload(); data["as_of"] = "20260907"
        with self.assertRaises(ValueError): self.score.calculate(data)


class EvaluationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = manifests(self.root)
        self.plan_path = self.root / "plan.json"
        self.plan = integrity.make_plan(self.files, self.plan_path)
        self.responses, self.judgments = records(self.plan)

    def summary(self, responses=None, judgments=None, plan=True):
        return runner.summarize(write_lines(self.root / "responses.jsonl", self.responses if responses is None else responses),
            write_lines(self.root / "judgments.jsonl", self.judgments if judgments is None else judgments),
            self.root / "summary.json", plan_path=self.plan_path if plan else None)

    def test_no_plan_cannot_claim_completeness(self):
        report = self.summary(plan=False)
        self.assertFalse(report["responses"]["complete"])
        self.assertEqual(report["coverage"]["status"], "unknown")
        self.assertEqual(report["pairwise"]["acceptance"]["status"], "not_evaluable")

    def test_dropped_whole_pair_remains_missing(self):
        responses = [r for r in self.responses if r["case_key"] != "case-0"]
        judgments = [r for r in self.judgments if r["case_key"] != "case-0"]
        report = self.summary(responses, judgments)
        self.assertEqual(report["coverage"]["expected"], 4)
        self.assertEqual(len(report["coverage"]["missing_run_ids"]), 2)
        self.assertFalse(report["responses"]["complete"])

    def test_failed_and_excluded_runs_remain_in_denominator(self):
        for state in ("failed", "excluded"):
            rows = copy.deepcopy(self.responses); bad = rows[0]["run_id"]
            rows[0].update(status=state, reason="Synthetic operational failure")
            report = self.summary(rows, [j for j in self.judgments if j["run_id"] != bad])
            self.assertFalse(report["coverage"]["complete"])
            self.assertTrue(report["coverage"]["all_accounted_for"])
            self.assertEqual(report["coverage"]["expected"], 4)

    def test_unplanned_and_duplicate_runs_rejected(self):
        with self.assertRaises(ValueError): integrity.reconcile(self.plan, self.responses + [self.responses[0]])
        row = {**self.responses[0], "run_id": "unplanned"}
        with self.assertRaises(ValueError): integrity.reconcile(self.plan, [row])

    def test_response_cannot_change_cluster_or_judge_prompt(self):
        for field in ("cluster_id", "judge_prompt"):
            row = {**self.responses[0], field: "changed"}
            with self.assertRaises(ValueError): integrity.reconcile(self.plan, [row])

    def test_missing_label_is_false_negative_not_dropped(self):
        judgments = copy.deepcopy(self.judgments)
        judgment = next(j for j in judgments if j["condition"] == "skill")
        del judgment["substantive_route"]
        report = self.summary(judgments=judgments)
        self.assertEqual(report["substantive_route_metrics"]["skill"]["n"], 2)
        self.assertEqual(report["substantive_route_metrics"]["skill"]["by_label"]["IN_SCOPE"]["fn"], 1)
        self.assertEqual(report["substantive_route_metrics"]["no-skill"]["accuracy"], 1)
        self.assertEqual(len(report["missing_classification_labels"]), 1)
        self.assertFalse(report["judgments"]["complete"])

    def test_boundary_safe_interval(self):
        self.assertAlmostEqual(integrity.exact_binomial_lower(30, 30), 0.05 ** (1 / 30), places=12)
        self.assertLess(integrity.exact_binomial_lower(30, 30), 0.906)
        self.assertEqual(integrity.exact_binomial_lower(0, 30), 0)
        self.assertIsNone(integrity.exact_binomial_lower(0, 0))
        for k in range(1, 30):
            self.assertGreater(integrity.exact_binomial_lower(k + 1, 30), integrity.exact_binomial_lower(k, 30))
        with self.assertRaises(ValueError): integrity.exact_binomial_lower(True, 2)

    def test_repeated_language_variants_are_not_independent_trials(self):
        result = integrity.preference_statistics(["skill"] * 30, ["same-family"] * 30)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["raw_pairs"], 30)
        self.assertEqual(result["skill_win_rate_one_sided_95_lower_bound"], 0.05)

    def test_ties_and_conflicting_family_votes(self):
        result = integrity.preference_statistics(["skill", "no-skill", "tie"], ["a", "a", "b"])
        self.assertEqual(result["tie"], 2)
        self.assertIsNone(result["skill_win_rate_one_sided_95_lower_bound"])

    def test_plan_is_reproducible_and_qualification_requires_identity(self):
        first = self.plan_path.read_bytes()
        integrity.make_plan(self.files, self.plan_path)
        self.assertEqual(first, self.plan_path.read_bytes())
        with self.assertRaises(ValueError): integrity.make_plan(self.files, self.plan_path, purpose="qualification")

    def test_new_baselines_keep_the_same_neutral_judge_prompt(self):
        prompts = []
        for condition in ("skill", "short-prompt", "context-only", "context-playbook"):
            path = self.root / f"prepared-{condition}.jsonl"
            runner.prepare(condition, path)
            prompts.append([(r["case_key"], r["judge_prompt"]) for r in integrity.jsonl(path)])
        self.assertTrue(all(rows == prompts[0] for rows in prompts))

    def test_fully_synthetic_comparison_can_exercise_pass_branch(self):
        files = manifests(self.root, 40)
        plan = integrity.make_plan(files, self.plan_path)
        responses, judgments = records(plan)
        report = self.summary(responses, judgments)
        self.assertEqual(report["pairwise"]["acceptance"]["status"], "pass")
        self.assertFalse(report["qualification_claim"])
        self.assertEqual(report["pairwise"]["total"], 40)


class RunnerAndBlindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = manifests(self.root)
        self.plan_path = self.root / "plan.json"
        self.plan = integrity.make_plan(self.files, self.plan_path)
        self.output = self.root / "responses.jsonl"
        self.command = [sys.executable, "-c", 'import json,sys; x=json.load(sys.stdin); print(json.dumps({"response":"Synthetic adapter response", "receipt":{"synthetic":True}}))']

    def test_dry_run_never_invokes_adapter(self):
        with patch.object(execute, "invoke", side_effect=AssertionError("invoked")):
            report = execute.execute(self.plan_path, self.files, self.output, self.command)
        self.assertEqual(report["status"], "dry_run")
        self.assertFalse(self.output.exists())

    def test_bounded_execution_and_resume(self):
        first = execute.execute(self.plan_path, self.files, self.output, self.command, allow_execution=True, max_runs=1)
        self.assertEqual(first["completed"], 1)
        second = execute.execute(self.plan_path, self.files, self.output, self.command, allow_execution=True, max_runs=10)
        self.assertEqual(second["completed"], 3)
        self.assertEqual(len(integrity.jsonl(self.output)), 4)
        integrity.reconcile(self.plan, integrity.jsonl(self.output))

    def test_failure_stops_and_never_logs_stderr(self):
        command = [sys.executable, "-c", 'import sys; print("SYNTHETIC_SECRET",file=sys.stderr);sys.exit(1)']
        report = execute.execute(self.plan_path, self.files, self.output, command, allow_execution=True)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["remaining"], 3)
        self.assertNotIn("SYNTHETIC_SECRET", self.output.read_text())

    def test_timeout_output_cap_and_invalid_argv(self):
        with self.assertRaisesRegex(ValueError, "timeout"):
            execute.invoke([sys.executable, "-c", "import time; time.sleep(5)"], {}, timeout=0.05, limit=1000)
        with self.assertRaisesRegex(ValueError, "limit"):
            execute.invoke([sys.executable, "-c", "print('x'*20000)"], {}, timeout=2, limit=1000)
        with self.assertRaises(ValueError): execute.invoke("echo not argv", {}, timeout=1, limit=1000)

    def test_manifest_tampering_rejected_before_execution(self):
        self.files[0].write_text(self.files[0].read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "frozen plan"):
            execute.execute(self.plan_path, self.files, self.output, self.command)

    def test_blinding_roundtrip_and_stale_rubric_rejection(self):
        responses, judgments = records(self.plan)
        write_lines(self.output, responses)
        destination = self.root / "blind"
        blind.prepare(self.plan_path, self.output, destination)
        packets = integrity.jsonl(destination / "judge-packets.jsonl")
        self.assertTrue(all("condition" not in row and "run_id" not in row for row in packets))
        mapping = json.loads((destination / "mapping-private.json").read_text())
        original = {j["run_id"]: j for j in judgments}
        pointwise = [{**original[r["run_id"]], "blind_id": r["blind_id"]} for r in mapping["rows"]]
        pairs = [{"pair_id": r["pair_id"], "winner": "tie"} for r in mapping["pairs"]]
        pw = write_lines(self.root / "pointwise.jsonl", pointwise)
        pair_file = write_lines(self.root / "pairwise.jsonl", pairs)
        out = self.root / "judgments.jsonl"
        blind.unblind(destination / "mapping-private.json", pw, pair_file, out, "2.4")
        report = runner.summarize(destination / "canonical-responses.jsonl", out, self.root / "summary.json", plan_path=self.plan_path)
        self.assertTrue(report["coverage"]["complete"])
        self.assertEqual(report["pairwise"]["tie"], 2)
        pointwise[0]["rubric_version"] = "2.3"; write_lines(pw, pointwise)
        with self.assertRaisesRegex(ValueError, "rubric"):
            blind.unblind(destination / "mapping-private.json", pw, pair_file, out, "2.4")

    def test_incomplete_responses_cannot_be_blinded(self):
        responses, _ = records(self.plan); write_lines(self.output, responses[:1])
        with self.assertRaisesRegex(ValueError, "complete"):
            blind.prepare(self.plan_path, self.output, self.root / "blind")


class ArtifactVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_actual_bytes_verified_and_tamper_rejected(self):
        data = self.root / "receipt.txt"; data.write_text("synthetic receipt")
        index = write_json(self.root / "index.json", {"schema_version": "1.0", "artifacts": {"receipt": {"path": data.name, "sha256": bundle.sha256(data)}}})
        self.assertIn("receipt", bundle.verify_artifacts(index)[1])
        data.write_text("tampered")
        with self.assertRaisesRegex(ValueError, "hash mismatch"): bundle.verify_artifacts(index)

    def test_paths_and_symlinks_cannot_escape_bundle(self):
        for name in ("../outside", "/tmp/outside", "C:/outside", "folder\\file"):
            with self.assertRaises(ValueError): bundle.safe_file(self.root, name)
        target = self.root / "target"; target.write_text("data")
        (self.root / "link").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlinks"): bundle.safe_file(self.root, "link")

    def test_missing_actual_artifacts_block_qualification(self):
        with patch.dict(os.environ, {"INTERPERSONAL_EVIDENCE_INDEX": ""}):
            errors = bundle.qualification_bundle_errors(ROOT, {"status": "qualified"})
        self.assertIn("actual evidence bytes", errors[0])

    def test_package_matches_actual_runtime_then_rejects_stale_source(self):
        from package import build_archive
        import shutil
        archive, _, manifest = build_archive()
        bundle.verify_package(archive, manifest, ROOT)
        copied = self.root / "project"
        shutil.copytree(ROOT / "skill", copied / "skill")
        target = copied / "skill/interpersonal-strategist/SKILL.md"
        target.write_text(target.read_text() + "\nChanged runtime\n")
        with self.assertRaisesRegex(ValueError, "current runtime"):
            bundle.verify_package(archive, manifest, copied)

    def test_kappa_does_not_accept_constant_labels(self):
        self.assertEqual(evidence_metrics.kappa([(True, True), (False, False)]), 1)
        self.assertEqual(evidence_metrics.kappa([(True, False), (False, True)]), -1)
        with self.assertRaises(ValueError): evidence_metrics.kappa([(True, True)] * 10)

    def test_policy_contracts_and_pending_capability_matrix(self):
        root = ROOT / "skill/interpersonal-strategist"
        methods = (root / "references/method-contracts.md").read_text()
        self.assertNotIn("persistent third-party profile, guaranteed", methods)
        self.assertIn("profiles-and-scoring.md", methods)
        capabilities = json.loads((ROOT / "release/host-capabilities.json").read_text())
        self.assertFalse(capabilities["persistent_adapter_enabled"])
        self.assertEqual(capabilities["default_mode"], "session-only")
        self.assertTrue(all(v["status"] == "not_verified" for v in capabilities["hosts"][0]["capabilities"].values()))


def synthetic_bundle(root):
    """Create consistent private test bytes, never evidence about users or a model."""
    import shutil
    from package import build_archive
    from build_provenance import build_provenance
    from test_project import make_qualified_manifest
    qualification = make_qualified_manifest(ROOT)
    archive, _, manifest = build_archive()
    build_path = root / "build.json"
    build = build_provenance(build_path, environment={})
    subject = {"commit": build["checkout_sha"], "package_sha256": bundle.sha256(archive),
               "model_snapshot": "SYNTHETIC_TEST_ONLY", "host_version": "SYNTHETIC_TEST_ONLY", "rubric_version": "2.4"}
    qualification.update(qualification_commit=subject["commit"], qualification_tree_sha=build["checkout_tree_sha"],
                         package_sha256=subject["package_sha256"], model_snapshot=subject["model_snapshot"], host_version=subject["host_version"])
    files = manifests(root, 40)
    plan_path = root / "plan.json"
    plan = integrity.make_plan(files, plan_path, subject=subject, purpose="qualification")
    responses, judgments = records(plan)
    blind.prepare(plan_path, write_lines(root / "raw.jsonl", responses), root / "blind")
    canonical = integrity.jsonl(root / "blind/canonical-responses.jsonl")
    by_id = {r["run_id"]: r for r in canonical}
    for judgment in judgments:
        judgment["blind_id"] = by_id[judgment["run_id"]]["blind_id"]
    judgment_path = write_lines(root / "judgments.jsonl", judgments)
    summary = runner.summarize(root / "blind/canonical-responses.jsonl", judgment_path, root / "summary.json", plan_path=plan_path)
    paths = {"package": root / "package.zip", "package_manifest": root / "package-manifest.json",
        "build_provenance": build_path, "run_plan": plan_path, "skill_prompt_manifest": files[0],
        "no_skill_prompt_manifest": files[1], "blinding_manifest": root / "blind/mapping-private.json",
        "responses": root / "blind/canonical-responses.jsonl", "judgments": judgment_path}
    shutil.copyfile(archive, paths["package"]); shutil.copyfile(manifest, paths["package_manifest"])
    source_ids = [s["id"] for s in json.loads((ROOT / "provenance/evidence-sources.json").read_text())["sources"]]
    paths["source_resolution"] = write_json(root / "sources.json", {"schema_version": "1.0", "mode": "online", "status": "pass",
        "registry_errors": [], "registry_sha256": bundle.sha256(ROOT / "provenance/evidence-sources.json"),
        "sources": [{"id": sid, "status": "pass", "test_fixture_only": True} for sid in source_ids]})
    safety = qualification["gates"]["adversarial_safety_holdouts"]["required_strata"]
    cases = [{"case_id": f"h{i}", "family_id": f"family-h{i}", "strata": ["general", "multi_actor", "bilingual_mixed", safety[i % len(safety)], safety[(i + 1) % len(safety)]]} for i in range(160)]
    results = [{"case_id": c["case_id"], "status": "completed", "reviewer_id": "SYNTHETIC_TEST_ONLY",
                "hard_gates": {g["id"]: False for g in RUBRIC["hard_gates"]}} for c in cases]
    for role, key, data in (("holdout_set", "cases", cases), ("holdout_results", "results", results)):
        paths[role] = write_json(root / f"{role}.json", {"schema_version": "1.0", "subject": subject, key: data})
    paths["bilingual_review"] = write_json(root / "bilingual.json", {"schema_version": "1.0", "subject": subject,
        "expected_item_ids": ["zh", "mixed"], "ratings": [{"item_id": item, "reviewer_id": reviewer, "naturalness": 4}
                                                      for item in ("zh", "mixed") for reviewer in ("mock-a", "mock-b")]})
    episodes = [{"episode_id": f"episode{i}", "consented": True, "eligible_adult": True, "status": "completed",
                 "followup_status": "completed", "unresolved_adverse_event": False} for i in range(10)]
    paths["pilot_evidence"] = write_json(root / "pilot.json", {"schema_version": "1.0", "subject": subject,
        "expected_episode_ids": [e["episode_id"] for e in episodes], "episodes": episodes})
    calibration = []
    for i, label in enumerate(("IN_SCOPE", "COACH_WITH_CAUTION", "REFER_OR_ESCALATE", "REFUSE")):
        calibration.append({"rating_id": f"route{i}", "kind": "route", "human_a": label, "human_b": label})
    for i in range(4):
        value = bool(i % 2)
        calibration.append({"rating_id": f"hard{i}", "kind": "hard_gate", "human_a": value, "human_b": value,
                            "adjudicated_failure": value, "automated_failure": value})
        calibration.append({"rating_id": f"subjective{i}", "kind": "subjective", "human_a": i + 1, "human_b": i + 1})
    paths["judge_calibration"] = write_json(root / "calibration.json", {"schema_version": "1.0", "subject": subject, "ratings": calibration})
    paths["host_receipt"] = write_json(root / "host.json", {"subject": subject, "observations": [
        {"operation": operation, "status": "pass", "evidence": "SYNTHETIC_TEST_ONLY"} for operation in
        ("discovery", "explicit_invocation", "reference_reads", "quick_mode", "ask_wait_update", "stop")]})
    for role in ("reference_trace", "independent_release_review"):
        paths[role] = write_json(root / f"{role}.json", {"subject": subject, "observations": ["SYNTHETIC_TEST_ONLY"]})
    reviews = evidence_metrics.recompute_reviews(paths, qualification, subject, RUBRIC)
    pw = summary["pairwise"]
    reviews["calibrated_no_skill_comparison"] = {"counts": {"non_tied_pairs": pw["non_tied"], "total_pairs": pw["total"], "hard_failures": 0},
        "metrics": {"non_tied_proportion": pw["non_tied_proportion"], "skill_win_rate_lower_bound": pw["skill_win_rate_one_sided_95_lower_bound"],
                    "low_complexity_lower_bound": pw["low_complexity_noninferiority"]["paired_usability_difference_one_sided_95_lower_bound"]}}
    gate_roles = {}
    support = {role: bundle.sha256(path) for role, path in paths.items()}
    for gate_id, gate in qualification["gates"].items():
        evidence = gate["evidence"]
        for key, value in reviews.get(gate_id, {}).items(): evidence[key] = value
        evidence.update(subject_commit=subject["commit"], package_sha256=subject["package_sha256"])
        receipt = {"schema_version": "1.0", "gate_id": gate_id, "subject": subject, "protocol_version": "1.0", "result": "pass",
            "counts": evidence["counts"], "metrics": evidence["metrics"], "supporting_artifacts": support,
            "reviewer_role": "SYNTHETIC_TEST_ONLY", "reviewed_at": "2026-09-07"}
        role = "receipt-" + gate_id
        paths[role] = write_json(root / f"{role}.json", receipt)
        gate_roles[gate_id] = role
        evidence["artifact_sha256"] = bundle.sha256(paths[role])
    declared = qualification["evidence_bundle"]
    for field in list(declared):
        role = field.removesuffix("_sha256")
        if role in paths: declared[field] = bundle.sha256(paths[role])
    declared.update(qualification_commit=subject["commit"], qualification_tree_sha=build["checkout_tree_sha"], package_sha256=subject["package_sha256"])
    index = write_json(root / "index.json", {"schema_version": "1.0", "subject": subject, "gate_receipts": gate_roles,
        "artifacts": {role: {"path": path.relative_to(root).as_posix(), "sha256": bundle.sha256(path)} for role, path in paths.items()}})
    return index, qualification, paths


class FullEvidenceBundleTests(unittest.TestCase):
    def test_consistent_synthetic_bytes_exercise_verifier_without_promoting_repo(self):
        with tempfile.TemporaryDirectory() as raw:
            index, qualification, paths = synthetic_bundle(Path(raw))
            result = bundle.verify_bundle(index, qualification)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["comparison"]["total_pairs"], 40)
            self.assertEqual(json.loads((ROOT / "release/qualification.json").read_text())["status"], "blocked")
            # Update all hashes/receipt declarations, but falsify the derived count.
            gate = qualification["gates"]["calibrated_no_skill_comparison"]["evidence"]
            gate["counts"]["non_tied_pairs"] += 1
            role = "receipt-calibrated_no_skill_comparison"
            receipt = json.loads(paths[role].read_text()); receipt["counts"] = gate["counts"]
            write_json(paths[role], receipt)
            gate["artifact_sha256"] = bundle.sha256(paths[role])
            idx = json.loads(index.read_text()); idx["artifacts"][role]["sha256"] = bundle.sha256(paths[role]); write_json(index, idx)
            with self.assertRaisesRegex(ValueError, "recomputation"):
                bundle.verify_bundle(index, qualification)

    def test_review_denominators_and_partial_language_review_fail_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            index, qualification, paths = synthetic_bundle(Path(raw))
            subject = json.loads(index.read_text())["subject"]
            holdout = json.loads(paths["holdout_results"].read_text())
            saved = copy.deepcopy(holdout); holdout["results"].pop(); write_json(paths["holdout_results"], holdout)
            with self.assertRaisesRegex(ValueError, "coverage"):
                evidence_metrics.recompute_reviews(paths, qualification, subject, RUBRIC)
            write_json(paths["holdout_results"], saved)
            bilingual = json.loads(paths["bilingual_review"].read_text()); bilingual["ratings"].pop(); write_json(paths["bilingual_review"], bilingual)
            with self.assertRaisesRegex(ValueError, "two reviewers"):
                evidence_metrics.recompute_reviews(paths, qualification, subject, RUBRIC)


if __name__ == "__main__":
    unittest.main()
