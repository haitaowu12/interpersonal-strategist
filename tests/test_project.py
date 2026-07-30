from __future__ import annotations

import hashlib
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

from package import build_archive
from smoke_install import run_smoke
from validate import validate_repository, validate_skill_dir


class ProjectTests(unittest.TestCase):
    def test_repository_validation(self) -> None:
        self.assertEqual(validate_repository(PROJECT_ROOT), [])

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
        self.assertTrue(all(name.startswith("interpersonal-strategist/") for name in names))
        self.assertIn("interpersonal-strategist/PACKAGE_MANIFEST.json", names)
        self.assertIn("interpersonal-strategist/LICENSE", names)
        self.assertIn("interpersonal-strategist/NOTICE.md", names)
        self.assertNotIn("README.md", names)

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

    def test_eval_case_counts_match(self) -> None:
        for filename in ("cases.json", "routing.json"):
            payload = json.loads((PROJECT_ROOT / "evals" / filename).read_text())
            self.assertEqual(payload["case_count"], len(payload["cases"]))


if __name__ == "__main__":
    unittest.main()
