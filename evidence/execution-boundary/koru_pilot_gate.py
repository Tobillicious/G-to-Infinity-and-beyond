"""Koru G controlled-pilot gate: local, synthetic, append-only transactions.

NOT real-world X3 certification, not a multi-service effect gateway, not a
replacement for target.py. A trusted in-process controller supplies independent
registries; the caller may NOT provide trusted evidence by placing it in an event.
The durable record contains ONLY event identity, digest, lineage and receipt.
"""
import sqlite3
import threading
from koru_shadow import ShadowVerifier, digest


class PilotGate:
    def __init__(self, db_path, *, contexts, signatures, witnesses,
                 authorities, provenances, context_ref, generation=1):
        self.lock = threading.RLock()
        self.contexts = contexts
        self.signatures = signatures
        self.witnesses = witnesses
        self.authorities = authorities
        self.provenances = provenances
        self.context_ref = context_ref
        self.db = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS gate_state (id INTEGER PRIMARY KEY CHECK (id=1), generation INTEGER NOT NULL, halted INTEGER NOT NULL, context_version INTEGER NOT NULL, context_digest TEXT NOT NULL, predecessor_ref TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS records (event_id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE, payload_digest TEXT NOT NULL, context_digest TEXT NOT NULL, predecessor_ref TEXT NOT NULL, receipt TEXT NOT NULL UNIQUE)")
        ctx = contexts[context_ref]
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

    def apply(self, event, *, now):
        """Check and persist together in ONE SQLite transaction; never enact external effects."""
        def act():
            generation, halted, version, context_hash, predecessor = self.db.execute(
                "SELECT generation, halted, context_version, context_digest, predecessor_ref "
                "FROM gate_state WHERE id=1").fetchone()
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
