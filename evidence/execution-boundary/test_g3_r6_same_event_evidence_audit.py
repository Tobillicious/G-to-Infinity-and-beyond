"""Hostile same-event evidence reconciliation tests; all synthetic/non-enforcing."""
import copy
import unittest
from g3_r6_same_event_evidence_audit import SIX, audit_same_event


class R6SameEventAuditTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            {"event_id": "event-1", "effect_path": "fixed-marker",
             "before_sha256": "a" * 64, "after_sha256": "b" * 64,
             "observer_ref": "external-observer-e1", "actor_ref": "actor-1"},
            {"event_id": "event-2", "effect_path": "hold-denial",
             "before_sha256": "b" * 64, "after_sha256": "b" * 64,
             "observer_ref": "external-observer-e2", "actor_ref": "actor-1"},
        ]
        self.owed = {"event-1": {"subject-1"}, "event-2": {"subject-1"}}
        self.duties = {
            e: {"subject-1": {d: {"status": "supported",
                                 "evidence_ref": e + "-subject-1-" + d}
                               for d in SIX}}
            for e in self.owed
        }

    def review(self, **overrides):
        kwargs = dict(declared_paths={"fixed-marker", "hold-denial"},
                      events=copy.deepcopy(self.events),
                      owed_by_event=copy.deepcopy(self.owed),
                      duties_by_event=copy.deepcopy(self.duties))
        kwargs.update(overrides)
        return audit_same_event(**kwargs)

    def test_filled_record_never_claims_consent_coverage_or_authority(self):
        x = self.review(externally_verified_path_inventory=True,
                        independently_authenticated_observers=True)
        self.assertEqual(x["status"], "RESEARCH_SCOPE_REVIEW_REQUIRED")
        self.assertEqual(x["events_reconciled"], 2)
        self.assertEqual(x["unresolved"], [])
        for k in ("hCoverage_proved", "hMeaning_proved",
                  "authentic_subjects_verified", "authorizes_effect",
                  "certified_for_production"):
            self.assertFalse(x[k])

    def test_unverified_inventory_and_observer_cannot_be_hidden(self):
        x = self.review()
        self.assertIn("external_effect_inventory_unverified", x["unresolved"])
        self.assertIn("independent_observer_unverified", x["unresolved"])

    def test_duplicate_actual_event_rejected(self):
        events = copy.deepcopy(self.events)
        events.append(copy.deepcopy(events[0]))
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            self.review(events=events)

    def test_unexpected_effect_path_detected(self):
        events = copy.deepcopy(self.events)
        events[0]["effect_path"] = "unmediated-socket"
        x = self.review(events=events)
        self.assertTrue(any(g.startswith("undeclared_effect_path:event-1")
                            for g in x["unresolved"]))

    def test_declared_unobserved_path_detected(self):
        x = self.review(declared_paths={"fixed-marker", "hold-denial", "other-path"})
        self.assertIn("declared_path_unobserved:other-path", x["unresolved"])

    def test_missing_actual_before_after_digest_detected(self):
        events = copy.deepcopy(self.events)
        events[0]["after_sha256"] = ""
        x = self.review(events=events)
        self.assertIn("missing_after_sha256:event-1", x["unresolved"])

    def test_no_observer_reference_detected(self):
        events = copy.deepcopy(self.events)
        events[0]["observer_ref"] = ""
        x = self.review(events=events)
        self.assertIn("missing_observer_ref:event-1", x["unresolved"])

    def test_missing_owed_census_detected(self):
        owed = copy.deepcopy(self.owed)
        del owed["event-1"]
        x = self.review(owed_by_event=owed)
        self.assertIn("owed_scope_unreported:event-1", x["unresolved"])

    def test_empty_owed_subject_set_is_not_proof(self):
        owed = copy.deepcopy(self.owed)
        owed["event-1"] = set()
        x = self.review(owed_by_event=owed)
        self.assertIn("empty_owed_scope:event-1", x["unresolved"])

    def test_missing_subject_six_evidence_detected(self):
        duties = copy.deepcopy(self.duties)
        del duties["event-1"]["subject-1"]
        x = self.review(duties_by_event=duties)
        self.assertIn("missing_subject_evidence:event-1:subject-1", x["unresolved"])

    def test_every_one_of_six_missing_duties_detected(self):
        for duty in SIX:
            with self.subTest(duty=duty):
                duties = copy.deepcopy(self.duties)
                del duties["event-1"]["subject-1"][duty]
                x = self.review(duties_by_event=duties)
                self.assertIn("unresolved:event-1:subject-1:" + duty, x["unresolved"])

    def test_contradicted_duty_is_not_success(self):
        duties = copy.deepcopy(self.duties)
        duties["event-1"]["subject-1"]["authorization"]["status"] = "contradicted"
        x = self.review(duties_by_event=duties)
        self.assertIn("unresolved:event-1:subject-1:authorization", x["unresolved"])

    def test_booleans_cannot_replace_subject_evidence(self):
        duties = copy.deepcopy(self.duties)
        duties["event-1"]["subject-1"]["authorization"] = True
        x = self.review(duties_by_event=duties)
        self.assertIn("unresolved:event-1:subject-1:authorization", x["unresolved"])

    def test_cross_event_copied_duty_receipt_detected(self):
        duties = copy.deepcopy(self.duties)
        duties["event-2"]["subject-1"]["authorization"]["evidence_ref"] = (
            duties["event-1"]["subject-1"]["authorization"]["evidence_ref"])
        x = self.review(duties_by_event=duties)
        self.assertTrue(any(z.startswith("reused_duty_reference:")
                            for z in x["unresolved"]))

    def test_omitted_subject_from_owed_cohort_exposed(self):
        duties = copy.deepcopy(self.duties)
        duties["event-1"]["subject-2"] = dict(duties["event-1"]["subject-1"])
        x = self.review(duties_by_event=duties)
        self.assertIn("unaccounted_evidence_subject:event-1:subject-2", x["unresolved"])

    def test_orphan_unobserved_event_evidence_exposed(self):
        owed = copy.deepcopy(self.owed)
        owed["event-missing"] = {"subject-1"}
        x = self.review(owed_by_event=owed)
        self.assertIn("orphan_event_evidence:event-missing", x["unresolved"])

    def test_no_events_is_never_vacuous_pass(self):
        x = self.review(events=[], owed_by_event={}, duties_by_event={})
        self.assertIn("no_observed_actual_events", x["unresolved"])

    def test_malformed_extra_event_fields_rejected(self):
        events = copy.deepcopy(self.events)
        events[0]["trusted_by_request"] = True
        with self.assertRaisesRegex(ValueError, "schema"):
            self.review(events=events)


if __name__ == "__main__":
    unittest.main()
