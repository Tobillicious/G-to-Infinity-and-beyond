"""Hostile composition tests: no self-asserted rights or cross-event substitution."""
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from g3_authority_evidence.authority_evidence import DOMAIN, encode_claim
from g3_rights_composition.same_event import inspect_same_event


class SameEventTests(unittest.TestCase):
    def setUp(self):
        self.key = Ed25519PrivateKey.generate()
        self.claim = dict(
            domain=DOMAIN, issuer="issuer-1", serial="rights-1",
            subject="author-1", action="publish-html", effect_digest="a"*64,
            scope="pilot-1", purpose="lesson", not_before=10, not_after=30,
            revocation_generation=4)
        self.packet = self.sign(self.claim)
        self.record = dict(
            subject="author-1", action="publish-html", effect_digest="a"*64,
            scope="pilot-1", purpose="lesson", decision="allow",
            authority_kind="self", verified_identity=True,
            capacity_reviewed=True, voluntariness_reviewed=True,
            delegation_verified=False, revoked=False, not_before=10,
            not_after=30, generation=4, provenance_ref="review-1")
        self.kw = dict(
            record_ref="rights-1", public_keys={"issuer-1":self.key.public_key()},
            revoked_serials=set(), trusted_records={"rights-1":self.record},
            current_generation=4, now=15, subject="author-1",
            action="publish-html", effect_digest="a"*64, scope="pilot-1",
            purpose="lesson")

    def sign(self, claim):
        return {"claim":copy.deepcopy(claim),
                "signature":self.key.sign(encode_claim(claim)).hex()}

    def check(self, packet=None, **changes):
        kwargs=dict(self.kw)
        kwargs.update(changes)
        return inspect_same_event(self.packet if packet is None else packet,**kwargs)

    def test_matching_records_are_never_execution_authority(self):
        x=self.check()
        self.assertTrue(x["signed_and_rights_records_match"])
        self.assertFalse(x["authorizes_effect"])
        self.assertFalse(x["authentic_consent_proved"])
        self.assertFalse(x["original_six_x3_proved"])

    def test_signed_claim_for_different_rights_record_denied(self):
        x=self.check(record_ref="rights-other",trusted_records={
            "rights-other":self.record})
        self.assertEqual(x["code"],"signed_serial_rights_reference_mismatch")

    def test_different_subject_action_content_scope_and_purpose_denied(self):
        for key,value in [("subject","author-other"),("action","delete"),
                          ("effect_digest","b"*64),("scope","other-pilot"),
                          ("purpose","advertising")]:
            with self.subTest(key=key):
                altered=dict(self.record,**{key:value})
                result=self.check(trusted_records={"rights-1":altered})
                self.assertEqual(result["code"],"rights_request_rights_mismatch")
                self.assertFalse(result["signed_and_rights_records_match"])

    def test_forged_and_stale_signed_claim_denied(self):
        changed=dict(self.claim,subject="other")
        forged=copy.deepcopy(self.packet)
        forged["claim"]=changed
        self.assertEqual(self.check(forged)["code"],"signature_invalid_signature")
        self.assertEqual(self.check(current_generation=5)["code"],
                         "signature_stale_revocation_generation")

    def test_rights_revocation_deny_and_withdrawn(self):
        for changed in [dict(self.record,revoked=True),
                        dict(self.record,decision="deny"),
                        dict(self.record,decision="withdrawn")]:
            with self.subTest(changed=changed["decision"]):
                result=self.check(trusted_records={"rights-1":changed})
                self.assertEqual(result["code"],"rights_rights_denied_or_withdrawn")

    def test_revoked_signed_serial_rejected(self):
        self.assertEqual(self.check(revoked_serials={"rights-1"})["code"],
                         "signature_revoked_record")

    def test_emergency_hold_is_authoritative_veto(self):
        result=self.check(emergency_hold=True)
        self.assertEqual(result["code"],"emergency_hold")
        self.assertFalse(result["authorizes_effect"])

    def test_rights_expiry_and_delegation(self):
        self.assertEqual(self.check(now=30)["code"],"signature_expired_or_not_yet_valid")
        changed=dict(self.record,authority_kind="representative",
                     delegation_verified=False)
        self.assertEqual(self.check(trusted_records={"rights-1":changed})["code"],
                         "rights_delegation_unverified")

    def test_missing_rights_and_unverified_identity(self):
        self.assertEqual(self.check(trusted_records={})["code"],
                         "rights_trusted_record_missing_or_invalid")
        changed=dict(self.record,verified_identity=False)
        self.assertEqual(self.check(trusted_records={"rights-1":changed})["code"],
                         "rights_identity_unverified")

    def test_untrusted_claim_cannot_insert_rights(self):
        malicious=copy.deepcopy(self.packet)
        malicious["rights_record"]=self.record
        self.assertEqual(self.check(malicious)["code"],"packet_schema")

    def test_record_generation_mismatch_is_denied(self):
        changed=dict(self.record,generation=3)
        self.assertEqual(self.check(trusted_records={"rights-1":changed})["code"],
                         "rights_rights_generation_stale")


if __name__=="__main__":
    unittest.main()
