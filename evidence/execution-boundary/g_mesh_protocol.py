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
LEASE_FIELDS = frozenset((
    "protocol", "type", "source_node_id", "target_node_id",
    "deployment_id", "policy_digest", "generation", "sequence",
    "not_after",
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


def _valid_lease(data, node_id, deployment, policy):
    return (type(data) is dict and set(data) == LEASE_FIELDS and
            data["protocol"] == PROTOCOL and data["type"] == "lease" and
            _nonempty(data["source_node_id"]) and
            data["target_node_id"] == node_id and
            data["deployment_id"] == deployment and
            data["policy_digest"] == policy and
            _positive(data["generation"]) and _positive(data["sequence"]) and
            _positive(data["not_after"]))


class GMeshProtocolHandler:
    """Durable, local-only source-scoped sequence and controller hold.

    Trusted keys are pinned at initialization. Peer-provided attestation_ref
    is UNVERIFIED metadata; deployment-level TEE verification is absent.
    A successful handshake is NOT authorization to enact an external effect.
    """

    def __init__(self, db_path, *, node_id, deployment_id, policy_digest,
                 issuer_keys, controller_keys, clock=None,
                 require_fresh_lease=False, max_lease_seconds=30):
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
        if type(require_fresh_lease) is not bool or (
                type(max_lease_seconds) is not int or
                max_lease_seconds < 1 or max_lease_seconds > 300):
            raise ValueError("bounded fresh-lease configuration required")
        self.require_fresh_lease = require_fresh_lease
        self.max_lease_seconds = max_lease_seconds
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
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS lease_state "
            "(id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER NOT NULL, "
            "not_after INTEGER NOT NULL, controller TEXT NOT NULL, "
            "last_seq INTEGER NOT NULL)")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS lease_sequence "
            "(controller TEXT PRIMARY KEY, last_seq INTEGER NOT NULL)")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS time_floor "
            "(id INTEGER PRIMARY KEY CHECK(id=1), last_seen INTEGER NOT NULL)")
        self.db.execute("INSERT OR IGNORE INTO time_floor VALUES (1,0)")

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

    def _observe_clock_locked(self, now):
        """Persist a local clock floor even when a permit/lease is expired.

        This only protects against rollback below previously observed local
        timestamps, not forged forward time, trusted UTC or host compromise.
        """
        prior = self.db.execute(
            "SELECT last_seen FROM time_floor WHERE id=1").fetchone()
        if prior is None or type(prior[0]) is not int or prior[0] < 0:
            return False, "clock_state_invalid"
        if now < prior[0]:
            return False, "clock_rollback"
        self.db.execute("UPDATE time_floor SET last_seen=? WHERE id=1", (now,))
        return True, "clock_current"

    def install_authority_lease(self, payload, signature, canonical=None):
        """Locally install a short-lived signed controller heartbeat/lease.

        This is NOT network consensus or consent. A partition or dropped
        renewal forces future handshakes to fail after local expiry.
        """
        if not _valid_lease(
                payload, self.node_id, self.deployment_id, self.policy_digest):
            return False, "invalid_lease_schema"
        key = self.controller_keys.get(payload["source_node_id"])
        if key is None or not self._verify_signature(
                key, payload, signature, canonical):
            return False, "invalid_controller_signature"
        try:
            now = self.clock()
            if type(now) is not int or now < 0 or now >= 2**63:
                return False, "clock_unavailable"
        except (TypeError, ValueError, OverflowError):
            return False, "clock_unavailable"

        def accept():
            clock_status = self._observe_clock_locked(now)
            if not clock_status[0]:
                return clock_status
            state = self.db.execute(
                "SELECT halted,generation FROM gmesh_state WHERE id=1"
            ).fetchone()
            if state is None or state[0]:
                return False, "FAIL_CLOSED_local_hold"
            if payload["generation"] != state[1]:
                return False, "stale_generation"
            if (payload["not_after"] <= now or
                    payload["not_after"] - now > self.max_lease_seconds):
                return False, "lease_expired_or_too_long"
            prior = self.db.execute(
                "SELECT last_seq FROM lease_sequence WHERE controller=?",
                (payload["source_node_id"],)).fetchone()
            if prior is not None and payload["sequence"] <= prior[0]:
                return False, "lease_replay"
            self.db.execute(
                "INSERT INTO lease_sequence VALUES (?,?) "
                "ON CONFLICT(controller) DO UPDATE SET last_seq=excluded.last_seq",
                (payload["source_node_id"], payload["sequence"]))
            self.db.execute(
                "INSERT INTO lease_state VALUES (1,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET generation=excluded.generation,"
                "not_after=excluded.not_after,controller=excluded.controller,"
                "last_seq=excluded.last_seq",
                (payload["generation"], payload["not_after"],
                 payload["source_node_id"], payload["sequence"]))
            return True, "local_lease_installed"
        return self._transaction(accept)

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
            clock_status = self._observe_clock_locked(now)
            if not clock_status[0]:
                return clock_status
            state = self.db.execute(
                "SELECT halted,generation FROM gmesh_state WHERE id=1"
            ).fetchone()
            if state is None or state[0]:
                return False, "FAIL_CLOSED_local_hold"
            if payload["generation"] != state[1]:
                return False, "stale_generation"
            if self.require_fresh_lease:
                lease = self.db.execute(
                    "SELECT generation,not_after FROM lease_state "
                    "WHERE id=1").fetchone()
                if (lease is None or lease[0] != state[1] or
                        now >= lease[1]):
                    return False, "FAIL_CLOSED_lease_unavailable"
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
