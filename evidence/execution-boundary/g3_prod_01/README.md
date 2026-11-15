# G3-PROD-01 — bounded local writer / generation-fenced recovery prototype

**Status: locally tested research-only engineering prototype. NOT production ready. NOT G3-integrated.**

This Linux Unix-socket reference-monitor experiment uses a local SQLite authority/effect-intent journal and a fixed private output directory. It is an **additive candidate** for review alongside the existing G3 architecture, **not** a replacement for PR #456's signed G3/G-Mesh checks.

## Run tests

```sh
cd evidence/execution-boundary/g3_prod_01
python3 -m unittest -v
```

Requires Linux, Python 3.9+, and private writable test directories. The original isolated harness passed eight local unit tests on 15 November 2026. The branch now has eleven tests and a dedicated GitHub Actions workflow; rely on exact-head CI for their results.

## Demonstrated in the limited test harness

- Startup increments authority epoch and disarms effects.
- Stale epochs and held state deny writes; local epoch and effect intentions use the same SQLite database (WAL, synchronous FULL).
- Only bounded content may be written, to hash-derived names in an independently configured private output directory. The request does not select arbitrary paths.
- Socket requests are one-per-connection, byte-bounded, checked against Linux SO_PEERCRED UIDs, and concurrency-limited.
- Unresolved previously journaled intentions block unrelated writes; existing output contents and type are verified.
- Output bytes are fully written and fsynced to a private staging inode before a no-overwrite hard-link publication. Orphan staging files are detected as integrity failures requiring trusted review.

## Release blockers: do not deploy

1. **Missing real G3 authorization**: No Ed25519 G3 permit, signed fresh G-Mesh lease, six original X3 duties, authentic consent, or policy correspondence is checked by Store.write. An allowed UID knowing the current epoch can issue writes. Epoch is NOT a cryptographic capability.
2. **Disarmed demonstration startup**: Store.arm is trusted in-process/test only. The CLI remains disarmed; never expose arm/revoke on the untrusted application socket.
3. **No measured multi-UID isolation**: The tests emulate UID rejection but do not provision distinct system accounts, mount namespaces, MAC/seccomp, inherited-FD hygiene, or non-bypass guarantees. Host root or kernel can bypass.
4. **Crash consistency gaps**: clean close/reopen is tested; SIGKILL, power loss, fsync boundaries, filesystem faults and atomic publication are not yet tested. Staging and publication crash points still require fault injection; orphan staging files fail closed.
5. **Physical-domain gap**: No hazard analysis, real consent, actual-world six-X3 grounding, hardware interlocks, actuators, distributed consensus, or universally protective result.
6. **Rollback and resource gaps**: Local SQLite is not anchored against privileged rollback; the socket directory must be securely provisioned. Additional process/resource exhaustion and race testing is required.
7. **Broker/protocol constraints**: This reference monitor does not expose original PR #456 signed envelope interface. Do not connect an untrusted agent or external service to this prototype as if it were G3.

## Next exact engineering integration

1. Retain [PR #456](https://github.com/Tobillicious/universal-protection-theory/pull/456) as the authoritative current G3/G-Mesh cryptographic admission and model evidence path.
2. Define one bounded target application and enumerate all effects, identities, OS permissions and policy rights; deny direct protected output writes using **actual OS isolation**, not merely application wrappers.
3. Specify and implement a **trusted commit-time authorization interface**: exact signed event and permit; fresh G-Mesh lease, generation and revocation; appropriate original six-X3 evidence; and an actual rights/consent source. Do not substitute an integer epoch for these checks.
4. Reconcile separate G3 and G-Mesh SQLite stores, or specify a verified authority decision with an enforceable commit fence, avoiding time-of-check/time-of-use escapes.
5. Make output publication atomic when possible, with durable staging, fsync, rename and exact fault injection at each step. Guarantee fail-closed behavior on integrity uncertainty, and verify recovery by observation.
6. Exercise separate UIDs, namespaces, fd inheritance, symlink/hard-link, lock contention, hostile slow clients, exhausted resources, restart and revocation races. Independently review the resulting evidence.

This addition is intentionally separate from Lean and the historical UPT proofs. No theorem, publication, DOI, or original proof chain is changed or weakened.
