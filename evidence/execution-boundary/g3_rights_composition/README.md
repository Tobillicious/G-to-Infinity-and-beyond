# G3 exact same-event signed claim and rights evidence composition (research)

This adapter joins two **already merged** research modules: `g3_authority_evidence` (PR #472) and `g3_rights_review` (PR #473), using one trusted request context. It does not modify those modules or the production writer.

## What the join adds

The Ed25519-signed claim's exact `serial` must equal the rights record reference from the separately trusted source. Both checks receive the same **trusted** subject, action, effect digest, scope, purpose, clock and revocation generation. A signature valid for some other rights reference, even for similar content, is not a valid join. Denial, withdrawal, hold, revoked serial, expiry, stale generation, missing identity-review, or unverified delegation cause rejection.

On a matching record the result is `signed_and_rights_records_match_for_review_only`, which means **only** that two separately provided pieces of evidence pass their own limited consistency checks. The output **always** says `authorizes_effect: false`, `authentic_consent_proved: false`, and `original_six_x3_proved: false`.

## Explicitly unresolved

The authority roster, trusted rights records, trusted clock, generation and revoked serials must be separately authenticated and current; an untrusted application cannot supply them. Nothing here determines whether a claimed signer actually possesses rights over the subject, authentic human consent, privacy or legal duties, or complete original-six X3 correspondence. There is no cross-process atomicity with the actual writer, authenticated external checkpoint custody, distributed revocation, or effect-time synchronization.

This module is a **non-enforcing integration test**, not an effect permit, deployment readiness statement or universal physical G3 certification.

Run:
```sh
cd evidence/execution-boundary
python3 -B -m unittest -v g3_rights_composition.test_same_event
```
