"""Three real Linux processes: writer, controller and untrusted requester.

Separate ephemeral UIDs. Root test orchestrator only provisions and signs an
offline fixture; it is NOT the writer or controller service. No live API, model,
external actuator, human rights claim or production deployment.
"""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from koru_ed25519_permit import issue_ed25519
from test_koru_shadow import fixtures


_WRITER = r"""
import json, os, sys, threading
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from koru_broker import SyntheticBroker
from koru_control_broker import TrustedControlBroker
from koru_protected_fs_sink import ProtectedFilesystemSink
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures

os.umask(0o077)
c = json.loads(sys.argv[1])
event, trust = fixtures()
gate = SyntheticEffectGate(
    c["db"], contexts=trust["contexts"], signatures=trust["signatures"],
    witnesses=trust["witnesses"], authorities=trust["authorities"],
    provenances=trust["provenances"], context_ref="ctx-one", generation=3,
    ed25519_public_key=Ed25519PublicKey.from_public_bytes(
        bytes.fromhex(c["public_key"])), permit_issuer="three-principal-issuer")
sink = ProtectedFilesystemSink(gate, c["effect_dir"])
public = SyntheticBroker(
    c["public_socket"], gate, allowed_client_uids={c["guest_uid"]},
    clock=lambda: 20, effect_sink=sink,
    request_timeout=0.75, max_connections=4)
control = TrustedControlBroker(
    c["control_socket"], gate, controller_uids={c["controller_uid"]},
    controller_group_access=True, request_timeout=0.75, max_connections=2)
servers = (public, control)
threads = [threading.Thread(target=s.serve_forever, daemon=True)
           for s in servers]
for t in threads:
    t.start()
print("READY", flush=True)
try:
    sys.stdin.readline()
finally:
    for server in servers:
        server.shutdown()
    for server in servers:
        server.server_close()
    for t in threads:
        t.join(timeout=3)
    sink.close()
    gate.close()
"""

_CALLER = r"""
import json, os, socket, sys
c = json.loads(sys.stdin.read())
direct = {}
for label, path, mode in (
    ("db", c["db"], os.O_RDWR),
    ("effects", os.path.join(c["effect_dir"], "forged.marker"),
     os.O_WRONLY | os.O_CREAT | os.O_EXCL)):
    try:
        fd = os.open(path, mode, 0o600)
        os.close(fd)
        direct[label] = "BYPASS"
    except PermissionError:
        direct[label] = "denied"
    except FileExistsError:
        direct[label] = "BYPASS"
socket_path = c["control_socket"] if c["role"] == "controller" else c["public_socket"]
msg = c["control_payload"] if c["role"] == "controller" else dict(
    op=c["op"], event=c["event"], permit=c["permit"])
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
    sock.settimeout(3)
    sock.connect(socket_path)
    sock.sendall(json.dumps(msg).encode() + b"\n")
    response = bytearray()
    while not response.endswith(b"\n"):
        part = sock.recv(4096)
        if not part: break
        response.extend(part)
print(json.dumps({"direct": direct, "result": json.loads(response)}))
"""


@unittest.skipUnless(sys.platform == "linux", "Linux kernel peer credentials")
class ThreePrincipalGatewayTests(unittest.TestCase):
    def test_controller_can_hold_but_cannot_write_effect_or_database(self):
        if os.geteuid() != 0:
            self.skipTest("requires isolated privileged GitHub Actions worker")
        writer_uid, controller_uid, guest_uid = 10001, 10002, 10003
        with tempfile.TemporaryDirectory(prefix="g3-three-uid-") as folder:
            parent = Path(folder)
            parent.chmod(0o755)
            private = parent / "private"
            private.mkdir(mode=0o710)
            os.chown(private, writer_uid, controller_uid)
            private.chmod(0o710)
            effect_dir = private / "effects"
            effect_dir.mkdir(mode=0o700)
            os.chown(effect_dir, writer_uid, controller_uid)
            effect_dir.chmod(0o700)
            # Only writer can create/remove the public socket inode.
            # Guest and controller may traverse its directory but cannot
            # replace or unlink it; SO_PEERCRED still gates requests.
            public_dir = parent / "public-transport"
            public_dir.mkdir(mode=0o755)
            os.chown(public_dir, writer_uid, controller_uid)
            public_dir.chmod(0o755)
            public_socket = str(public_dir / "public.sock")
            control_socket = str(private / "controller.sock")
            db = str(private / "state.sqlite")

            event, _trusted = fixtures()
            issuer = Ed25519PrivateKey.generate()
            permit = issue_ed25519(
                issuer, issuer="three-principal-issuer",
                event=event, expires_at=100)
            public_bytes = issuer.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw).hex()
            config = dict(
                db=db, effect_dir=str(effect_dir),
                public_socket=public_socket, control_socket=control_socket,
                public_key=public_bytes, controller_uid=controller_uid,
                guest_uid=guest_uid)
            # GitHub runner checkouts can be inaccessible after setuid.
            # Stage ONLY source modules into an unprivileged read-only code
            # directory; never expand filesystem rights on the checkout.
            staged = parent / "test-code"
            staged.mkdir(mode=0o755)
            for module in Path(__file__).resolve().parent.glob("*.py"):
                copy = staged / module.name
                shutil.copyfile(module, copy)
                copy.chmod(0o644)
            root = str(staged)
            worker = None

            def lower_to(uid, gid):
                def drop():
                    os.setgroups([])
                    os.setgid(gid)
                    os.setuid(uid)
                return drop

            def caller(role, *, op=None, payload=None):
                uid = controller_uid if role == "controller" else guest_uid
                args = dict(config, role=role, op=op,
                            event=event, permit=permit, control_payload=payload)
                proc = subprocess.run(
                    [sys.executable, "-B", "-c", _CALLER],
                    input=json.dumps(args), capture_output=True, text=True,
                    timeout=7, check=False, cwd="/", env={},
                    preexec_fn=lower_to(uid, uid))
                self.assertEqual(proc.returncode, 0, proc.stderr)
                result = json.loads(proc.stdout)
                self.assertEqual(result["direct"],
                                 {"db": "denied", "effects": "denied"})
                return result["result"]

            try:
                worker = subprocess.Popen(
                    [sys.executable, "-B", "-c", _WRITER, json.dumps(config)],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, cwd="/",
                    env={"PYTHONPATH": root},
                    preexec_fn=lower_to(writer_uid, controller_uid))
                # Worker reports READY only after both sockets bind. This
                # avoids timing guesses and permits deterministic CI checks.
                import select
                ready, _, _ = select.select([worker.stdout], [], [], 7)
                self.assertTrue(ready, "writer startup timed out")
                line = worker.stdout.readline().strip()
                if line != "READY":
                    err = worker.stderr.read() if worker.poll() is not None else ""
                    self.fail("writer did not bind: " + line + " " + err)
                self.assertEqual(
                    caller("guest", op="admit")["code"],
                    "durable_synthetic_record")
                self.assertEqual(
                    caller("guest", op="effect_marker")["code"],
                    "filesystem_marker_applied")
                self.assertEqual(len(list(effect_dir.iterdir())), 1)
                self.assertEqual(
                    caller("controller", payload={
                        "op": "hold", "minimum_generation": 4})["code"],
                    "held")
                self.assertEqual(
                    caller("guest", op="effect_marker")["code"],
                    "held_at_effect")
                self.assertEqual(len(list(effect_dir.iterdir())), 1)
                self.assertEqual(
                    caller("controller", payload={
                        "op": "revoke", "authority_ref": "auth-lesson"})["code"],
                    "revoked")
            finally:
                if worker is not None:
                    if worker.poll() is None:
                        worker.communicate(input="\n", timeout=10)
                    else:
                        worker.communicate(timeout=3)


if __name__ == "__main__":
    unittest.main()
