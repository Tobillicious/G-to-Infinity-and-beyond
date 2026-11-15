# G3 first physical-effect boundary: executable release contract

**Status:** proposed engineering contract; NOT a production release, physical-safety certificate, universal G proof, or replacement for the original six-X3 obligations.
**Base:** PR #456 signed G-Mesh lease → G3 protected empty-marker effect.
**First bounded application:** offline Markdown→HTML compilation using synthetic, non-sensitive documents only.
**Scope exclusion:** internet-facing gateways, live Te Kete Ako deployment, student records, public deployment, physical actuators, distributed atomicity.

## Goal and security property

The application is untrusted. It may request an output effect but must never obtain raw write access to the protected output tree. The only writer is a separately isolated, minimal effect broker.

For every published output `o`:
`published(o) ⇒ committed_intent(o) ∧ policy_valid(o) ∧ authorized_exact_digest(o) ∧ generation_current_at_commit(o) ∧ audit_recoverable(o)`.

This is a *target property*, not a claim about present PR #456. Safety and liveness are separately evaluated: fail-closed decisions do not by themselves guarantee availability or human safety.

## Threat and trust boundary

Trust: Linux kernel and host configuration, broker binary/runtime, broker signing keys, durable-storage semantics, policy/rights configuration and authenticated authority updates. All require independent review.

Adversary: attacker-controlled Markdown, compiler process, child processes, inherited file descriptors, symlinks, socket clients, stale signed requests, replayed signatures, crashed/restarted workers, concurrent workers, disk-full and abrupt power failures.

Never accept a client-provided output path, UID, policy identifier, generation, capability or effect type as sufficient authorization. The broker resolves a preconfigured output root and an allowlisted logical target. The compiler has no filesystem access to the output root or broker journal.

OS enforcement requirements: distinct UIDs; restricted mounts, capabilities and namespace visibility; close-on-exec and exhaustive FD hygiene; deny outbound networking unless separately justified; limit subprocesses, CPU, memory, file sizes and execution duration. Containerization alone is not proof of mediation. Verify alternate handles, hard links, symlink races, `/proc` FD access and privileged-bypass assumptions. Root or host-admin compromise is outside this initial threat model and must be explicitly documented.

## Authorized request envelope

Canonical, versioned fields:
- `request_id`: unique, unguessable operation identifier;
- `source_digest`, `output_digest`: exact byte hashes;
- `logical_target`: allowlisted target key, not arbitrary filesystem path;
- `policy_digest`, `authority_id`, `generation`;
- `not_before`, `not_after`: bounded validity and monotonic-time requirements;
- `g3_permit` and signed G-Mesh freshness evidence bound to all above;
- `rights_evidence_ref`: externally inspected domain-specific rights/consent evidence, not a cryptographic assertion of authentic consent.

Reject unknown mandatory fields, noncanonical encoding, mismatched digests, wrong subject/destination, stale generations, missing holds, replay, revoked authority, expired lease and absent mandatory rights evidence. A signed request must not override a current durable hold.

## Single-domain durable state machine

One authoritative SQLite database controls broker decisions, generations, revocations and publication intents. This first candidate avoids the two-store split from PR #456; it does not attempt a distributed transaction.

Allowed states:
- `DENIED`: no publication possible;
- `PREPARED`: durable intent records exact output identity/digest, target and generation;
- `STAGED`: bytes in an unexposed temporary location, with digest verified and file synchronized;
- `PUBLISHED`: target points to staged verified bytes using same-filesystem atomic replace and directory synchronization;
- `COMPLETE`: journal reconciled with filesystem state.

Transitions are monotonic for each `request_id`. A new request never reuses an old request ID. Generation fencing is checked under a serialized durable decision boundary immediately before publication. Authority updates and publication decisions must use one lock/transaction regime; distinguish this local guarantee from cross-host consensus.

Publication cannot be rolled back by mere lease expiry after it happens. Define a `publication-commit instant`: a lease must be valid at this instant; subsequent revocation prevents *new* publications, not retroactively unwrites bytes. Choose a monotonic clock for local freshness and a defended restart/clock-rollback policy.

### Crash protocol (candidate, to test before implementation claims)

1. Verify the exact signed envelope and current durable authorization.
2. Write `PREPARED` and commit with tested durability settings.
3. Create staged bytes in a broker-private directory on the destination filesystem. Hash, size-check, flush and `fsync` the staged file.
4. Verify authorization and generation again at the serialized publication decision boundary; record the decision durably.
5. Atomically publish within one filesystem and synchronize destination directory. Avoid path traversal, symlink following and replacement outside the allowlist.
6. Reconcile journal status and return an idempotent response tied to `request_id`.

The filesystem rename and database commit are NOT atomic together. Recovery MUST inspect both the durable intent and the actual file/digest, including power loss between rename and final journal update. If reconciliation cannot distinguish states, quarantine and deny new effects rather than guessing. WAL, `synchronous=FULL`, and `fsync` require verification against actual filesystem/hardware failure semantics; a hash chain alone is not tamper-proof absent external anchoring.

## Required negative tests

| Attack / failure | Acceptance result |
| --- | --- |
| Direct output write by compiler, child or inherited FD | OS denies; no protected bytes change |
| Broker socket without valid permit and signed lease | Denied; no output |
| Signed permit for different digest or target | Denied |
| Replayed request after success | Same outcome reported; no second publication |
| Expired lease or durable hold before commit | Denied; no publication |
| Concurrent revocation and write | One well-defined serialized order and audit |
| Generation rollback and stale worker | Denied |
| Crash before intent persistence | No publication |
| Crash after intent, before staged output | Recovery denies/reconciles safely |
| Crash after staging, before publication | Recovery verifies digest and cleans/quarantines |
| Crash after rename, before completion record | Recovery recognizes exact digest and reconciles without duplicate effect |
| Disk full, interrupted writes or corrupted journal | Deny/hold; no unverified publication |
| Stalled client, oversized payload and request flood | Timeouts, quotas and bounded memory/FDs |
| Alternate output path, symlink swap and hardlink attack | No unauthorized mutation |

Run crash injection at every transition, then kill *the broker process*, not just throw an exception. Repeat on the target filesystem and isolate logs, journal and output from the compiler UID. Record exact source SHA, OS/kernel and filesystem, test commands, failures and CI run URLs.

## Domain-specific original-six X3 release gate

For **every affected person/particular in the selected application**, independently map original-six X3 duties (historical continuity, authentic authorization, freedom, least-necessary restraint, feasible maximality, provenance) to actual source evidence and negative tests. The G-Mesh handshake's `attestation_ref` is not that evidence; synthetic witnesses alone do not certify it. A signed lease is an authorization mechanism, not consent or a universal physical-safety proof.

## Te Kete Ako production boundary

Do NOT wire this experimental broker into `te-kete-ako-production` yet. Its AGENTS.md parks Sovereign Lattice/SLH-J work from TKA time and requires agent task claims, registration for new scripts, independent checks and explicit release ownership. The first educational pilot, *if independently authorized*, should compile entirely synthetic teaching Markdown outside the live site and must not read real student, teacher-account, Supabase, Stripe or KAMAR data. A separate product-scoped approval and threat-model review is required before any Te Kete Ako PR.

## Implementation order

1. Existing #456 code remains unchanged; pin the exact baseline and reproduce current unit tests.
2. Implement a standalone, opt-in offline broker fixture with a one-store generation/hold/intention state machine and crash-injection hooks.
3. Run adversarial isolation tests under distinct OS UIDs and non-root compilation.
4. Independent adversarial review + exact-head CI + crash matrix.
5. Only after these pass, assess a real, bounded application pilot and publish a narrow, evidence-backed release statement.

**No implementation, CI, root isolation, crash durability, physical deployment, or universal protection is certified by this document alone.**
