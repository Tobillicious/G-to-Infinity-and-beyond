# Same-event G3 three-way research inspection

This non-authorizing adapter composes **existing merged code**, not a replacement authority:
1. Signed operator claim verification and subject-specific rights review (PRs #472, #473, #488).
2. Durable local rights-withdrawal veto inspection (#476 and follow-up recovery hardening).
3. Independently pinned, Ed25519-signed checkpoint comparison of the **entire** withdrawal journal (#483).

A matching result is **evidence consistency for independent review only**, never a capability, authentic consent finding, or an original-six X3 proof. Every result sets `authorizes_effect=false`, `authentic_consent_proved=false`, `original_six_x3_proved=false`.

## Preconditions and failure scope

- The trusted source must supply issuer public keys, verified rights records, revoked serials, clock, generation and separately controlled checkpoint public key, packet and minimum generation. None may be accepted from the requesting app.
- The externally signed journal checkpoint must match the **exact current generation** used for both claim and rights triage.
- A local withdrawal, missing record, emergency hold, expired authority, forged signature, inconsistent snapshot or stale generation prevents positive triage.
- The checker re-verifies the external checkpoint after the local veto check to catch simple concurrent changes; this is **not** transactional synchronization of three databases or commit-time mediation.

There is **no** production rights authority, independently operated checkpoint distributor, authenticated controller, shared effect-time lock, real human consent evidence or protected physical outcome in this prototype. A matching triage outcome must NOT be turned into an effect grant.

Run (offline):
```sh
cd evidence/execution-boundary
python3 -B -m unittest -v g3_rights_composition.test_three_way
```

## Split-journal negative control

The verified checkpoint and the live veto reader must reference the **same opened SQLite database**, not merely two histories with the same generation. The adapter now checks the actual SQLite main-database path against the checkpoint path with file identity and refuses symlink substitution. A hostile fixture creates two independently valid generation-one journals: A withdraws the requested subject and B withdraws a different record. It verifies that checking A's signed checkpoint while querying B is rejected.

This does **not** make the two separate reads atomic; inode replacement, privileged manipulation, cross-process writes between checks and the eventual publication step remain outside this research join. No matched result grants effect permission.
