"""Prototype event-bound HMAC permit for the isolated Koru synthetic pilot.

The signing secret MUST be provided by a trusted, separated issuer in a real
deployment. HMAC demonstrates message authenticity only while the key remains
secret; it does not establish human consent or an original-six-X3 certificate.
Do not embed production keys in code, fixtures, logs or untrusted agents.
"""
import hashlib
import hmac
import json

from koru_shadow import digest

PERMIT_VERSION = "koru-pilot-permit-v1"
FIELDS = frozenset({"version", "issuer", "event_digest", "context_digest",
                    "authority_ref", "expires_at", "mac"})


def _body(issuer, event, expires_at):
    if (type(issuer) is not str or not issuer or len(issuer) > 160
            or type(event) is not dict or type(expires_at) is not int
            or expires_at < 0):
        raise ValueError("invalid permit inputs")
    return {"version": PERMIT_VERSION, "issuer": issuer,
            "event_digest": digest(event),
            "context_digest": event["context_digest"],
            "authority_ref": event["authority_ref"],
            "expires_at": expires_at}


def _mac(key, payload):
    if type(key) is not bytes or len(key) < 32:
        raise ValueError("at least 32 bytes of independent secret key required")
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    return hmac.new(key, raw, hashlib.sha256).hexdigest()


def issue_permit(key, *, issuer, event, expires_at):
    """Trusted issuer ONLY. Never expose this operation to an agent."""
    body = _body(issuer, event, expires_at)
    return {**body, "mac": _mac(key, body)}


def verify_permit(key, permit, *, issuer, event, now):
    """Fail closed on malformed, expired, re-bound, or fabricated permits."""
    try:
        if type(permit) is not dict or set(permit) != FIELDS:
            return False
        if type(now) is not int or now < 0:
            return False
        body = _body(issuer, event, permit["expires_at"])
        if (permit["version"] != PERMIT_VERSION or
                any(permit[field] != value for field, value in body.items())):
            return False
        supplied = permit["mac"]
        if type(supplied) is not str or len(supplied) != 64:
            return False
        if not hmac.compare_digest(supplied, _mac(key, body)):
            return False
        return now < body["expires_at"]
    except (TypeError, ValueError, KeyError, OverflowError, RecursionError):
        return False
