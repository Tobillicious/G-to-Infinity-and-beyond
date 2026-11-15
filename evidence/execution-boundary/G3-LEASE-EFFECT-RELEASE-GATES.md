# G3 lease-fenced marker effect — implementation and release gate

**Status:** research integration only, not production-deployed universal protection.

## What this increments

- `g_mesh_effect_bridge.py` binds an exact signed G-Mesh handshake's
  `event_digest` to the event being checked by the separately issued
  G3 Ed25519 permit and local synthetic witnesses.
- The bridge demands `require_fresh_lease=True`; an expired, missing,
  rollback-denied or locally revoked lease refuses the filesystem marker.
  Local G-Mesh handler lock covers its handshake authorization and the
  downstream protected marker dispatch, serializing holds issued **through
  that handler instance in the same service process**. Distinct processes
  need stronger coordination and complete OS enforcement.
- The Linux broker requires an additional signed mesh envelope for
  `effect_marker` when a lease-bound sink is installed; no old
  `effect_marker` request can silently take a bypass. A G3 signed
  permit, hold check, synthetic whole-context check and durable marker
  audit all still run. No arbitrary file/network/hardware effect is exposed.
- Replaying an exact mesh sequence refuses a second handshake, even if
  an idempotent effect is already journaled.

## Security limits and unresolved blockers

This adapter has **two SQLite stores** and a local Python lock, not one
atomic distributed transaction. Local mesh hold/revocation is serialized
only for a single handler instance; another process or privileged writer
can bypass the lock. Lease expiry may occur while a synchronous file
operation is in progress; the check is at the local effect-entry boundary,
and no filesystem effect can be rolled back. The signed mesh lease
authorizes only a local handshake, **not** original-six X3 evidence,
authentic consent or a universal physical safety certificate. Clock
trust/forward jumps, lease propagation delays, root/FD bypass, complete
capability mediation, operator consent, external attestation, audit logs,
independent process isolation, error containment, slowloris resistance,
and durable cross-resource crash recovery all need independent validation.

**Release decision:** research code may merge if exact-head CI passes.
Do not launch an internet-facing broker, production protected effect,
live model-provider gateway, physical actuator or claim universal G.
A narrowly named application with an independently checked capability
inventory, signed policy and explicit effect rights is required for a
production candidate.

## Next steps

1. Run independent host/UID isolation for mesh controller and effect writer;
   verify alternate handles, spawn/fork FD hygiene, and crash-window behavior.
2. Bound broker concurrency and request-read timeouts; add hostile stalled
   client tests.
3. Bind lease/authority revocation into *one durable effect-time decision
   domain* or build a rigorously specified cross-service protocol.
4. Run full six-X3 source correspondence and rights/consent tests on a
   selected actual-world application before authorizing any nontrivial effect.
