# G3-PROD-01 certification evidence ledger — bounded offline HTML pilot

**Status: NOT CERTIFIED.** This document is an acceptance ledger, not a self-issued safety certificate, a universal physical theorem, or an AI model endorsement.

**Scope:** offline conversion of *synthetic, non-sensitive* Markdown curriculum fixtures into allowlisted HTML artifacts on one controlled Linux host. Trust assumes an uncompromised Linux kernel, root/operator, filesystem, writer and pinned public-key policy configuration. Remote hosts, Internet-facing gateways, real learners' records, actuators, and universal protection are excluded from this pilot.

## Exact acceptance statements

1. **Proven/tested locally:** the merged research fixture has a signed G3/G-Mesh path to bounded effects; a separate-UID denial test; restart lease invalidation; a bounded protocol reader; reproducible process-death and injected-fsync negative controls. These statements depend on each test's pinned source SHA and environment.
2. **New test in this PR:** race a fully signed publication with an independent process executing a local writer hold. The held file lock must serialize publication and revocation, and the post-revocation request must fail. This is a *cooperating local-process* ordering property, not remote consistency.
3. **Not proved:** complete physical-world protection, original-six X3 authenticity for actual persons, secure time, cross-machine revocation, host-root compromise resistance, physical power loss, supply-chain integrity, or exhaustive syscall mediation.

## Mandatory release evidence gates

| Gate | Required evidence | Current status |
| --- | --- | --- |
| G3 exact event and permit | Invalid/expired/forged permit denial and valid exact request on actual writer IPC | Research CI coverage, not deployment certificate |
| Fresh G-Mesh lease | Restart, partition expiry, replay and wrong-event denial at the effect boundary | Research CI coverage |
| Same-host write/hold ordering | Separate OS process revokes while signed writer is publishing; verify serialized order and later denial | This PR test pending exact-head CI |
| OS complete mediation | Compile under unprivileged UID; enumerate every writable FD, mount, filesystem, network and IPC route; adversarial bypass attempts | Partial distinct-UID tests only |
| Durable publication | Kill at each prepare/stage/link/fsync/complete boundary; test disk full, storage corruption and actual power cut on target host | Partial simulated failures and process kill only |
| Cryptographic state freshness | Provisioned authority keys, trusted clock, rollback-resistant state, key rotation and emergency control | Not met |
| Revocation across hosts | Define decision linearization and test partitions, stale leaders, competing writers and delayed authority messages | Not met |
| Independent review | External reviewer reproduces tests, audits code/trust boundary, records platform and threat exclusions | Not met |
| Original six-X3 evidence | Source-to-subject mapping and hostile counterexamples for every owed particular in the selected actual use | Not met |

## Original-six evidence correspondence for the *candidate application*

For each directly or indirectly affected author, educator, learner, institution, and other rights-holder, an independent review must document:

- **Historical continuity:** source and artifact revisions and their exact antecedents; verify no silent history erasure.
- **Authentic authorization:** independently verified authority to process and publish each source, including copyrighted or personal material when applicable; a signature alone is not consent.
- **Freedom:** enforce ability to decline or withdraw where the applicable rights require it, without coercive side effects.
- **Least-necessary restraint:** restrict operations to exact allowed transformations, destinations, and time periods; test excess privilege denial.
- **Feasible maximality:** evaluate attainable protective alternatives and explicit tradeoffs under resource constraints; test why a less protective action was unavoidable when claimed.
- **Provenance:** reconstruct inputs, content digests, authorized source, transformation version, output and reliable audit lineage.

No real parties are used in the synthetic pilot, so no pilot test can establish actual-world universal original-six coverage. The research target remains unchanged.

## Certification decision protocol

- **Research integration pass:** exact-head CI, source pin, negative control suite and reproducible logs.
- **Bounded pilot ready:** research pass + configured separate-principal host + independent threat-model review + all required local effect/rights tests + measured crash and storage assumptions.
- **Production certificate:** bounded pilot-ready evidence, external security review, signed release manifest identifying *precisely* what host, build, policy, principals, rights records and effects are covered.
- **Universal physical G3:** not derivable merely from any finite pilot; needs independent general arguments and real-world correspondence across its full claimed domain.

Never populate an external quorum ledger or claim reviewer signatures without genuine signed entries. Do not conflate a green pipeline with a deployment or consent certificate.
