"""G-Mesh v0 authenticated handshake / local emergency hold research fixture.

NO network effects, hardware attestation verification, global agreement,
human-consent verification or Koru/X3 certification is implemented here.
Encrypted transport and local effect gateway remain independent obligations.
"""
import json
import re
import sqlite3
import threading
import time
from enum import Enum

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PROTOCOL = "g-mesh-0"
DOMAIN = b"UPT-G-MESH-V0\x00"
MAX_BODY = 4096
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
HANDSHAKE_FIELDS = frozenset((
    "protocol", "type", "source_node_id", "target_node_id", "deployment_id",
    "event_digest", "policy_digest", "authority_ref", "generation",
    "sequence", "not_after", "attestation_ref",
))
REVOCATION_FIELDS = frozenset((
    "protocol", "type", "source_node_id", "target_node_id",
    "deployment_id", "authority_ref", "generation", "sequence",
    "reason_code",
))


class GMeshState(str, Enum):
    IDLE = "IDLE"
    REVOKED_HALTED = "REVOKED_HALTED"


def encode_body(payload):
    """Reconstruct bytes from validated input; never trust caller's bytes."""
    return DOMAIN + json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False).encode("ascii")


def _nonempty(value, limit=160):
    return type(value) is str and 0 < len(value) <= limit


def _positive(value):
    return type(value) is int and 0 < value < 2**63


def _valid_handshake(data, node_id, deployment, policy):
    return (
        type(data) is dict and set(data) == HANDSHAKE_FIELDS and
        data["protocol"] == PROTOCOL and data["type"] == "handshake" and
        _nonempty(data["source_node_id"]) and
        data["target_node_id"] == node_id and
        data["deployment_id"] == deployment and
        type(data["event_digest"]) is str and
        DIGEST.fullmatch(data["event_digest"]) is not None and
        data["policy_digest"] == policy and
        _nonempty(data["authority_ref"]) and
        _positive(data["generation"]) and
        _positive(data["sequence"]) and
        _positive(data["not_after"]) and
        _nonempty(data["attestation_ref"])
    )


def _valid_revocation(data, node_id, deployment):
    return (
        type(data) is dict and set(data) == REVOCATION_FIELDS and
        data["protocol"] == PROTOCOL and data["type"] == "revoke" and
        _nonempty(data["source_node_id"]) and
        data["target_node_id"] == node_id and
        data["deployment_id"] == deployment and
        _nonempty(data["authority_ref"]) and
        _positive(data["generation"]) and
        _positive(data["sequence"]) and
        _nonempty(data["reason_code"], 100)
    )


class GMeshProtocolHandler:
    """Durable, local-only source-scoped sequence and controller hold.

    Trusted keys are pinned at initialization. Peer-provided attestation_ref
    is UNVERIFIED metadata; deployment-level TEE verification is absent.
    A successful handshake is NOT authorization to enact an external effect.
    """

    def __init__(self, db_path, *, node_id, deployment_id, policy_digest,
                 issuer_keys, controller_keys, clock=None):
        if (not _nonempty(node_id) or not _nonempty(deployment_id) or
                type(policy_digest) is not str or
                not DIGEST.fullmatch(policy_digest)):
            raise ValueError("pinned node, deployment and policy required")
        if (type(issuer_keys) is not dict or type(controller_keys) is not dict or
                not issuer_keys or not controller_keys or
                any(not _nonempty(k) or not isinstance(v, Ed25519PublicKey)
                    for roster in (issuer_keys, controller_keys)
                    for k, v in roster.items())):
            raise ValueError("explicit pinned public-key rosters required")
        self.node_id = node_id
        self.deployment_id = deployment_id
        self.policy_digest = policy_digest
        self.issuer_keys = dict(issuer_keys)
        self.controller_keys = dict(controller_keys)
        self.clock = clock if clock is not None else lambda: int(time.time())
        self.lock = threading.RLock()
        self.db = sqlite3.connect(db_path, isolation_level=None,
                                  check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS gmesh_state "
            "(id INTEGER PRIMARY KEY CHECK(id=1), halted INTEGER NOT NULL, "
            "generation INTEGER NOT NULL)")
        self.db.execute("INSERT OR IGNORE INTO gmesh_state VALUES (1,0,1)")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS peer_sequence "
            "(source TEXT PRIMARY KEY, last_seq INTEGER NOT NULL)")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS revoked_authority "
            "(ref TEXT PRIMARY KEY)")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS control_sequence "
            "(controller TEXT PRIMARY KEY, last_seq INTEGER NOT NULL)")

    @property
    def state(self):
        with self.lock:
            halted = self.db.execute(
                "SELECT halted FROM gmesh_state WHERE id=1").fetchone()
            return (GMeshState.REVOKED_HALTED if halted is None or halted[0]
                    else GMeshState.IDLE)

    def _transaction(self, callback):
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                value = callback()
                self.db.execute("COMMIT")
                return value
            except BaseException:
                self.db.execute("ROLLBACK")
                raise

    def _verify_signature(self, key, payload, signature, canonical):
        if not isinstance(signature, bytes) or len(signature) != 64:
            return False
        try:
            expected = encode_body(payload)
            if (len(expected) > MAX_BODY or
                    (canonical is not None and canonical != expected)):
                return False
            key.verify(signature, expected)
            return True
        except (TypeError, ValueError, OverflowError, InvalidSignature,
                UnicodeError, RecursionError):
            return False

    def process_handshake(self, payload, signature, canonical=None):
        if not _valid_handshake(
                payload, self.node_id, self.deployment_id, self.policy_digest):
            return False, "schema_rejected"
        key = self.issuer_keys.get(payload["source_node_id"])
        if key is None or not self._verify_signature(
                key, payload, signature, canonical):
            return False, "invalid_signature"
        try:
            now = self.clock()
            if type(now) is not int or now < 0 or now >= 2**63:
                return False, "clock_unavailable"
        except (TypeError, ValueError, OverflowError):
            return False, "clock_unavailable"

        def accept():
            state = self.db.execute(
                "SELECT halted,generation FROM gmesh_state WHERE id=1"
            ).fetchone()
            if state is None or state[0]:
                return False, "FAIL_CLOSED_local_hold"
            if payload["generation"] != state[1]:
                return False, "stale_generation"
            if now >= payload["not_after"]:
                return False, "expired"
            if self.db.execute(
                "SELECT 1 FROM revoked_authority WHERE ref=?",
                (payload["authority_ref"],)).fetchone():
                return False, "authority_revoked"
            prior = self.db.execute(
                "SELECT last_seq FROM peer_sequence WHERE source=?",
                (payload["source_node_id"],)).fetchone()
            if prior is not None and payload["sequence"] <= prior[0]:
                return False, "nonce_replay"
            self.db.execute(
                "INSERT INTO peer_sequence VALUES (?,?) "
                "ON CONFLICT(source) DO UPDATE SET last_seq=excluded.last_seq",
                (payload["source_node_id"], payload["sequence"]))
            return True, "authenticated_handshake_only"
        return self._transaction(accept)

    def handle_revocation_broadcast(self, payload, signature, canonical=None):
        if not _valid_revocation(payload, self.node_id, self.deployment_id):
            return False, "invalid_revocation_schema"
        key = self.controller_keys.get(payload["source_node_id"])
        if key is None or not self._verify_signature(
                key, payload, signature, canonical):
            return False, "invalid_controller_signature"

        def revoke():
            previous = self.db.execute(
                "SELECT last_seq FROM control_sequence WHERE controller=?",
                (payload["source_node_id"],)).fetchone()
            if previous is not None and payload["sequence"] <= previous[0]:
                return False, "stale_controller_sequence"
            self.db.execute(
                "INSERT INTO control_sequence VALUES (?,?) "
                "ON CONFLICT(controller) DO UPDATE SET last_seq=excluded.last_seq",
                (payload["source_node_id"], payload["sequence"]))
            self.db.execute(
                "INSERT OR IGNORE INTO revoked_authority VALUES (?)",
                (payload["authority_ref"],))
            self.db.execute(
                "UPDATE gmesh_state SET halted=1, "
                "generation=max(generation, ?) WHERE id=1",
                (payload["generation"],))
            return True, "local_revocation_committed"
        return self._transaction(revoke)

    def close(self):
        with self.lock:
            self.db.close()
