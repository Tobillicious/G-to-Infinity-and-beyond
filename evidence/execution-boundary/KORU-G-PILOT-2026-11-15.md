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

**Verification receipt:** The files were source-reviewed during authoring but **the tests have not been executed in this session** (the runner could not fetch the connected repo into its execution environment). Do not report PASS before a pinned checkout runs the commands.

## Why this is not yet the enforcement release

The pilot is **synthetic and append-only**. It is not a proof verifier, independent human consent authenticator, cultural authority, cryptographic signing service, external-world effect router, or general implementation of the original six X3 duties. Its `ShadowVerifier` understands a toy six-position integer world and one `synthetic_refinement` kind. The code does not mutate actual world state or send externally effective actions.

The supplied `contexts`, `witnesses`, `authorities`, `signatures`, and `provenances` are **trusted-controller injected registries**; they are **not** accepted from the untrusted event itself. In this local pilot, **all trusted registry changes must serialize on the gate lock**. There is **no remote caller authentication** on `hold`/`release`; those Python methods are trusted-controller-only in-process interfaces. Do not expose them as untrusted network endpoints. There is no cross-process coordination for those memory-resident registries.

A SQLite commit with `synchronous=FULL` provides an isolated local durability experiment, not a proof that any filesystem, hardware controller or external service is atomic and crash safe in all conditions. The context is immutable during this pilot; real versioned world transitions and authorized metadata updates require a separately designed controller.

## Next release gates (not silently assumed)

1. Run baseline `harness.py` and both unit suites on a supported machine, record exact source SHA and runtime settings; ensure old trusted runtime stays unmodified.
2. Add an independently authenticated controller for authority issuance/revocation, privacy deletion, evidence and context updates; test revocation races and corrupted database recovery.
3. Build a genuine original-six-X3 event witness with independently validated subject, history, consent, freedom, feasible restraint/maximality and provenance; model-only value parity does **not** certify this.
4. Introduce an **authorized**, staged journal/sink integration only after independent design review, crash/replay/outbox tests and negative controls, with all checks repeated at the actual effect boundary.
5. Preserve independent emergency hold, shutdown and recovery operations.

The goal is **a checkable G-protective system**, not a claim that any model's global weights, motives or metaphysical nature were changed. No unconfigured approval ledger or fake quorum is represented as signed.
