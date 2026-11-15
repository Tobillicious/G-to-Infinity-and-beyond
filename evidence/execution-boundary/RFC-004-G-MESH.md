# RFC-004 — G-Mesh: federated G3 enforcement protocol (proposal)

**Status:** DRAFT / NOT IMPLEMENTED / NOT DEPLOYED  
**Scope:** Federated protected effect gateways within explicitly enrolled, independently audited deployments  
**Goal:** Extend the UPT ethical commitment to protect every owed particular through verifiable cooperation. No claim of globally enforced or unconditional physical protection follows from this RFC.

## 1. Security model

Local G3 protections, including the Ed25519-bound event gate, Linux credential checks and opt-in cross-process lock, apply only to a bounded protected effect path. Federation must not silently turn an unaudited remote node into an authority.

**Assumptions to verify, not axioms:**
- Each node enumerates all its real effect capabilities and prohibits direct bypass by untrusted code.
- Each node has a pinned trust policy, independent authority roster, secure key custody, local fail-closed gateway and an independently witnessed deployment identity.
- Network messages can be duplicated, reordered, delayed, dropped or partitioned. Hosts and individual members can be compromised. Byzantine behavior requires a separately specified fault model and consensus algorithm.
- A signed record is not authentic human consent, proof of the six X3 duties, nor a complete-state Koru preservation certificate.

Koru is the project’s **whole-preserving relational boundary**, not the unary function K or an arbitrary scalar balance score. Any proposed numerical balance proxy (e.g. `B(A,P) >= 0`) must be explicitly justified as a sound and complete refinement of the original relational duties before it becomes enforcement policy. None is assumed here.

## 2. Typed wire envelope (version 0, proposed)

All authenticated messages use explicitly versioned, length-limited canonical serialization and reject unknown critical fields. Schema proposal:

```json
{
  "protocol": "g-mesh-0",
  "type": "permit_request",
  "source_node_id": "node-public-key-fingerprint",
  "target_node_id": "node-public-key-fingerprint",
  "deployment_id": "audited-deployment-id",
  "event_digest": "sha256-of-canonical-whole-event",
  "policy_digest": "sha256-of-pinned-policy-version",
  "authority_ref": "registered-issuer",
  "generation": 3,
  "sequence": 1,
  "not_after": 100,
  "attestation_ref": "verifiable-attestation-evidence-id",
  "signature": "ed25519-over-canonical-body"
}
```

- The wire `sequence` is **per issuer/deployment/target stream** and atomically bound to durable store state; it is not claimed to be a magic globally monotonic nonce.
- Signature verification binds domain separator, source, target, event, policy, generation, sequence, expiry and deployment. Verify the public-key identity against the authoritative roster and its revocation epoch.
- Accept/reject/replay decisions require ACID storage **at the target effect-enactment gate**. Distributed agreement on remote authorization is necessary in some policies but never replaces local effect-time revalidation.
- No private keys or fake quorum signatures appear in source control.

## 3. Revocation, partitions and holds

**No instantaneous revocation guarantee.** A broadcast has unbounded latency under partitions. A remote hold becomes globally effective only under a separately stated synchrony assumption and audited propagation bound. Therefore:
1. Each enrolled gateway maintains an independent local emergency hold that blocks new effects immediately upon local activation.
2. To permit any external effect, the gateway must obtain an **unexpired, authenticated, policy-bound authority lease** and verify freshness against its own trusted clock and durable sequence floor. The lease bounds exposure to missed remote revocation, not necessarily to milliseconds.
3. If the policy requires quorum confirmation, unavailable consensus => **fail closed** for protected effects; do not silently fall back to cached approvals.
4. Revocation records advance monotonically with a signed authority epoch. Replays of older approvals cannot override a newer epoch.
5. On anomaly: **hold the protected effect gateway and preserve audit evidence. Do not invoke kernel panic, purge all state or kill unrelated services.** Emergency shutdown has its own safety and availability hazard assessment.

A safety claim must account for already completed physical effects; revocation cannot undo them.

## 4. Consensus, attestation and OS isolation

- Consensus choice (Raft vs Byzantine quorum) is a security decision. **Raft tolerates crash faults, not malicious byzantine quorum forgery.** Document exact adversary threshold and membership changes before any federation.
- A distributed lock alone does not provide cross-network atomic external side effects. Use explicit idempotency keys, transactional outbox or target-side finalization, recovery proofs and adversarial network tests.
- TPM/TEE quotes are evidence of measured code/configuration under a particular threat model; **they do not automatically prevent kernel compromise**, all DMA/device attacks or collusion. Hardware claim verification, quote freshness, trust anchor and independent verifier are separate obligations.
- Adopt a dedicated least-privilege effect writer OS identity; separate issuer and controller identities; restrict network, filesystem and inherited descriptor capabilities. Host root and a deliberately inherited privileged write FD remain bypasses under normal Linux DAC, explicitly shown by `test_g3_kernel_uid_fence.py`.

## 5. Protocol states and no-bypass invariant

For a *named* local effect capability `E` and enrollment policy `P`, the proposed invariant is:

```
effect_completed(E) =>
  authenticated_request(E)
  AND exact_event_and_policy_match(E)
  AND currently_valid_authority(E)
  AND current_local_hold_is_clear(E)
  AND locally_verified_fresh_lease_if_required(E)
  AND original_six_X3_predicates_witnessed_for_actual_E
  AND kernel-enforced_no_alternative_effect_path(E)
```

All actual-world predicates and the kernel bypass inventory remain obligations. Existence of a Lean lemma or this schema does not discharge them.

## 6. Staged verification plan

1. Parse/serialize/version tests with RFC fixtures and rejects for missing or unknown critical fields.
2. Two simulated nodes with **no real effects**: duplicate/reordered permits, forged issuer, replay, stale epoch, partition, restart and expired lease tests.
3. Three independent Linux OS principals for client/controller/effect writer and negative controls demonstrating root and leaked-FD bypasses. No bogus claim root is denied by `0600`.
4. Targeted kernel restrictions, FD scrub, no ambient capabilities, no mount/path bypass, negative controls against each real effect capability.
5. A carefully scoped production candidate with independent consent/source attestations and a threat-model review; do not deploy an abstract global promise.

## 7. Publication and evidence discipline

This RFC supplements, but does not revise, the historical source record or existing DOIs. Publication metadata must be syntax-checked against files that actually exist (`CITATION.cff`, `PUBLISHED-4.4.json`, `release.json`). Formatting checks cannot certify Zenodo record existence, publication completeness or theorem validity. Keep mathematical verification and deploy approval separately auditable.

## 8. Experimental v0 implementation (not a real federation)

The research implementation in `g_mesh_protocol.py` and
`g_mesh_provider.py` demonstrates **local**, per-source handshake sequence
checks and **locally committed** signed emergency holds, not agreement
between remote nodes. A pinned issuer public-key roster signs exact v0
`handshake` messages; a separately pinned controller roster signs
`revoke` messages. Signatures cover reconstructed canonical JSON with
a protocol domain separator. Inputs with extra fields or caller-supplied
bytes that disagree with canonical encoding are rejected. The source's
sequence floor and controller's revocation sequence floor are durable
SQLite state, with `BEGIN IMMEDIATE` for atomic check/update.

A valid handshake means **authenticated research message only**.
It does **not** verify the attestation reference, actual original-six
duty coverage, real consent, remote lease freshness, protected
hardware, or an actual world's physical invariants. The protocol
handler has NO network server and NO effect API. A signed local
revocation makes the node fail closed and survives process restart.
Untrusted / malformed packets are refused without empowering arbitrary
remote senders to trigger a global halt.

The optional registry uses injected *offline mock callbacks only*.
It neither holds provider API keys nor performs HTTP requests. Model
outputs are returned as `verified_for_effects=False`; even a harmless
text response is not a certificate of Koru preservation. Model content
may require independent privacy, safety and authorization review before
any release or effect. This v0 is **not wire-compatible** with the
draft handshake fields in the user's earlier `g-mesh/1.0` sketch;
no negotiation or automatic upgrade is offered. The RFC's proposed
distributed quorum, TEE, network-isolation and original-six bridges
remain pending.

## 9. Two-node partition experiment and short signed leases

`g_mesh_protocol.py` now optionally enables `require_fresh_lease=True`
and accepts short, exactly scoped, controller-signed `lease` messages.
The issuer public key cannot sign controller leases; each lease binds the
protocol domain separator, intended target, deployment, pinned policy digest,
generation, per-controller monotone sequence and absolute expiry. The local
SQLite store atomically persists the lease and its signed sequence floor,
and a durable last-observed-clock floor denies time rollback. Lease length
is explicitly bounded by `max_lease_seconds` (10 seconds in tests;
configurable 1–300 seconds). No path without a valid local lease can pass
handshake admission when fresh-lease mode is enabled.

`test_g_mesh_two_node.py` simulates two independent SQLite nodes, explicit
delivery, dropped controls, reordered renewals, forged keys, replay after
restart, clock rollback and bounded expiry. It **deliberately demonstrates**
that a remote hold delivered to Alpha cannot instantly invalidate Beta
while Beta is partitioned and still has an unexpired local lease. At expiry,
Beta blocks new handshakes until it receives a fresh, separately authenticated
lease; an old/reordered renewal cannot extend the deadline.

**Limits:** this is offline simulation, not distributed consensus or a trusted
global clock. Signed renewals are assumed to come from an uncompromised
controller; an adversary controlling that key can authorize a new lease.
The temporary interval before expiry is an **explicit residual revocation
window**, not universal instantaneous guardianship. No actual external effects
are exposed here, and a handshake itself is NOT enactment authorization. Any
future real effect gateway must recheck the lease atomically at the local
effect boundary, establish actual original-six X3 coverage and verify all
alternative effect paths. Operator clocks, process privileges, TEE roots and
true network timing remain independently unverified.
