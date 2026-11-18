# G3 R7 — independently inspectable cross-UID evidence index (research only)

**Candidate source:** `Tobillicious/universal-protection-theory`, PR [#646](https://github.com/Tobillicious/universal-protection-theory/pull/646), exact Git HEAD `cc0434d225fb71902d248d5e87ac7e4956d18b84`.

**Status:** A recorded technical replay, **not** a release certificate, independently administered custody proof, all-real-effect theorem discharge, or authenticated external review. This document indexes immutable observations from one GitHub Actions head. The GitHub CI administrator and reporter are not an independent custodian.

## Full cross-UID signed-HOLD replay

- Workflow: [G3 cross-UID signed HOLD research, run 44076412754](https://github.com/Tobillicious/universal-protection-theory/actions/runs/44076412754), job `134015462224`; result **success** on the exact head above.
- Existing disposable Linux signed-HOLD suite: **903 tests, OK** (278.946 s), as recorded in the job log.
- Observed-syscall probe suite: **2 tests, OK** (0.603 s), separately recorded in the same job log.
- All workflow steps, including syscall trace and both evidence uploads, concluded successfully. This is not a second independently administered machine.

### Retained evidence with recomputed digests

| Artifact | Artifact ID | GitHub ZIP SHA-256 | Extracted file / SHA-256 |
| --- | --- | --- | --- |
| G3 runtime inventory | `14325621732` | `ecb4cd303ad450feff08a3e30422fb8f630030c4a29c35de0e779430ef953f53` | `g3-runtime-evidence.json` / `c6cd18154d5f3efb11ec597f0857fc3b3dcb57383a492af68806cacffc12af55` |
| Observed R5 syscalls | `14325581774` | `b42b726d5d84a2a1bf03c0f11288326bf29753140af18f38ec2629018a393287` | `g3-r5-syscall-inventory.json` / `ed78cee8103b3ff1295feb6095116995f0ebd67de900aef2bf1a5e3de9b5904c` |
| Integrated R4–R6 / R7 bounded replay | `14325805646` | `99ae1ff6983373e68b94cc12ae0d2d69f184d7c23c5dc42549f252492500c674` | `g3-r7-scoped-replay.json` / `51b7d4f7e642cdbee7734de477b145ecdedeebd79fa4695d03c989323222c11f` |

**Artifact inspection:** The runtime JSON names `checkout_sha=cc0434d225fb71902d248d5e87ac7e4956d18b84`, CPython 3.13.18, cryptography 46.0.4, Linux x86-64 kernel `7.0.0-1014-aws`, interpreter/native-extension fingerprints, and source SHA-256 hashes. It explicitly states this is an observed CI process environment, **not** loaded-object attestation.

The observed-syscall JSON reports schema `g3-r5-observed-syscalls-v4`. It contains **three traced children**: one `synthetic_effect_returned` and two `authority_denied`; each had one tracked pre-filter authority connection and **zero post-filter socket creation attempts** in the recorded normal-request traces. This is distinct from the dedicated R5 v3 adversarial `EPERM` artifact on the same head. Absence of observed attempts in three selected normal traces is **not** a proof that all possible effect paths are closed.

The combined R7 receipt reports **144 unique passing test executions**, no duplicate identities, exact checkout/source match, the bounded alternative-channel regressions and the existing forest six-duty gap checks. All **nine** workflows triggered on the exact Git commit concluded success.

## R7 acceptance crosswalk: keep each premise separate

| Gate | What is actually demonstrated | Required evidence still absent |
| --- | --- | --- |
| R4 operator custody | Same-host simulated rollback vs retained operator floor; fail-closed recovery and challenge tests | A separately administered off-host operator, independently witnessed rollback survival, access and key-custody review |
| R5 effect-path coverage | Strict kernel probes, residual IPC / descriptor / process creation / socket controls, cross-UID hostile suites, observed bounded authority requests | An independently fixed and **complete** inventory of in-scope effect routes, with exhaustive adversarial mediation review for the specified real deployment |
| R6 original six | Existing mathematical interfaces and fail-closed forest checker for missing owed subjects and each duty; same-admin separate-process marker observations | Authentic identity/rights and consent evidence for **every** genuinely owed subject, their actual events, six duties and faithful `realStep/read` mapping |
| R7 acceptance | Exact-head reproducible CI plus preserved artifact digests and review protocol | An externally administered independent replay and a real reviewer-signed, scope-specific decision |

No person or organization is falsely entered as an external reviewer. No synthetic subject Boolean is treated as a verified authentic reflection. **R7 production decision remains HOLD unresolved; this document authorizes no effect.**

### Independent reviewer handoff

Reproduce the identified source SHA, validate archive hashes and run logs, inspect source and binary/environment fingerprints, independently verify every application effect route and real owed subject, then test separately administered operator rollback and HOLD fail-closed behavior. Preserve the reviewer identity, independence constraints, time, platform, exact evidence digests, adverse findings and signed accept/reject/HOLD decision outside the applicant's administrative authority.

Never infer general physical protection or unconditional G3 from this finite synthetic Linux acceptance packet.
