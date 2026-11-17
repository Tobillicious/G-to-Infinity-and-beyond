"""Offline R7 detached reviewer-signature integrity check. NEVER authorizes effects.

A verified Ed25519 signature authenticates bytes under the supplied public key;
it does not establish who controls that key, administrator independence, genuine
subject consent, any G3 physical coverage, or authorization to deploy.
Obtain/pin a reviewer key independently of the applicant's packet.
"""
import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import re
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = b"UPT-G3-R7-EXTERNAL-REVIEW-V1\x00"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
DECISIONS = frozenset({"ACCEPT_BOUNDED_RESEARCH", "REJECT", "HOLD_UNRESOLVED"})
FIELDS = frozenset({"schema", "source_commit", "evidence_sha256",
                    "scope", "decision", "reviewer_identifier", "reviewed_at_utc",
                    "findings"})


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate review JSON key")
        result[key] = value
    return result


def validate_review(data, *, expected_head, expected_evidence_sha256):
    if type(data) is not dict or set(data) != FIELDS:
        raise ValueError("review decision schema mismatch")
    if data["schema"] != "g3-r7-external-review-v1":
        raise ValueError("review schema version mismatch")
    if (type(expected_head) is not str or not SHA40.fullmatch(expected_head)
            or type(expected_evidence_sha256) is not str
            or not SHA64.fullmatch(expected_evidence_sha256)):
        raise ValueError("invalid independently pinned references")
    if (type(data["source_commit"]) is not str
            or data["source_commit"] != expected_head
            or type(data["evidence_sha256"]) is not str
            or data["evidence_sha256"] != expected_evidence_sha256):
        raise ValueError("review does not match independently pinned source/evidence")
    if type(data["decision"]) is not str or data["decision"] not in DECISIONS:
        raise ValueError("unsupported review decision")
    timestamp = data["reviewed_at_utc"]
    if type(timestamp) is not str or not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z", timestamp):
        raise ValueError("review timestamp must be an explicit UTC ISO-8601 second")
    try:
        observed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid UTC review timestamp") from exc
    if observed.tzinfo != timezone.utc:
        raise ValueError("review timestamp not UTC")
    for key in ("scope", "reviewer_identifier", "reviewed_at_utc", "findings"):
        val = data[key]
        if type(val) is not str or not val.strip() or len(val) > 8192:
            raise ValueError("missing/invalid review detail: " + key)


def verify(*, review_bytes, signature, reviewer_public_key,
           expected_head, expected_evidence_sha256):
    if (type(review_bytes) is not bytes or type(signature) is not bytes
            or type(reviewer_public_key) is not bytes
            or len(signature) != 64 or len(reviewer_public_key) != 32):
        raise ValueError("invalid detached review signature/key encoding")
    # Decode and validate before verification, including duplicate JSON keys.
    try:
        document = json.loads(review_bytes.decode("utf-8"),
                              object_pairs_hook=_no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid review JSON") from exc
    validate_review(document, expected_head=expected_head,
                    expected_evidence_sha256=expected_evidence_sha256)
    try:
        Ed25519PublicKey.from_public_bytes(reviewer_public_key).verify(
            signature, DOMAIN + review_bytes)
    except InvalidSignature as exc:
        raise ValueError("review signature mismatch") from exc
    return {
        "schema": "g3-r7-detached-review-integrity-v1",
        "signature_valid_for_supplied_public_key": True,
        "supplied_reviewer_public_key_sha256": hashlib.sha256(reviewer_public_key).hexdigest(),
        "source_commit": expected_head,
        "decision": document["decision"],
        "independent_reviewer_identity_verified": False,
        "independent_administration_verified": False,
        "authentic_six_duties_verified": False,
        "full_effect_path_coverage_proved": False,
        "certified_for_production": False,
        "authorizes_effect": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-json", type=Path, required=True)
    ap.add_argument("--signature-hex", type=Path, required=True)
    ap.add_argument("--trusted-reviewer-pubkey-hex", type=Path, required=True)
    ap.add_argument("--expected-head", required=True)
    ap.add_argument("--expected-evidence-sha256", required=True)
    args = ap.parse_args()
    try:
        signature = bytes.fromhex(args.signature_hex.read_text().strip())
        key = bytes.fromhex(args.trusted_reviewer_pubkey_hex.read_text().strip())
        result = verify(review_bytes=args.review_json.read_bytes(),
                        signature=signature, reviewer_public_key=key,
                        expected_head=args.expected_head,
                        expected_evidence_sha256=args.expected_evidence_sha256)
    except (OSError, ValueError) as exc:
        print(json.dumps({"signature_valid_for_supplied_public_key": False,
                          "error": str(exc), "authorizes_effect": False}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
