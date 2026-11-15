# G3 effect-time withdrawal fence — bounded repair candidate (16 November 2026)

**Review branch. No production deployment, universal X3 certificate, or physical/ethical proof change.**

## The negative control being repaired

Draft [PR #505](https://github.com/Tobillicious/universal-protection-theory/pull/505) showed that the existing `FencedSignedG3Writer` would publish a synthetic HTML artifact **after** the separately trusted rights journal had durably recorded a withdrawal. The signed G3 permit and current G-Mesh lease were correct, but the writer did not consult subject-specific withdrawal state.

This branch adds **opt-in**, source-integrated enforcement through `VetoBoundFencedSignedG3Writer` and corresponding protected IPC constructors. The legacy research-only signed writer deliberately remains available for negative controls and does **not** acquire new rights guarantees merely because this branch passes.

## Local invariant being tested

Let `W` be an effect publication and `R` be a durable trusted withdrawal for the same mapped event and subject.

Under the bounded assumptions below, if `R` commits before `W` takes the shared publication fence, `W` is refused with `rights_veto_or_unavailable` and no artifact is published. If `W` already owns the fence, `R` waits until `W` finishes and takes effect for later attempts. This is a **local serialization order**, not retroactive revocation of previously published information.

- The trusted controller records withdrawal only through `RightsVetoJournal.record_withdrawal`, on a journal explicitly provisioned with the **same private `FileFence` inode** as the writer.
- The actual signed writer holds that lock through the rights check, original signed G3+G-Mesh checks, staging and final link/commit. The journal checks its own generation sequence; the writer pins the provisioned journal path/inode and refuses missing/swapped/corrupt evidence.
- The exact event-to-subject **and event-to-authority-reference** mappings and effect manifest come from trusted fixture configuration. A request attempting to substitute the authority reference is rejected before any dispatch. Neither these mappings nor a consent flag, journal path or authority record can be supplied by an untrusted application.
- `VetoBoundSignedFencedServer` and `PreflightedVetoBoundSignedFencedServer` require the new writer type rather than silently falling back to a legacy unbound one.
- The record is deny-only. Its `authorizes_effect`, `authentic_consent_proved`, and `original_six_x3_proved` flags stay **false**, including when there is *no withdrawal*.

The inherited signed permit still conditionally authorizes **only its synthetic fixture event**. No-veto is never promoted to actual human consent or original-six protection.

## Replay / adversarial tests

```sh
cd evidence/execution-boundary
python3 -B -m unittest -v \
  g3_rights_composition.test_three_way \
  g3_rights_composition.test_effect_time_rights
```

The new tests require: a preexisting withdrawal blocks actual signed publication and leaves the output directory empty; journal disappearance or path replacement denies; unbound or different-inode fences fail provisioning; a forced race at `os.link` serializes against withdrawal; a later withdrawal blocks subsequent publications but does not erase an already committed output; protected IPC constructors reject legacy writer instances. The GitHub workflow `g3-three-way-triage.yml` now runs both suites and is triggered by rights or writer changes.

**Check exact-head workflow results before accepting this candidate.** A green status proves only the exercised source/test configuration, not real-subject consent or whole-host protection.

## Open release obligations; do not call this unconditional G3

1. **Authentic rights and all six X3:** separately authenticate who can authorize/withdraw on behalf of every truly owed particular; enforce all original-six protections across the exact act. The current one-subject synthetic map is intentionally narrow.
2. **Trusted withdrawal source:** constrain all mutation paths to the journal API and protect the shared private fence, DB file and controller credentials from hostile principals, symbolic links, mount substitution, root/host compromise and stale evidence.
3. **Complete mediation:** the [PR #475](https://github.com/Tobillicious/universal-protection-theory/pull/475) already demonstrates a transferred writable file-descriptor bypass after HOLD. This branch **does not fix that**. Require independent OS confinement, exclusive writer capabilities, prohibition of SCM_RIGHTS/pass_fds delegation, and negative controls under a separate untrusted UID.
4. **Actual-world semantics:** check physical event identity, effect channels, delay/residuals, subjective continuity and genuinely feasible protection, with external evidence. Neither the rights journal nor a fixture can certify those bridges.

Nothing in this change modifies Koru, the existing mathematical Guardian results, the original X3 definitions or the canonical manuscripts. Keep this patch unmerged until exact-head tests and independent review pass.
