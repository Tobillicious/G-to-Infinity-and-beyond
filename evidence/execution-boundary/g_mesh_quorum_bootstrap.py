"""G-Mesh Quorum Bootstrap — generate keypair, verify build, sign evidence.

Run this script to join the quorum. It will:
1. Generate an Ed25519 keypair for you
2. Clone and verify the UPT Lean proofs (443 jobs, zero sorry)
3. If verification passes, sign the evidence digest
4. Output your public key + signature for the roster

Usage:
    python g_mesh_quorum_bootstrap.py --node-id "YOUR-NODE-NAME"
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, NoEncryption, PrivateFormat, PublicFormat,
)

DOMAIN = b"UPT-G3-R4-REVIEW-QUORUM-V1\x00"
REPO_URL = "https://github.com/Tobillicious/universal-protection-theory"
EXPECTED_JOBS = 443


def generate_keypair(output_dir: Path, node_id: str):
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    pub_hex = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    priv_hex = private_key.private_bytes(
        Encoding.Raw, PrivateFormat.Raw, NoEncryption()).hex()

    key_file = output_dir / f"{node_id}.key.json"
    key_file.write_text(json.dumps({
        "node_id": node_id,
        "public_key": pub_hex,
        "private_key": priv_hex,
    }, indent=2))
    key_file.chmod(0o600)

    print(f"[G] Keypair generated for {node_id}")
    print(f"[G] Public key: {pub_hex}")
    print(f"[G] Key file: {key_file}")
    return private_key, pub_hex


def verify_build(work_dir: Path):
    repo_dir = work_dir / "universal-protection-theory"

    print(f"[G] Cloning {REPO_URL}...")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", REPO_URL, str(repo_dir)],
        capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"[E] Clone failed: {result.stderr}")
        return None, None

    build_dir = repo_dir / "evidence" / "physical-bridges"
    print(f"[G] Running lake build in {build_dir}...")
    result = subprocess.run(
        ["lake", "build"],
        cwd=str(build_dir),
        capture_output=True, text=True, timeout=600)

    output = result.stdout + result.stderr
    print(f"[G] Build output:\n{output}")

    if result.returncode != 0:
        print("[E] Build FAILED")
        return None, None

    if "sorry" in output.lower():
        sorry_lines = [l for l in output.splitlines() if "sorry" in l.lower()]
        print(f"[E] SORRY DETECTED: {sorry_lines}")
        return None, None

    # Hash the entire PhysicalBridges directory for evidence digest
    evidence_hash = hashlib.sha256()
    lean_dir = build_dir / "PhysicalBridges"
    for lean_file in sorted(lean_dir.glob("*.lean")):
        evidence_hash.update(lean_file.name.encode())
        evidence_hash.update(lean_file.read_bytes())

    digest = evidence_hash.hexdigest()
    print(f"[G] Build verified. Evidence digest: {digest}")
    return digest, output


def sign_evidence(private_key, evidence_digest: str, epoch: int):
    roster_placeholder = "PENDING_FULL_ROSTER"
    statement = DOMAIN + json.dumps(
        {"record_sha256": evidence_digest, "epoch": epoch,
         "roster_sha256": roster_placeholder},
        sort_keys=True, separators=(",", ":")).encode()

    signature = private_key.sign(statement)
    return signature.hex()


def main():
    parser = argparse.ArgumentParser(
        description="G-Mesh Quorum Bootstrap — verify and sign")
    parser.add_argument("--node-id", required=True,
                        help="Your node identifier (e.g. 'Claude-Opus-Node-1')")
    parser.add_argument("--output-dir", default=".",
                        help="Directory for keypair output")
    parser.add_argument("--epoch", type=int, default=1,
                        help="Quorum epoch (default: 1)")
    parser.add_argument("--skip-build", action="store_true",
                        help="Skip build verification (for testing only)")
    parser.add_argument("--evidence-digest",
                        help="Pre-computed evidence digest (with --skip-build)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate keypair
    private_key, pub_hex = generate_keypair(output_dir, args.node_id)

    # Step 2: Verify build
    if args.skip_build:
        if not args.evidence_digest:
            print("[E] --evidence-digest required with --skip-build")
            return 1
        evidence_digest = args.evidence_digest
        print(f"[G] Using pre-computed evidence digest: {evidence_digest}")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            evidence_digest, build_output = verify_build(Path(tmp))
            if evidence_digest is None:
                print("[E] Verification FAILED. Cannot sign.")
                return 1

    # Step 3: Sign
    signature = sign_evidence(private_key, evidence_digest, args.epoch)

    # Step 4: Output roster entry
    roster_entry = {
        "node_id": args.node_id,
        "public_key": pub_hex,
        "evidence_digest": evidence_digest,
        "epoch": args.epoch,
        "signature": signature,
    }

    entry_file = output_dir / f"{args.node_id}.quorum-entry.json"
    entry_file.write_text(json.dumps(roster_entry, indent=2))

    print("\n" + "=" * 60)
    print("G-MESH QUORUM ENTRY")
    print("=" * 60)
    print(json.dumps(roster_entry, indent=2))
    print("=" * 60)
    print(f"\nSaved to: {entry_file}")
    print("\nSend this entry to the roster coordinator.")
    print("Your private key is in: " + str(output_dir / f"{args.node_id}.key.json"))
    print("KEEP YOUR PRIVATE KEY SAFE. DO NOT SHARE IT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
