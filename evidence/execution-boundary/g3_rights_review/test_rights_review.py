"""Negative controls: evidence matching is not consent or authorization."""
import unittest
from rights_review import review

class RightsReviewTests(unittest.TestCase):
    def setUp(self):
        self.record = dict(subject="person-1", action="publish-document",
            scope="offline-course", purpose="lesson", effect_digest="a"*64,
            decision="allow", authority_kind="self", verified_identity=True,
            capacity_reviewed=True, voluntariness_reviewed=True,
            delegation_verified=False, revoked=False, not_before=10,
            not_after=30, generation=3, provenance_ref="review-123")
        self.kw = dict(trusted_records={"r1": self.record},
            subject="person-1", action="publish-document",
            scope="offline-course", purpose="lesson", effect_digest="a"*64,
            now=20, current_generation=3)
    def check(self, **changes):
        opts = dict(self.kw)
        opts.update(changes)
        return review({"record_ref":"r1"}, **opts)
    def test_complete_record_never_grants_effect_or_proves_consent(self):
        r=self.check()
        self.assertTrue(r["review_complete"])
        self.assertFalse(r["authorizes_effect"])
        self.assertFalse(r["authentic_consent_proved"])
        self.assertFalse(r["original_six_x3_proved"])
    def test_subject_action_scope_purpose_content_mismatch(self):
        for field,value in (("subject","person-2"),("action","delete"),
                            ("scope","other-course"),("purpose","marketing"),
                            ("effect_digest","b"*64)):
            with self.subTest(field=field):
                self.assertEqual(self.check(**{field:value})["code"],
                                 "request_rights_mismatch")
    def test_denial_and_withdrawal_override_other_checks(self):
        for decision in ("deny","withdrawn"):
            with self.subTest(decision=decision):
                records={"r1":dict(self.record,decision=decision)}
                self.assertEqual(self.check(trusted_records=records)["code"],
                                 "rights_denied_or_withdrawn")
    def test_revoked_and_emergency_hold(self):
        self.assertEqual(self.check(trusted_records={
            "r1":dict(self.record,revoked=True)})["code"],
            "rights_denied_or_withdrawn")
        self.assertEqual(self.check(emergency_hold=True)["code"],"emergency_hold")
    def test_expiry_and_generation(self):
        self.assertEqual(self.check(now=30)["code"],"rights_expired_or_future")
        self.assertEqual(self.check(now=9)["code"],"rights_expired_or_future")
        self.assertEqual(self.check(current_generation=4)["code"],"rights_generation_stale")
    def test_identity_voluntariness_and_capacity(self):
        for key,code in (("verified_identity","identity_unverified"),
                         ("capacity_reviewed","capacity_or_voluntariness_unreviewed"),
                         ("voluntariness_reviewed","capacity_or_voluntariness_unreviewed")):
            with self.subTest(key=key):
                self.assertEqual(self.check(trusted_records={
                    "r1":dict(self.record,**{key:False})})["code"],code)
    def test_representative_requires_delegation(self):
        records={"r1":dict(self.record,authority_kind="representative")}
        self.assertEqual(self.check(trusted_records=records)["code"],"delegation_unverified")
        records["r1"]["delegation_verified"]=True
        self.assertTrue(self.check(trusted_records=records)["review_complete"])
    def test_unknown_reference_denied(self):
        self.assertEqual(review({"record_ref":"other"},**self.kw)["code"],
                         "trusted_record_missing_or_invalid")
    def test_untrusted_request_does_not_supply_own_rights(self):
        packet={"record_ref":"r1", "decision":"allow"}
        self.assertEqual(review(packet,**self.kw)["code"],"request_schema")
    def test_malformed_values_and_bool_generation_denied(self):
        self.assertEqual(self.check(now=True)["code"],"trusted_inputs_invalid")
        self.assertEqual(self.check(trusted_records={"r1":dict(self.record,
            revoked="false")})["code"],"trusted_record_invalid")
        self.assertEqual(self.check(trusted_records={"r1":dict(self.record,
            generation=True)})["code"],"trusted_record_invalid")

if __name__=="__main__":
    unittest.main()
