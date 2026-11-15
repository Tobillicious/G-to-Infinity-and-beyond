"""Failure injection at the narrow G3 SQLite-to-filesystem marker boundary.

This tests actual empty marker effects only. These are controlled OSError
injections, NOT process-kill/power-loss durability certification. A failed
fsync leaves an uncertain outcome until independent reconciliation.
"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_ed25519_permit import issue_ed25519
from koru_protected_fs_sink import ProtectedFilesystemSink
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


class MarkerFaultInjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-fault-injection-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        private = root / "private"
        private.mkdir(mode=0o700)
        effects = private / "effects"
        effects.mkdir(mode=0o700)
        self.event, trust = fixtures()
        issuer = Ed25519PrivateKey.generate()
        self.permit = issue_ed25519(
            issuer, issuer="fault-test-issuer", event=self.event,
            expires_at=200)
        self.gate = SyntheticEffectGate(
            str(private / "state.sqlite"),
            contexts=trust["contexts"], signatures=trust["signatures"],
            witnesses=trust["witnesses"], authorities=trust["authorities"],
            provenances=trust["provenances"], context_ref="ctx-one",
            generation=3, ed25519_public_key=issuer.public_key(),
            permit_issuer="fault-test-issuer")
        self.addCleanup(self.gate.close)
        self.sink = ProtectedFilesystemSink(self.gate, str(effects))
        self.addCleanup(self.sink.close)
        self.effects = effects
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])

    def _retry(self):
        return self.sink.apply_marker(self.event, now=20, permit=self.permit)

    def test_create_failure_retains_pending_journal_and_does_not_execute(self):
        real_open = os.open
        def fail_marker_create(path, flags, *args, **kwargs):
            if (type(path) is str and path.endswith(".marker")
                    and flags & os.O_CREAT):
                raise OSError("injected marker create failure")
            return real_open(path, flags, *args, **kwargs)

        with patch("koru_protected_fs_sink.os.open", side_effect=fail_marker_create):
            with self.assertRaises(OSError):
                self._retry()
        self.assertEqual(self.gate.effect_count(), 1)
        self.assertEqual(list(self.effects.iterdir()), [])
        report = self.sink.reconcile_report()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["pending_count"], 1)
        # Authorization is rechecked on recovery; an intervening revocation
        # must stop the retry rather than manufacture the missing effect.
        self.gate.revoke_authority(self.event["authority_ref"])
        self.assertEqual(self._retry()["code"], "authority_revoked_at_effect")
        self.assertEqual(list(self.effects.iterdir()), [])

    def test_file_fsync_failure_recovers_without_second_marker(self):
        real_fsync = os.fsync
        triggered = []
        def fail_file_sync(fd):
            if fd != self.sink.dirfd and not triggered:
                triggered.append(fd)
                raise OSError("injected marker fsync failure")
            return real_fsync(fd)

        with patch("koru_protected_fs_sink.os.fsync", side_effect=fail_file_sync):
            with self.assertRaises(OSError):
                self._retry()
        self.assertTrue(triggered)
        self.assertEqual(self.gate.effect_count(), 1)
        self.assertEqual(len(list(self.effects.iterdir())), 1)
        self.assertEqual(self._retry()["code"], "marker_already_applied")
        self.assertEqual(len(list(self.effects.iterdir())), 1)
        self.assertEqual(self.sink.reconcile_report()["pending_count"], 0)

    def test_directory_fsync_failure_reconciles_and_replays_idempotently(self):
        real_fsync = os.fsync
        triggered = []
        def fail_directory_sync(fd):
            if fd == self.sink.dirfd and not triggered:
                triggered.append(fd)
                raise OSError("injected directory fsync failure")
            return real_fsync(fd)

        with patch("koru_protected_fs_sink.os.fsync",
                   side_effect=fail_directory_sync):
            with self.assertRaises(OSError):
                self._retry()
        self.assertTrue(triggered)
        self.assertEqual(self.gate.effect_count(), 1)
        self.assertEqual(len(list(self.effects.iterdir())), 1)
        self.assertEqual(self._retry()["code"], "marker_already_applied")
        self.assertEqual(len(list(self.effects.iterdir())), 1)
        self.assertEqual(self.sink.reconcile_report()["applied_count"], 1)


if __name__ == "__main__":
    unittest.main()
