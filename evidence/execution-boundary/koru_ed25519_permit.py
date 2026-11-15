"""Ed25519 event permits for an isolated Koru G research gate (Python 3.9+).

Dependency: cryptography. The gate needs ONLY the public verification key.
Issuance is an offline/trusted-issuer operation and must never be exposed to
untrusted agents. No production secrets or live consent authority are supplied.
"""
import binascii
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey,
)
from koru_shadow import digest

VERSION = "koru-ed25519-event-v1"
FIELDS = frozenset(("version", "issuer", "event_digest", "context_digest",
                    "authority_ref", "expires_at", "signature"))


def _body(issuer, event, expires_at):
    if (type(issuer) is not str or not issuer or len(issuer) > 160 or
            type(event) is not dict or type(expires_at) is not int or
            expires_at < 0 or type(event.get("context_digest")) is not str or
            type(event.get("authority_ref")) is not str):
        raise ValueError("invalid permit arguments")
    return {"version": VERSION, "issuer": issuer,
            "event_digest": digest(event),
            "context_digest": event["context_digest"],
            "authority_ref": event["authority_ref"],
            "expires_at": expires_at}


def _encode(body):
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def issue_ed25519(private_key, *, issuer, event, expires_at):
    """TRUSTED ISSUER ONLY; no private key belongs in the gate or agent."""
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("Ed25519 private key required")
    body = _body(issuer, event, expires_at)
    return {**body, "signature": private_key.sign(_encode(body)).hex()}


def verify_ed25519(public_key, permit, *, issuer, event, now):
    """Strict event-bound verification using a pinned public key only."""
    try:
        if not isinstance(public_key, Ed25519PublicKey):
            return False
        if type(now) is not int or now < 0:
            return False
        if type(permit) is not dict or set(permit) != FIELDS:
            return False
        body = _body(issuer, event, permit["expires_at"])
        if any(permit.get(k) != v for k, v in body.items()):
            return False
        signature = permit["signature"]
        if (type(signature) is not str or len(signature) != 128 or
                any(ch not in "0123456789abcdef" for ch in signature)):
            return False
        public_key.verify(bytes.fromhex(signature), _encode(body))
        return now < body["expires_at"]
    except (InvalidSignature, TypeError, ValueError, KeyError, OverflowError,
            RecursionError, binascii.Error):
        return False
