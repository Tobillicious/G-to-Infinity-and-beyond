"""Test exact-head bounded R7 replay receipts without issuing review authority."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from g3_r7_same_head_replay_receipt import WATCH, inspect

SHA = "a" * 40

class ExactHeadReplayReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        modules = self.root / "evidence" / "execution-boundary"
        modules.mkdir(parents=True)
        for name in WATCH:
            (modules / name).write_text("reviewed source " + name)
        self.log = self.root / "replay.txt"
        self.log.write_text("test_x ... ok\n\nRan 138 tests in 50.051s\n\nOK\n")

    def check(self, sha=SHA):
        with patch("g3_r7_same_head_replay_receipt.subprocess.run") as run:
            run.return_value.stdout = SHA + "\n"
            return inspect(log=self.log, checkout=self.root, expected_sha=sha)

    def test_valid_replay_never_certifies(self):
        record = self.check()
        self.assertEqual(record["test_count"], 138)
        self.assertEqual(len(record["tested_source_sha256"]), len(WATCH))
        for flag in ("r4_independently_administered_custody_verified",
                     "r5_all_actual_effects_covered",
                     "r6_authentic_six_reflections_verified",
                     "r7_independent_reviewer_accepted",
                     "certified_for_production", "authorizes_effect"):
            self.assertIs(record[flag], False)

    def test_stale_head_rejected(self):
        with self.assertRaisesRegex(ValueError, "checkout"):
            self.check("b" * 40)

    def test_failed_replay_rejected(self):
        self.log.write_text("Ran 138 tests in 1.0s\n\nFAILED (failures=1)\n")
        with self.assertRaisesRegex(ValueError, "OK"):
            self.check()

    def test_success_with_hidden_traceback_rejected(self):
        self.log.write_text("ERROR: test\nRan 138 tests in 1.0s\n\nOK\n")
        with self.assertRaisesRegex(ValueError, "failure"):
            self.check()

    def test_ambiguous_duplicate_summary_rejected(self):
        self.log.write_text("Ran 138 tests in 1.0s\nRan 1 test in 0.1s\nOK\n")
        with self.assertRaisesRegex(ValueError, "summary"):
            self.check()

    def test_symlinked_source_rejected(self):
        p = self.root / "evidence" / "execution-boundary" / WATCH[0]
        p.unlink()
        p.symlink_to(self.log)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.check()

    def test_invalid_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, "exact commit"):
            self.check("not-a-commit")

if __name__ == "__main__":
    unittest.main()
