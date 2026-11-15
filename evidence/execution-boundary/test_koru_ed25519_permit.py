"""Adversarial G3 Ed25519 permit integration tests. Purely synthetic."""
import copy
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_ed25519_permit import issue_ed25519, verify_ed25519
from koru_pilot_gate import PilotGate
from test_koru_shadow import fixtures


class TestG3PublicKeyPermit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.event, self.trusted = fixtures()
        self.private = Ed25519PrivateKey.generate()  # ephemeral only, never committed
        self.public = self.private.public_key()
        self.gate = PilotGate(
            str(Path(self.tmp.name) / "pilot.db"),
            contexts=self.trusted["contexts"],
            signatures=self.trusted["signatures"],
            witnesses=self.trusted["witnesses"],
            authorities=self.trusted["authorities"],
            provenances=self.trusted["provenances"],
            context_ref="ctx-one", generation=3,
            ed25519_public_key=self.public, permit_issuer="trusted-independent")
        self.permit = issue_ed25519(
            self.private, issuer="trusted-independent",
            event=self.event, expires_at=50)

    def tearDown(self):
        self.gate.close()
        self.tmp.cleanup()

    def test_signed_event_succeeds_only_once(self):
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "invalid_permit")
        self.assertTrue(self.gate.apply(self.event, now=20, permit=self.permit)["ok"])
        self.assertEqual(self.gate.apply(self.event, now=20, permit=self.permit)["code"],
                         "replay")
        self.assertEqual(self.gate.record_count(), 1)

    def test_wrong_issuer_wrong_key_and_expiry(self):
        self.assertFalse(verify_ed25519(self.public, self.permit,
                                        issuer="another-issuer", event=self.event, now=20))
        other = Ed25519PrivateKey.generate().public_key()
        self.assertFalse(verify_ed25519(other, self.permit,
                                        issuer="trusted-independent", event=self.event, now=20))
        self.assertEqual(self.gate.apply(self.event, now=50, permit=self.permit)["code"],
                         "invalid_permit")
        self.assertEqual(self.gate.record_count(), 0)

    def test_tamper_event_scope_and_context(self):
        event = copy.deepcopy(self.event)
        event["purpose"] = "altered"
        self.assertEqual(self.gate.apply(event, now=20, permit=self.permit)["code"],
                         "invalid_permit")
        event = copy.deepcopy(self.event)
        event["context_digest"] = "0" * 64
        self.assertEqual(self.gate.apply(event, now=20, permit=self.permit)["code"],
                         "stale_context")
        self.assertEqual(self.gate.record_count(), 0)

    def test_tamper_signature_and_expiry(self):
        for fake in (dict(self.permit, signature="0" * 128),
                     dict(self.permit, expires_at=900),
                     dict(self.permit, signature="bad"),
                     dict(self.permit, unknown="x")):
            self.assertEqual(self.gate.apply(self.event, now=20, permit=fake)["code"],
                             "invalid_permit")
        self.assertEqual(self.gate.record_count(), 0)

    def test_valid_signature_is_not_immune_to_revocation_or_hold(self):
        self.gate.revoke_authority("auth-lesson")
        self.assertEqual(self.gate.apply(self.event, now=20, permit=self.permit)["code"],
                         "authority_revoked")
        self.gate.hold(4)
        self.assertEqual(self.gate.apply(self.event, now=20, permit=self.permit)["code"],
                         "held")
        self.assertEqual(self.gate.record_count(), 0)

    def test_gate_has_no_private_signing_capability(self):
        self.assertFalse(hasattr(self.gate, "private_key"))
        self.assertFalse(hasattr(self.gate, "issue_permit"))
        self.assertTrue(verify_ed25519(self.public, self.permit,
                                       issuer="trusted-independent",
                                       event=self.event, now=20))


if __name__ == "__main__":
    unittest.main()
