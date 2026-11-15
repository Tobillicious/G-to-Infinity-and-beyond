"""Linux privileged OS-boundary negative control, synthetic effects ONLY.

Run under root in an isolated CI worker. Never execute against production
paths. The root-owned broker and unprivileged child MUST have distinct UIDs.
"""
import json
import os
import pathlib
import pwd
import subprocess
import sys
import tempfile
import threading
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_broker import SyntheticBroker, send_request
from koru_ed25519_permit import issue_ed25519
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


_CHILD = r'''
import json, os, sys
from koru_broker import send_request
req = json.loads(sys.stdin.read())
db = req["db"]
denied = False
try:
    fd = os.open(db, os.O_RDWR)
    os.close(fd)
except PermissionError:
    denied = True
r1 = send_request(req["sock"], "admit", req["event"], req["permit"], 10)
r2 = send_request(req["sock"], "dispatch", req["event"], req["permit"], 20)
forbidden = send_request(req["sock"], "hold", req["event"], req["permit"], 20)
print(json.dumps({"db_denied": denied, "admit": r1["code"],
                  "dispatch": r2["code"], "hold": forbidden["code"]}))
'''


class TestLinuxOSPrincipalBoundary(unittest.TestCase):
    def test_distinct_uid_cannot_write_effect_store(self):
        if sys.platform != "linux" or os.geteuid() != 0:
            self.fail("This security test REQUIRES Linux root and a distinct unprivileged UID")
        guest = pwd.getpwnam("nobody")
        if guest.pw_uid == 0:
            self.fail("unsafe guest identity")
        with tempfile.TemporaryDirectory(prefix="koru-os-") as folder:
            os.chmod(folder, 0o755)
            private = pathlib.Path(folder) / "trusted"
            private.mkdir(mode=0o700)
            db = str(private / "events.db")
            socket_path = str(pathlib.Path(folder) / "broker.sock")
            event, trust = fixtures()
            signing_key = Ed25519PrivateKey.generate()
            permit = issue_ed25519(signing_key, issuer="offline-test-issuer",
                                   event=event, expires_at=100)
            gate = SyntheticEffectGate(
                db, contexts=trust["contexts"], signatures=trust["signatures"],
                witnesses=trust["witnesses"], authorities=trust["authorities"],
                provenances=trust["provenances"], context_ref="ctx-one",
                generation=3, ed25519_public_key=signing_key.public_key(),
                permit_issuer="offline-test-issuer")
            broker = SyntheticBroker(socket_path, gate)
            thread = threading.Thread(target=broker.serve_forever, daemon=True)
            thread.start()
            try:
                # Under the test account, DB directory traversal must be
                # denied even though the specific IPC socket is reachable.
                def drop():
                    os.setgroups([])
                    os.setgid(guest.pw_gid)
                    os.setuid(guest.pw_uid)
                request = dict(db=db, sock=socket_path, event=event, permit=permit)
                proc = subprocess.run(
                    [sys.executable, "-B", "-c", _CHILD],
                    input=json.dumps(request), text=True,
                    capture_output=True, timeout=15, check=False,
                    preexec_fn=drop, cwd=folder,
                    env={"PYTHONPATH": str(pathlib.Path(__file__).resolve().parent)})
                self.assertEqual(proc.returncode, 0, proc.stderr)
                result = json.loads(proc.stdout)
                self.assertTrue(result["db_denied"], result)
                self.assertEqual(result["admit"], "durable_synthetic_record")
                self.assertEqual(result["dispatch"], "synthetic_effect_recorded")
                self.assertEqual(result["hold"], "unsupported_operation")
                self.assertEqual(gate.effect_count(), 1)
                # The same valid signed event must not execute twice.
                repeated = send_request(socket_path, "dispatch", event, permit, 20)
                self.assertEqual(repeated["code"], "already_dispatched")
                self.assertEqual(gate.effect_count(), 1)
            finally:
                broker.shutdown()
                broker.server_close()
                thread.join(timeout=5)
                gate.close()


if __name__ == "__main__":
    unittest.main()
