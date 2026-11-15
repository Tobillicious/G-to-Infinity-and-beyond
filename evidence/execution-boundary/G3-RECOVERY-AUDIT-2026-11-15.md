# G3 protected filesystem crash/recovery reconciliation — 15 November 2026

**Scope:** follow-up to merged PR #447; protected **zero-byte test marker** only. Neither broad real-world effect control nor universal physical protection has been established.

## Problem
The signed SQLite effect journal and the actual filesystem marker do not share one atomic commit. A failure may occur after the journal says `synthetic_effect_recorded` but before creation or fsync of a marker. An unsafe recovery procedure could duplicate, invent, or execute a revoked effect.

## Added
- `ProtectedFilesystemSink.reconcile_report()`: read-only inventory under the gate lock; verifies the existing SQLite journal and compares authenticated-in-the-pilot event identities with marker filenames. Records pending journal effects missing markers, flags unexpected files and invalid marker content/links. It **never** replays an event, creates a file or overrides authority.
- The `apply_marker()` idempotent existing-marker path now opens through the protected directory descriptor with `O_NOFOLLOW` and fsyncs both existing marker and directory before acknowledging an already-present marker. This helps cover the crash window between exclusive create and durability flush. It remains a local-fs durability experiment, not cross-resource atomicity.
- Negative controls: report missing effect without replay; revocation stops a later recovery attempt; valid retry completes once; detect orphan/corrupt/symlink markers; open/restart without automatic effect.

## Security/interpretation
- The recovery inventory is intended only for trusted offline controllers, **not** the public socket. It includes event IDs; do not log them publicly without a privacy/retention review.
- A privileged attacker with direct database/filesystem access can forge coherent artifacts. The plain receipt digests are not externally signed attestations.
- The private directory and OS access policies are prerequisites. The demo runs as root in CI only; a production service should use a least-privilege dedicated principal and independent controller.
- In a pending state, remediation requires a **new effect-time signed permit, current non-revoked authority, valid source witness and cleared hold/generation**, via the existing `apply_marker` path. A pending item MUST NOT be automatically replayed on startup.
- A separate external effect or arbitrary filesystem write is **not** implemented. No production deployment in this change.

## Verification
GitHub Actions `.github/workflows/koru-shadow.yml` runs the updated filesystem suite; Lean physical bridges and full-law/publication checks run independently. Only report success after recording the final PR head SHA and successful jobs.

## Mandatory effect-time integrity precondition

`ProtectedFilesystemSink.apply_marker` now takes the gate lock and invokes
`reconcile_report()` **before** appending its own synthetic effect or writing
a marker. Unexpected filesystem entries, malformed or symlinked existing
markers, or an inconsistent journal must fail closed. If any *different*
journaled event is still missing its real marker, subsequent effect requests
fail with `unresolved_prior_effect` until that earlier event has been
individually reauthorized and recovered. No automatic replay is performed.

This prevents a local gate operator from observing an integrity violation
in the read-only audit yet continuing to create fresh markers through the
normal sink. It is deliberately conservative; a revoked pending event may
block subsequent writes until trusted review, rather than silently skipping
the missing side effect. Manual recovery cannot waive current permit and
revocation rules.

**Residual boundary:** this is serialized by the trusted Python process and
OS-private effect directory, not a system-wide transaction against privileged
modification. Root or another privileged holder of the directory may modify
its contents between verification and creation; such access must be eliminated
or constrained independently for a real target. The SQLite-to-filesystem
crash atomicity gap remains. These are marker-only tests, not proof of
universal actual-world protection.
