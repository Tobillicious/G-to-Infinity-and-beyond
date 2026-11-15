"""Linux OS-identity negative controls for the G3 deployment threat model.

This is not a user-namespace implementation of the protected G3 service.
It tests real kernel discretionary access controls with distinct OS UIDs,
and intentionally shows that host root and deliberately leaked writable FDs
can bypass them. Never run outside an ephemeral dedicated CI runner.
"""
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


_CHILD = r"""
import os, sys
mode, path = sys.argv[1:3]
if mode == "create":
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(fd)
elif mode == "overwrite":
    fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW)
    os.write(fd, b"altered")
    os.close(fd)
elif mode == "inherited_fd":
    # Simulates a *buggy privileged launcher* deliberately leaking a writable
    # descriptor. This is a counterexample: UID isolation is insufficient.
    fd = int(sys.argv[3])
    os.write(fd, b"leaked")
else:
    raise ValueError("unknown fixture operation")
"""


@unittest.skipUnless(sys.platform == "linux", "Linux-only security fixture")
class TestKernelUidBoundary(unittest.TestCase):
    """Uses no live files: private ephemeral paths and numerical test UIDs."""

    @classmethod
    def setUpClass(cls):
        if os.geteuid() != 0:
            raise unittest.SkipTest("requires isolated Linux root CI worker")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-principals-")
        self.parent = Path(self.temp.name)
        self.parent.chmod(0o755)
        self.effect_dir = self.parent / "effect-writer-only"
        self.effect_dir.mkdir(mode=0o700)
        self.writer_uid = 10001
        self.controller_uid = 10002
        self.untrusted_uid = 10003
        self.effect_dir.chown(self.writer_uid, self.writer_uid)
        self.marker = self.effect_dir / "g3-only.marker"

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _as_uid(uid):
        def switch():
            os.setgroups([])
            os.setgid(uid)
            os.setuid(uid)
        return switch

    def run_child(self, uid, mode, path, *, pass_fds=(), extra=()):
        return subprocess.run(
            [sys.executable, "-B", "-c", _CHILD, mode, str(path), *extra],
            capture_output=True, text=True, timeout=10, check=False,
            preexec_fn=self._as_uid(uid), pass_fds=pass_fds,
            cwd="/", env={})

    def test_separate_writer_controller_and_guest_kernel_permissions(self):
        allowed = self.run_child(self.writer_uid, "create", self.marker)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        info = self.marker.stat()
        self.assertEqual(info.st_uid, self.writer_uid)
        self.assertEqual(stat.S_IMODE(info.st_mode), 0o600)
        for uid in (self.controller_uid, self.untrusted_uid):
            with self.subTest(uid=uid):
                denied = self.run_child(uid, "overwrite", self.marker)
                self.assertNotEqual(denied.returncode, 0)
                self.assertIn("PermissionError", denied.stderr)
                self.assertEqual(self.marker.stat().st_size, 0)

    def test_host_root_is_NOT_restrained_by_mode_0600(self):
        allowed = self.run_child(self.writer_uid, "create", self.marker)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        # Deliberate demonstration, not a successful protection claim.
        with open(self.marker, "wb") as handle:
            handle.write(b"root can write")
        self.assertEqual(self.marker.read_bytes(), b"root can write")

    def test_forged_writable_descriptor_bypasses_uid_isolation(self):
        allowed = self.run_child(self.writer_uid, "create", self.marker)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        fd = os.open(self.marker, os.O_WRONLY)
        try:
            # Normal subprocess close_fds prevents accidental inheritance.
            denied = self.run_child(
                self.controller_uid, "inherited_fd", self.marker,
                extra=(str(fd),))
            self.assertNotEqual(denied.returncode, 0)
            # Deliberately whitelisting the privileged fd defeats UID DAC.
            bypass = self.run_child(
                self.controller_uid, "inherited_fd", self.marker,
                pass_fds=(fd,), extra=(str(fd),))
            self.assertEqual(bypass.returncode, 0, bypass.stderr)
            self.assertEqual(self.marker.read_bytes(), b"leaked")
        finally:
            os.close(fd)

    def test_private_directory_rejects_untrusted_creation(self):
        for uid in (self.controller_uid, self.untrusted_uid):
            with self.subTest(uid=uid):
                denied = self.run_child(uid, "create",
                                        self.effect_dir / "forged.marker")
                self.assertNotEqual(denied.returncode, 0)
                self.assertIn("PermissionError", denied.stderr)
        self.assertEqual(list(self.effect_dir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
