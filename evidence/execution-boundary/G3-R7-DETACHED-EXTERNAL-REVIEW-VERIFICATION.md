# G3 R7 external signature verification — non-authorizing handoff

This tool **checks signed bytes**, not whether the signer is an independent reviewer. A true review requires a person or institution outside the application's administrative authority to examine the evidence and attest to scope, identity, administrative separation and findings. No synthetic CI key or signature counts as that review.

## Source and evidence binding

Use the existing exact-head R7 research replay and cross-UID evidence register. The reviewer must obtain the Git head and the expected evidence SHA-256 through an independently controlled channel (not from a mutable field inside the review file). Obtain the reviewer's **Ed25519 public key** through a separately authenticated channel. Keep private keys away from the Git repository and CI.

The detached review JSON contains exactly these keys:

```json
{
  "schema": "g3-r7-external-review-v1",
  "source_commit": "<40 lowercase hex characters>",
  "evidence_sha256": "<64 lowercase hex characters>",
  "scope": "<precise bounded deployment/research scope>",
  "decision": "HOLD_UNRESOLVED",
  "reviewer_identifier": "<externally verified reviewer identifier>",
  "reviewed_at_utc": "<timestamp recorded by the reviewer>",
  "findings": "<specific favorable, adverse and unresolved findings>"
}
```

Allowed decisions are `ACCEPT_BOUNDED_RESEARCH`, `REJECT`, and `HOLD_UNRESOLVED`. There is **no production or universal-G3 ACCEPT decision** in this schema. The detached 64-byte Ed25519 signature signs the raw UTF-8 JSON bytes prefixed by `UPT-G3-R7-EXTERNAL-REVIEW-V1\0`; the verifier performs no JSON canonicalization. Reviewers must sign the exact bytes they publish. Never commit a private key, impersonate an external reviewer, or generate a test signature with a real reviewer's identifier.

Offline verifier invocation, using a separately provisioned public key file:

```sh
cd evidence/execution-boundary
python3 -B g3_r7_external_review_signature.py \
  --review-json REVIEW.json \
  --signature-hex REVIEW.sig.hex \
  --trusted-reviewer-pubkey-hex TRUSTED_REVIEWER_PUBKEY.hex \
  --expected-head EXPECTED_40_CHAR_GIT_SHA \
  --expected-evidence-sha256 EXPECTED_64_CHAR_EVIDENCE_SHA256
```

This checks the cryptographic integrity of one independently pinned review/evidence pair. A successful verification outputs `signature_valid_for_supplied_public_key=true` and *always* `independent_reviewer_identity_verified=false`, `independent_administration_verified=false`, `authentic_six_duties_verified=false`, `full_effect_path_coverage_proved=false`, `certified_for_production=false`, and `authorizes_effect=false`. Those remaining findings require separate actual evidence, not a software assertion.

The CI unit tests use **fresh synthetic ephemeral keys** and do not create review decisions or roster entries. A missing review, unknown key, invalid signature, mismatched source/evidence or unauthenticated real-world reviewer means **R7 external acceptance remains unresolved**. This tool does not modify HOLD or grant any effects.
