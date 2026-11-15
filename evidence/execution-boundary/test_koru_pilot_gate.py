"""Controlled pilot negative controls. Run with:
python3 -B -m unittest discover -s evidence/execution-boundary -p 'test_koru_pilot_gate.py' -v
"""
import copy
import tempfile
import threading
import unittest
from pathlib import Path
from koru_shadow import digest
from koru_pilot_gate import PilotGate
from koru_pilot_permit import issue_permit, verify_permit
from test_koru_shadow import fixtures


class TestKoruPilotGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.event, self.trusted = fixtures()
        self.db_path = str(Path(self.tmp.name) / "pilot.sqlite")
        self.gate = PilotGate(self.db_path, contexts=self.trusted["contexts"],
                              signatures=self.trusted["signatures"],
                              witnesses=self.trusted["witnesses"],
                              authorities=self.trusted["authorities"],
                              provenances=self.trusted["provenances"],
                              context_ref="ctx-one", generation=3)

    def tearDown(self):
        self.gate.close()
        self.tmp.cleanup()

    def test_valid_commit_and_durable_replay_refusal(self):
        result = self.gate.apply(copy.deepcopy(self.event), now=20)
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(result["receipt"]), 64)
        self.assertEqual(self.gate.record_count(), 1)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "replay")
        self.gate.close()
        self.gate = PilotGate(self.db_path, contexts=self.trusted["contexts"],
                              signatures=self.trusted["signatures"],
                              witnesses=self.trusted["witnesses"],
                              authorities=self.trusted["authorities"],
                              provenances=self.trusted["provenances"],
                              context_ref="ctx-one", generation=1)
        self.assertEqual(self.gate.record_count(), 1)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "replay")

    def test_revoked_authority_cannot_commit(self):
        self.gate.revoke_authority("auth-lesson")
        result = self.gate.apply(self.event, now=20)
        self.assertEqual(result["code"], "authority_revoked")
        self.assertEqual(self.gate.record_count(), 0)

    def test_changed_whole_context_and_payload_cannot_commit(self):
        event = copy.deepcopy(self.event)
        event["action_expr"] = {"op": "identity", "args": [{"atom": "p1"}]}
        self.assertEqual(self.gate.apply(event, now=20)["code"], "trusted_witness")
        # Caller-owned fixture tampering does not change the gate's trusted copy.
        context = self.trusted["contexts"]["ctx-one"]
        context["positions"][5]["value"] += 1
        self.assertTrue(self.gate.apply(self.event, now=20)["ok"])
        self.assertEqual(self.gate.record_count(), 1)

    def test_revocation_survives_restart(self):
        self.gate.revoke_authority("auth-lesson")
        self.gate.close()
        self.gate = PilotGate(self.db_path, contexts=self.trusted["contexts"],
                              signatures=self.trusted["signatures"],
                              witnesses=self.trusted["witnesses"],
                              authorities=self.trusted["authorities"],
                              provenances=self.trusted["provenances"],
                              context_ref="ctx-one", generation=3)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "authority_revoked")
        self.assertEqual(self.gate.record_count(), 0)

    def test_external_registry_mutation_does_not_grant_privilege(self):
        self.gate.revoke_authority("auth-lesson")
        self.trusted["authorities"]["auth-lesson"]["active"] = True
        self.trusted["witnesses"].clear()
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "authority_revoked")
        self.assertEqual(self.gate.record_count(), 0)

    def test_revoke_serializes_with_apply(self):
        outcomes = []
        barrier = threading.Barrier(2)
        def apply():
            barrier.wait()
            outcomes.append(self.gate.apply(copy.deepcopy(self.event), now=20))
        def revoke():
            barrier.wait()
            self.gate.revoke_authority("auth-lesson")
        a = threading.Thread(target=apply)
        b = threading.Thread(target=revoke)
        a.start()
        b.start()
        a.join()
        b.join()
        # Both linearization orders are legitimate: applied-before-revoked
        # or revoked-before-applied; after revocation, never admit again.
        self.assertIn(outcomes[0]["code"], ("durable_synthetic_record", "authority_revoked"))
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "authority_revoked")

    def test_audit_detects_tampered_record_and_fails_closed(self):
        self.assertEqual(self.gate.audit()["code"], "local_consistency_only")
        self.assertTrue(self.gate.apply(self.event, now=20)["ok"])
        self.gate.db.execute(
            "UPDATE records SET payload_digest=? WHERE event_id=?",
            ("0" * 64, self.event["event_id"]))
        self.assertEqual(self.gate.audit()["code"], "record_integrity")
        other = copy.deepcopy(self.event)
        other["event_id"] = "new-id"
        self.assertEqual(self.gate.apply(other, now=20)["code"], "record_integrity")
        self.assertEqual(self.gate.record_count(), 1)

    def test_audit_detects_modified_durable_context(self):
        self.gate.db.execute(
            "UPDATE gate_state SET context_digest=? WHERE id=1",
            ("f" * 64,))
        self.assertEqual(self.gate.audit()["code"], "trusted_context_mismatch")
        self.assertEqual(self.gate.apply(self.event, now=20)["code"],
                         "trusted_context_mismatch")
        self.assertEqual(self.gate.record_count(), 0)

    def test_audit_detects_tampered_receipt(self):
        self.assertTrue(self.gate.apply(self.event, now=20)["ok"])
        self.gate.db.execute(
            "UPDATE records SET receipt=? WHERE event_id=?",
            ("x" * 64, self.event["event_id"]))
        self.assertEqual(self.gate.audit()["code"], "record_integrity")

    def test_authenticated_event_permit_admission(self):
        key = b"A" * 32  # test fixture ONLY, never a production secret
        self.gate.close()
        self.gate = PilotGate(
            self.db_path, contexts=self.trusted["contexts"],
            signatures=self.trusted["signatures"],
            witnesses=self.trusted["witnesses"],
            authorities=self.trusted["authorities"],
            provenances=self.trusted["provenances"],
            context_ref="ctx-one", generation=3,
            permit_verification_key=key, permit_issuer="test-independent-issuer")
        permit = issue_permit(key, issuer="test-independent-issuer",
                              event=self.event, expires_at=40)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "invalid_permit")
        self.assertEqual(self.gate.apply(self.event, now=40, permit=permit)["code"],
                         "invalid_permit")
        self.assertFalse(verify_permit(key, permit,
                                     issuer="wrong-issuer", event=self.event, now=20))
        self.assertTrue(self.gate.apply(self.event, now=20, permit=permit)["ok"])
        self.assertEqual(self.gate.apply(self.event, now=20, permit=permit)["code"], "replay")

    def test_permit_forgery_event_binding_and_revocation(self):
        key = b"B" * 32
        self.gate.close()
        self.gate = PilotGate(
            self.db_path, contexts=self.trusted["contexts"],
            signatures=self.trusted["signatures"],
            witnesses=self.trusted["witnesses"],
            authorities=self.trusted["authorities"],
            provenances=self.trusted["provenances"],
            context_ref="ctx-one", generation=3,
            permit_verification_key=key, permit_issuer="authority-pilot")
        permit = issue_permit(key, issuer="authority-pilot",
                              event=self.event, expires_at=50)
        changed = copy.deepcopy(self.event)
        changed["purpose"] = "other"
        self.assertEqual(self.gate.apply(changed, now=20, permit=permit)["code"],
                         "invalid_permit")
        forged = dict(permit, mac="0" * 64)
        self.assertEqual(self.gate.apply(self.event, now=20, permit=forged)["code"],
                         "invalid_permit")
        self.gate.revoke_authority("auth-lesson")
        self.assertEqual(self.gate.apply(self.event, now=20, permit=permit)["code"],
                         "authority_revoked")
        self.assertEqual(self.gate.record_count(), 0)

    def test_signed_permit_rejects_tampered_scope_and_expiry(self):
        key = b"C" * 32
        permit = issue_permit(key, issuer="trusted-issuer", event=self.event,
                              expires_at=80)
        self.assertTrue(verify_permit(key, permit, issuer="trusted-issuer",
                                      event=self.event, now=20))
        self.assertFalse(verify_permit(key, dict(permit, expires_at=800),
                                       issuer="trusted-issuer", event=self.event,
                                       now=20))
        self.assertFalse(verify_permit(key, dict(permit, authority_ref="fake"),
                                       issuer="trusted-issuer", event=self.event,
                                       now=20))
        self.assertFalse(verify_permit(key, dict(permit, mac="fake"),
                                       issuer="trusted-issuer", event=self.event,
                                       now=20))
        self.assertFalse(verify_permit(key, dict(permit, extra="x"),
                                       issuer="trusted-issuer", event=self.event,
                                       now=20))
        self.assertFalse(verify_permit(key, permit, issuer="trusted-issuer",
                                       event=dict(self.event, scope="delete"),
                                       now=20))

    def test_hold_and_released_generation(self):
        self.gate.hold(4)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "held")
        self.gate.release(5)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "stale_generation")
        self.assertEqual(self.gate.record_count(), 0)

    def test_stale_context_and_lineage(self):
        event = copy.deepcopy(self.event)
        event["context_version"] = 3
        self.assertEqual(self.gate.apply(event, now=20)["code"], "stale_context")
        event = copy.deepcopy(self.event)
        event["predecessor_ref"] = "wrong"
        self.assertEqual(self.gate.apply(event, now=20)["code"], "lineage_mismatch")
        self.assertEqual(self.gate.record_count(), 0)

    def test_concurrent_duplicate_only_once(self):
        results = []
        def worker():
            results.append(self.gate.apply(copy.deepcopy(self.event), now=20))
        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(sum(r["ok"] for r in results), 1)
        self.assertEqual(self.gate.record_count(), 1)

    def test_bad_witness_and_unknown_event(self):
        event = copy.deepcopy(self.event)
        event["witness_ref"] = "fabricated"
        self.assertEqual(self.gate.apply(event, now=20)["code"], "trusted_witness")
        self.assertEqual(self.gate.apply({}, now=20)["code"], "wrong_context")
        self.assertEqual(self.gate.record_count(), 0)


if __name__ == "__main__":
    unittest.main()
