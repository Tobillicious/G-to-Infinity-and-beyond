"""G3 synthetic EFFECT boundary: check again at dispatch, not just admission.

Only writes a SQLite fixture table. Never performs external IO, never imports
or changes target.py, and is NOT a real-world actuator gateway. All controller
operations and dispatches use the inherited local SQLite serialized boundary.
"""
import sqlite3

from koru_shadow import ShadowVerifier, digest
from koru_ed25519_permit import verify_ed25519
from koru_pilot_gate import PilotGate


class SyntheticEffectGate(PilotGate):
    def __init__(self, db_path, **kwargs):
        # A protected effect path MUST NOT inherit permissive unsigned/HMAC modes.
        if kwargs.get("ed25519_public_key") is None:
            raise ValueError("synthetic effect path requires Ed25519 public key")
        if kwargs.get("permit_verification_key") is not None:
            raise ValueError("shared-secret permit is not allowed in effect path")
        super().__init__(db_path, **kwargs)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS synthetic_effects ("
            "event_id TEXT PRIMARY KEY, payload_digest TEXT NOT NULL, "
            "receipt TEXT NOT NULL UNIQUE)")

    def dispatch_synthetic(self, event, *, now, permit):
        """Check registered event + live permit, then atomically write ONE toy effect.

        Admission receipt never grants effect permission on its own. Every check
        is repeated at effect time in the same SQLite transaction as local write.
        """
        def act():
            audit = self._audit_locked()
            if not audit["ok"]:
                return audit
            if type(event) is not dict:
                return {"ok": False, "code": "envelope_schema"}
            state = self.db.execute(
                "SELECT generation, halted, context_version, context_digest, "
                "predecessor_ref FROM gate_state WHERE id=1").fetchone()
            generation, halted, version, context_hash, predecessor = state
            if halted:
                return {"ok": False, "code": "held_at_effect"}
            if (event.get("context_ref") != self.context_ref or
                    event.get("context_version") != version or
                    event.get("context_digest") != context_hash or
                    event.get("predecessor_ref") != predecessor):
                return {"ok": False, "code": "stale_effect_context"}
            # Verify the *current* signature, expiry and authority under the lock.
            if not verify_ed25519(
                    self.ed25519_public_key, permit, issuer=self.permit_issuer,
                    event=event, now=now):
                return {"ok": False, "code": "invalid_permit_at_effect"}
            if self.db.execute(
                    "SELECT 1 FROM revoked_authorities WHERE authority_ref=?",
                    (event.get("authority_ref"),)).fetchone():
                return {"ok": False, "code": "authority_revoked_at_effect"}
            payload_hash = digest(event)
            row = self.db.execute(
                "SELECT payload_digest, context_digest, predecessor_ref, receipt "
                "FROM records WHERE event_id=?", (event.get("event_id"),)).fetchone()
            if row is None:
                return {"ok": False, "code": "not_admitted"}
            prior_hash, prior_context, prior_head, admission_receipt = row
            expected = digest(["koru-pilot-v1", event["event_id"], payload_hash,
                               context_hash, predecessor])
            if (prior_hash != payload_hash or prior_context != context_hash or
                    prior_head != predecessor or admission_receipt != expected):
                return {"ok": False, "code": "effect_payload_mismatch"}
            # Re-evaluate the whole synthetic expression and current authority,
            # suppressing admission replay checks: this is a DIFFERENT boundary.
            checked = ShadowVerifier(
                contexts=self.contexts, signatures=self.signatures,
                witnesses=self.witnesses, authorities=self.authorities,
                provenances=self.provenances, minimum_generation=generation,
                applied_ids=(), applied_keys=()).inspect(event, now=now)
            if not checked["shadow_pass"]:
                return {"ok": False, "code": "effect_" + checked["code"]}
            existing = self.db.execute(
                "SELECT payload_digest, receipt FROM synthetic_effects "
                "WHERE event_id=?", (event["event_id"],)).fetchone()
            if existing is not None:
                if existing[0] != payload_hash:
                    return {"ok": False, "code": "effect_collision"}
                return {"ok": True, "code": "already_dispatched", "receipt": existing[1]}
            receipt = digest(["synthetic-effect-only-v1", event["event_id"],
                              payload_hash, admission_receipt])
            self.db.execute(
                "INSERT INTO synthetic_effects VALUES (?,?,?)",
                (event["event_id"], payload_hash, receipt))
            return {"ok": True, "code": "synthetic_effect_recorded",
                    "receipt": receipt}
        return self._transaction(act)

    def effect_count(self):
        with self.lock:
            return self.db.execute(
                "SELECT COUNT(*) FROM synthetic_effects").fetchone()[0]
