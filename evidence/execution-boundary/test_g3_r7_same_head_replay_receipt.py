"""Adversarial exact-head replay receipt checks; never grants release authority."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from g3_r7_same_head_replay_receipt import WATCH, REQUIRED_TEST_MODULES, inspect

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
        self.cases = [
            "test_case_%d (%s.Case.test_case_%d) ... ok" % (i, module, i)
            for i, module in enumerate(sorted(REQUIRED_TEST_MODULES))
        ]
        self.rewrite(self.cases)

    def rewrite(self, cases, *, count=None, status="OK"):
        total = len(cases) if count is None else count
        self.log.write_text("\n".join(cases) + "\n\nRan %d tests in 0.1s\n\n%s\n" % (total, status))

    def check(self, sha=SHA):
        with patch("g3_r7_same_head_replay_receipt.subprocess.run") as run:
            run.return_value.stdout = SHA + "\n"
            return inspect(log=self.log, checkout=self.root, expected_sha=sha)

    def test_valid_replay_never_certifies(self):
        record = self.check()
        self.assertEqual(record["test_count"], len(REQUIRED_TEST_MODULES))
        self.assertEqual(set(record["covered_test_modules"]), REQUIRED_TEST_MODULES)
        self.assertEqual(len(record["tested_source_sha256"]), len(WATCH))
        self.assertEqual(len(record["test_case_identity_sha256"]), 64)
        for flag in ("r4_independently_administered_custody_verified",
                     "r5_all_actual_effects_covered",
                     "r6_authentic_six_reflections_verified",
                     "r7_independent_reviewer_accepted",
                     "certified_for_production", "universal_physical_protection_proved",
                     "authorizes_effect"):
            self.assertFalse(record[flag])

    def test_stale_head_rejected(self):
        with self.assertRaisesRegex(ValueError, "checkout"):
            self.check("b" * 40)

    def test_failed_replay_rejected(self):
        self.rewrite(self.cases, status="FAILED (failures=1)")
        with self.assertRaisesRegex(ValueError, "OK"):
            self.check()

    def test_success_with_hidden_traceback_rejected(self):
        self.log.write_text("ERROR: test\n" + self.log.read_text())
        with self.assertRaisesRegex(ValueError, "failure"):
            self.check()

    def test_ambiguous_duplicate_summary_rejected(self):
        self.log.write_text(self.log.read_text() + "\nRan 1 test in 0.1s\n")
        with self.assertRaisesRegex(ValueError, "summary"):
            self.check()

    def test_case_count_not_equal_summary_rejected(self):
        self.rewrite(self.cases, count=138)
        with self.assertRaisesRegex(ValueError, "case count"):
            self.check()

    def test_duplicate_case_identity_rejected(self):
        self.rewrite(self.cases + [self.cases[0]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check()

    def test_skipped_test_rejected(self):
        changed = self.cases.copy()
        changed[0] = changed[0].replace("... ok", "... skipped 'not ready'")
        self.rewrite(changed)
        with self.assertRaisesRegex(ValueError, "outcome"):
            self.check()

    def test_missing_module_rejected(self):
        self.rewrite(self.cases[:-1])
        with self.assertRaisesRegex(ValueError, "mandatory"):
            self.check()

    def test_malformed_test_output_rejected(self):
        self.rewrite(self.cases[:-1] + ["test_case_X ... ok"])
        with self.assertRaisesRegex(ValueError, "outcome"):
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
