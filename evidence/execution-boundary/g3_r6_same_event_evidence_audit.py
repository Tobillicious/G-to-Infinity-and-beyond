"""Research-only same-event R6 evidence reconciliation; NEVER authorizes effects.

Caller-supplied records and references are NOT authenticated observers, consent,
actual universe coverage, or proofs of the original six. This checker catches
structural omissions and cross-event substitutions for a declared bounded scope.
"""
from collections.abc import Mapping
import re

SIX = ("historicalContinuity", "authorization", "freedom",
       "restraint", "maximality", "provenance")
SHA = re.compile(r"[0-9a-f]{64}\Z")
FIELDS = frozenset({"event_id", "effect_path", "before_sha256",
                    "after_sha256", "observer_ref", "actor_ref"})


def _identifier(x):
    return type(x) is str and 1 <= len(x) <= 200 and x.strip() == x


def audit_same_event(*, declared_paths, events, owed_by_event, duties_by_event,
                     externally_verified_path_inventory=False,
                     independently_authenticated_observers=False):
    if (type(declared_paths) not in (set, frozenset)
            or not declared_paths or any(not _identifier(p) for p in declared_paths)
            or type(events) not in (list, tuple)
            or type(owed_by_event) is not dict
            or type(duties_by_event) is not dict
            or type(externally_verified_path_inventory) is not bool
            or type(independently_authenticated_observers) is not bool):
        raise ValueError("invalid event evidence boundary")
    gaps = []
    event_ids = set()
    seen_paths = set()
    evidence_references = set()
    for i, event in enumerate(events):
        if type(event) is not dict or set(event) != FIELDS:
            raise ValueError("event record schema mismatch")
        event_id, path = event["event_id"], event["effect_path"]
        if not _identifier(event_id) or not _identifier(path):
            raise ValueError("invalid event identity or effect path")
        if event_id in event_ids:
            raise ValueError("duplicate event identity")
        event_ids.add(event_id)
        seen_paths.add(path)
        if path not in declared_paths:
            gaps.append("undeclared_effect_path:" + event_id + ":" + path)
        for name in ("before_sha256", "after_sha256"):
            digest = event[name]
            if type(digest) is not str or not SHA.fullmatch(digest):
                gaps.append("missing_" + name + ":" + event_id)
        for name in ("observer_ref", "actor_ref"):
            if not _identifier(event[name]):
                gaps.append("missing_" + name + ":" + event_id)
        if event_id not in owed_by_event:
            gaps.append("owed_scope_unreported:" + event_id)
            continue
        subjects = owed_by_event[event_id]
        if type(subjects) not in (set, frozenset):
            raise ValueError("invalid owed-subject census")
        if not subjects:
            gaps.append("empty_owed_scope:" + event_id)
        if any(not _identifier(s) for s in subjects):
            raise ValueError("invalid owed subject identity")
        evidence = duties_by_event.get(event_id)
        if type(evidence) is not dict:
            gaps.append("missing_six_evidence:" + event_id)
            continue
        for extra in set(evidence) - subjects:
            gaps.append("unaccounted_evidence_subject:" + event_id + ":" + str(extra))
        for subject in sorted(subjects):
            fields = evidence.get(subject)
            if type(fields) is not dict:
                gaps.append("missing_subject_evidence:" + event_id + ":" + subject)
                continue
            for extra in set(fields) - set(SIX):
                gaps.append("unexpected_duty:" + event_id + ":" + subject + ":" + str(extra))
            for duty in SIX:
                item = fields.get(duty)
                if type(item) is not dict or set(item) != {"status", "evidence_ref"}:
                    gaps.append("unresolved:" + event_id + ":" + subject + ":" + duty)
                    continue
                status, evidence_ref = item["status"], item["evidence_ref"]
                if status not in ("supported", "unresolved", "contradicted"):
                    gaps.append("invalid_status:" + event_id + ":" + subject + ":" + duty)
                    continue
                if status != "supported" or not _identifier(evidence_ref):
                    gaps.append("unresolved:" + event_id + ":" + subject + ":" + duty)
                    continue
                # A copied receipt from another event/particular/duty is not
                # independent evidence of this event's authentic meaning.
                if evidence_ref in evidence_references:
                    gaps.append("reused_duty_reference:" + event_id + ":" + subject + ":" + duty)
                evidence_references.add(evidence_ref)
    for event_id in set(owed_by_event) | set(duties_by_event):
        if event_id not in event_ids:
            gaps.append("orphan_event_evidence:" + str(event_id))
    for path in sorted(declared_paths - seen_paths):
        gaps.append("declared_path_unobserved:" + path)
    if not event_ids:
        gaps.append("no_observed_actual_events")
    if not externally_verified_path_inventory:
        gaps.append("external_effect_inventory_unverified")
    if not independently_authenticated_observers:
        gaps.append("independent_observer_unverified")
    return {
        "status": "RESEARCH_GAPS" if gaps else "RESEARCH_SCOPE_REVIEW_REQUIRED",
        "events_reconciled": len(event_ids),
        "unresolved": sorted(gaps),
        "hCoverage_proved": False,
        "hMeaning_proved": False,
        "authentic_subjects_verified": False,
        "authorizes_effect": False,
        "certified_for_production": False,
    }
