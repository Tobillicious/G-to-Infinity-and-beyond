"""Synthetic ephemeral-key tests only; no actual reviewer or release signature."""
import json
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from g3_r7_external_review_signature import DOMAIN, verify

HEAD = "a" * 40
DIGEST = "b" * 64


class R7ReviewSignatureTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key().public_bytes(
            encoding=Encoding.Raw, format=PublicFormat.Raw)
        self.doc = {
            "schema": "g3-r7-external-review-v1",
            "source_commit": HEAD,
            "evidence_sha256": DIGEST,
            "scope": "synthetic disposable CI fixture only",
            "decision": "HOLD_UNRESOLVED",
            "reviewer_identifier": "synthetic-test-key-not-an-external-reviewer",
            "reviewed_at_utc": "2026-11-18T00:00:00Z",
            "findings": "Synthetic test: no independently administered custody",
        }

    def signed(self, body=None, *, pubkey=None, sig=None):
        body = body if body is not None else json.dumps(self.doc, sort_keys=True).encode()
        sig = sig if sig is not None else self.private.sign(DOMAIN + body)
        return verify(review_bytes=body, signature=sig,
                      reviewer_public_key=pubkey if pubkey is not None else self.public,
                      expected_head=HEAD, expected_evidence_sha256=DIGEST)

    def test_valid_signature_still_does_not_certify_or_authorize(self):
        receipt = self.signed()
        self.assertTrue(receipt["signature_valid_for_supplied_public_key"])
        self.assertEqual(receipt["decision"], "HOLD_UNRESOLVED")
        for key in ("independent_reviewer_identity_verified",
                    "independent_administration_verified",
                    "authentic_six_duties_verified",
                    "full_effect_path_coverage_proved",
                    "certified_for_production", "authorizes_effect"):
            self.assertFalse(receipt[key])

    def test_wrong_public_key_rejected(self):
        other = Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=Encoding.Raw, format=PublicFormat.Raw)
        with self.assertRaisesRegex(ValueError, "signature mismatch"):
            self.signed(pubkey=other)

    def test_tampered_review_rejected(self):
        body = json.dumps(self.doc, sort_keys=True).encode()
        sig = self.private.sign(DOMAIN + body)
        modified = body.replace(b"HOLD_UNRESOLVED", b"ACCEPT_BOUNDED_RESEARCH")
        with self.assertRaisesRegex(ValueError, "signature mismatch"):
            self.signed(modified, sig=sig)

    def test_stale_source_head_rejected(self):
        self.doc["source_commit"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "pinned source"):
            self.signed()

    def test_other_evidence_digest_rejected(self):
        self.doc["evidence_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "pinned source"):
            self.signed()

    def test_non_bounded_accept_decision_rejected(self):
        self.doc["decision"] = "PRODUCTION_ACCEPT"
        with self.assertRaisesRegex(ValueError, "unsupported review"):
            self.signed()

    def test_duplicate_json_keys_rejected_even_if_signed(self):
        raw = json.dumps(self.doc).encode()
        raw = raw[:-1] + b',"decision":"HOLD_UNRESOLVED"}'
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.signed(raw)

    def test_missing_scope_rejected(self):
        self.doc["scope"] = ""
        with self.assertRaisesRegex(ValueError, "review detail"):
            self.signed()

    def test_wrong_domain_signature_rejected(self):
        body = json.dumps(self.doc, sort_keys=True).encode()
        with self.assertRaisesRegex(ValueError, "signature mismatch"):
            self.signed(body, sig=self.private.sign(body))

    def test_missing_key_or_bad_sig_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid detached"):
            self.signed(pubkey=b"\x00" * 4)
        with self.assertRaisesRegex(ValueError, "invalid detached"):
            self.signed(sig=b"\x00" * 4)

    def test_signed_bounded_accept_is_not_production_certificate(self):
        self.doc["decision"] = "ACCEPT_BOUNDED_RESEARCH"
        receipt = self.signed()
        self.assertEqual(receipt["decision"], "ACCEPT_BOUNDED_RESEARCH")
        self.assertFalse(receipt["certified_for_production"])
        self.assertFalse(receipt["independent_reviewer_identity_verified"])


if __name__ == "__main__":
    unittest.main()
