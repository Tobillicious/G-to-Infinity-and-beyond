"""Actual local filesystem marker security fixture: no external actuators.

CI on Ubuntu with sudo to test distinct UID direct-write denial. The only
sanctioned real effect is an empty marker under a private temporary directory.
"""
import hashlib
import os
from pathlib import Path
import pwd
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_ed25519_permit import issue_ed25519
from koru_protected_fs_sink import ProtectedFilesystemSink
from koru_shadow import digest
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


class ProtectedFilesystemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-protected-fs-")
        self.parent = Path(self.temp.name)
        self.private = self.parent / "private"
        self.private.mkdir(mode=0o700)
        self.db = str(self.private / "g3.sqlite")
        self.effects = self.private / "effects"
        self.effects.mkdir(mode=0o700)
        self.event, trust = fixtures()
        self.issuer = Ed25519PrivateKey.generate()
        self.permit = issue_ed25519(self.issuer, issuer="trusted-test-issuer",
                                    event=self.event, expires_at=200)
        self.gate = SyntheticEffectGate(
            self.db, contexts=trust["contexts"],
            signatures=trust["signatures"], witnesses=trust["witnesses"],
            authorities=trust["authorities"],
            provenances=trust["provenances"],
            context_ref="ctx-one", generation=3,
            ed25519_public_key=self.issuer.public_key(),
            permit_issuer="trusted-test-issuer")
        self.sink = ProtectedFilesystemSink(self.gate, str(self.effects))
        self.marker = self.effects / (
            hashlib.sha256(self.event["event_id"].encode()).hexdigest() + ".marker")

    def tearDown(self):
        self.sink.close()
        self.gate.close()
        self.temp.cleanup()

    def test_real_marker_requires_signed_admission_and_dispatch(self):
        self.assertEqual(self.sink.apply_marker(self.event, now=20, permit=self.permit)["code"],
                         "not_admitted")
        self.assertFalse(self.marker.exists())
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        done = self.sink.apply_marker(self.event, now=20, permit=self.permit)
        self.assertEqual(done["code"], "filesystem_marker_applied")
        self.assertTrue(self.marker.exists())
        self.assertEqual(self.marker.stat().st_size, 0)
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "marker_already_applied")
        self.assertEqual(len(list(self.effects.iterdir())), 1)

    def test_revocation_or_hold_before_file_effect_prevents_write(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.gate.hold(4)
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "held_at_effect")
        self.assertFalse(self.marker.exists())
        self.gate.release(5)
        self.gate.revoke_authority("auth-lesson")
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "authority_revoked_at_effect")
        self.assertFalse(self.marker.exists())

    def test_expiry_and_forgery_do_not_write_file(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertEqual(self.sink.apply_marker(
            self.event, now=200, permit=self.permit)["code"], "invalid_permit_at_effect")
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=dict(self.permit, signature="0" * 128))["code"],
                         "invalid_permit_at_effect")
        self.assertFalse(self.marker.exists())

    def test_recovery_after_synthetic_dispatch_before_filesystem_effect(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        self.assertFalse(self.marker.exists())
        # Simulate failure after the DB effect committed, before the file existed.
        # Retrying with STILL VALID authorization safely creates it once.
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "filesystem_marker_applied")
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "marker_already_applied")

    def test_reconciliation_reports_missing_real_effect_without_replaying(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        report = self.sink.reconcile_report()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["pending_count"], 1)
        self.assertEqual(report["applied_count"], 0)
        self.assertEqual(report["pending_event_ids"], [self.event["event_id"]])
        self.assertFalse(self.marker.exists())
        self.gate.revoke_authority("auth-lesson")
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"],
            "authority_revoked_at_effect")
        self.assertFalse(self.marker.exists())
        self.assertEqual(self.sink.reconcile_report()["pending_count"], 1)

    def test_reconciliation_reports_applied_after_valid_recovery(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        self.assertEqual(self.sink.reconcile_report()["pending_count"], 1)
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"],
            "filesystem_marker_applied")
        report = self.sink.reconcile_report()
        self.assertEqual(report["pending_count"], 0)
        self.assertEqual(report["applied_count"], 1)

    def test_reconciliation_detects_orphan_and_rejects_it(self):
        (self.effects / "forged.marker").touch(mode=0o600)
        report = self.sink.reconcile_report()
        self.assertFalse(report["ok"])
        self.assertEqual(report["code"], "unaccounted_files")
        self.assertEqual(report["count"], 1)

    def test_reconciliation_detects_tampered_and_symlinked_marker(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "filesystem_marker_applied")
        self.marker.write_text("tampered")
        self.assertEqual(self.sink.reconcile_report()["code"], "marker_integrity")
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"], "effect_store_marker_integrity")
        self.marker.unlink()
        self.marker.symlink_to("/dev/null")
        self.assertEqual(self.sink.reconcile_report()["code"], "marker_integrity")

    def test_reopened_sink_reconciles_without_automatic_effect(self):
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        self.sink.close()
        self.sink = ProtectedFilesystemSink(self.gate, str(self.effects))
        report = self.sink.reconcile_report()
        self.assertEqual(report["pending_count"], 1)
        self.assertFalse(self.marker.exists())

    def test_orphan_prevents_new_effect_before_journal_commit(self):
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])
        (self.effects / "orphan.marker").touch(mode=0o600)
        denied = self.sink.apply_marker(
            self.event, now=20, permit=self.permit)
        self.assertEqual(denied["code"], "effect_store_unaccounted_files")
        self.assertEqual(self.gate.effect_count(), 0)
        self.assertFalse(self.marker.exists())
        (self.effects / "orphan.marker").unlink()
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"],
            "filesystem_marker_applied")
        self.assertEqual(self.gate.effect_count(), 1)

    def test_corrupt_prior_marker_prevents_attempted_replay(self):
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"],
            "filesystem_marker_applied")
        self.marker.write_text("tampered")
        denied = self.sink.apply_marker(
            self.event, now=20, permit=self.permit)
        self.assertEqual(denied["code"], "effect_store_marker_integrity")
        self.assertEqual(self.gate.effect_count(), 1)

    def test_pending_from_other_event_blocks_followup_marker(self):
        # A synthetic journaled effect with no filesystem marker is a
        # recovery obligation. Later distinct effects must not leapfrog it.
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        later = dict(self.event, event_id=self.event["event_id"] + "-later",
                     idempotency_key=self.event["idempotency_key"] + "-later",
                     witness_ref="witness-74-later")
        # Independently bind the second test event to a fresh trusted fixture
        # witness. Reusing the first event's witness would be correctly denied.
        self.gate.witnesses["witness-74-later"] = dict(
            self.gate.witnesses[self.event["witness_ref"]],
            event_digest=digest(later))
        later_permit = issue_ed25519(
            self.issuer, issuer="trusted-test-issuer",
            event=later, expires_at=200)
        self.assertTrue(self.gate.apply(
            later, now=20, permit=later_permit)["ok"])
        denied = self.sink.apply_marker(later, now=20, permit=later_permit)
        self.assertEqual(denied["code"], "unresolved_prior_effect")
        self.assertEqual(self.gate.effect_count(), 1)
        self.assertEqual(self.sink.apply_marker(
            self.event, now=20, permit=self.permit)["code"],
            "filesystem_marker_applied")
        self.assertEqual(self.sink.apply_marker(
            later, now=20, permit=later_permit)["code"],
            "filesystem_marker_applied")
        self.assertEqual(self.gate.effect_count(), 2)

    def test_untrusted_os_identity_cannot_write_effect_directory(self):
        if sys.platform != "linux" or os.geteuid() != 0:
            self.skipTest("privileged Linux CI negative-control only")
        guest = pwd.getpwnam("nobody")
        code = (
            "import os,sys; "
            "p=sys.argv[1]; "
            "f=os.path.join(p,'forged.marker'); "
            "os.open(f,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)"
        )
        def drop():
            os.setgroups([])
            os.setgid(guest.pw_gid)
            os.setuid(guest.pw_uid)
        proc = subprocess.run(
            [sys.executable, "-B", "-c", code, str(self.effects)],
            text=True, capture_output=True, timeout=10, check=False,
            cwd="/", env={}, preexec_fn=drop)
        self.assertNotEqual(proc.returncode, 0)
        self.assertTrue("PermissionError" in proc.stderr, proc.stderr)
        self.assertFalse((self.effects / "forged.marker").exists())

    def test_world_writable_effect_directory_is_rejected(self):
        self.effects.chmod(0o777)
        with self.assertRaises(PermissionError):
            ProtectedFilesystemSink(self.gate, str(self.effects))


if __name__ == "__main__":
    unittest.main()
