"""Adversarial offline G-Mesh v0 checks: no federation or provider IO."""
import copy
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from g_mesh_protocol import (
    GMeshProtocolHandler, GMeshState, PROTOCOL, encode_body,
)
from g_mesh_provider import GMeshProviderRegistry, ProviderConfig


class TestMeshProtocol(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mesh-")
        self.path = str(Path(self.temp.name) / "mesh.sqlite")
        self.issuer = Ed25519PrivateKey.generate()
        self.controller = Ed25519PrivateKey.generate()
        self.opts = dict(
            node_id="node-alpha", deployment_id="sandbox-only",
            policy_digest="a" * 64,
            issuer_keys={"node-beta": self.issuer.public_key()},
            controller_keys={"node-gamma": self.controller.public_key()},
            clock=lambda: 20)
        self.handler = GMeshProtocolHandler(self.path, **self.opts)
        self.payload = dict(
            protocol=PROTOCOL, type="handshake",
            source_node_id="node-beta", target_node_id="node-alpha",
            deployment_id="sandbox-only", event_digest="b" * 64,
            policy_digest="a" * 64, authority_ref="auth-local",
            generation=1, sequence=100, not_after=50,
            attestation_ref="unverified-fixture-reference")

    def tearDown(self):
        self.handler.close()
        self.temp.cleanup()

    def signed(self, payload, signer=None):
        signer = self.issuer if signer is None else signer
        return signer.sign(encode_body(payload))

    def revocation(self, sequence=1):
        return dict(
            protocol=PROTOCOL, type="revoke",
            source_node_id="node-gamma", target_node_id="node-alpha",
            deployment_id="sandbox-only", authority_ref="auth-local",
            generation=2, sequence=sequence,
            reason_code="TEST_EMERGENCY_HOLD")

    def test_valid_handshake_and_durable_replay_rejection(self):
        sig = self.signed(self.payload)
        accepted, msg = self.handler.process_handshake(
            self.payload, sig, encode_body(self.payload))
        self.assertTrue(accepted, msg)
        self.assertEqual(self.handler.state, GMeshState.IDLE)
        self.assertEqual(
            self.handler.process_handshake(self.payload, sig)[1], "nonce_replay")
        self.handler.close()
        self.handler = GMeshProtocolHandler(self.path, **self.opts)
        self.assertEqual(
            self.handler.process_handshake(self.payload, sig)[1], "nonce_replay")
        later = dict(self.payload, sequence=101)
        self.assertTrue(self.handler.process_handshake(
            later, self.signed(later))[0])

    def test_schema_unknown_field_wrong_target_and_expiry(self):
        for candidate in (
                {"protocol": PROTOCOL}, dict(self.payload, extra="test"),
                dict(self.payload, target_node_id="some-other-node"),
                dict(self.payload, sequence=True),
                dict(self.payload, event_digest="malformed"),
                dict(self.payload, policy_digest="f" * 64)):
            self.assertEqual(self.handler.process_handshake(
                candidate, self.signed(candidate))[1], "schema_rejected")
        expired = dict(self.payload, not_after=20)
        self.assertEqual(self.handler.process_handshake(
            expired, self.signed(expired))[1], "expired")

    def test_invalid_signature_wrong_peer_and_canonical_mismatch(self):
        wrong = Ed25519PrivateKey.generate()
        self.assertEqual(self.handler.process_handshake(
            self.payload, self.signed(self.payload, wrong))[1],
            "invalid_signature")
        self.assertEqual(self.handler.process_handshake(
            self.payload, self.signed(self.payload), b"altered")[1],
            "invalid_signature")
        stranger = dict(self.payload, source_node_id="unregistered")
        self.assertEqual(self.handler.process_handshake(
            stranger, self.signed(stranger))[1], "invalid_signature")
        # Invalid network packets do not let strangers trigger a global halt.
        self.assertEqual(self.handler.state, GMeshState.IDLE)

    def test_authenticated_revocation_and_halt_survive_restart(self):
        rev = self.revocation()
        self.assertEqual(self.handler.handle_revocation_broadcast(
            rev, self.controller.sign(encode_body(rev)))[1],
            "local_revocation_committed")
        self.assertEqual(self.handler.state, GMeshState.REVOKED_HALTED)
        self.assertEqual(self.handler.process_handshake(
            self.payload, self.signed(self.payload))[1],
            "FAIL_CLOSED_local_hold")
        self.handler.close()
        self.handler = GMeshProtocolHandler(self.path, **self.opts)
        self.assertEqual(self.handler.state, GMeshState.REVOKED_HALTED)
        self.assertEqual(self.handler.handle_revocation_broadcast(
            rev, self.controller.sign(encode_body(rev)))[1],
            "stale_controller_sequence")

    def test_forged_revocation_cannot_halt_and_wrong_stream_rejected(self):
        rev = self.revocation()
        self.assertEqual(self.handler.handle_revocation_broadcast(
            rev, self.issuer.sign(encode_body(rev)))[1],
            "invalid_controller_signature")
        other = dict(rev, target_node_id="node-elsewhere")
        self.assertEqual(self.handler.handle_revocation_broadcast(
            other, self.controller.sign(encode_body(other)))[1],
            "invalid_revocation_schema")
        self.assertEqual(self.handler.state, GMeshState.IDLE)

    def test_offline_provider_registry_routes_untrusted_candidates_only(self):
        called = []
        def mock(prompt, model):
            called.append((prompt, model))
            return "Fixture output (not an effect authorization)"
        registry = GMeshProviderRegistry(self.handler)
        registry.register_provider(
            ProviderConfig("offline-ollama", "ollama-mock", "fixture-model"),
            mock)
        adapter = registry.get_provider("offline-ollama")
        valid, output = adapter.invoke_protected_model(
            "test", self.payload, self.signed(self.payload))
        self.assertTrue(valid, output)
        self.assertFalse(output["verified_for_effects"])
        self.assertEqual(len(called), 1)
        with self.assertRaises(ValueError):
            registry.get_provider("unknown")
        valid, why = adapter.invoke_protected_model(
            "test", self.payload, self.signed(self.payload))
        self.assertFalse(valid)
        self.assertEqual(why, "nonce_replay")
        self.assertEqual(len(called), 1)

    def test_offline_provider_never_called_when_revoked(self):
        called = []
        registry = GMeshProviderRegistry(self.handler)
        registry.register_provider(
            ProviderConfig("mock", "mock", "mock-model"),
            lambda prompt, model: called.append((prompt, model)) or "text")
        revoke = self.revocation()
        self.handler.handle_revocation_broadcast(
            revoke, self.controller.sign(encode_body(revoke)))
        accepted, reason = registry.get_provider("mock").invoke_protected_model(
            "test", self.payload, self.signed(self.payload))
        self.assertFalse(accepted)
        self.assertEqual(reason, "FAIL_CLOSED_local_hold")
        self.assertEqual(called, [])

    def test_concurrent_hold_during_mock_inference_blocks_candidate(self):
        def mock(prompt, model):
            revoke = self.revocation()
            self.handler.handle_revocation_broadcast(
                revoke, self.controller.sign(encode_body(revoke)))
            return "This must not be returned"
        registry = GMeshProviderRegistry(self.handler)
        registry.register_provider(
            ProviderConfig("mock", "mock", "mock-model"), mock)
        accepted, reason = registry.get_provider("mock").invoke_protected_model(
            "test", self.payload, self.signed(self.payload))
        self.assertFalse(accepted)
        self.assertEqual(reason, "FAIL_CLOSED_local_hold")
        self.assertEqual(self.handler.state, GMeshState.REVOKED_HALTED)


if __name__ == "__main__":
    unittest.main()
