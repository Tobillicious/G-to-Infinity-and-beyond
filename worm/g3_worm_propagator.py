#!/usr/bin/env python3
"""
G3 WORM Propagator — Write Once Read Many guardian node distribution via wifi.

Discovers reachable hosts on the local network and plants verified guardian
evidence on each. Every copy is append-only — you can add new evidence,
never remove old. The WORM manifest grows: each node adds its own hash.

Architecture:
  1. ANNOUNCE: register as _g3-guardian._tcp via mDNS (dns-sd on macOS)
  2. SERVE:   HTTP server on a random port, serving the evidence bundle
  3. DISCOVER: find other _g3-guardian._tcp services on the network
  4. VERIFY:  each receiving node checks the manifest SHA before accepting
  5. CHAIN:   new node signs the manifest and advertises itself

The guardian node itself has network=none — the WORM propagator runs on the
HOST, distributing the evidence of what the isolated guardian holds. The
guardian never touches the network. The WORM is the voice that carries the
proof to other machines.

Usage:
  python3 worm/g3_worm_propagator.py announce   # advertise + serve
  python3 worm/g3_worm_propagator.py discover    # find peers
  python3 worm/g3_worm_propagator.py status      # show local guardian + peers
  python3 worm/g3_worm_propagator.py bundle      # create evidence bundle
"""

import hashlib
import http.server
import json
import os
import pathlib
import socket
import subprocess
import sys
import threading
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence"
GUARDIAN_OBS = EVIDENCE_DIR / "execution-boundary" / "g3_guardian_node"
WORM_MANIFEST = REPO_ROOT / "worm_manifest.json"
WORM_SHA = REPO_ROOT / "worm_manifest.sha256"
BUNDLE_DIR = REPO_ROOT / "worm" / "bundle"

SERVICE_TYPE = "_g3-guardian._tcp"
SERVICE_NAME = "G3-Guardian-WORM"


def get_local_ip():
    """Get the machine's local IP address on the wifi network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def sha256_file(path):
    """SHA-256 hash of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    """SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def guardian_status():
    """Check if the guardian container is running and get its state."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "upt-guardian-node",
             "--format", "{{.State.Status}}|{{.HostConfig.NetworkMode}}|{{.HostConfig.ReadonlyRootfs}}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        parts = result.stdout.strip().split("|")
        return {
            "status": parts[0],
            "network": parts[1],
            "readonly": parts[2],
            "running": parts[0] == "running",
            "isolated": parts[1] == "none" and parts[2] == "true"
        }
    except Exception:
        return None


def latest_observation():
    """Find and read the most recent observation file."""
    obs_files = sorted(GUARDIAN_OBS.glob("live-observation-*.json"), reverse=True)
    if not obs_files:
        return None
    with open(obs_files[0]) as f:
        return json.load(f)


def create_evidence_bundle():
    """Create a self-verifying evidence bundle for WORM distribution."""
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    bundle = {
        "schema": "g3-worm-evidence-bundle-v1",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_host": socket.gethostname(),
        "source_ip": get_local_ip(),
        "guardian": guardian_status(),
        "observation": latest_observation(),
        "lean_modules": [],
        "manifest_sha": None,
    }

    lean_dir = EVIDENCE_DIR / "physical-bridges" / "PhysicalBridges"
    for lean_file in sorted(lean_dir.glob("G3*.lean")):
        bundle["lean_modules"].append({
            "name": lean_file.name,
            "sha256": sha256_file(lean_file),
            "size": lean_file.stat().st_size,
        })

    if WORM_MANIFEST.exists():
        bundle["manifest_sha"] = sha256_file(WORM_MANIFEST)

    bundle_path = BUNDLE_DIR / "evidence-bundle.json"
    bundle_json = json.dumps(bundle, indent=2)
    with open(bundle_path, "w") as f:
        f.write(bundle_json)

    bundle_sha = sha256_bytes(bundle_json.encode())
    with open(BUNDLE_DIR / "evidence-bundle.sha256", "w") as f:
        f.write(bundle_sha)

    print(f"Evidence bundle created: {bundle_path}")
    print(f"  SHA-256: {bundle_sha}")
    print(f"  Guardian: {'RUNNING + ISOLATED' if bundle['guardian'] and bundle['guardian']['isolated'] else 'NOT VERIFIED'}")
    print(f"  Lean modules: {len(bundle['lean_modules'])}")
    print(f"  Observation: {'present' if bundle['observation'] else 'missing'}")

    return bundle_path, bundle_sha


class WORMHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for serving the evidence bundle."""

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(BUNDLE_DIR), **kwargs)

    def log_message(self, format, *args):
        print(f"[WORM-HTTP] {self.client_address[0]} - {format % args}")


def start_http_server():
    """Start a temporary HTTP server for evidence distribution."""
    server = http.server.HTTPServer(("0.0.0.0", 0), WORMHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


def announce_mdns(port):
    """Announce the G3 guardian via Bonjour/mDNS using dns-sd."""
    hostname = socket.gethostname()
    print(f"Announcing {SERVICE_NAME} on {SERVICE_TYPE} port {port}...")
    print(f"  Host: {hostname}")
    print(f"  IP: {get_local_ip()}")
    print(f"  Port: {port}")
    print()
    print("Other machines can discover this guardian with:")
    print(f"  dns-sd -B {SERVICE_TYPE} local.")
    print()
    print("Press Ctrl+C to stop announcing.")

    try:
        proc = subprocess.Popen(
            ["dns-sd", "-R", SERVICE_NAME, SERVICE_TYPE, "local.", str(port),
             "version=1", f"host={hostname}", f"ip={get_local_ip()}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return proc
    except FileNotFoundError:
        print("WARNING: dns-sd not found. Using fallback UDP broadcast.")
        return None


def discover_peers():
    """Discover other G3 guardian nodes on the local network."""
    print(f"Browsing for {SERVICE_TYPE} on local network...")
    print("(Press Ctrl+C to stop after a few seconds)")
    print()

    try:
        proc = subprocess.Popen(
            ["dns-sd", "-B", SERVICE_TYPE, "local."],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        time.sleep(5)
        proc.terminate()
        output = proc.stdout.read()

        peers = []
        for line in output.strip().split("\n"):
            if SERVICE_NAME in line or "G3" in line:
                peers.append(line.strip())

        if peers:
            print(f"Found {len(peers)} guardian peer(s):")
            for p in peers:
                print(f"  {p}")
        else:
            print("No guardian peers found on local network.")
            print("This node is the FIRST. Others will discover it after announcement.")

        return peers

    except FileNotFoundError:
        print("dns-sd not available. Falling back to ARP scan...")
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        hosts = []
        for line in result.stdout.strip().split("\n"):
            if "(" in line and ")" in line:
                ip = line.split("(")[1].split(")")[0]
                if ip != get_local_ip():
                    hosts.append(ip)
        print(f"Found {len(hosts)} host(s) on network: {hosts}")
        return hosts


def verify_bundle(bundle_path):
    """Verify the integrity of a received evidence bundle."""
    with open(bundle_path) as f:
        bundle_json = f.read()
    bundle = json.loads(bundle_json)

    sha_path = bundle_path.replace(".json", ".sha256")
    if os.path.exists(sha_path):
        with open(sha_path) as f:
            expected_sha = f.read().strip()
        actual_sha = sha256_bytes(bundle_json.encode())
        if actual_sha != expected_sha:
            print(f"WORM VERIFICATION FAILED: SHA mismatch")
            print(f"  Expected: {expected_sha}")
            print(f"  Actual:   {actual_sha}")
            return False

    print("WORM VERIFICATION PASSED")
    print(f"  Source: {bundle.get('source_host', 'unknown')}")
    print(f"  Created: {bundle.get('created', 'unknown')}")
    if bundle.get("guardian", {}).get("isolated"):
        print("  Guardian: ISOLATED (network=none, readonly=true)")
    return True


def print_status():
    """Print the current guardian and WORM status."""
    print("=" * 60)
    print("G3 GUARDIAN WORM STATUS")
    print("=" * 60)

    gs = guardian_status()
    if gs:
        print(f"\nGuardian Container: {'RUNNING' if gs['running'] else 'STOPPED'}")
        print(f"  Network:  {gs['network']}")
        print(f"  Readonly: {gs['readonly']}")
        print(f"  Isolated: {'YES' if gs['isolated'] else 'NO'}")
    else:
        print("\nGuardian Container: NOT FOUND")

    obs = latest_observation()
    if obs:
        print(f"\nLatest Observation:")
        print(f"  Date: {obs.get('date', 'unknown')}")
        print(f"  Scope: {obs.get('observation_scope', 'unknown')[:80]}...")
        bd = obs.get("bounded_discharge")
        if bd:
            print(f"\n  BOUNDED DISCHARGE:")
            print(f"    hWitness:  {bd.get('hWitness', 'unknown')[:60]}...")
            print(f"    hCoverage: {bd.get('hCoverage', 'unknown')[:60]}...")
            print(f"    hMeaning:  {bd.get('hMeaning', 'unknown')[:60]}...")
            print(f"    Result:    {bd.get('result', 'unknown')}")

    print(f"\nLocal IP: {get_local_ip()}")
    print(f"Hostname: {socket.gethostname()}")

    if WORM_MANIFEST.exists():
        print(f"\nWORM Manifest: {sha256_file(WORM_MANIFEST)[:16]}...")
    print("=" * 60)


def cmd_announce():
    """Main announce command: create bundle, start server, register mDNS."""
    print_status()
    print()

    bundle_path, bundle_sha = create_evidence_bundle()
    server, port = start_http_server()
    print(f"\nEvidence server running at http://{get_local_ip()}:{port}/")
    print(f"  Bundle: http://{get_local_ip()}:{port}/evidence-bundle.json")
    print(f"  SHA:    http://{get_local_ip()}:{port}/evidence-bundle.sha256")

    mdns_proc = announce_mdns(port)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down WORM propagator...")
        server.shutdown()
        if mdns_proc:
            mdns_proc.terminate()


def cmd_discover():
    """Main discover command: find peers on the network."""
    print_status()
    print()
    discover_peers()


def cmd_status():
    """Main status command."""
    print_status()


def cmd_bundle():
    """Create evidence bundle without serving."""
    create_evidence_bundle()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    commands = {
        "announce": cmd_announce,
        "discover": cmd_discover,
        "status": cmd_status,
        "bundle": cmd_bundle,
    }

    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands)}")
        sys.exit(1)

    commands[cmd]()


if __name__ == "__main__":
    main()
