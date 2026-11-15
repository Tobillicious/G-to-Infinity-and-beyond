"""Read-only G3 triage: exact signed claim + rights + witnessed veto state.

All checks are evidence-only. There is NO publish, authorization, or consent
capability here; an authenticated controller and commit-time lock are absent.
"""
from g3_rights_composition.same_event import inspect_same_event
from g3_rights_veto.external_checkpoint import verify_checkpoint


def inspect_three_way(packet, *, record_ref, public_keys, revoked_serials,
                      trusted_records, current_generation, now, subject, action,
                      effect_digest, scope, purpose, emergency_hold,
                      veto_journal, veto_db_path, checkpoint_packet, pinned_checkpoint_key,
                      deployment, trusted_generation_floor):
    """Require independently witnessed withdrawal state for same exact event.

    Authority inputs and checkpoint provenance must be supplied by trusted
    sources, never by the applicant. A returned match is NOT a grant to act.
    """
    def response(code, complete=False):
        return {
            "code": code, "three_way_evidence_consistent": complete,
            "authorizes_effect": False, "authentic_consent_proved": False,
            "original_six_x3_proved": False,
        }
    if (type(current_generation) is not int or current_generation < 0
            or type(trusted_generation_floor) is not int
            or trusted_generation_floor < 0):
        return response("generation_inputs_invalid")
    if current_generation < trusted_generation_floor:
        return response("stale_rights_generation")
    if type(emergency_hold) is not bool or emergency_hold:
        return response("emergency_hold_or_invalid")
    if veto_journal is None or type(deployment) is not str:
        return response("missing_trusted_veto_source")

    # Require EXACT generation equality between the signed externally
    # witnessed journal and the rights/claim view, not merely >= a floor.
    check = verify_checkpoint(
        veto_db_path, checkpoint_packet,
        pinned_public_key=pinned_checkpoint_key, deployment=deployment,
        minimum_generation=trusted_generation_floor)
    if not check["checkpoint_matches"]:
        return response("checkpoint_" + check["code"])
    cp = checkpoint_packet["checkpoint"]
    if cp["generation"] != current_generation:
        return response("checkpoint_rights_generation_mismatch")

    joined = inspect_same_event(
        packet, record_ref=record_ref, public_keys=public_keys,
        revoked_serials=revoked_serials, trusted_records=trusted_records,
        current_generation=current_generation, now=now, subject=subject,
        action=action, effect_digest=effect_digest, scope=scope,
        purpose=purpose, emergency_hold=emergency_hold)
    if not joined["signed_and_rights_records_match"]:
        return response("joined_" + joined["code"])

    veto = veto_journal.inspect(
        record_ref=record_ref, subject=subject, action=action,
        effect_digest=effect_digest, expected_generation=current_generation)
    if veto.get("local_veto") is not False or veto.get("code") != "no_local_withdrawal_found_not_authorized":
        return response("veto_" + str(veto.get("code", "invalid")))

    # Catch state advancing during the three separate evidence reads.
    # This does NOT create an atomic decision or protect the eventual writer.
    again = verify_checkpoint(
        veto_db_path, checkpoint_packet,
        pinned_public_key=pinned_checkpoint_key, deployment=deployment,
        minimum_generation=trusted_generation_floor)
    if not again["checkpoint_matches"]:
        return response("postcheck_" + again["code"])
    return response("three_way_consistent_for_independent_review_only", complete=True)
