"""Research-only rights evidence triage, never effect authorization.

Trusted records must come from an independently verified authority system.
This module does not determine whether genuine human consent occurred.
"""
FIELDS = frozenset({
    "subject", "action", "scope", "purpose", "effect_digest",
    "decision", "authority_kind", "verified_identity", "capacity_reviewed",
    "voluntariness_reviewed", "delegation_verified", "revoked",
    "not_before", "not_after", "generation", "provenance_ref",
})
TEXT = ("subject", "action", "scope", "purpose", "provenance_ref")
HEX = frozenset("0123456789abcdef")


def review(evidence, *, trusted_records, subject, action, scope, purpose,
           effect_digest, now, current_generation, emergency_hold=False):
    """Inspect only independently supplied trusted records.

    Evidence is an untrusted reference ID, not a grant. The resulting flag
    indicates completeness for further human review, never permission to act.
    """
    def answer(code, complete=False):
        return {"review_complete": complete, "code": code,
                "authorizes_effect": False, "authentic_consent_proved": False,
                "original_six_x3_proved": False}

    if (type(now) is not int or not 0 <= now < 2**63
            or type(current_generation) is not int
            or not 0 <= current_generation < 2**63
            or type(emergency_hold) is not bool
            or type(trusted_records) is not dict):
        return answer("trusted_inputs_invalid")
    if emergency_hold:
        return answer("emergency_hold")
    if type(evidence) is not dict or set(evidence) != {"record_ref"}:
        return answer("request_schema")
    ref = evidence["record_ref"]
    if type(ref) is not str or not 1 <= len(ref) <= 160:
        return answer("request_schema")
    record = trusted_records.get(ref)
    if type(record) is not dict or set(record) != FIELDS:
        return answer("trusted_record_missing_or_invalid")
    if (any(type(record[k]) is not str or not 1 <= len(record[k]) <= 160
            for k in TEXT)
            or type(record["effect_digest"]) is not str
            or len(record["effect_digest"]) != 64
            or any(c not in HEX for c in record["effect_digest"])
            or type(record["decision"]) is not str
            or record["decision"] not in ("allow", "deny", "withdrawn")
            or type(record["authority_kind"]) is not str
            or record["authority_kind"] not in ("self", "representative")
            or any(type(record[k]) is not bool for k in (
                "verified_identity", "capacity_reviewed", "voluntariness_reviewed",
                "delegation_verified", "revoked"))
            or any(type(record[k]) is not int or not 0 <= record[k] < 2**63
                   for k in ("not_before", "not_after", "generation"))
            or record["not_before"] >= record["not_after"]):
        return answer("trusted_record_invalid")
    if record["revoked"] or record["decision"] in ("deny", "withdrawn"):
        return answer("rights_denied_or_withdrawn")
    if (record["subject"] != subject or record["action"] != action
            or record["scope"] != scope or record["purpose"] != purpose
            or record["effect_digest"] != effect_digest):
        return answer("request_rights_mismatch")
    if not record["not_before"] <= now < record["not_after"]:
        return answer("rights_expired_or_future")
    if record["generation"] != current_generation:
        return answer("rights_generation_stale")
    if not record["verified_identity"]:
        return answer("identity_unverified")
    if not record["capacity_reviewed"] or not record["voluntariness_reviewed"]:
        return answer("capacity_or_voluntariness_unreviewed")
    if record["authority_kind"] == "representative" and not record["delegation_verified"]:
        return answer("delegation_unverified")
    return answer("trusted_record_matches_for_review", complete=True)
