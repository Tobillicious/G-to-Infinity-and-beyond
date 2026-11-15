"""Koru G controlled-pilot gate: local, synthetic, append-only transactions.

NOT real-world X3 certification, not a multi-service effect gateway, not a
replacement for target.py. A trusted in-process controller supplies independent
registries; the caller may NOT provide trusted evidence by placing it in an event.
The durable record contains ONLY event identity, digest, lineage and receipt.
"""
import copy
import sqlite3
import threading
from koru_shadow import ShadowVerifier, digest


class PilotGate:
    def __init__(self, db_path, *, contexts, signatures, witnesses,
                 authorities, provenances, context_ref, generation=1):
        self.lock = threading.RLock()
        # Freeze caller-supplied trust stores to prevent external mutation.
        self.contexts = copy.deepcopy(contexts)
        self.signatures = copy.deepcopy(signatures)
        self.witnesses = copy.deepcopy(witnesses)
        self.authorities = copy.deepcopy(authorities)
        self.provenances = copy.deepcopy(provenances)
        self.context_ref = context_ref
        self.db = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS gate_state (id INTEGER PRIMARY KEY CHECK (id=1), generation INTEGER NOT NULL, halted INTEGER NOT NULL, context_version INTEGER NOT NULL, context_digest TEXT NOT NULL, predecessor_ref TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS records (event_id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE, payload_digest TEXT NOT NULL, context_digest TEXT NOT NULL, predecessor_ref TEXT NOT NULL, receipt TEXT NOT NULL UNIQUE)")
        self.db.execute("CREATE TABLE IF NOT EXISTS revoked_authorities (authority_ref TEXT PRIMARY KEY)")
        ctx = self.contexts[context_ref]
        self.db.execute("INSERT OR IGNORE INTO gate_state VALUES (1, ?, 0, ?, ?, ?)",
                        (generation, ctx["version"], digest(ctx), ctx["predecessor_ref"]))

    def _transaction(self, f):
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                result = f()
                self.db.execute("COMMIT")
                return result
            except BaseException:
                self.db.execute("ROLLBACK")
                raise

    def revoke_authority(self, authority_ref):
        """Trusted-controller-only durable revocation; serializes with apply.

        This prototype has no remote authentication or grant issuance API.
        """
        if type(authority_ref) is not str or not authority_ref:
            raise ValueError("invalid authority ref")
        def act():
            self.db.execute("INSERT OR IGNORE INTO revoked_authorities VALUES (?)",
                            (authority_ref,))
        self._transaction(act)

    def hold(self, minimum_generation):
        """Trusted-controller call only. No untrusted HTTP/RPC access is provided."""
        def act():
            current = self.db.execute("SELECT generation FROM gate_state WHERE id=1").fetchone()[0]
            self.db.execute("UPDATE gate_state SET generation=?, halted=1 WHERE id=1",
                            (max(current, minimum_generation),))
        self._transaction(act)

    def release(self, generation):
        """Trusted-controller call only; advances fence, never decreases it."""
        def act():
            current = self.db.execute("SELECT generation FROM gate_state WHERE id=1").fetchone()[0]
            if type(generation) is not int or generation <= current:
                raise ValueError("release requires higher generation")
            self.db.execute("UPDATE gate_state SET generation=?, halted=0 WHERE id=1", (generation,))
        self._transaction(act)

    def _audit_locked(self):
        """Local consistency check; SHA-256 receipts are NOT authenticated MACs."""
        row = self.db.execute("PRAGMA quick_check").fetchone()
        if row is None or row[0] != "ok":
            return {"ok": False, "code": "database_integrity"}
        ctx_hash = digest(self.contexts[self.context_ref])
        context = self.contexts[self.context_ref]
        state = self.db.execute(
            "SELECT context_version, context_digest, predecessor_ref "
            "FROM gate_state WHERE id=1").fetchone()
        if state != (context["version"], ctx_hash, context["predecessor_ref"]):
            return {"ok": False, "code": "trusted_context_mismatch"}
        for event_id, key, payload_hash, record_ctx, predecessor, receipt in self.db.execute(
                "SELECT event_id, idempotency_key, payload_digest, "
                "context_digest, predecessor_ref, receipt FROM records"):
            expected = digest(["koru-pilot-v1", event_id, payload_hash,
                               record_ctx, predecessor])
            if (type(event_id) is not str or not event_id or
                    type(key) is not str or not key or
                    type(payload_hash) is not str or len(payload_hash) != 64 or
                    record_ctx != ctx_hash or predecessor != context["predecessor_ref"] or
                    receipt != expected):
                return {"ok": False, "code": "record_integrity"}
        return {"ok": True, "code": "local_consistency_only"}

    def audit(self):
        """Audit the synthetic journal under the transaction lock."""
        return self._transaction(self._audit_locked)

    def apply(self, event, *, now):
        """Check and persist together in ONE SQLite transaction; never enact external effects."""
        def act():
            generation, halted, version, context_hash, predecessor = self.db.execute(
                "SELECT generation, halted, context_version, context_digest, predecessor_ref "
                "FROM gate_state WHERE id=1").fetchone()
            audit = self._audit_locked()
            if not audit["ok"]:
                return audit
            if halted:
                return {"ok": False, "code": "held"}
            if not isinstance(event, dict):
                return {"ok": False, "code": "envelope_schema"}
            if event.get("context_ref") != self.context_ref:
                return {"ok": False, "code": "wrong_context"}
            if event.get("context_version") != version or event.get("context_digest") != context_hash:
                return {"ok": False, "code": "stale_context"}
            if event.get("predecessor_ref") != predecessor:
                return {"ok": False, "code": "lineage_mismatch"}
            # Independent trust stores may only be updated by the trusted controller.
            # All accesses and authority revocation must serialize on self.lock.
            ids = {row[0] for row in self.db.execute("SELECT event_id FROM records")}
            keys = {row[0] for row in self.db.execute("SELECT idempotency_key FROM records")}
            if self.db.execute(
                    "SELECT 1 FROM revoked_authorities WHERE authority_ref=?",
                    (event.get("authority_ref"),)).fetchone():
                return {"ok": False, "code": "authority_revoked"}
            verifier = ShadowVerifier(
                contexts=self.contexts, signatures=self.signatures,
                witnesses=self.witnesses, authorities=self.authorities,
                provenances=self.provenances, minimum_generation=generation,
                applied_ids=ids, applied_keys=keys)
            result = verifier.inspect(event, now=now)
            if not result["shadow_pass"]:
                return {"ok": False, "code": result["code"]}
            payload_hash = digest(event)
            receipt = digest(["koru-pilot-v1", event["event_id"], payload_hash,
                              context_hash, predecessor])
            self.db.execute("INSERT INTO records VALUES (?,?,?,?,?,?)",
                            (event["event_id"], event["idempotency_key"],
                             payload_hash, context_hash, predecessor, receipt))
            # This pilot records events on an immutable context snapshot.
            # It does not alter protected actual world state or authorize an effect.
            return {"ok": True, "code": "durable_synthetic_record", "receipt": receipt}
        return self._transaction(act)

    def record_count(self):
        with self.lock:
            return self.db.execute("SELECT COUNT(*) FROM records").fetchone()[0]

    def close(self):
        with self.lock:
            self.db.close()
