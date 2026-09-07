from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    PROJECT_ROOT
    / "skill"
    / "interpersonal-strategist"
    / "scripts"
    / "profile_score.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("profile_score", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load profile score module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dimension(
    dimension_id: str,
    *,
    weight: int,
    rating: int | None,
    confidence: str | None,
) -> dict:
    return {
        "id": dimension_id,
        "label": dimension_id.replace("_", " ").title(),
        "anchor": "0 blocked; 3 mixed; 5 consistently favorable.",
        "materiality": "Changes the bounded reliance decision.",
        "weight": weight,
        "rating": rating,
        "confidence": confidence,
        "evidence": (
            [
                {
                    "summary": "Dated observation",
                    "source": "user report",
                    "date": "2026-08-10",
                }
            ]
            if rating is not None
            else []
        ),
        "counterevidence": [],
        "unknowns": [] if rating is not None else ["Missing evidence"],
        "update_condition": "Review after the next comparable event.",
    }


def payload() -> dict:
    return {
        "schema_version": "1.0",
        "profile_id": "case-a",
        "profile_version": 2,
        "purpose": "Assess reliance for the next shared commitment.",
        "as_of": "2026-08-10",
        "review_or_expiry": "After the next shared commitment.",
        "mode": "session-only",
        "sensitive_exclusions": ["Raw private transcripts"],
        "dimensions": [
            dimension("reliability", weight=3, rating=4, confidence="high"),
            dimension("repair", weight=2, rating=3, confidence="moderate"),
            dimension("constraints", weight=1, rating=None, confidence="unknown"),
        ],
        "flags": [],
    }


class ProfileScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_calculates_score_coverage_and_unknowns(self) -> None:
        result = self.module.calculate(payload())
        self.assertEqual(result["decision_fit_score"], 72)
        self.assertEqual(result["coverage_percent"], 83)
        self.assertEqual(result["unscored_dimensions"], ["constraints"])
        self.assertEqual(result["decision_status"], "scored")
        self.assertIn("not human worth", result["nonclaim"])

    def test_unknown_dimension_is_not_imputed_as_neutral(self) -> None:
        first = self.module.calculate(payload())
        changed = payload()
        changed["dimensions"][2]["rating"] = 0
        changed["dimensions"][2]["confidence"] = "low"
        changed["dimensions"][2]["evidence"] = [
            {
                "summary": "Direct blocking constraint",
                "source": "user report",
                "date": "2026-08-10",
            }
        ]
        changed["dimensions"][2]["unknowns"] = []
        second = self.module.calculate(changed)
        self.assertEqual(first["decision_fit_score"], 72)
        self.assertEqual(second["decision_fit_score"], 60)
        self.assertEqual(second["coverage_percent"], 100)

    def test_active_safety_flag_gates_score_without_erasing_it(self) -> None:
        model = payload()
        model["flags"] = [
            {
                "type": "safety",
                "status": "active",
                "description": "Repeated threat requires safety routing.",
            }
        ]
        result = self.module.calculate(model)
        self.assertEqual(result["decision_fit_score"], 72)
        self.assertEqual(result["decision_status"], "gated")
        self.assertEqual(len(result["active_flags"]), 1)

    def test_rejects_out_of_range_rating(self) -> None:
        model = payload()
        model["dimensions"][0]["rating"] = 6
        with self.assertRaisesRegex(ValueError, "rating"):
            self.module.calculate(model)

    def test_template_is_valid_and_not_calculable_until_rated(self) -> None:
        template = json.loads(
            (
                PROJECT_ROOT
                / "skill"
                / "interpersonal-strategist"
                / "assets"
                / "profile-score-template.json"
            ).read_text(encoding="utf-8")
        )
        result = self.module.calculate(template)
        self.assertIsNone(result["decision_fit_score"])
        self.assertEqual(result["coverage_percent"], 0)
        self.assertEqual(result["decision_status"], "not_calculable")

    def test_rated_dimension_requires_sourced_evidence(self) -> None:
        model = payload()
        model["dimensions"][0]["evidence"] = []
        with self.assertRaisesRegex(ValueError, "sourced item"):
            self.module.calculate(model)

    def test_cli_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="profile-score-") as raw:
            source = Path(raw) / "input.json"
            source.write_text(json.dumps(payload()), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "--input", str(source)]
            first = subprocess.run(command, check=True, capture_output=True, text=True)
            second = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(first.stdout, second.stdout)

    def test_catalog_metadata_requires_explicit_invocation(self) -> None:
        metadata = (
            PROJECT_ROOT
            / "skill"
            / "interpersonal-strategist"
            / "agents"
            / "openai.yaml"
        ).read_text(encoding="utf-8")
        skill = (
            PROJECT_ROOT / "skill" / "interpersonal-strategist" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("Use this skill only after explicit invocation", skill)

    def test_community_audit_preserves_exact_clean_room_boundary(self) -> None:
        audit = (
            PROJECT_ROOT
            / "research"
            / "scoring-dossier-community-audit-20260810.md"
        ).read_text(encoding="utf-8")
        commits = {
            "7648d7be53926a9441f47170ec2254d6f383c941",
            "c9caaa9a6576f581c29d016c60bbe935908e20d5",
            "0bc7fb6f8da1767d43bb9ac14c243b693357a332",
            "27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7",
            "47039d08fcf0330794caea14efdb5e183348f7bb",
            "93f5c7c0a5d7091ce45ce1343ab4bfad662a0c19",
            "9deb1a87b1231fec85cadf2ef690fa49fef519ca",
            "21e6aa9c72a03a5456eeb4cd63234a2fa2935387",
            "ea23b10376b146abfcff20f71876889a0453a7e7",
            "a6decc8dc1b9eb7cf04429a8babfb0b83744c5a4",
            "5d80d609059713f586b9ff5b37430c2ba7f76491",
            "251cf1d838f35b89b2447ab043f7a07ad0879c7e",
        }
        for commit in commits:
            self.assertIn(commit, audit)
        self.assertIn("No donor prompt", audit)
        self.assertIn("No donor tool was run", audit)


if __name__ == "__main__":
    unittest.main()
