"""OS-separated emergency controls for synthetic G3, on an isolated Linux CI runner.

The unprivileged caller has no database or controller socket access.
No live process or external effect is controlled by this fixture.
"""
import json
import os
from pathlib import Path
import pwd
import subprocess
import sys
import tempfile
import threading
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_broker import SyntheticBroker
from koru_control_broker import TrustedControlBroker, send_control
from koru_ed25519_permit import issue_ed25519
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


_GUEST = r'''
import json, os, socket, sys
data = json.loads(sys.stdin.read())
def send(op):
    message = json.dumps({"op": op, "event": data["event"],
                          "permit": data["permit"]}).encode() + b"\n"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect(data["public"])
        sock.sendall(message)
        reply = bytearray()
        while not reply.endswith(b"\n"):
            chunk = sock.recv(4096)
            if not chunk or len(reply) + len(chunk) > 4096:
                raise ValueError("bad reply")
            reply.extend(chunk)
    return json.loads(reply)["code"]
denied = False
try:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        sock.connect(data["private"])
except PermissionError:
    denied = True
print(json.dumps({"controller_denied": denied, "result": send(data["op"]),
                  "untrusted_hold": send("hold")}))
'''


class TestTrustedControlBroker(unittest.TestCase):
    def test_isolated_controller_enforces_hold_release_revoke(self):
        if sys.platform != "linux" or os.geteuid() != 0:
            self.fail("requires isolated Linux root CI fixture")
        guest = pwd.getpwnam("nobody")
        if guest.pw_uid == 0:
            self.fail("guest must be distinct from controller")
        with tempfile.TemporaryDirectory(prefix="g3-control-") as folder:
            os.chmod(folder, 0o755)
            private = Path(folder) / "root-private"
            private.mkdir(mode=0o700)
            db = str(private / "effects.sqlite")
            public_socket = str(Path(folder) / "events.sock")
            control_socket = str(private / "control.sock")
            event, stores = fixtures()
            issuer = Ed25519PrivateKey.generate()
            permit = issue_ed25519(issuer, issuer="isolated-issuer",
                                  event=event, expires_at=100)
            options = dict(contexts=stores["contexts"],
                           signatures=stores["signatures"],
                           witnesses=stores["witnesses"],
                           authorities=stores["authorities"],
                           provenances=stores["provenances"],
                           context_ref="ctx-one", generation=3,
                           ed25519_public_key=issuer.public_key(),
                           permit_issuer="isolated-issuer")
            gate = SyntheticEffectGate(db, **options)
            public = SyntheticBroker(public_socket, gate,
                                     allowed_client_uids={guest.pw_uid},
                                     clock=lambda: 20)
            control = TrustedControlBroker(control_socket, gate, controller_uids={0})
            servers = (public, control)
            threads = [threading.Thread(target=s.serve_forever, daemon=True)
                       for s in servers]
            for t in threads:
                t.start()

            def guest_request(op):
                def drop():
                    os.setgroups([])
                    os.setgid(guest.pw_gid)
                    os.setuid(guest.pw_uid)
                args = dict(event=event, permit=permit, public=public_socket,
                            private=control_socket, op=op)
                proc = subprocess.run(
                    [sys.executable, "-B", "-c", _GUEST],
                    input=json.dumps(args), text=True, capture_output=True,
                    timeout=15, check=False, cwd=folder, env={}, preexec_fn=drop)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                result = json.loads(proc.stdout)
                self.assertTrue(result["controller_denied"], result)
                self.assertEqual(result["untrusted_hold"], "unsupported_operation")
                return result["result"]

            try:
                self.assertEqual(guest_request("admit"), "durable_synthetic_record")
                self.assertEqual(send_control(
                    control_socket, {"op": "hold", "minimum_generation": 4})["code"],
                    "held")
                self.assertEqual(guest_request("dispatch"), "held_at_effect")
                self.assertEqual(gate.effect_count(), 0)
                self.assertEqual(send_control(
                    control_socket, {"op": "release", "generation": 4})["code"],
                    "invalid_control_request")
                self.assertEqual(guest_request("dispatch"), "held_at_effect")
                self.assertEqual(send_control(
                    control_socket, {"op": "release", "generation": 5})["code"],
                    "released")
                self.assertEqual(guest_request("dispatch"), "effect_stale_generation")
                self.assertEqual(send_control(
                    control_socket, {"op": "revoke",
                                     "authority_ref": "auth-lesson"})["code"],
                    "revoked")
                self.assertEqual(guest_request("dispatch"), "authority_revoked_at_effect")
                self.assertEqual(gate.effect_count(), 0)
                self.assertEqual(send_control(
                    control_socket, {"op": "issue", "authority_ref": "auth-lesson"})["code"],
                    "unsupported_control")
                self.assertEqual(send_control(
                    control_socket, {"op": "release", "generation": True})["code"],
                    "invalid_control_request")
            finally:
                for server in servers: server.shutdown()
                for server in servers: server.server_close()
                for t in threads: t.join(timeout=5)
                gate.close()

            # Persisted revocation/hold state cannot be reset by restart.
            reopened = SyntheticEffectGate(db, **options)
            try:
                generation, halted = reopened.db.execute(
                    "SELECT generation, halted FROM gate_state WHERE id=1").fetchone()
                self.assertEqual((generation, halted), (5, 0))
                self.assertEqual(reopened.dispatch_synthetic(
                    event, now=20, permit=permit)["code"],
                    "authority_revoked_at_effect")
                self.assertEqual(reopened.effect_count(), 0)
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
