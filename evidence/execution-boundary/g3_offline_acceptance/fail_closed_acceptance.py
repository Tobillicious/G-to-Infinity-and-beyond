#!/usr/bin/env python3
"""Offline fail-closed cross-component G3 acceptance probe.

NO real effect, host writer, network socket, stored personal data, or live
authority. A result of READINESS_BLOCKED is the expected outcome.
Run existing independent negative-control suites separately.
"""
import json
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "g3_authority_evidence"))
sys.path.insert(0, str(ROOT / "g3_rights_review"))
sys.path.insert(0, str(ROOT / "g3_rights_veto"))

from authority_evidence import DOMAIN as AUTH_DOMAIN, encode_claim, inspect_claim
from rights_review import review
from rights_veto import RightsVetoJournal


def _blocked(reply):
    return (reply.get("authorizes_effect") is False
            and reply.get("authentic_consent_proved") is False
            and reply.get("original_six_x3_proved") is False)


def run_probe():
    # All identifiers and claims are synthetic fixtures, not real persons.
    signer = Ed25519PrivateKey.generate()
    subject, action, scope, purpose = "fixture-1", "offline-publish", "sandbox", "test-only"
    digest, ref = "a" * 64, "offline-r1"
    claim = dict(domain=AUTH_DOMAIN, issuer="fixture-issuer", serial="fixture-event-1",
                 subject=subject, action=action, scope=scope, purpose=purpose,
                 effect_digest=digest, not_before=10, not_after=30,
                 revocation_generation=0)
    packet = dict(claim=claim, signature=signer.sign(encode_claim(claim)).hex())
    authenticated = inspect_claim(packet,
        public_keys={"fixture-issuer": signer.public_key()}, revoked_serials=set(),
        minimum_generation=0, now=20, subject=subject, action=action,
        effect_digest=digest, scope=scope, purpose=purpose)

    record = dict(subject=subject, action=action, scope=scope, purpose=purpose,
                  effect_digest=digest, decision="allow", authority_kind="self",
                  verified_identity=True, capacity_reviewed=True,
                  voluntariness_reviewed=True, delegation_verified=False,
                  revoked=False, not_before=10, not_after=30, generation=0,
                  provenance_ref="fixture-only")
    screened = review(dict(record_ref=ref), trusted_records={ref: record},
        subject=subject, action=action, scope=scope, purpose=purpose,
        effect_digest=digest, now=20, current_generation=0)

    with tempfile.TemporaryDirectory(prefix="g3-fail-closed-") as td:
        path = Path(td) / "veto.sqlite"
        journal = RightsVetoJournal(path, initialize=True)
        try:
            before = journal.inspect(record_ref=ref, subject=subject,
                                     action=action, effect_digest=digest,
                                     expected_generation=0)
            withdrawal = journal.record_withdrawal(record_ref=ref,
                subject=subject, action=action, effect_digest=digest, generation=1)
            after = journal.inspect(record_ref=ref, subject=subject,
                                    action=action, effect_digest=digest,
                                    expected_generation=1)
            stale = journal.inspect(record_ref=ref, subject=subject,
                                    action=action, effect_digest=digest,
                                    expected_generation=0)
        finally:
            journal.close()

    # The positive fixture must be accepted ONLY as a record check.
    assertions = {
        "signed_record_valid_but_non_authorizing":
            authenticated["signature_valid_for_record"] is True and _blocked(authenticated),
        "rights_record_reviewable_but_non_authorizing":
            screened["review_complete"] is True and _blocked(screened),
        "absence_of_veto_not_an_allow":
            before["code"] == "no_local_withdrawal_found_not_authorized"
            and _blocked(before),
        "durable_veto_recorded":
            withdrawal["ok"] is True and after["code"] == "record_withdrawn"
            and after["local_veto"] is True and _blocked(after),
        "stale_generation_denied":
            stale["code"] == "stale_generation"
            and stale["local_veto"] is True and _blocked(stale),
    }
    passed = all(assertions.values())
    missing = [
        "independent genuine consent and moral/rights authority",
        "independently authenticated complete owed-particular scope",
        "six authentic X3 event-to-subject soundness witnesses",
        "atomic effect-time withdrawal versus writer commit fence",
        "bounded complete host/OS effect mediation and fifth-cause audit",
        "external observed effects, provenance, and adversarial reproducibility",
    ]
    result = {
        "test": "g3-offline-physical-evidence-readiness",
        "status": "READINESS_BLOCKED" if passed else "CONTROL_TEST_FAILURE",
        "safety_controls": assertions,
        "real_world_effect_authorized": False,
        "physically_verified_original_six": False,
        "missing_independent_evidence": missing if passed else ["offline negative control failure"],
        "scope": "synthetic local fixtures; no live writer, real subject, or network",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run_probe())
