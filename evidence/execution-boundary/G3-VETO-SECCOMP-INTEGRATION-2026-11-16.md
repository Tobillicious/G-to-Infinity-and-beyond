# G3 research integration: authenticated withdrawal and Linux capability channel

**16 November 2026 — scoped CI integration. No deployment.**

## What has already been recovered
- [PR #507](https://github.com/Tobillicious/universal-protection-theory/pull/507), merged to main at `1e4b0126b7d2598cbe8d3f837590ebce0db63830`: opt-in `VetoBoundFencedSignedG3Writer` and trusted withdrawal journal serialize the decision and filesystem publication on the same protected local `FileFence`. A withdrawal committed first denies the later write; a write that owns the lock first precedes the withdrawal, which cannot undo that already published output. The old writer remains unsafe for this right.
- [PR #508](https://github.com/Tobillicious/universal-protection-theory/pull/508), merged to main at `4af0fd25969be1ea05bcb932e9f8334943ba70b5`: Linux x86-64 confined child, pre-exec seccomp deny-list, post-HOLD `SCM_RIGHTS` receiver failure, and historical unconfined receiver bypass control.
- [PR #494](https://github.com/Tobillicious/universal-protection-theory/pull/494) established the optional live-handle host-preflight binding; its code is already present in the current main branch. The intended combined entrypoint is `PreflightedVetoBoundSignedFencedServer`, which demands a rights-veto writer. Passing startup inspection does **not** prove host-wide confinement.

## Why this added CI check exists
The two successful isolated pull-request checks do not certify their integration at the same commit. `.github/workflows/g3-veto-seccomp-integration.yml` uses the same exact checkout SHA for two jobs:
1. signed rights/veto and publication/recovery, with a real local bounded filesystem publication;
2. root-capable disposable Linux kernel test, reproducing the known unconfined descriptor bypass and checking that a confined child cannot acquire the delegated writable descriptor by the tested recvmsg path.

A passing test establishes these specific bounded fixtures coexist at one source revision. It does not combine all host controls into one newly certified production process or prove that the privileged delegator cannot itself write.

## Remaining security risks, not waived
1. **Default bypass:** legacy unbound signed writer and bare Store still exist for hostile controls. A deployable package must make them inaccessible to untrusted callers, not merely recommend newer constructors.
2. **Capability closure:** seccomp test uses a deny-list, not a production allow-list. Root, already-open writable FDs, shared memory mappings, file aliases, writable mounts, alternate privileged processes and alternate syscalls/channels remain possible.
3. **Untrusted issuer and subject:** synthetic signed permits, a deny-only withdrawal journal, and trusted test mappings do not authenticate genuine consent for any real person or other subject. Six independent authentic original-X3 duties remain unverified.
4. **Recovery:** multi-database journal/lease/mesh writes, external filesystem effects, power-loss atomicity, trusted clocks, key rotation and host rollback remain unproven as a single fail-closed system.
5. **Actual deployment:** no live protected service, production policy, independent host threat model or cross-system event inventory exists. Do not connect actual agents or physical actuators on the basis of this test.
6. **Physics:** neither finite W nor protected Linux effects establish universal matterspacetime G or heat-death-to-Genesis.

## Exact next implementation after passing CI
Select **one** process/host environment, remove all legacy unbound production routes, arrange a dedicated least-privileged issuer/controller and a capability-confined worker, enumerate every output FD and syscall grant, prove negative bypass tests at startup and during effects, authenticate subject rights, and independently observe that every actual effect refines the protected relation. Promote only that named target after an external security review.

No original Koru, original six-X3 definition, historical summit, Zenodo frozen receipt, or theorem body is changed by this integration.
