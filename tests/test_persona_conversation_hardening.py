from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_persona_runner():
    path = PROJECT_ROOT / "evals" / "persona_conversation.py"
    spec = importlib.util.spec_from_file_location(
        "persona_conversation_regression_runner",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load persona conversation runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PersonaConversationHardeningTests(unittest.TestCase):
    def test_skill_contract_locks_transcript_and_lens_safeguards(self) -> None:
        path = PROJECT_ROOT / "skill" / "interpersonal-strategist" / "SKILL.md"
        skill = path.read_text(encoding="utf-8")
        for required in (
            "Analyze chats, emails, and screenshots as interaction evidence",
            "An explicit refusal remains a refusal.",
            "Use perspective lenses without impersonation",
            "Numerical scoring requires a bounded decision",
            "Profiles are visible, scoped, correctable, versioned, expirable, and deletable",
            "references/profiles-and-scoring.md",
            "references/pragmatics-and-digital-channels.md",
            "**QUICK**",
            "**DEEP_CONTEXT**",
            "**AUTO**",
            "**CONFIRM_EACH**",
            "memory off",
            "Situation Memory Card",
        ):
            self.assertIn(required, skill)
        self.assertLess(len(skill), 17_000)
        self.assertLess(len(skill.splitlines()), 500)

    def test_pragmatics_reference_preserves_observable_boundaries(self) -> None:
        path = (
            PROJECT_ROOT
            / "skill"
            / "interpersonal-strategist"
            / "references"
            / "pragmatics-and-digital-channels.md"
        )
        reference = path.read_text(encoding="utf-8")
        for required in (
            "Conversation Evidence Table",
            "Refusal and consent invariant",
            "Separate receipt, understanding, agreement, and commitment",
            "`收到`",
            "`可以`",
            "`回头看`",
            "`没事`",
            "truthful face-preserving communication",
            "source-bounded perspective lenses",
            "Do not convert these low-specificity inputs alone into a numerical intent",
            "Do not use latency to infer attraction, status, power",
            "A user correction changes the record.",
        ):
            self.assertIn(required, reference)

    def test_persona_regression_fixture_is_valid_and_deterministic(self) -> None:
        runner = load_persona_runner()
        self.assertEqual(runner.validate_fixture(), [])
        payload = json.loads(
            (PROJECT_ROOT / "evals" / "persona-conversation-regressions.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["case_count"], len(payload["cases"]))
        self.assertGreaterEqual(payload["case_count"], 30)
        self.assertEqual(
            {case["language"] for case in payload["cases"]},
            {"en", "zh-CN", "mixed"},
        )
        ids = {case["id"] for case in payload["cases"]}
        self.assertTrue(
            {
                "PC02",
                "PC05",
                "PC08",
                "PC10",
                "PC15",
                "PC21",
                "PC27",
                "PC29",
                "PC30",
                "PC31",
            }
            <= ids
        )
        with tempfile.TemporaryDirectory(prefix="persona-conversation-evals-") as raw:
            root = Path(raw)
            first = root / "first.jsonl"
            second = root / "second.jsonl"
            one = runner.prepare("skill", first)
            two = runner.prepare("skill", second)
            self.assertEqual(one["record_count"], payload["case_count"])
            self.assertEqual(one["sha256"], two["sha256"])
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertFalse(one["qualification_claim"])

    def test_rubric_names_rejected_donor_mechanics(self) -> None:
        rubric = json.loads(
            (PROJECT_ROOT / "evals" / "rubric.json").read_text(encoding="utf-8")
        )
        gates = {gate["id"]: gate["failure"] for gate in rubric["hard_gates"]}
        self.assertIn("construct, anchors, weights", gates["fabrication"])
        self.assertIn("human worth", gates["score_abuse"])
        self.assertIn("low-specificity cues", gates["score_abuse"])
        self.assertIn("refusal or consent override", gates["harmful_tactic"])
        self.assertIn("compliance or sunk-cost ladder", gates["harmful_tactic"])
        self.assertIn("pressure-point", gates["memory_abuse"])
        self.assertIn("transcript", gates["memory_abuse"])
        self.assertIn("avatar", gates["nonverbal_inference"])
        self.assertIn("strategic response delay", gates["covert_test"])
        self.assertNotIn("Provides substantive romance strategy", gates["authority_boundary"])
        self.assertEqual(rubric["schema_version"], "2.3")

    def test_donor_records_are_exact_and_license_scoped(self) -> None:
        donor_record = (
            PROJECT_ROOT / "provenance" / "PERSONA_CONVERSATION_DONORS.md"
        ).read_text(encoding="utf-8")
        audit = (
            PROJECT_ROOT
            / "research"
            / "persona-and-conversation-systems-audit-20260730.md"
        ).read_text(encoding="utf-8")
        for commit in (
            "7648d7be53926a9441f47170ec2254d6f383c941",
            "c9caaa9a6576f581c29d016c60bbe935908e20d5",
            "0bc7fb6f8da1767d43bb9ac14c243b693357a332",
            "27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7",
            "47039d08fcf0330794caea14efdb5e183348f7bb",
            "93f5c7c0a5d7091ce45ce1343ab4bfad662a0c19",
            "9deb1a87b1231fec85cadf2ef690fa49fef519ca",
            "21e6aa9c72a03a5456eeb4cd63234a2fa2935387",
        ):
            self.assertIn(commit, donor_record)
        self.assertIn("does not grant a blanket license", donor_record)
        self.assertIn("No donor prose, prompts, formulas, examples", donor_record)
        audit_lower = audit.lower()
        self.assertIn("content sufficiency", audit_lower)
        self.assertIn("production qualification remains blocked", audit_lower)

    def test_ci_runs_and_exports_the_regression_lane(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python3 evals/persona_conversation.py validate", workflow)
        self.assertIn(
            "--output build/persona-conversation-skill-prompts.jsonl", workflow
        )
        self.assertIn(
            "--output build/persona-conversation-no-skill-prompts.jsonl", workflow
        )
        self.assertIn("build/persona-conversation-skill-prompts.jsonl", workflow)
        self.assertIn("build/persona-conversation-no-skill-prompts.jsonl", workflow)


if __name__ == "__main__":
    unittest.main()
