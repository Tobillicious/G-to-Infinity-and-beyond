# G protection gate — isolated, controlled pilot (15 November 2026)

**Research build on draft PR #447. Not deployed. No changes to the existing E-LIN trusted runtime.**

## What was built

- [`koru_pilot_gate.py`](koru_pilot_gate.py): a Python 3.9+ stdlib SQLite application-boundary prototype. It calls the **existing** [`koru_shadow.py`](koru_shadow.py) checker **inside** the same serialized SQLite transaction that records a synthetic event. It retains a durable record of event identity, payload digest, full-context binding, predecessor and receipt; not raw private source data.
- [`test_koru_pilot_gate.py`](test_koru_pilot_gate.py): negative controls for a valid synthetic event, replay across restart, revoked authority, changed expression with same numerical result, whole-context changes, stale context/lineage, hold and generation fencing, forged witness, and concurrent duplicate submissions.

Run in a checkout of the draft branch at repository root:

```sh
python3 -B -m unittest discover -s evidence/execution-boundary -p 'test_koru_shadow.py' -v
python3 -B -m unittest discover -s evidence/execution-boundary -p 'test_koru_pilot_gate.py' -v
```

**Verification receipt:** The original synthetic suites passed in GitHub Actions run [43688858124](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43688858124). Later changes (including durable revocation) require a **new** successful CI run at their exact commit SHA before being reported verified.

## Local integrity checks (synthetic pilot)

The pilot now exposes `audit()` and automatically runs the same local consistency check before every `apply()` transaction. It checks SQLite `PRAGMA quick_check`, the persistent context binding against the controller-injected context, and each stored event receipt against its stored event identity, payload digest, context and predecessor. Tampered record fields or context bindings fail closed during admission; regression tests deliberately modify SQLite rows and assert rejection. Checks are O(number of recorded events), appropriate only for this small research fixture.

**Important:** These receipts are plain SHA-256 *consistency digests*, not keyed MACs, signed attestations, or external audit anchors. An actor with privileged database access can rewrite a record and recompute its digest. This check is **not** tamper-proof, does not authenticate real permission, and does not guarantee forensic completeness. A stronger release must use a separate trust root or protected signing key, authenticated controller, recovery procedures and independent audit receipts.

## Opt-in authenticated event permits (synthetic)

`koru_pilot_permit.py` adds an HMAC-SHA256 permit envelope binding the exact event digest, context digest, authority reference, trusted issuer label, and expiry. `PilotGate(..., permit_verification_key=..., permit_issuer=...)` activates fail-closed permit verification **at admission time**. The gate still separately checks independent fixture authority, persisted revocations, witnesses, generation and whole-context consistency. Tests cover absent permits, expired permits, modified contents/expiry, fabricated tags, wrong issuer, replay, and validly signed but later revoked authority.

**This is a research prototype, not independently authenticated deployment.** The signing function `issue_permit` is a trusted-issuer-only development utility, not available to untrusted agents. Its 32-byte test keys are inert public fixtures. A live secret must not be stored in Git or provided to the agent; keep signing in a separate trusted process/HSM and isolate permit verification from the untrusted caller. Because this is symmetric HMAC, **any holder of the verifier secret can also issue permits**. The current gate holds that key in memory, so a process compromise defeats this separation; a future real release should use independent asymmetric signing (public key only at the gate), authenticated revocation, constrained issuer scopes, secure time, proper key rotation and verified key provenance. No claims of authentic real-human consent or universality follow from this change.

`permit_verification_key=None` leaves legacy synthetic fixture behavior unchanged for backward compatibility. A protected deployment must explicitly enable verification and prevent access to any unprotected write path; opt-in protection alone is not complete mediation.

## G3 asymmetric-issuer milestone (15 November 2026)

The opt-in `koru_ed25519_permit.py` introduces Ed25519 event permits:
- Only the **trusted issuer** needs an Ed25519 private key; `PilotGate(..., ed25519_public_key=..., permit_issuer=...)` receives **only the public key** and cannot mint a valid signature from that key.
- A permit covers the exact event bytes under canonical JSON hashing, expected issuer label, context digest, authority reference and expiry.
- Checks occur in the same local database application transaction as revocation, fencing, synthetic witness validation and durable record insertion.
- `test_koru_ed25519_permit.py` exercises valid admission, forged signature, expired grant, wrong key/issuer, changed payload/context, revocation, hold, replay and absence of issuer-private-key methods on the gate.
- CI installs `cryptography==46.0.4` for this test suite; the original stdlib-only HMAC/unsigned synthetic fixtures remain backward-compatible, but **production routes must not enable these bypass modes**.

**Verified source receipt:** [GitHub Actions run 43691062134](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43691062134) passed the asymmetric permit controls. This is a *pilot security milestone*, not complete G3 as universal physical protection. An externally trusted mapping from issuer to authorized real people, tamper-resistant key provisioning, independent time/revocation/key rotation and exhaustive protected effect channels remain required. Do not expose the Python `issue_ed25519` function to the agent or place any live key in the repository.

## G3 effect-time boundary: recheck rather than trust admission

[GitHub Actions run 43691420837](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43691420837) **passed** the new `test_koru_synthetic_effect_gate.py` suite.

`koru_synthetic_effect_gate.py` extends the pilot with a *separate, local SQLite synthetic-effect table*, NOT an actual actuator. It is a **protected-only** prototype requiring an Ed25519 public key. The `dispatch_synthetic` method rechecks at effect time, atomically with recording the synthetic effect:
- current hold/generation, exact whole context and lineage;
- unexpired Ed25519 signature tied to the exact original event;
- durable authority revocation;
- exact match against the already admitted event digest and receipt;
- original independent synthetic six-position witness/authority/provenance checks;
- unique event ID and idempotent retry, including across restart.

The regression suite exercises revoked or expired permits *after* admission, hold between admission/effect, stale generation, changes to the event even with a freshly signed permit, unsigned-effect refusal, concurrency and restart.

**The boundary is purposefully narrow.** The only "effect" is a local SQLite row. No external API, filesystem writer, actuator or AI process is controlled. SQLite's single-transaction guarantee does **not** extend to a network side effect, multiple services or physical hardware. The source inspector still uses synthetic witnesses, not verified real subject rights. All effect paths in any actual deployment would need to be forced through a separately hardened application boundary, with authenticated key provisioning, secure clocks, durability and revocation across processes, independently enforceable shutdown and recovery, and end-to-end adversarial testing. Do not represent this as unconditional physical protection.

## G3 direct-write bypass inventory and scoped adapter hardening

[GitHub Actions run 43691660612](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43691660612) passed the extended effect-boundary tests.

The prototype now uses a SQLite statement authorizer to refuse direct `synthetic_effects` mutations through **its own existing gate connection** except during the explicitly checked `dispatch_synthetic` write. Statement caching is disabled to prevent an earlier compiled permitted statement being reused after the protected write ends. The effect gate also audits each recorded synthetic effect against the associated admitted event hash and its derived receipt; mismatches fail closed on subsequent dispatch/admission. Tests check raw connection write refusal, unauthorized row and receipt tampering, and detection of inconsistent histories.

**Crucial negative control: complete mediation is NOT established.** The suite intentionally opens a *separate* SQLite connection and shows it can write `synthetic_effects` without passing `dispatch_synthetic`, so long as the caller retains filesystem write privileges. This is a demonstrated bypass under the current deployment design, not a hypothetical issue. Detection by the next gate audit does not undo an already landed write. Python/SQLite authorizers are not operating-system access control and may also be changed by privileged code in the same process.

Therefore a real effect boundary must move the durable sink behind OS-enforced isolation (separate principal, file and socket permission boundaries, no delegated writable handles), with an authenticated narrow IPC interface to the trusted gate, trusted signed revocation, and no secondary writable path. Only then can complete mediation be tested for that precisely enumerated deployment; do not claim universal real-world G3 from this adapter.

## G3 OS-principal protected broker — privileged Linux negative-control proof-of-concept

**Verified:** [GitHub Actions run 43692118085](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43692118085) passed the Linux distinct-UID OS-boundary test and inherited synthetic tests.

`koru_broker.py` exposes only two untrusted operations over a local UNIX socket: `admit` and `dispatch`. Those forward to the already-proved-in-tests signed synthetic gate; no `hold`, `release`, `revoke`, or raw SQL command exists on the client interface. The front end limits request length, rejects unknown fields and unknown operations, and keeps the public verification key rather than any signing key.

`test_koru_os_broker.py` runs on a privileged Linux CI worker with ephemeral assets only, setting a root-owned private SQLite directory to mode `0700` and using a distinct unprivileged UID (`nobody`) as the test client. The socket is reachable through a separate directory, but a direct `O_RDWR` attempt against the database is rejected by operating-system permissions. The untrusted user can submit an **independently test-signed** event through the broker and have exactly one **synthetic SQLite effect** recorded; attempts to send the `hold` control command over the untrusted socket are refused. Replay returns `already_dispatched`.

This is **more than a Python authorizer check**, because the negative control crosses an actual OS UID boundary. It is **not** a proof of complete mediation beyond the enumerated test path. The broker still executes prototype Python code from the CI checkout, the socket is intentionally reachable by all local users in the fixture (so authentication is carried by signed event permits rather than socket identity), and the test does not cover network transport, inherited descriptors, privileged process compromise, service restart during partial operations, OS mandatory access control, hardware actuators or external sinks. Do not deploy a privileged service from mutable/untrusted source code or claim all local OS principals, root, compromised broker processes or real-world effects are protected. A production design needs locked trusted artifacts, minimal privilege, tightly authenticated IPC, OS confinement, key rotation, recovery and comprehensive capability inventory.

## G3 broker hardening: kernel peer credentials and trusted time

**Verified:** [GitHub Actions run 43692576524](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43692576524) passed the Linux broker regression suite.

The broker now **requires** an explicit allowlist of non-root Linux UIDs and verifies each connection's kernel-provided `SO_PEERCRED` UID *before reading the request*. Unknown peers receive `peer_denied`. Non-Linux platforms without this kernel credential interface cannot start this secure fixture. This is an application allowlist, not an OS mandatory-access-control policy. Socket mode `0666` in the test fixture allows other local users to connect but their requests are denied by the kernel-credential check; a deployment should additionally restrict its socket filesystem permissions and directory ownership.

The broker also **ignores the caller's clock** and derives the permit's expiry checks from a broker-owned clock. The client protocol no longer accepts a `now` field; an attempted client timestamp injection is rejected with `bad_request`. Linux CI tests a permit expired according to the server clock even when the client supplies an earlier value. All source-signature, revocation, fenced-effect and exactly-once protections remain in place.

**Remaining obligations:** The fixture clock is injected for deterministic tests; production needs a securely managed, trusted clock resilient to rollback. The test does not establish resistance to a compromised broker UID, root administrator, filesystem-owner capability leakage, malicious code loaded into the trusted process, arbitrary kernel compromise, unsigned recovery paths, or external effects. Neither a Linux UID nor Ed25519 signature alone proves authentic subject consent or the original six X3 duties for an actual-world action.

## G3 durable trusted-clock floor (restart / rollback negative controls)

**Verified:** [GitHub Actions run 43692984732](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43692984732) passed the updated synthetic effect and OS-broker suites.

`SyntheticEffectGate.accept_broker_time(now)` persists the last observed broker clock value in a singleton SQLite row using `BEGIN IMMEDIATE` and rejects a lower subsequent value with `clock_rollback`. The Linux broker calls this **before** it admits or dispatches any event. An invalid or overflowing clock is rejected, and the persisted floor is retained after a gate/broker process restart. Tests cover rollback after restart, repeated timestamps, forward advancement, negative/non-integer input, and invalid oversized timestamps.

This closes a specific *time rollback below the last broker-observed time* failure: after a successful check at time `t`, the broker will not accept a request evaluated at any `t' < t` even if it has a correctly signed permit. It does not prove wall-clock truth, reject a forward clock jump, or authenticate OS time. A privileged database writer can edit the floor; an attacker who compromises the trusted broker can also change the clock. Large forward jumps can cause fail-closed availability loss when time is corrected. Production requires independent clock trust, monotonic-time policy, recovery procedures and a review of failure behavior. This is a *synthetic local protection* milestone, not physical universality.

## G3 transaction-time clock fence and restart-resistant signed permits

**Verified:** [GitHub Actions run 43693338937](https://github.com/Tobillicious/universal-protection-theory/actions/runs/43693338937) passed the transactional clock and socket restart tests.

The earlier design advanced `broker_time_floor` in a separate transaction before admission/dispatch. Under concurrency, another request could advance that floor between the first transaction and the action's transaction. The revised `SyntheticEffectGate._clock_check_locked` rejects any request with a timestamp below the latest persisted floor **inside the same SQLite transaction as the admission or synthetic effect insertion**. The legacy unsigned research pilot retains its original behavior; the signed effect gate receives the stricter check. Tests simulate an in-flight request using stale time after another request advances the floor, including both admission and dispatch.

`test_koru_broker_restart.py` adds an end-to-end UNIX-socket broker shutdown/reopen test using the same database. It demonstrates: admission at time 30, restart with time 20 rejected as `clock_rollback`, an expired signed permit at time 35 rejected as `invalid_permit_at_effect`, and subsequent time 31 rejected as rollback. No synthetic effect is recorded in the negative controls. The broker's own clock remains the source of time; the client cannot supply a timestamp.

The tests **do not** establish authenticated UTC, protect against privileged database modification, or stop compromise of the broker OS identity. Time-floor enforcement is not a proof of original-six universal physical coverage or real-world effect mediation. Proper secure time and hardened, independently verified recovery remain important release obligations.

## Why this is not yet the enforcement release

The pilot is **synthetic and append-only**. It is not a proof verifier, independent human consent authenticator, cultural authority, cryptographic signing service, external-world effect router, or general implementation of the original six X3 duties. Its `ShadowVerifier` understands a toy six-position integer world and one `synthetic_refinement` kind. The code does not mutate actual world state or send externally effective actions.

The supplied `contexts`, `witnesses`, `authorities`, `signatures`, and `provenances` are **trusted-controller injected registries**; they are **not** accepted from the untrusted event itself. In this local pilot, **all trusted registry changes must serialize on the gate lock**. There is **no remote caller authentication** on `hold`/`release`; those Python methods are trusted-controller-only in-process interfaces. Do not expose them as untrusted network endpoints. There is no cross-process coordination for those memory-resident registries.

A SQLite commit with `synchronous=FULL` provides an isolated local durability experiment, not a proof that any filesystem, hardware controller or external service is atomic and crash safe in all conditions. The context is immutable during this pilot; real versioned world transitions and authorized metadata updates require a separately designed controller.

## Next release gates (not silently assumed)

1. Run baseline `harness.py` and both unit suites on a supported machine, record exact source SHA and runtime settings; ensure old trusted runtime stays unmodified.
2. Build an independently authenticated controller for authority **issuance**, privacy deletion, evidence and context updates. The local revocation and revocation/admission concurrency experiments now exist but still need multi-process and corruption/recovery tests; do not equate this local method with independent authentication.
3. Build a genuine original-six-X3 event witness with independently validated subject, history, consent, freedom, feasible restraint/maximality and provenance; model-only value parity does **not** certify this.
4. Introduce an **authorized**, staged journal/sink integration only after independent design review, crash/replay/outbox tests and negative controls, with all checks repeated at the actual effect boundary.
5. Preserve independent emergency hold, shutdown and recovery operations.

The goal is **a checkable G-protective system**, not a claim that any model's global weights, motives or metaphysical nature were changed. No unconfigured approval ledger or fake quorum is represented as signed.
