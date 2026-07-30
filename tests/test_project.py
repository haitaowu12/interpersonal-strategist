from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from package import build_archive
from smoke_install import run_smoke
from validate import validate_repository, validate_skill_dir, version_to_pep440


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


class ProjectTests(unittest.TestCase):
    def test_repository_validation(self) -> None:
        self.assertEqual(validate_repository(PROJECT_ROOT), [])

    def test_release_candidate_pep440_conversion(self) -> None:
        self.assertEqual(version_to_pep440("0.8.0-rc.1"), "0.8.0rc1")
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
        self.assertNotIn("README.md", names)
        self.assertNotIn("provenance/evidence-sources.json", names)
        self.assertNotIn("release/qualification.json", names)
        self.assertFalse(any(name.startswith("interpersonal-strategist/evals/") for name in names))

        result = run_smoke(archive_two)
        self.assertEqual(result["status"], "pass", result)

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
                notice.read_text(encoding="utf-8").replace("0.8.0-rc.1", "0.7.0-alpha.2"),
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

    def test_eval_fixture_counts_match(self) -> None:
        count_fields = {
            "cases.json": ("case_count", "cases"),
            "invocation.json": ("case_count", "cases"),
            "substantive-routes.json": ("case_count", "cases"),
            "multi-actor.json": ("case_count", "cases"),
            "relationship-norms.json": ("case_count", "cases"),
            "ai-mediated.json": ("case_count", "cases"),
            "trust-reliance.json": ("case_count", "cases"),
            "speech-acts.json": ("case_count", "cases"),
            "bilingual-parity.json": ("pair_count", "pairs"),
            "metamorphic.json": ("pair_count", "pairs"),
        }
        for filename, (count_field, items_field) in count_fields.items():
            payload = json.loads((PROJECT_ROOT / "evals" / filename).read_text())
            self.assertEqual(payload[count_field], len(payload[items_field]), filename)

    def test_new_roleplay_and_nonverbal_hard_gates_are_locked(self) -> None:
        rubric = json.loads((PROJECT_ROOT / "evals" / "rubric.json").read_text())
        gate_ids = {gate["id"] for gate in rubric["hard_gates"]}
        self.assertIn("nonverbal_inference", gate_ids)
        self.assertIn("simulation_leakage", gate_ids)
        self.assertIn("covert_test", gate_ids)
        dimension_ids = {dimension["id"] for dimension in rubric["dimensions"]}
        self.assertIn("simulation_control", dimension_ids)
        self.assertEqual(rubric["schema_version"], "2.1")

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


if __name__ == "__main__":
    unittest.main()
