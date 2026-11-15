"""G3 synthetic effect boundary tests. No external actuator, network or secrets."""
import copy
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_ed25519_permit import issue_ed25519
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


class TestG3SyntheticEffectBoundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "effects.sqlite")
        self.event, self.trusted = fixtures()
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key()
        self.kwargs = dict(
            contexts=self.trusted["contexts"],
            signatures=self.trusted["signatures"],
            witnesses=self.trusted["witnesses"],
            authorities=self.trusted["authorities"],
            provenances=self.trusted["provenances"],
            context_ref="ctx-one", generation=3,
            ed25519_public_key=self.public, permit_issuer="separate-issuer")
        self.gate = SyntheticEffectGate(self.path, **self.kwargs)
        self.permit = issue_ed25519(self.private, issuer="separate-issuer",
                                    event=self.event, expires_at=100)

    def tearDown(self):
        self.gate.close()
        self.tmp.cleanup()

    def admit(self):
        result = self.gate.apply(self.event, now=10, permit=self.permit)
        self.assertTrue(result["ok"], result)

    def test_cannot_dispatch_without_signed_admission(self):
        result = self.gate.dispatch_synthetic(self.event, now=20, permit=self.permit)
        self.assertEqual(result["code"], "not_admitted")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_admit_then_dispatch_once_even_with_concurrent_retries(self):
        self.admit()
        results = []
        def worker():
            results.append(self.gate.dispatch_synthetic(
                copy.deepcopy(self.event), now=20, permit=self.permit))
        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(sum(r["code"] == "synthetic_effect_recorded" for r in results), 1)
        self.assertTrue(all(r["ok"] for r in results))
        self.assertEqual(self.gate.effect_count(), 1)
        self.assertEqual(len({r["receipt"] for r in results}), 1)

    def test_revoked_between_admission_and_effect(self):
        self.admit()
        self.gate.revoke_authority("auth-lesson")
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"],
            "authority_revoked_at_effect")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_hold_between_admission_and_effect(self):
        self.admit()
        self.gate.hold(4)
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"], "held_at_effect")
        self.gate.release(5)
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"],
            "effect_stale_generation")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_expiry_and_tampered_permit_at_effect(self):
        self.admit()
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=100, permit=self.permit)["code"],
            "invalid_permit_at_effect")
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=dict(self.permit, signature="0" * 128))["code"],
            "invalid_permit_at_effect")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_changed_payload_with_new_valid_signature_not_admitted(self):
        self.admit()
        modified = copy.deepcopy(self.event)
        modified["purpose"] = "unapproved"
        modified_permit = issue_ed25519(
            self.private, issuer="separate-issuer", event=modified, expires_at=100)
        self.assertEqual(self.gate.dispatch_synthetic(
            modified, now=20, permit=modified_permit)["code"],
            "effect_payload_mismatch")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_restart_preserves_exactly_once_effect(self):
        self.admit()
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        self.gate.close()
        self.gate = SyntheticEffectGate(self.path, **self.kwargs)
        result = self.gate.dispatch_synthetic(self.event, now=20, permit=self.permit)
        self.assertEqual(result["code"], "already_dispatched")
        self.assertEqual(self.gate.effect_count(), 1)

    def test_direct_effect_write_through_adapter_connection_denied(self):
        # This adapter connection cannot bypass dispatch_synthetic.
        with self.assertRaises(sqlite3.DatabaseError):
            self.gate.db.execute(
                "INSERT INTO synthetic_effects VALUES (?,?,?)",
                ("forged", "a" * 64, "b" * 64))
        self.assertEqual(self.gate.effect_count(), 0)
        self.admit()
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        # Cached statements are disabled: the same SQL form must be denied
        # after the legitimate write as well.
        with self.assertRaises(sqlite3.DatabaseError):
            self.gate.db.execute(
                "INSERT INTO synthetic_effects VALUES (?,?,?)",
                ("forged-again", "a" * 64, "b" * 64))
        self.assertEqual(self.gate.effect_count(), 1)

    def test_tampered_effect_record_detected_before_followup(self):
        self.admit()
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["ok"])
        # Independent DB access (outside the protected adapter) remains a
        # demonstrable bypass: complete mediation is NOT established yet.
        with sqlite3.connect(self.path) as outsider:
            outsider.execute("UPDATE synthetic_effects SET receipt=? WHERE event_id=?",
                            ("0" * 64, self.event["event_id"]))
        self.assertEqual(self.gate.audit()["code"], "synthetic_effect_integrity")
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"],
            "synthetic_effect_integrity")
        self.assertEqual(self.gate.effect_count(), 1)

    def test_direct_db_connection_still_bypasses_python_authorizer(self):
        # A known hostile counterexample, deliberately kept as a test:
        # another process/user with DB write permissions can inject an
        # effect; filesystem/OS isolation is essential for full mediation.
        with sqlite3.connect(self.path) as outsider:
            outsider.execute(
                "INSERT INTO synthetic_effects VALUES (?,?,?)",
                ("unauthorized", "a" * 64, "b" * 64))
        self.assertEqual(self.gate.audit()["code"], "synthetic_effect_integrity")
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"],
            "synthetic_effect_integrity")

    def test_broker_time_floor_survives_restart_and_rejects_rollback(self):
        self.assertEqual(self.gate.accept_broker_time(30)["code"],
                         "clock_advanced")
        self.assertEqual(self.gate.accept_broker_time(29)["code"],
                         "clock_rollback")
        self.assertEqual(self.gate.accept_broker_time(30)["code"],
                         "clock_advanced")
        self.gate.close()
        self.gate = SyntheticEffectGate(self.path, **self.kwargs)
        self.assertEqual(self.gate.accept_broker_time(1)["code"],
                         "clock_rollback")
        self.assertEqual(self.gate.accept_broker_time(31)["code"],
                         "clock_advanced")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_broker_time_rejects_bad_inputs_without_poisoning_floor(self):
        for invalid in (-1, True, 1.5, "20", 2**65):
            self.assertEqual(self.gate.accept_broker_time(invalid)["code"],
                             "clock_unavailable")
        self.assertEqual(self.gate.accept_broker_time(10)["code"],
                         "clock_advanced")
        self.assertEqual(self.gate.accept_broker_time(9)["code"],
                         "clock_rollback")
        self.assertEqual(self.gate.accept_broker_time(11)["code"],
                         "clock_advanced")

    def test_stale_inflight_admission_cannot_bypass_advanced_floor(self):
        # Simulates a broker request that saw t=10 before another caller
        # durably advanced the floor to t=30.
        self.assertTrue(self.gate.accept_broker_time(30)["ok"])
        result = self.gate.apply(self.event, now=10, permit=self.permit)
        self.assertEqual(result["code"], "clock_rollback")
        self.assertEqual(self.gate.record_count(), 0)
        self.assertTrue(self.gate.apply(self.event, now=30, permit=self.permit)["ok"])

    def test_stale_inflight_effect_cannot_bypass_advanced_floor(self):
        self.admit()
        self.assertTrue(self.gate.accept_broker_time(30)["ok"])
        rejected = self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)
        self.assertEqual(rejected["code"], "clock_rollback")
        self.assertEqual(self.gate.effect_count(), 0)
        self.assertTrue(self.gate.dispatch_synthetic(
            self.event, now=30, permit=self.permit)["ok"])
        self.assertEqual(self.gate.effect_count(), 1)

    def test_clock_fence_persists_across_restart_for_both_operations(self):
        self.assertTrue(self.gate.accept_broker_time(60)["ok"])
        self.gate.close()
        self.gate = SyntheticEffectGate(self.path, **self.kwargs)
        self.assertEqual(self.gate.apply(
            self.event, now=20, permit=self.permit)["code"], "clock_rollback")
        self.assertTrue(self.gate.apply(
            self.event, now=60, permit=self.permit)["ok"])
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"], "clock_rollback")
        self.assertEqual(self.gate.effect_count(), 0)

    def test_unsigned_effect_mode_not_permitted(self):
        kwargs = dict(self.kwargs, ed25519_public_key=None)
        with self.assertRaises(ValueError):
            SyntheticEffectGate(str(Path(self.tmp.name) / "bad.sqlite"), **kwargs)

    def test_revocation_and_dispatch_race_serializes(self):
        self.admit()
        barrier = threading.Barrier(2)
        results = []
        def dispatch():
            barrier.wait()
            results.append(self.gate.dispatch_synthetic(
                self.event, now=20, permit=self.permit))
        def revoke():
            barrier.wait()
            self.gate.revoke_authority("auth-lesson")
        a = threading.Thread(target=dispatch)
        b = threading.Thread(target=revoke)
        a.start()
        b.start()
        a.join()
        b.join()
        self.assertIn(results[0]["code"],
                      ("synthetic_effect_recorded", "authority_revoked_at_effect"))
        self.assertLessEqual(self.gate.effect_count(), 1)
        self.assertEqual(self.gate.dispatch_synthetic(
            self.event, now=20, permit=self.permit)["code"],
            "authority_revoked_at_effect")


if __name__ == "__main__":
    unittest.main()
