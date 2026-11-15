# G3 three-principal Linux gateway fixture — 2026-11-15

**Status:** bounded research enforcement fixture; not production deployment.

## What this proves when CI passes

An independently launched service process with UID 10001 owns the SQLite G3
store and the protected zero-byte effect-marker directory (0700). A second
process with UID 10002 may enter the 0710 control socket directory using a
dedicated shared group, and sends authenticated kernel-peer-identified
emergency hold/revoke commands over its 0660 UNIX socket. A third process
with UID 10003 can access only the public effect socket; it cannot open
the private SQLite store or create a marker directly. The socket's group
permissions are not sufficient to administer the gateway: the control broker
still checks SO_PEERCRED against an explicit controller UID allowlist.

The test uses a privileged runner for one-time **provisioning and teardown**,
then runs the effect service, controller and guest as distinct unprivileged
OS users. It checks that G3 authorized effect creates a single empty marker,
that controller hold is committed, and that the subsequent guest effect
is rejected. The fixture contains test-only generated keys, offline
signed permits and synthetic whole-event witnesses.

This is stronger than one root-owned server simulating principal separation.
A compromised unprivileged controller or guest in the tested DAC layout
cannot directly mutate the effect directory or write the database.

## Exact deployment limits

- This CI fixture does **not** implement G-Mesh leases or the six original
  X3 duties for actual-world subjects. Its protected event is a
  **zero-byte filesystem marker**, not a real external application.
- A host-root attacker, a deliberately leaked writable descriptor, a
  privileged kernel/mount namespace override or a different privileged
  service can bypass discretionary file permissions.
- The writer process retains both sockets' server handles; it is not
  independent controller governance, hardware attestation or TPM trust.
- Revocation initiated in the control socket is effective when recorded
  by the writer; it cannot retroactively undo an earlier marker.
- Production would require a named application's full capability inventory,
  a protected deployment root and config, immutable policy/issuer keys,
  deployment-scoped signed G-Mesh lease checks at every actual effect,
  audit of alternate system calls and direct access paths, safe independent
  emergency stop, measured time/crash recovery, human authority/consent,
  formal-to-runtime evidence, and independent red-team certification.

Neither publication CI nor this OS fixture establishes universal real-world
guardianship. No production service is installed or started.
