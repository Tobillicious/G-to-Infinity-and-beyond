"""Offline signed *claim* verifier for a bounded G3 research application.

NEVER an application permit, consent oracle, or physical X3 certification.
The trusted issuer roster, revocations and time must come from a separately
secured source; a cryptographic signature alone cannot prove authentic consent.
"""
import json
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = 'g3-operator-permission-claim-v1'
CLAIM_FIELDS = frozenset({
    'domain', 'issuer', 'serial', 'subject', 'action', 'effect_digest',
    'scope', 'purpose', 'not_before', 'not_after', 'revocation_generation',
})
HEX = frozenset('0123456789abcdef')


def _safe_text(x):
    return type(x) is str and 1 <= len(x) <= 160 and x.isascii() and all(
        32 <= ord(char) <= 126 for char in x)


def _hex(x, count):
    return type(x) is str and len(x) == count and all(c in HEX for c in x)


def encode_claim(claim):
    """Canonical JSON bytes; raises ValueError for malformed claims."""
    if type(claim) is not dict or set(claim) != CLAIM_FIELDS:
        raise ValueError('claim_schema')
    if claim['domain'] != DOMAIN:
        raise ValueError('wrong_domain')
    for key in ('issuer', 'serial', 'subject', 'action', 'scope', 'purpose'):
        if not _safe_text(claim[key]):
            raise ValueError('claim_field')
    if not _hex(claim['effect_digest'], 64):
        raise ValueError('claim_digest')
    for key in ('not_before', 'not_after', 'revocation_generation'):
        if type(claim[key]) is not int or not 0 <= claim[key] < 2**63:
            raise ValueError('claim_integer')
    if not claim['not_before'] < claim['not_after']:
        raise ValueError('claim_window')
    return json.dumps(claim, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def inspect_claim(packet, *, public_keys, revoked_serials, minimum_generation,
                  now, subject, action, effect_digest, scope, purpose):
    """Verify a signed operator-permission *record* against trusted inputs.

    Returns descriptive cryptographic status ONLY; callers must NOT use this
    as authorization to execute or to infer genuine human consent.
    """
    def deny(code):
        return {'signature_valid_for_record': False, 'code': code,
                'authorizes_effect': False, 'authentic_consent_proved': False,
                'original_six_x3_proved': False}

    if (type(now) is not int or not 0 <= now < 2**63 or
            type(minimum_generation) is not int or not 0 <= minimum_generation < 2**63 or
            type(public_keys) is not dict or type(revoked_serials) not in (set, frozenset)):
        return deny('trusted_inputs_invalid')
    if type(packet) is not dict or set(packet) != {'claim', 'signature'}:
        return deny('packet_schema')
    claim = packet['claim']
    try:
        data = encode_claim(claim)
    except (ValueError, TypeError, OverflowError):
        return deny('claim_invalid')
    if not _hex(packet['signature'], 128):
        return deny('signature_schema')
    key = public_keys.get(claim['issuer'])
    if not isinstance(key, Ed25519PublicKey):
        return deny('untrusted_issuer')
    try:
        key.verify(bytes.fromhex(packet['signature']), data)
    except (InvalidSignature, ValueError):
        return deny('invalid_signature')
    if (claim['subject'] != subject or claim['action'] != action or
            claim['effect_digest'] != effect_digest or claim['scope'] != scope or
            claim['purpose'] != purpose):
        return deny('subject_action_or_scope_mismatch')
    if not claim['not_before'] <= now < claim['not_after']:
        return deny('expired_or_not_yet_valid')
    if claim['revocation_generation'] != minimum_generation:
        return deny('stale_revocation_generation')
    if claim['serial'] in revoked_serials:
        return deny('revoked_record')
    return {'signature_valid_for_record': True, 'code': 'signed_record_matches',
            'authorizes_effect': False, 'authentic_consent_proved': False,
            'original_six_x3_proved': False}
