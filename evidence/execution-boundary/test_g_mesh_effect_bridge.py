"""Research-only mesh lease -> real empty-marker effect integration tests.

No external APIs or production subjects. The *same trusted process* holds
both G3 and mesh handlers; OS-level separate-process guarantees remain open.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from g_mesh_effect_bridge import LeasedFilesystemEffect
from g_mesh_protocol import GMeshProtocolHandler, PROTOCOL, encode_body
from koru_broker import SyntheticBroker
from koru_ed25519_permit import issue_ed25519
from koru_shadow import digest
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


class TestLeasedFilesystemBridge(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-leased-marker-")
        self.path = Path(self.temp.name)
        self.directory = self.path / "effects"
        self.directory.mkdir(mode=0o700)
        self.now = [20]
        self.event, registries = fixtures()
        self.g3_key = Ed25519PrivateKey.generate()
        self.mesh_key = Ed25519PrivateKey.generate()
        self.controller_key = Ed25519PrivateKey.generate()
        self.permit = issue_ed25519(
            self.g3_key, issuer="g3-test-issuer", event=self.event,
            expires_at=100)
        self.g3 = SyntheticEffectGate(
            str(self.path / "g3.sqlite"),
            contexts=registries["contexts"],
            signatures=registries["signatures"],
            witnesses=registries["witnesses"],
            authorities=registries["authorities"],
            provenances=registries["provenances"],
            context_ref="ctx-one", generation=3,
            ed25519_public_key=self.g3_key.public_key(),
            permit_issuer="g3-test-issuer")
        self.mesh_opts = dict(
            node_id="local-target", deployment_id="test-deployment",
            policy_digest="a" * 64,
            issuer_keys={"mesh-issuer": self.mesh_key.public_key()},
            controller_keys={"controller": self.controller_key.public_key()},
            clock=lambda: self.now[0],
            require_fresh_lease=True, max_lease_seconds=10)
        self.mesh_path = str(self.path / "mesh.sqlite")
        self.mesh = GMeshProtocolHandler(self.mesh_path, **self.mesh_opts)
        self.sink = LeasedFilesystemEffect(
            self.g3, str(self.directory), mesh=self.mesh)

    def tearDown(self):
        self.sink.close()
        self.mesh.close()
        self.g3.close()
        self.temp.cleanup()

    def lease(self, seq=1, until=25):
        packet = dict(
            protocol=PROTOCOL, type="lease", source_node_id="controller",
            target_node_id="local-target", deployment_id="test-deployment",
            policy_digest="a"*64, generation=1, sequence=seq,
            not_after=until)
        return self.mesh.install_authority_lease(
            packet, self.controller_key.sign(encode_body(packet)))

    def packet(self, seq=1, *, event=None):
        event = self.event if event is None else event
        body = dict(
            protocol=PROTOCOL, type="handshake",
            source_node_id="mesh-issuer", target_node_id="local-target",
            deployment_id="test-deployment", event_digest=digest(event),
            policy_digest="a"*64, authority_ref="auth-lesson",
            generation=1, sequence=seq, not_after=100,
            attestation_ref="unverified-fixture")
        return body, self.mesh_key.sign(encode_body(body))

    def effect(self, seq=1, *, event=None, permit=None):
        packet, signature = self.packet(seq, event=event)
        return self.sink.apply_marker(
            self.event if event is None else event, now=self.now[0],
            permit=self.permit if permit is None else permit,
            mesh_handshake=packet, mesh_signature=signature)

    def admit(self):
        self.assertTrue(self.g3.apply(
            self.event, now=20, permit=self.permit)["ok"])

    def marker_present(self):
        return bool(list(self.directory.iterdir()))

    def test_missing_lease_denies_real_effect_without_journal_write(self):
        self.admit()
        r = self.effect()
        self.assertEqual(r["code"], "mesh_FAIL_CLOSED_lease_unavailable")
        self.assertFalse(self.marker_present())
        self.assertEqual(self.g3.effect_count(), 0)

    def test_bounded_lease_allows_exactly_one_marker(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        self.assertEqual(self.effect()["code"], "filesystem_marker_applied")
        self.assertTrue(self.marker_present())
        self.assertEqual(self.g3.effect_count(), 1)
        self.assertEqual(self.effect()["code"], "mesh_nonce_replay")
        self.assertEqual(len(list(self.directory.iterdir())), 1)

    def test_expired_remote_lease_during_partition_blocks_marker(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        self.now[0] = 25
        self.assertEqual(self.effect()["code"],
                         "mesh_FAIL_CLOSED_lease_unavailable")
        self.assertFalse(self.marker_present())
        self.assertEqual(self.g3.effect_count(), 0)

    def test_local_authenticated_hold_denies_real_effect(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        msg = dict(protocol=PROTOCOL, type="revoke",
                   source_node_id="controller", target_node_id="local-target",
                   deployment_id="test-deployment", authority_ref="auth-lesson",
                   generation=2, sequence=1, reason_code="TEST_HOLD")
        self.assertTrue(self.mesh.handle_revocation_broadcast(
            msg, self.controller_key.sign(encode_body(msg)))[0])
        self.assertEqual(self.effect()["code"], "mesh_FAIL_CLOSED_local_hold")
        self.assertFalse(self.marker_present())

    def test_invalid_g3_permit_cannot_write_under_valid_mesh_lease(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        invalid = dict(self.permit, signature="0"*128)
        self.assertEqual(self.effect(permit=invalid)["code"],
                         "invalid_permit_at_effect")
        self.assertFalse(self.marker_present())

    def test_signed_mesh_envelope_cannot_authorize_different_event(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        body, signature = self.packet()
        substituted = dict(self.event, event_id="forged")
        outcome = self.sink.apply_marker(
            substituted, now=20, permit=self.permit,
            mesh_handshake=body, mesh_signature=signature)
        self.assertEqual(outcome["code"], "mesh_effect_digest_mismatch")
        self.assertFalse(self.marker_present())

    def test_mesh_state_restart_does_not_restore_expired_lease(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        self.now[0] = 25
        self.mesh.close()
        self.mesh = GMeshProtocolHandler(self.mesh_path, **self.mesh_opts)
        self.sink.mesh = self.mesh
        self.assertEqual(self.effect()["code"],
                         "mesh_FAIL_CLOSED_lease_unavailable")
        self.assertFalse(self.marker_present())

    def test_broker_denies_missing_mesh_envelope_and_accepts_signed_one(self):
        self.admit()
        self.assertTrue(self.lease()[0])
        broker_path = str(self.path / "broker.sock")
        # This is an in-process integration test, not multi-UID isolation.
        broker = SyntheticBroker(
            broker_path, self.g3, allowed_client_uids={os.geteuid()},
            clock=lambda: self.now[0], effect_sink=self.sink)
        server_thread = threading.Thread(
            target=broker.serve_forever, daemon=True)
        server_thread.start()

        def request(body):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect(broker_path)
                sock.sendall(json.dumps(body).encode() + b"\n")
                response = bytearray()
                while not response.endswith(b"\n"):
                    part = sock.recv(4096)
                    if not part: break
                    response.extend(part)
            return json.loads(response)

        try:
            base = dict(op="effect_marker", event=self.event,
                        permit=self.permit)
            self.assertEqual(request(base)["code"], "bad_request")
            self.assertFalse(self.marker_present())
            self.assertEqual(request(dict(base, mesh_handshake={},
                        mesh_signature="0"*128))["code"],
                        "mesh_effect_digest_mismatch")
            self.assertFalse(self.marker_present())
            packet, signature = self.packet()
            correct = dict(base, mesh_handshake=packet,
                           mesh_signature=signature.hex())
            self.assertEqual(request(correct)["code"],
                             "filesystem_marker_applied")
            self.assertEqual(request(correct)["code"], "mesh_nonce_replay")
            self.assertEqual(self.g3.effect_count(), 1)
        finally:
            broker.shutdown()
            broker.server_close()
            server_thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
