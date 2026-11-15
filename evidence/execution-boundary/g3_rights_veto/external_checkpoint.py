"""Read-only externally signed checkpoint comparison for a research rights journal.

Checkpoint and pinned key must arrive via a separate trusted channel.
This does not authorize effects, consent, or universal physical protection.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = "g3-rights-journal-checkpoint-v1"
FIELDS = frozenset(("domain", "deployment", "generation", "digest"))
HEX = frozenset("0123456789abcdef")


def canonical_checkpoint(payload):
    if type(payload) is not dict or set(payload) != FIELDS:
        raise ValueError("checkpoint_schema")
    if payload["domain"] != DOMAIN:
        raise ValueError("checkpoint_domain")
    if (type(payload["deployment"]) is not str or
            not 1 <= len(payload["deployment"]) <= 160 or
            not payload["deployment"].isascii()):
        raise ValueError("checkpoint_deployment")
    if (type(payload["generation"]) is not int or
            not 0 <= payload["generation"] < 2**63):
        raise ValueError("checkpoint_generation")
    d = payload["digest"]
    if type(d) is not str or len(d) != 64 or any(ch not in HEX for ch in d):
        raise ValueError("checkpoint_digest")
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def journal_snapshot(db_path):
    """Read durable logical records; error on missing or inconsistent history."""
    path = Path(db_path)
    if not path.is_file() or path.is_symlink():
        raise ValueError("journal_missing_or_unsafe")
    db = sqlite3.connect("file:" + str(path.resolve()) + "?mode=ro",
                         uri=True, isolation_level=None)
    try:
        db.execute("BEGIN")
        control = db.execute(
            "SELECT generation, halted FROM control WHERE id=1").fetchall()
        records = db.execute(
            "SELECT record_ref,subject,action,effect_digest,generation "
            "FROM withdrawn ORDER BY generation").fetchall()
        db.execute("COMMIT")
    finally:
        db.close()
    if len(control) != 1 or type(control[0][0]) is not int or control[0][1] != 1:
        raise ValueError("journal_control_invalid")
    generation = control[0][0]
    if not 0 <= generation < 2**63 or len(records) != generation:
        raise ValueError("journal_generation_gap")
    for index, record in enumerate(records, start=1):
        if (record[4] != index or any(type(x) is not str for x in record[:4])
                or len(record[3]) != 64 or any(x not in HEX for x in record[3])):
            raise ValueError("journal_row_invalid")
    raw = json.dumps({"generation": generation, "records": records},
                     sort_keys=True, separators=(",", ":")).encode("utf-8")
    return generation, hashlib.sha256(raw).hexdigest()


def verify_checkpoint(db_path, packet, *, pinned_public_key,
                      deployment, minimum_generation):
    """Return integrity only. Does NOT produce an executable permission."""
    def result(code, match=False):
        return {"code": code, "checkpoint_matches": match,
                "authorizes_effect": False, "authentic_consent_proved": False,
                "original_six_x3_proved": False}
    if (not isinstance(pinned_public_key, Ed25519PublicKey)
            or type(deployment) is not str
            or type(minimum_generation) is not int
            or not 0 <= minimum_generation < 2**63):
        return result("trusted_inputs_invalid")
    if type(packet) is not dict or set(packet) != {"checkpoint", "signature"}:
        return result("packet_invalid")
    try:
        message = canonical_checkpoint(packet["checkpoint"])
        signature = packet["signature"]
        if (type(signature) is not str or len(signature) != 128 or
                any(ch not in HEX for ch in signature)):
            return result("signature_schema")
        pinned_public_key.verify(bytes.fromhex(signature), message)
    except (InvalidSignature, ValueError, TypeError):
        return result("checkpoint_not_verified")
    claim = packet["checkpoint"]
    if claim["deployment"] != deployment:
        return result("deployment_mismatch")
    if claim["generation"] < minimum_generation:
        return result("stale_external_checkpoint")
    try:
        generation, digest = journal_snapshot(db_path)
    except (OSError, sqlite3.Error, ValueError):
        return result("journal_integrity_unknown")
    if generation != claim["generation"] or digest != claim["digest"]:
        return result("journal_checkpoint_mismatch")
    return result("checkpoint_matches_only", match=True)
