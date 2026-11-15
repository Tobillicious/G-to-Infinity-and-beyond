"""Negative controls for the non-certifying G3 evidence inventory."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from release_evidence import REQUIRED, inspect

COMMIT = "b1910b23cb3c3bd4b8ad47f4e7e5b228cc94fae3"


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.packet = {"schema": "g3-evidence-inventory-v1",
                       "source_commit": COMMIT, "evidence": {}}
        for key in REQUIRED:
            data = key.encode()
            (self.root / (key + ".txt")).write_bytes(data)
            self.packet["evidence"][key] = {
                "path": key + ".txt",
                "sha256": hashlib.sha256(data).hexdigest(),
                "reviewer": "unverified-test-metadata",
                "reviewed_commit": COMMIT}

    def test_complete_inventory_does_not_certify(self):
        result = inspect(self.packet, self.root)
        self.assertTrue(result["ready_for_independent_review"])
        self.assertFalse(result["certified_for_production"])
        self.assertFalse(result["universal_physical_protection_proved"])

    def test_missing_x3_category_denied(self):
        del self.packet["evidence"]["original_six_x3_correspondence"]
        self.assertFalse(inspect(self.packet, self.root)["ready_for_independent_review"])

    def test_changed_bytes_denied(self):
        (self.root / "crash_recovery.txt").write_text("different")
        self.assertIn("crash_recovery:content_mismatch",
                      inspect(self.packet, self.root)["errors"])

    def test_stale_commit_denied(self):
        self.packet["evidence"]["emergency_revocation"]["reviewed_commit"] = "b" * 40
        self.assertIn("emergency_revocation:unreviewed_or_stale",
                      inspect(self.packet, self.root)["errors"])

    def test_unsafe_paths_denied(self):
        item = self.packet["evidence"]["signed_effect_boundary"]
        item["path"] = "../escape"
        self.assertIn("signed_effect_boundary:unsafe_path",
                      inspect(self.packet, self.root)["errors"])
        item["path"] = "symlink"
        (self.root / "symlink").symlink_to(self.root / "crash_recovery.txt")
        self.assertIn("signed_effect_boundary:missing_or_unsafe_file",
                      inspect(self.packet, self.root)["errors"])

    def test_duplicate_path_denied(self):
        a = self.packet["evidence"]["crash_recovery"]["path"]
        self.packet["evidence"]["emergency_revocation"]["path"] = a
        self.assertFalse(inspect(self.packet, self.root)["ready_for_independent_review"])

    def test_actual_format_git_commit_and_sha256_are_separate(self):
        self.assertEqual(len(COMMIT), 40)
        self.assertTrue(inspect(self.packet, self.root)["ready_for_independent_review"])
        self.packet["source_commit"] = "a" * 64
        self.assertIn("source_commit_invalid",
                      inspect(self.packet, self.root)["errors"])

    def test_nested_symlink_alias_is_rejected(self):
        real = self.root / "real"
        real.mkdir()
        (real / "document.txt").write_bytes(b"claimed")
        alias = self.root / "alias"
        alias.symlink_to(real, target_is_directory=True)
        key = "signed_effect_boundary"
        item = self.packet["evidence"][key]
        item["path"] = "alias/document.txt"
        item["sha256"] = hashlib.sha256(b"claimed").hexdigest()
        self.assertIn(key + ":missing_or_unsafe_file",
                      inspect(self.packet, self.root)["errors"])

    def test_bad_schema_denied(self):
        self.packet["evidence"]["crash_recovery"] = None
        self.assertIn("crash_recovery:schema", inspect(self.packet, self.root)["errors"])


if __name__ == "__main__":
    unittest.main()
