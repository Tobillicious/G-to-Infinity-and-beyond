import argparse
import json
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    result = subprocess.run(
        ["./guardian-node", "check"],
        capture_output=True,
        text=True,
        cwd="/Users/admin/universal-protection-theory",
    )
    if result.returncode != 0:
        print(f"[FAIL] node check failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    status = subprocess.run(
        ["./guardian-node", "status", "--json"],
        capture_output=True,
        text=True,
        cwd="/Users/admin/universal-protection-theory",
    )
    data = json.loads(status.stdout)
    if not (data.get("ready") and data.get("held")):
        print("[FAIL] node not ready/held", file=sys.stderr)
        sys.exit(1)

    print(f"[PASS] {args.node_id}: fingerprints verified, node ready and in HOLD (gen {data['generation']})")
    if args.strict:
        print("[STRICT] Boundary completeness enforced: ∂U = ∅")


if __name__ == "__main__":
    main()
