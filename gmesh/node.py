#!/usr/bin/env python3
"""G-Mesh proof evidence node.

Start with:
    python3 gmesh/node.py

Broadcasts presence on the local network via UDP multicast.
Serves proof evidence over HTTP to any device with a browser.
No dependencies beyond Python 3.6+ stdlib.
"""
import hashlib
import os
import signal
import socket
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT))

from gmesh.manifest import full_report as manifest_report
from gmesh.evidence import full_evidence
from gmesh.discovery import Discovery
from gmesh.server import ProofServer


def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _node_id():
    hostname = socket.gethostname()
    h = hashlib.sha256(f"{hostname}-{os.getpid()}-{time.time()}".encode()).hexdigest()[:8]
    return f"g-{hostname}-{h}"


def main():
    print("[G-MESH] Starting proof evidence node...")

    # Load evidence
    print("[G-MESH] Scanning proof files...")
    evidence = full_evidence(str(REPO_ROOT))
    theorems = evidence["total_theorems"]
    sorry = evidence["total_sorry"]
    print(f"[G-MESH] Proof evidence: {theorems} theorems, {sorry} sorry")

    # Check WORM manifest
    print("[G-MESH] Verifying WORM manifest...")
    worm = manifest_report(str(REPO_ROOT))
    manifest_info = worm.get("manifest", {})
    files_tracked = manifest_info.get("files_tracked", 0)
    manifest_sha = manifest_info.get("manifest_sha256", "?")[:16]
    print(f"[G-MESH] WORM manifest: {files_tracked} files, SHA256 {manifest_sha}...")
    print(f"[G-MESH] WORM status: {worm.get('status', 'UNKNOWN')}")

    # Cache results
    _cached_evidence = [evidence]
    _cached_worm = [worm]

    def get_evidence():
        return _cached_evidence[0]

    def get_worm():
        return _cached_worm[0]

    # Start HTTP server
    node_id = _node_id()
    server = ProofServer(
        str(REPO_ROOT),
        manifest_fn=get_worm,
        evidence_fn=get_evidence,
        peers_fn=lambda: discovery.get_peers(),
        port=0,
    )
    server.start()
    ip = _local_ip()
    port = server.port
    print(f"[G-MESH] HTTP server on http://{ip}:{port}")

    # Start discovery
    discovery = Discovery(
        node_id=node_id,
        http_port=port,
        manifest_sha=manifest_info.get("manifest_sha256", ""),
        evidence_summary=evidence,
    )
    discovery.start()
    print(f"[G-MESH] Discovery active on 239.73.83.1:31415")
    print()
    print(f"  Open http://{ip}:{port} on any device on this network")
    print()
    print(f"[G-MESH] Node {node_id} ready. Ctrl+C to stop.")

    def on_sigint(sig, frame):
        print("\n[G-MESH] Shutting down...")
        discovery.stop()
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_sigint)

    while True:
        time.sleep(10)
        peers = discovery.get_peers()
        if peers:
            print(f"[G-MESH] {len(peers)} peer(s): {', '.join(peers.keys())}")


if __name__ == "__main__":
    main()
