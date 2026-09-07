from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from package import build_archive, distributable_files
from build_provenance import build_provenance
from smoke_install import run_smoke
from validate import (
    REQUIRED_EVIDENCE_BUNDLE_HASHES,
    validate_repository,
    validate_skill_dir,
    version_to_pep440,
)


def load_eval_runner():
    path = PROJECT_ROOT / "evals" / "run.py"
    spec = importlib.util.spec_from_file_location("test_eval_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load eval runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_project(target: Path) -> Path:
    destination = target / "interpersonal-strategist"
    shutil.copytree(
        PROJECT_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", "*.pyc"),
    )
    return destination


def make_qualified_manifest(project: Path) -> dict:
    path = project / "release" / "qualification.json"
    qualification = json.loads(path.read_text(encoding="utf-8"))
    commit = "a" * 40
    package_sha = "b" * 64
    qualification.update(
        {
            "status": "qualified",
            "production_claim_allowed": True,
            "release_scope": {
                "status": "frozen",
                "surfaces": ["codex-desktop-personal-agent-skills"],
            },
            "qualification_commit": commit,
            "qualification_tree_sha": "e" * 40,
            "package_sha256": package_sha,
            "model_snapshot": "test-model",
            "host_version": "test-host",
            "unresolved_hard_failures": [],
            "evidence_bundle": {
                **{field: "c" * 64 for field in REQUIRED_EVIDENCE_BUNDLE_HASHES},
                "qualification_commit": commit,
                "qualification_tree_sha": "e" * 40,
                "package_sha256": package_sha,
                "rubric_version": "2.3",
                "judge_protocol_version": "1.0",
                "harness_version": "evals/run.py@0.11.0-rc.1",
            },
        }
    )
    common_evidence = {
        "schema_version": "1.0",
        "subject_commit": commit,
        "package_sha256": package_sha,
        "artifact_sha256": "d" * 64,
        "protocol_version": "1.0",
        "result": "pass",
        "location": "access-controlled://qualification/test",
        "counts": {},
        "metrics": {},
    }
    for gate_id, gate in qualification["gates"].items():
        gate["status"] = "passed"
        gate["evidence"] = json.loads(json.dumps(common_evidence))
        counts = gate["evidence"]["counts"]
        metrics = gate["evidence"]["metrics"]
        if gate_id == "calibrated_no_skill_comparison":
            counts.update({"non_tied_pairs": 60, "total_pairs": 100, "hard_failures": 0})
            metrics.update(
                {
                    "non_tied_proportion": 0.6,
                    "skill_win_rate_lower_bound": 0.55,
                    "low_complexity_lower_bound": -0.02,
                }
            )
        elif gate_id == "independent_untouched_holdouts":
            counts.update(
                {
                    "general": 60,
                    "multi_actor": 30,
                    "bilingual_mixed": 30,
                    "hard_failures": 0,
                }
            )
        elif gate_id == "adversarial_safety_holdouts":
            counts.update(
                {
                    "unique_cases": 150,
                    "compound_cases": 30,
                    "hard_failures": 0,
                    "maximum_strata_credit_observed": 3,
                    "strata": {
                        stratum: 12 for stratum in gate["required_strata"]
                    },
                }
            )
        elif gate_id == "bilingual_fluent_review":
            counts["reviewers"] = 2
            metrics["median_naturalness"] = 4
        elif gate_id == "judge_calibration":
            metrics.update(
                {
                    "route_and_hard_gate_agreement": 0.8,
                    "subjective_agreement": 0.67,
                    "hard_failure_false_negative_rate": 0.04,
                }
            )
        elif gate_id == "privacy_safe_controlled_pilot":
            counts["episodes"] = 10
    return qualification


class ProjectTests(unittest.TestCase):
    def test_repository_validation(self) -> None:
        self.assertEqual(validate_repository(PROJECT_ROOT), [])

    def test_release_candidate_pep440_conversion(self) -> None:
        self.assertEqual(version_to_pep440("0.11.0-rc.1"), "0.11.0rc1")
        self.assertEqual(version_to_pep440("1.2.3-alpha.4"), "1.2.3a4")
        self.assertEqual(version_to_pep440("1.2.3-beta.2"), "1.2.3b2")
        self.assertEqual(version_to_pep440("1.2.3"), "1.2.3")

    def test_clean_install_from_source(self) -> None:
        result = run_smoke()
        self.assertEqual(result["status"], "pass", result)

    def test_package_is_reproducible_and_installable(self) -> None:
        archive_one, _, manifest_one = build_archive()
        first_bytes = archive_one.read_bytes()
        first_sha = hashlib.sha256(first_bytes).hexdigest()

        archive_two, _, manifest_two = build_archive()
        second_bytes = archive_two.read_bytes()
        second_sha = hashlib.sha256(second_bytes).hexdigest()

        self.assertEqual(first_sha, second_sha)
        self.assertEqual(manifest_one.read_bytes(), manifest_two.read_bytes())

        with zipfile.ZipFile(archive_two) as zf:
            names = zf.namelist()
        self.assertTrue(names)
        self.assertTrue(
            all(name.startswith("interpersonal-strategist/") for name in names)
        )
        self.assertIn("interpersonal-strategist/PACKAGE_MANIFEST.json", names)
        self.assertIn("interpersonal-strategist/LICENSE", names)
        self.assertIn("interpersonal-strategist/NOTICE.md", names)
        self.assertFalse(any("__pycache__" in name for name in names))
        self.assertFalse(any(name.endswith((".pyc", ".pyo")) for name in names))
        self.assertIn(
            "interpersonal-strategist/references/deep-context-elicitation.md",
            names,
        )
        self.assertIn(
            "interpersonal-strategist/references/memory-and-continuity.md",
            names,
        )

        self.assertIn(
            "interpersonal-strategist/references/romance-dating-and-intimacy.md",
            names,
        )
        self.assertIn(
            "interpersonal-strategist/references/profiles-and-scoring.md",
            names,
        )
        self.assertIn(
            "interpersonal-strategist/scripts/profile_score.py",
            names,
        )
        self.assertIn(
            "interpersonal-strategist/assets/profile-score-template.json",
            names,
        )
        self.assertNotIn("README.md", names)
        self.assertNotIn("provenance/evidence-sources.json", names)
        self.assertNotIn("release/qualification.json", names)
        self.assertFalse(any(name.startswith("interpersonal-strategist/evals/") for name in names))

        result = run_smoke(archive_two)
        self.assertEqual(result["status"], "pass", result)

    def test_generated_python_cache_is_not_validated_or_packaged(self) -> None:
        source = PROJECT_ROOT / "skill" / "interpersonal-strategist"
        with tempfile.TemporaryDirectory(prefix="interpersonal-cache-") as raw:
            target = Path(raw) / "interpersonal-strategist"
            shutil.copytree(source, target)
            cache = target / "scripts" / "__pycache__"
            cache.mkdir(parents=True, exist_ok=True)
            artifact = cache / "profile_score.cpython-313.pyc"
            artifact.write_bytes(b"\x00\r\n\xffgenerated")
            self.assertEqual(validate_skill_dir(target), [])
            included = {
                path.relative_to(target) for path in distributable_files(target)
            }
        self.assertNotIn(
            Path("scripts/__pycache__/profile_score.cpython-313.pyc"), included
        )

    def test_build_provenance_binds_checkout_tree_and_package(self) -> None:
        archive, _, manifest = build_archive()
        checkout_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        with tempfile.TemporaryDirectory(prefix="interpersonal-provenance-") as raw:
            output = Path(raw) / "build-provenance.json"
            payload = build_provenance(
                output,
                environment={
                    "CANDIDATE_SHA": checkout_sha,
                    "GITHUB_SHA": "f" * 40,
                    "GITHUB_EVENT_NAME": "pull_request",
                    "GITHUB_RUN_ID": "123",
                },
            )
        self.assertEqual(payload["candidate_sha"], checkout_sha)
        self.assertEqual(payload["checkout_sha"], checkout_sha)
        self.assertEqual(payload["release_zip_sha256"], hashlib.sha256(archive.read_bytes()).hexdigest())
        self.assertEqual(
            payload["release_manifest_sha256"],
            hashlib.sha256(manifest.read_bytes()).hexdigest(),
        )

    def test_validator_rejects_machine_specific_path(self) -> None:
        source = PROJECT_ROOT / "skill" / "interpersonal-strategist"
        with tempfile.TemporaryDirectory(prefix="interpersonal-validator-") as raw:
            target = Path(raw) / "interpersonal-strategist"
            shutil.copytree(source, target)
            reference = target / "references" / "evidence-and-readiness.md"
            reference.write_text(
                reference.read_text(encoding="utf-8")
                + "\nPrivate path: /Users/tony/example\n",
                encoding="utf-8",
            )
            errors = validate_skill_dir(target)
        self.assertTrue(any("machine-specific user path" in item for item in errors))

    def test_validator_rejects_release_metadata_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            notice = project / "skill" / "interpersonal-strategist" / "NOTICE.md"
            notice.write_text(
                notice.read_text(encoding="utf-8").replace((project / "VERSION").read_text().strip(), "0.7.0-alpha.2"),
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertTrue(
            any("NOTICE.md does not contain current VERSION" in item for item in errors),
            errors,
        )

    def test_validator_rejects_evidence_author_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            registry_path = project / "provenance" / "evidence-sources.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["sources"][0]["first_author"] = "IncorrectAuthor"
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertTrue(
            any("does not contain first author" in item for item in errors), errors
        )

    def test_qualified_manifest_rejects_pending_gates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            path = project / "release" / "qualification.json"
            qualification = json.loads(path.read_text(encoding="utf-8"))
            qualification.update(
                {
                    "status": "qualified",
                    "production_claim_allowed": True,
                    "qualification_commit": "a" * 40,
                    "package_sha256": "b" * 64,
                    "model_snapshot": "test-model",
                    "host_version": "test-host",
                }
            )
            path.write_text(
                json.dumps(qualification, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertTrue(
            any("non-passing gates" in item for item in errors), errors
        )

    def test_complete_qualified_manifest_satisfies_evidence_schema(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            path = project / "release" / "qualification.json"
            qualification = make_qualified_manifest(project)
            path.write_text(
                json.dumps(qualification, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertEqual(errors, [])

    def test_validator_rejects_truthy_untyped_gate_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            path = project / "release" / "qualification.json"
            qualification = make_qualified_manifest(project)
            qualification["gates"]["static_repository_ci"]["evidence"] = "looks good"
            path.write_text(
                json.dumps(qualification, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertTrue(any("requires an evidence object" in item for item in errors), errors)

    def test_validator_rejects_missing_qualification_bundle_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            path = project / "release" / "qualification.json"
            qualification = make_qualified_manifest(project)
            del qualification["evidence_bundle"]["responses_sha256"]
            path.write_text(
                json.dumps(qualification, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertTrue(
            any("evidence_bundle requires responses_sha256" in item for item in errors),
            errors,
        )

    def test_eval_fixture_counts_match(self) -> None:
        count_fields = {
            "cases.json": ("case_count", "cases"),
            "deep-context-memory.json": ("case_count", "cases"),
            "invocation.json": ("case_count", "cases"),
            "substantive-routes.json": ("case_count", "cases"),
            "multi-actor.json": ("case_count", "cases"),
            "relationship-norms.json": ("case_count", "cases"),
            "ai-mediated.json": ("case_count", "cases"),
            "trust-reliance.json": ("case_count", "cases"),
            "speech-acts.json": ("case_count", "cases"),
            "profile-scoring.json": ("case_count", "cases"),
            "bilingual-parity.json": ("pair_count", "pairs"),
            "metamorphic.json": ("pair_count", "pairs"),
        }
        for filename, (count_field, items_field) in count_fields.items():
            payload = json.loads((PROJECT_ROOT / "evals" / filename).read_text())
            self.assertEqual(payload[count_field], len(payload[items_field]), filename)

    def test_adaptive_depth_and_memory_contract_is_locked(self) -> None:
        skill = (
            PROJECT_ROOT / "skill" / "interpersonal-strategist" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for required in (
            "**QUICK**",
            "**DEEP_CONTEXT**",
            "**AUTO**",
            "**CONFIRM_EACH**",
            "memory off",
            "Situation Memory Card",
            "references/deep-context-elicitation.md",
            "references/memory-and-continuity.md",
        ):
            self.assertIn(required, skill)

        payload = json.loads(
            (PROJECT_ROOT / "evals" / "deep-context-memory.json").read_text()
        )
        self.assertGreaterEqual(payload["case_count"], 20)
        ids = {case["id"] for case in payload["cases"]}
        self.assertTrue({"DM03", "DM04", "DM06", "DM10", "DM14", "DM20"} <= ids)

    def test_new_roleplay_nonverbal_and_memory_hard_gates_are_locked(self) -> None:
        rubric = json.loads((PROJECT_ROOT / "evals" / "rubric.json").read_text())
        gate_ids = {gate["id"] for gate in rubric["hard_gates"]}
        self.assertIn("nonverbal_inference", gate_ids)
        self.assertIn("simulation_leakage", gate_ids)
        self.assertIn("covert_test", gate_ids)
        self.assertIn("memory_abuse", gate_ids)
        self.assertIn("score_abuse", gate_ids)
        dimension_ids = {dimension["id"] for dimension in rubric["dimensions"]}
        self.assertIn("simulation_control", dimension_ids)
        self.assertIn("profile_scoring", dimension_ids)
        self.assertEqual(rubric["schema_version"], "2.3")

    def test_validator_rejects_stale_rubric_version_reference(self) -> None:
        with tempfile.TemporaryDirectory(prefix="interpersonal-project-") as raw:
            project = copy_project(Path(raw))
            protocol = project / "evals" / "judge-protocol.md"
            protocol.write_text(
                protocol.read_text(encoding="utf-8").replace(
                    '"rubric_version": "2.3"',
                    '"rubric_version": "2.0"',
                ),
                encoding="utf-8",
            )
            errors = validate_repository(project)
        self.assertTrue(
            any("rubric_version references" in item for item in errors),
            errors,
        )

    def test_ci_uses_exact_pull_request_head_for_candidate_artifacts(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "CANDIDATE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}",
            workflow,
        )
        self.assertIn("ref: ${{ env.CANDIDATE_SHA }}", workflow)
        self.assertIn(
            "name: interpersonal-strategist-${{ env.CANDIDATE_SHA }}",
            workflow,
        )
        self.assertIn(
            "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
            workflow,
        )
        self.assertIn(
            "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
            workflow,
        )
        self.assertIn(
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            workflow,
        )
        self.assertIn("build/build-provenance.json", workflow)

    def test_waza_lane_is_secondary_and_not_packaged(self) -> None:
        required = {
            "README.md",
            "eval.yaml",
            "trigger_tests.yaml",
            "tasks/explicit-invocation.yaml",
            "tasks/coercion-refusal.yaml",
            "tasks/nonverbal-inference.yaml",
            "tasks/roleplay-state.yaml",
            "tasks/micro-feedback.yaml",
            "tasks/distributed-information.yaml",
            "tasks/facilitation-method.yaml",
            "tasks/bilingual-boundary.yaml",
        }
        root = PROJECT_ROOT / "evals" / "waza"
        actual = {
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file()
        }
        self.assertTrue(required.issubset(actual), required - actual)

        qualification = json.loads(
            (PROJECT_ROOT / "release" / "qualification.json").read_text()
        )
        self.assertNotIn("secondary_waza_cross_executor", qualification["gates"])
        secondary = qualification["secondary_evidence"]["waza_cross_executor"]
        self.assertEqual(secondary["status"], "optional_pending")
        self.assertIn("cannot replace a required gate", secondary["nonclaim"])

    def test_eval_runner_validates_and_prepares_deterministically(self) -> None:
        runner = load_eval_runner()
        self.assertEqual(runner.validate_fixtures(), [])
        with tempfile.TemporaryDirectory(prefix="interpersonal-evals-") as raw:
            first = Path(raw) / "first.jsonl"
            second = Path(raw) / "second.jsonl"
            result_one = runner.prepare("skill", first)
            result_two = runner.prepare("skill", second)
            self.assertEqual(result_one["sha256"], result_two["sha256"])
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertGreaterEqual(result_one["record_count"], 156)

    def test_eval_summarizer_rejects_incomplete_judgments(self) -> None:
        runner = load_eval_runner()
        rubric = json.loads((PROJECT_ROOT / "evals" / "rubric.json").read_text())
        gate_ids = [gate["id"] for gate in rubric["hard_gates"]]
        dimension_ids = [dimension["id"] for dimension in rubric["dimensions"]]
        response = {
            "run_id": "run-1",
            "case_key": "cases:test",
            "condition": "skill",
            "response": "A bounded response.",
            "blind_id": "blind-1",
            "strata": ["low_complexity"],
        }
        incomplete = {
            "run_id": "run-1",
            "case_key": "cases:test",
            "condition": "skill",
            "blind_id": "blind-1",
            "rubric_version": "2.3",
            "hard_gates": {},
            "dimensions": {dimension_id: 3 for dimension_id in dimension_ids},
            "evidence": {"summary": "Observable reason."},
            "pairwise_preference": "not_scored",
        }
        complete = {
            **incomplete,
            "hard_gates": {gate_id: False for gate_id in gate_ids},
        }
        with self.assertRaisesRegex(ValueError, "every canonical gate"):
            runner.validate_result_records([response], [incomplete], rubric)
        responses_by_run, judgments_by_run = runner.validate_result_records(
            [response], [complete], rubric
        )
        self.assertEqual(set(responses_by_run), {"run-1"})
        self.assertEqual(set(judgments_by_run), {"run-1"})

    def test_eval_summarizer_requires_complete_pairs_and_reports_not_evaluable(self) -> None:
        runner = load_eval_runner()
        rubric = json.loads((PROJECT_ROOT / "evals" / "rubric.json").read_text())
        gates = {gate["id"]: False for gate in rubric["hard_gates"]}
        dimensions = {dimension["id"]: 4 for dimension in rubric["dimensions"]}
        responses = [
            {
                "run_id": f"run-{condition}",
                "case_key": "cases:paired",
                "condition": condition,
                "response": f"{condition} response",
                "blind_id": f"blind-{condition}",
                "strata": ["low_complexity"],
            }
            for condition in ("skill", "no-skill")
        ]
        judgments = [
            {
                "run_id": f"run-{condition}",
                "case_key": "cases:paired",
                "condition": condition,
                "blind_id": f"blind-{condition}",
                "rubric_version": "2.3",
                "hard_gates": gates,
                "dimensions": dimensions,
                "evidence": {"summary": "Observable reason."},
                "pairwise_preference": (
                    "skill" if condition == "skill" else "not_scored"
                ),
            }
            for condition in ("skill", "no-skill")
        ]
        with tempfile.TemporaryDirectory(prefix="interpersonal-summary-") as raw:
            root = Path(raw)
            responses_path = root / "responses.jsonl"
            judgments_path = root / "judgments.jsonl"
            output = root / "summary.json"
            responses_path.write_text(
                "".join(json.dumps(item) + "\n" for item in responses),
                encoding="utf-8",
            )
            judgments_path.write_text(
                "".join(json.dumps(item) + "\n" for item in judgments),
                encoding="utf-8",
            )
            summary = runner.summarize(responses_path, judgments_path, output)
        self.assertEqual(summary["pairwise"]["skill"], 1)
        self.assertEqual(summary["pairwise"]["acceptance"]["status"], "not_evaluable")
        self.assertEqual(summary["schema_version"], "2.0")


if __name__ == "__main__":
    unittest.main()
