"""Research-only same-event join of two existing non-authorizing G3 checks.

No permission or consent can be inferred from this result. The issuer roster,
rights records, current generation, revocations and clock MUST be supplied
by a separately trusted authority, not by the request or agent.
"""
from g3_authority_evidence.authority_evidence import inspect_claim
from g3_rights_review.rights_review import review


def inspect_same_event(packet, *, record_ref, public_keys, revoked_serials,
                       trusted_records, current_generation, now, subject,
                       action, effect_digest, scope, purpose,
                       emergency_hold=False):
    """Check a single event and record reference across two independent models.

    A signed record serial must be the exact rights-record reference, not just
    a signature for a separate, possibly unrelated, authorized operation.
    The output is evidence consistency, not permission to commit any effect.
    """
    def outcome(code, matched=False):
        return {
            "code": code,
            "signed_and_rights_records_match": matched,
            "authorizes_effect": False,
            "authentic_consent_proved": False,
            "original_six_x3_proved": False,
        }

    if type(emergency_hold) is not bool:
        return outcome("hold_input_invalid")
    if emergency_hold:
        return outcome("emergency_hold")
    if type(record_ref) is not str or not 1 <= len(record_ref) <= 160:
        return outcome("record_reference_invalid")
    if type(packet) is not dict or set(packet) != {"claim", "signature"}:
        return outcome("packet_schema")
    claim = packet["claim"]
    if type(claim) is not dict or claim.get("serial") != record_ref:
        return outcome("signed_serial_rights_reference_mismatch")

    # Same trusted generation and time are used for BOTH checks. Nothing
    # from the user-supplied claim becomes the authority's time or epoch.
    signature = inspect_claim(
        packet, public_keys=public_keys, revoked_serials=revoked_serials,
        minimum_generation=current_generation, now=now, subject=subject,
        action=action, effect_digest=effect_digest, scope=scope, purpose=purpose)
    if not signature["signature_valid_for_record"]:
        return outcome("signature_" + signature["code"])
    rights = review(
        {"record_ref": record_ref}, trusted_records=trusted_records,
        subject=subject, action=action, scope=scope, purpose=purpose,
        effect_digest=effect_digest, now=now,
        current_generation=current_generation, emergency_hold=emergency_hold)
    if not rights["review_complete"]:
        return outcome("rights_" + rights["code"])

    return outcome("signed_and_rights_records_match_for_review_only", matched=True)
