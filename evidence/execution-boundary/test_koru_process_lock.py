"""Deterministic G3 interprocess lock test; Linux research fixture only.

A separate controller OS process must block behind the effect service lock.
This proves serialization only for cooperating holders of the SAME private
lock inode; it cannot constrain a compromised privileged process.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_ed25519_permit import issue_ed25519
from koru_process_lock import InterprocessRLock
from koru_protected_fs_sink import ProtectedFilesystemSink
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


# This is a fresh Python interpreter, NOT a forked inherited lock descriptor.
_CONTROLLER = r"""
import sys
from pathlib import Path
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
db, lock, ready, completed, operation = sys.argv[1:]
event, trust = fixtures()
issuer = Ed25519PrivateKey.generate()
gate = SyntheticEffectGate(db, contexts=trust["contexts"],
    signatures=trust["signatures"], witnesses=trust["witnesses"],
    authorities=trust["authorities"], provenances=trust["provenances"],
    context_ref="ctx-one", generation=3,
    ed25519_public_key=issuer.public_key(), permit_issuer="test-issuer",
    cross_process_lock_path=lock)
Path(ready).write_text("waiting")
if operation == "hold":
    gate.hold(4)
elif operation == "revoke":
    gate.revoke_authority("auth-lesson")
else:
    raise ValueError("unknown operation")
Path(completed).write_text("completed")
gate.close()
"""


@unittest.skipUnless(sys.platform == "linux", "Linux/POSIX cross-process fixture")
class TestG3InterprocessFence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-ipc-")
        self.root = Path(self.temp.name)
        self.private = self.root / "trusted"
        self.private.mkdir(mode=0o700)
        self.db = str(self.private / "gate.sqlite")
        self.lockfile = str(self.private / "effect.lock")
        self.effects = self.private / "effects"
        self.effects.mkdir(mode=0o700)
        event, trust = fixtures()
        self.event = event
        self.key = Ed25519PrivateKey.generate()
        self.permit = issue_ed25519(self.key, issuer="test-issuer",
                                    event=event, expires_at=100)
        self.gate = SyntheticEffectGate(
            self.db, contexts=trust["contexts"],
            signatures=trust["signatures"], witnesses=trust["witnesses"],
            authorities=trust["authorities"],
            provenances=trust["provenances"], context_ref="ctx-one",
            generation=3, ed25519_public_key=self.key.public_key(),
            permit_issuer="test-issuer",
            cross_process_lock_path=self.lockfile)
        self.sink = ProtectedFilesystemSink(self.gate, str(self.effects))

    def tearDown(self):
        self.sink.close()
        self.gate.close()
        self.temp.cleanup()

    def controller(self, operation):
        ready = self.root / (operation + "-ready")
        done = self.root / (operation + "-done")
        process = subprocess.Popen(
            [sys.executable, "-B", "-c", _CONTROLLER,
             self.db, self.lockfile, str(ready), str(done), operation],
            cwd=str(self.root),
            env={"PYTHONPATH": str(Path(__file__).resolve().parent)},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return process, ready, done

    def wait_ready(self, process, ready):
        until = time.monotonic() + 6
        while not ready.exists() and time.monotonic() < until:
            if process.poll() is not None:
                out, err = process.communicate()
                self.fail("controller exited before lock attempt: " + err + out)
            time.sleep(0.01)
        self.assertTrue(ready.exists(), "controller never reached lock attempt")

    def test_independent_hold_cannot_commit_during_effect_critical_section(self):
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])
        proc = None
        try:
            with self.gate.lock:
                proc, ready, done = self.controller("hold")
                self.wait_ready(proc, ready)
                # Controller reached hold() in a different process; while
                # the gate's effect lock is held it cannot record a hold.
                time.sleep(0.25)
                self.assertFalse(done.exists())
                self.assertEqual(self.gate.db.execute(
                    "SELECT halted FROM gate_state WHERE id=1").fetchone()[0], 0)
            out, err = proc.communicate(timeout=10)
            self.assertEqual(proc.returncode, 0, err + out)
            self.assertTrue(done.exists())
            self.assertEqual(self.sink.apply_marker(
                self.event, now=20, permit=self.permit)["code"],
                "held_at_effect")
            self.assertFalse(any(self.effects.iterdir()))
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.communicate()

    def test_independent_revocation_serializes_before_effect(self):
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])
        proc = None
        try:
            with self.gate.lock:
                proc, ready, done = self.controller("revoke")
                self.wait_ready(proc, ready)
                time.sleep(0.25)
                self.assertFalse(done.exists())
                self.assertEqual(self.gate.db.execute(
                    "SELECT COUNT(*) FROM revoked_authorities").fetchone()[0], 0)
            out, err = proc.communicate(timeout=10)
            self.assertEqual(proc.returncode, 0, err + out)
            self.assertEqual(self.sink.apply_marker(
                self.event, now=20, permit=self.permit)["code"],
                "authority_revoked_at_effect")
            self.assertFalse(any(self.effects.iterdir()))
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.communicate()

    def test_nested_lock_allows_protected_effect(self):
        self.assertTrue(self.gate.apply(
            self.event, now=20, permit=self.permit)["ok"])
        with self.gate.lock:
            self.assertEqual(self.sink.apply_marker(
                self.event, now=20, permit=self.permit)["code"],
                "filesystem_marker_applied")
        self.assertEqual(len(list(self.effects.iterdir())), 1)

    def test_insecure_lock_directory_is_rejected(self):
        self.private.chmod(0o777)
        with self.assertRaises(PermissionError):
            InterprocessRLock(self.lockfile)
        self.private.chmod(0o700)

    def test_symlink_lock_file_rejected(self):
        alternate = self.private / "elsewhere"
        alternate.write_text("not a lock")
        # Existing protected lock remains held by gate; a second name that
        # points through a symlink MUST NOT be accepted.
        symlink = self.private / "linked.lock"
        symlink.symlink_to(alternate)
        with self.assertRaises(OSError):
            InterprocessRLock(str(symlink))


if __name__ == "__main__":
    unittest.main()
