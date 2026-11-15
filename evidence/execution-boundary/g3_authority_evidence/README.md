# Signed operator-permission *record* verifier (research only)

**NOT an authorization service, consent oracle, production gate, or original-six X3 certificate.**

This standalone component verifies that an Ed25519-signed record, under a **separately pinned issuer key**, matches the *exact* subject, action, effect-content digest, scope and purpose. It checks a bounded validity interval, trusted clock, externally supplied current revocation generation and explicitly revoked serials. It rejects malformed schemas, signatures from untrusted issuers and mismatches.

**Crucial distinction:** a correct signature only proves possession of a signing key for the encoded claim. It does not prove that the human subject genuinely consented, that the key owner has legal/moral authority, or that any original-six X3 obligation holds in the physical world.

The API only returns `signature_valid_for_record`. The output fields `authorizes_effect`, `authentic_consent_proved` and `original_six_x3_proved` are **always false**, including when the signature is valid. This module must never be wired into an effect writer as an automatic allow decision.

## Inputs and trust boundary

- `packet`: untrusted signed record (all exact fields are checked and encoded as canonical JSON).
- `public_keys`: issuer-name to pinned Ed25519 public key, secured independently of the request.
- `revoked_serials`, `minimum_generation`, `now`: independently maintained live trusted state. Passing user-controlled values here breaks the security model.
- `subject`, `action`, `effect_digest`, `scope`, `purpose`: trusted application context, not merely duplicated from the claim.

The verifier is deliberately stateless, does not record consumption, does not ensure single use, and does not synchronize with the writer's commit fence. A signed record is **not** a substitute for G3/G-Mesh permits, OS mediation, or commit-time revocation checks.

An actual consent/rights authority still requires subject identity verification, proof of capacity and voluntariness where applicable, representation/delegation rules, revocation publication, protection for nonconsenting or dependent subjects, provenance and independent six-X3 validation.

## Offline tests

```bash
cd evidence/execution-boundary/g3_authority_evidence
python3 -B -m unittest -v test_authority_evidence.py
```

This is a separate, additive research lane from the merged G3-PROD-01 signed writer. Never deploy or connect it to a live actuator.
