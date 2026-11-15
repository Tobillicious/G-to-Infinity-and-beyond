# G3 subject-specific rights review — non-authorizing research

A separate deny-first *evidence triage* prototype. It does **not** determine genuine consent, confer authority, authorize an effect, or establish original-six X3 correspondence in reality.

The caller supplies only a record reference. A separate, trusted source must supply a complete record for the specific subject, action, scope, purpose, exact output digest, authorization/delegation status, decision, generation and validity window. Without that source, evidence cannot be evaluated. Records marked denied, withdrawn or revoked always fail; an independently controlled emergency hold always takes priority.

The model rejects identity, capacity, voluntariness, or delegation facts recorded as missing. A representative claim must contain an independently verified delegation signal. These values are *assertions supplied by the trusted test fixture*, **not** independent proof of rights, consent or human competence. The adapter does not collect personal data or make assessments of people's competence.

All responses include `authorizes_effect: false`, `authentic_consent_proved: false`, and `original_six_x3_proved: false` regardless of a matching record. `review_complete` means only that the supplied record satisfies this limited schema and consistency check.

No write, socket, signing, or other actuator capability is exposed. Do not integrate this adapter as an allow gate without a real trusted rights authority, authenticated revocation, decision audit, subject protection analysis, and independent security review. Do not trust a caller-provided record table or accept stale revocation snapshots.

Run:
```sh
cd evidence/execution-boundary/g3_rights_review
python3 -B -m unittest -v test_rights_review.py
```

This is a parallel research component designed not to interfere with the merged signed G3 writer or PR #472's signed-record provenance checker.
