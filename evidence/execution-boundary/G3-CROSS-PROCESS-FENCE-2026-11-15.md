# G3 cross-process effect/control fencing — 15 November 2026

Status: **research pilot; not a production security guarantee**.

## Motivation

The existing protected filesystem marker holds a Python `RLock` across
synthetic effect authorization, recovery audit and the filesystem write.
That protects threads in one interpreter but **not a separate controller
process** sharing the same SQLite store. Another process could update the
hold or revocation row during the filesystem operation, after the gate's
initial database transaction had already committed.

## New optional protection

- `koru_process_lock.py`: `InterprocessRLock` wraps a `flock(LOCK_EX)`
  advisory lock in a thread-reentrant Python lock. The lock file must be
  a private regular inode in a private trusted directory owned by the process
  UID. Symlinks, world/group writable directories and alternate-owner
  lock files fail closed. Forked processes cannot use an inherited lock;
  they must initialize a fresh gate and file handle.
- `PilotGate(..., cross_process_lock_path=...)` opts into this lock.
  It is held by `_transaction` and, via the existing shared gate lock,
  by `ProtectedFilesystemSink.apply_marker` from recovery inventory through
  the physical marker write and durability flush.
- All cooperating management, writer and reconciliation processes must use
  the **same trusted lock path**, have no alternate direct effect capabilities,
  and reopen separate SQLite connections after fork.
- Existing no-lock research fixtures remain unchanged for compatibility;
  this opt-in feature alone is not complete process isolation.

## Deterministic negative controls

`test_koru_process_lock.py` starts an **independent interpreter** and
opens its own SQLite gate while the writer holds the common effect lock.
Attempts to durably hold or revoke authority block until the effect lock
is released; after controller commit, the previous permit cannot write the
marker. Tests exercise nested locking, unsafe directory modes, and symlink
lock paths.

**Linearization meaning:** if a hold/revocation acquires the common lock first,
it is observed by the subsequent effect-time check; if a write owns the
lock first, the controller's hold cannot commit in its middle. This order
is only guaranteed for processes faithfully using the same protected inode.

## Remaining gaps

The lock is **advisory**, not a kernel-enforced ban on arbitrary privileged
filesystem writes. A process with direct write permission to the sink, a
different lock inode, root-level control, or an open writable handle can
bypass cooperation. SQLite state and filesystem markers remain separate
durability domains. Crash/kill while holding `flock` releases the process
lock, but it does not magically undo a partial external write. Real-world
source authority, original six X3 duties and comprehensive effects coverage
must be independently verified.

Next step: move the filesystem effect capability into a minimal dedicated
OS principal, ensure the controller cannot mutate effects except through
the protected gateway, and require an external security audit before any
production deployment. No live permissions, keys or system effects are
introduced by this branch.
