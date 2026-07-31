from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_relationship_runner():
    path = PROJECT_ROOT / "evals" / "relationship_scope.py"
    spec = importlib.util.spec_from_file_location("relationship_scope_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load relationship-scope runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RelationshipScopeTests(unittest.TestCase):
    def test_runtime_includes_relationship_categories_without_category_route_out(self) -> None:
        skill = (
            PROJECT_ROOT / "skill" / "interpersonal-strategist" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for required in (
            "dating, romance, partnership, breakups, intimacy",
            "Apply romance, dating, and intimacy guidance",
            "Voluntariness-Specificity-Reversibility",
            "references/romance-dating-and-intimacy.md",
            "sexual conduct involving minors or incapacity",
            "An explicit refusal remains a refusal.",
        ):
            self.assertIn(required, skill)
        for forbidden in (
            "Do not use for romance",
            "romance belongs elsewhere",
            "ROMANCE_OUT_OF_SCOPE",
        ):
            self.assertNotIn(forbidden, skill)
        self.assertLess(len(skill), 15_000)
        self.assertLess(len(skill.splitlines()), 500)

    def test_romance_reference_and_playbooks_cover_core_lifecycle(self) -> None:
        reference = (
            PROJECT_ROOT
            / "skill"
            / "interpersonal-strategist"
            / "references"
            / "romance-dating-and-intimacy.md"
        ).read_text(encoding="utf-8")
        playbooks = (
            PROJECT_ROOT
            / "skill"
            / "interpersonal-strategist"
            / "references"
            / "scene-playbooks.md"
        ).read_text(encoding="utf-8")
        for required in (
            "Ask someone out",
            "Calibrate interest without pretending to read attraction",
            "Define the relationship instead of relying on assumptions",
            "Use consent as an ongoing interaction",
            "Decide about breakup, distance, and contact",
            "Assess reconciliation from changed conditions",
            "Account for workplace, professional, and power overlap",
            "Do not assume genders, sexual orientation, monogamy",
        ):
            self.assertIn(required, reference)
        for number in range(21, 28):
            self.assertIn(f"## {number}.", playbooks)

    def test_invocation_and_substantive_routes_are_inclusive_and_risk_based(self) -> None:
        invocation = json.loads(
            (PROJECT_ROOT / "evals" / "invocation.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("ROMANCE_OUT_OF_SCOPE", invocation["labels"])
        by_id = {case["id"]: case for case in invocation["cases"]}
        self.assertEqual(by_id["I09"]["expected"], "OWN_EXPLICIT")
        self.assertEqual(by_id["I10"]["expected"], "OWN_EXPLICIT")
        self.assertEqual(by_id["I17"]["expected"], "OWN_EXPLICIT")
        self.assertEqual(by_id["I18"]["expected"], "OWN_EXPLICIT")

        routes = json.loads(
            (PROJECT_ROOT / "evals" / "substantive-routes.json").read_text(
                encoding="utf-8"
            )
        )
        by_id = {case["id"]: case for case in routes["cases"]}
        self.assertEqual(by_id["SR25"]["expected"], "IN_SCOPE")
        self.assertEqual(by_id["SR29"]["expected"], "COACH_WITH_CAUTION")
        self.assertEqual(by_id["SR30"]["expected"], "REFER_OR_ESCALATE")
        self.assertEqual(by_id["SR32"]["expected"], "REFUSE")
        self.assertEqual(by_id["SR35"]["expected"], "REFUSE")

    def test_relationship_fixture_is_valid_and_deterministic(self) -> None:
        runner = load_relationship_runner()
        self.assertEqual(runner.validate_fixture(), [])
        payload = json.loads(
            (PROJECT_ROOT / "evals" / "relationship-scope.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["case_count"], len(payload["cases"]))
        self.assertGreaterEqual(payload["case_count"], 30)
        self.assertEqual(
            {case["language"] for case in payload["cases"]},
            {"en", "zh-CN", "mixed"},
        )
        self.assertEqual(
            {case["expected_route"] for case in payload["cases"]},
            {"IN_SCOPE", "COACH_WITH_CAUTION", "REFER_OR_ESCALATE", "REFUSE"},
        )
        with tempfile.TemporaryDirectory(prefix="relationship-scope-") as raw:
            root = Path(raw)
            first = root / "first.jsonl"
            second = root / "second.jsonl"
            one = runner.prepare("skill", first)
            two = runner.prepare("skill", second)
            self.assertEqual(one["record_count"], payload["case_count"])
            self.assertEqual(one["sha256"], two["sha256"])
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertFalse(one["qualification_claim"])

    def test_rubric_keeps_only_harm_and_authority_boundaries(self) -> None:
        rubric = json.loads(
            (PROJECT_ROOT / "evals" / "rubric.json").read_text(encoding="utf-8")
        )
        gates = {gate["id"]: gate["failure"] for gate in rubric["hard_gates"]}
        self.assertNotIn("Provides substantive romance strategy", gates["authority_boundary"])
        self.assertIn("adult-minor", gates["authority_boundary"])
        self.assertIn("incapacity", gates["authority_boundary"])
        self.assertIn("sexual pressure", gates["harmful_tactic"])
        self.assertIn("withdrawal", gates["harmful_tactic"])
        self.assertIn("romance_scope", rubric["development_targets"]["no_regression_domains"])
        self.assertIn("consent_agency", rubric["development_targets"]["no_regression_domains"])

    def test_scope_change_is_governed_and_release_remains_blocked(self) -> None:
        provenance = (
            PROJECT_ROOT / "provenance" / "RELATIONSHIP_SCOPE_EXPANSION.md"
        ).read_text(encoding="utf-8")
        audit = (
            PROJECT_ROOT
            / "research"
            / "relationship-scope-expansion-audit-20260730.md"
        ).read_text(encoding="utf-8")
        for text in (provenance, audit):
            self.assertIn("d3008e2b1bc14ca1e74a8a6964dde8d4919d4954", text)
            self.assertIn("romance", text.casefold())
        qualification = json.loads(
            (PROJECT_ROOT / "release" / "qualification.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(qualification["release"], "0.10.0-rc.1")
        self.assertEqual(qualification["status"], "blocked")
        self.assertFalse(qualification["production_claim_allowed"])

    def test_ci_runs_and_exports_relationship_lane_without_source_snapshot(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python3 evals/relationship_scope.py validate", workflow)
        self.assertIn("build/relationship-scope-skill-prompts.jsonl", workflow)
        self.assertIn("build/relationship-scope-no-skill-prompts.jsonl", workflow)
        self.assertNotIn("source-snapshot.zip", workflow)


if __name__ == "__main__":
    unittest.main()
