"""Negative controls for independently signed rights-history checkpoints."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from external_checkpoint import DOMAIN, canonical_checkpoint, journal_snapshot, verify_checkpoint
from rights_veto import RightsVetoJournal


class ExternalCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-veto-checkpoint-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "veto.sqlite"
        self.journal = RightsVetoJournal(self.path, initialize=True)
        self.addCleanup(self.journal.close)
        self.signer = Ed25519PrivateKey.generate()
        self.other = Ed25519PrivateKey.generate()
        self.right = dict(record_ref="r1",subject="p1",action="publish",
                          effect_digest="a"*64)
        self.kw = dict(pinned_public_key=self.signer.public_key(),
                       deployment="offline-pilot-1",minimum_generation=0)

    def packet(self, key=None, **changes):
        generation,digest=journal_snapshot(self.path)
        claim=dict(domain=DOMAIN, deployment="offline-pilot-1",
                   generation=generation, digest=digest)
        claim.update(changes)
        signing_key=key or self.signer
        return {"checkpoint":claim,"signature":signing_key.sign(
            canonical_checkpoint(claim)).hex()}

    def test_matching_signature_is_not_consent_or_authorization(self):
        result=verify_checkpoint(self.path,self.packet(),**self.kw)
        self.assertTrue(result["checkpoint_matches"])
        self.assertFalse(result["authorizes_effect"])
        self.assertFalse(result["authentic_consent_proved"])
        self.assertFalse(result["original_six_x3_proved"])

    def test_older_self_consistent_rollback_detected(self):
        old=self.packet()
        self.assertTrue(self.journal.record_withdrawal(**self.right,generation=1)["ok"])
        newest=self.packet()
        self.assertEqual(verify_checkpoint(self.path,newest,**self.kw)["code"],
                         "checkpoint_matches_only")
        self.assertEqual(verify_checkpoint(self.path,old,**dict(
            self.kw,minimum_generation=1))["code"],"stale_external_checkpoint")
        self.assertEqual(verify_checkpoint(self.path,old,**self.kw)["code"],
                         "journal_checkpoint_mismatch")

    def test_restored_older_valid_database_rejected_by_newer_checkpoint(self):
        # Snapshot the genuinely valid generation-zero SQLite database using
        # the SQLite backup API (not a brittle copy of an active WAL file).
        backup_path = self.path.parent / "before-withdrawal.sqlite"
        with sqlite3.connect(backup_path) as backup:
            self.journal.db.backup(backup)
        self.assertTrue(self.journal.record_withdrawal(**self.right,generation=1)["ok"])
        latest = self.packet()
        self.assertEqual(verify_checkpoint(self.path,latest,**self.kw)["code"],
                         "checkpoint_matches_only")

        # A privileged storage rollback produces an internally consistent
        # database, but the independently retained newer checkpoint detects it.
        self.journal.close()
        self.path.write_bytes(backup_path.read_bytes())
        result = verify_checkpoint(self.path, latest, **dict(
            self.kw, minimum_generation=1))
        self.assertEqual(result["code"], "journal_checkpoint_mismatch")
        self.assertFalse(result["checkpoint_matches"])
        self.assertFalse(result["authorizes_effect"])

    def test_same_generation_subject_and_digest_substitution_rejected(self):
        self.assertTrue(self.journal.record_withdrawal(**self.right,generation=1)["ok"])
        checkpoint = self.packet()
        self.journal.db.execute(
            "UPDATE withdrawn SET subject=?, effect_digest=? WHERE record_ref=?",
            ("other-person", "b"*64, "r1"))
        result = verify_checkpoint(self.path,checkpoint,**dict(
            self.kw,minimum_generation=1))
        self.assertEqual(result["code"],"journal_checkpoint_mismatch")
        self.assertFalse(result["checkpoint_matches"])
        self.assertFalse(result["authorizes_effect"])

    def test_same_generation_reference_replacement_rejected(self):
        self.assertTrue(self.journal.record_withdrawal(**self.right,generation=1)["ok"])
        checkpoint = self.packet()
        self.journal.db.execute(
            "UPDATE withdrawn SET record_ref=? WHERE record_ref=?",
            ("different-right", "r1"))
        result = verify_checkpoint(self.path,checkpoint,**dict(
            self.kw,minimum_generation=1))
        self.assertEqual(result["code"],"journal_checkpoint_mismatch")
        self.assertFalse(result["checkpoint_matches"])
        self.assertFalse(result["original_six_x3_proved"])

    def test_wrong_signer(self):
        self.assertEqual(verify_checkpoint(self.path,self.packet(key=self.other),**self.kw)["code"],
                         "checkpoint_not_verified")

    def test_wrong_deployment(self):
        self.assertEqual(verify_checkpoint(self.path,self.packet(deployment="other"),**self.kw)["code"],
                         "deployment_mismatch")

    def test_missing_checkpoint_and_bad_signature(self):
        self.assertEqual(verify_checkpoint(self.path,{},**self.kw)["code"],"packet_invalid")
        p=self.packet()
        p["signature"]="0"*128
        self.assertEqual(verify_checkpoint(self.path,p,**self.kw)["code"],
                         "checkpoint_not_verified")

    def test_mismatched_digest(self):
        self.assertEqual(verify_checkpoint(self.path,self.packet(digest="b"*64),**self.kw)["code"],
                         "journal_checkpoint_mismatch")

    def test_missing_journal(self):
        self.journal.close()
        self.path.unlink()
        self.assertEqual(verify_checkpoint(self.path,self.packet_from_empty(),**self.kw)["code"],
                         "journal_integrity_unknown")

    def packet_from_empty(self):
        claim=dict(domain=DOMAIN,deployment="offline-pilot-1",generation=0,digest="0"*64)
        return {"checkpoint":claim,"signature":self.signer.sign(
            canonical_checkpoint(claim)).hex()}

    def test_deleted_row_after_checkpoint(self):
        self.assertTrue(self.journal.record_withdrawal(**self.right,generation=1)["ok"])
        p=self.packet()
        self.journal.db.execute("DELETE FROM withdrawn WHERE record_ref='r1'")
        self.assertEqual(verify_checkpoint(self.path,p,**self.kw)["code"],
                         "journal_integrity_unknown")

    def test_boolean_generation_denied(self):
        self.assertEqual(verify_checkpoint(self.path,self.packet(),**dict(
            self.kw, minimum_generation=True))["code"],"trusted_inputs_invalid")


if __name__=="__main__":
    unittest.main()
