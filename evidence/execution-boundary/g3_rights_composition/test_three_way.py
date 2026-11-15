"""Research negative controls for a same-event, signed rights + veto join."""
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from g3_authority_evidence.authority_evidence import DOMAIN, encode_claim
from g3_rights_veto.rights_veto import RightsVetoJournal
from g3_rights_veto.external_checkpoint import DOMAIN as CP_DOMAIN, canonical_checkpoint, journal_snapshot
from g3_rights_composition.three_way import inspect_three_way


class ThreeWayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"veto.sqlite"
        self.j=RightsVetoJournal(self.path,initialize=True)
        self.addCleanup(self.j.close)
        self.issuer=Ed25519PrivateKey.generate()
        self.anchor=Ed25519PrivateKey.generate()
        self.claim=dict(domain=DOMAIN,issuer="issuer",serial="r1",subject="p1",
            action="publish",effect_digest="a"*64,scope="pilot",purpose="lesson",
            not_before=10,not_after=30,revocation_generation=0)
        self.record=dict(subject="p1",action="publish",effect_digest="a"*64,
            scope="pilot",purpose="lesson",decision="allow",authority_kind="self",
            verified_identity=True,capacity_reviewed=True,voluntariness_reviewed=True,
            delegation_verified=False,revoked=False,not_before=10,not_after=30,
            generation=0,provenance_ref="review")
        self.args=dict(record_ref="r1",public_keys={"issuer":self.issuer.public_key()},
            revoked_serials=set(),trusted_records={"r1":self.record},
            current_generation=0,now=15,subject="p1",action="publish",
            effect_digest="a"*64,scope="pilot",purpose="lesson",emergency_hold=False,
            veto_journal=self.j,veto_db_path=self.path,checkpoint_packet=self.checkpoint(),
            pinned_checkpoint_key=self.anchor.public_key(),deployment="pilot",
            trusted_generation_floor=0)

    def signed(self):
        return dict(claim=self.claim.copy(),signature=self.issuer.sign(
            encode_claim(self.claim)).hex())

    def checkpoint(self):
        generation,digest=journal_snapshot(self.path)
        msg=dict(domain=CP_DOMAIN,deployment="pilot",generation=generation,digest=digest)
        return dict(checkpoint=msg,signature=self.anchor.sign(canonical_checkpoint(msg)).hex())

    def check(self,**overrides):
        args=dict(self.args)
        args.update(overrides)
        return inspect_three_way(self.signed(),**args)

    def test_positive_match_never_authorizes(self):
        r=self.check()
        self.assertTrue(r["three_way_evidence_consistent"])
        self.assertFalse(r["authorizes_effect"])
        self.assertFalse(r["authentic_consent_proved"])
        self.assertFalse(r["original_six_x3_proved"])

    def test_missing_checkpoint_denied(self):
        r=self.check(checkpoint_packet={})
        self.assertFalse(r["three_way_evidence_consistent"])
        self.assertFalse(r["authorizes_effect"])

    def test_wrong_signer_denied(self):
        r=self.check(pinned_checkpoint_key=Ed25519PrivateKey.generate().public_key())
        self.assertEqual(r["code"],"checkpoint_checkpoint_not_verified")

    def test_wrong_rights_particular_denied(self):
        changed=dict(self.record,subject="other")
        r=self.check(trusted_records={"r1":changed})
        self.assertEqual(r["code"],"joined_rights_request_rights_mismatch")

    def test_emergency_hold_denied(self):
        self.assertEqual(self.check(emergency_hold=True)["code"],
                         "emergency_hold_or_invalid")

    def test_revoked_claim_denied(self):
        self.assertEqual(self.check(revoked_serials={"r1"})["code"],
                         "joined_signature_revoked_record")

    def test_generation_mismatch_denied(self):
        self.assertEqual(self.check(current_generation=1)["code"],
                         "checkpoint_rights_generation_mismatch")

    def test_withdrawn_right_denied_after_matching_fresh_checkpoint(self):
        self.assertTrue(self.j.record_withdrawal(
            record_ref="r1",subject="p1",action="publish",effect_digest="a"*64,
            generation=1)["ok"])
        self.claim["revocation_generation"]=1
        updated=dict(self.record,generation=1)
        result=self.check(current_generation=1,trusted_records={"r1":updated},
                          checkpoint_packet=self.checkpoint())
        self.assertEqual(result["code"],"veto_record_withdrawn")
        self.assertFalse(result["three_way_evidence_consistent"])

    def test_stale_checkpoint_rejected(self):
        self.assertTrue(self.j.record_withdrawal(
            record_ref="other",subject="p1",action="publish",effect_digest="b"*64,
            generation=1)["ok"])
        self.assertFalse(self.check()["three_way_evidence_consistent"])

    def test_two_different_same_generation_journals_cannot_be_combined(self):
        # Journal A is checkpointed and contains the actual r1 withdrawal.
        # Journal B has a different withdrawal at the same generation, so a
        # naive two-database join reports no local veto for r1.
        self.assertTrue(self.j.record_withdrawal(
            record_ref="r1", subject="p1", action="publish",
            effect_digest="a"*64, generation=1)["ok"])
        latest = self.checkpoint()
        other_path = Path(self.tmp.name) / "decoy.sqlite"
        decoy = RightsVetoJournal(other_path, initialize=True)
        self.addCleanup(decoy.close)
        self.assertTrue(decoy.record_withdrawal(
            record_ref="other", subject="p1", action="publish",
            effect_digest="b"*64, generation=1)["ok"])
        self.claim["revocation_generation"] = 1
        updated = dict(self.record, generation=1)
        result = self.check(
            veto_journal=decoy, veto_db_path=self.path,
            current_generation=1, trusted_records={"r1": updated},
            checkpoint_packet=latest, trusted_generation_floor=1)
        self.assertEqual(result["code"], "veto_journal_identity_mismatch")
        self.assertFalse(result["three_way_evidence_consistent"])
        self.assertFalse(result["authorizes_effect"])

    def test_checkpoint_path_substitution_rejected(self):
        other_path = Path(self.tmp.name) / "other.sqlite"
        other = RightsVetoJournal(other_path, initialize=True)
        self.addCleanup(other.close)
        result = self.check(veto_db_path=other_path)
        self.assertEqual(result["code"], "veto_journal_identity_mismatch")

    def test_symlink_checkpoint_path_rejected(self):
        alias = Path(self.tmp.name) / "alias.sqlite"
        alias.symlink_to(self.path)
        result = self.check(veto_db_path=alias)
        self.assertEqual(result["code"], "veto_journal_identity_mismatch")

    def test_withdrawal_between_veto_read_and_postcheck_denied(self):
        # Simulate a trusted controller recording a withdrawal right after
        # the first local veto read but before checkpoint re-verification.
        original = self.j.inspect
        def inspect_then_withdraw(**kwargs):
            result = original(**kwargs)
            inserted = self.j.record_withdrawal(
                record_ref="r1", subject="p1", action="publish",
                effect_digest="a"*64, generation=1)
            self.assertTrue(inserted["ok"])
            return result
        self.j.inspect = inspect_then_withdraw
        self.addCleanup(lambda: setattr(self.j, "inspect", original))
        result = self.check()
        self.assertEqual(result["code"],
                         "postcheck_journal_checkpoint_mismatch")
        self.assertFalse(result["three_way_evidence_consistent"])
        self.assertFalse(result["authorizes_effect"])

    def test_stale_floor_rejected(self):
        self.assertEqual(self.check(trusted_generation_floor=1)["code"],
                         "stale_rights_generation")


if __name__=="__main__":
    unittest.main()
