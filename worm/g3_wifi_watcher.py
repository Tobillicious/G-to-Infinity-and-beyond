#!/usr/bin/env python3
"""
G3 WiFi Watcher — auto-propagate guardian evidence on every new network.

Monitors wifi state changes on macOS. When the machine joins a new SSID
(one not seen before), it automatically:
  1. Creates the evidence bundle for the current guardian state
  2. Starts the mDNS announcement on the new network
  3. Serves the evidence bundle to the new network
  4. Logs the propagation event

The watcher maintains a persistent record of every SSID it has propagated
to, ensuring the WORM touches each network exactly once per session but
re-announces on reconnection (wifi roaming).

Install as a launchd agent for automatic startup:
  python3 worm/g3_wifi_watcher.py install

Run directly:
  python3 worm/g3_wifi_watcher.py watch

Stop the launchd agent:
  python3 worm/g3_wifi_watcher.py uninstall
"""

import hashlib
import http.server
import json
import os
import pathlib
import plistlib
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WORM_DIR = REPO_ROOT / "worm"
BUNDLE_DIR = WORM_DIR / "bundle"
PROPAGATION_LOG = WORM_DIR / "propagation-log.json"
KNOWN_SSIDS = WORM_DIR / "known-ssids.json"
PLIST_NAME = "com.upt.g3.wifi-watcher"
PLIST_PATH = pathlib.Path.home() / "Library" / "LaunchAgents" / f"{PLIST_NAME}.plist"

POLL_INTERVAL = 10  # seconds between wifi checks


def get_current_ssid():
    """Get the current wifi SSID on macOS."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPAirPortDataType"],
            capture_output=True, text=True, timeout=10
        )
        in_current = False
        for line in result.stdout.split("\n"):
            if "Current Network Information:" in line:
                in_current = True
                continue
            if in_current and line.strip().endswith(":"):
                ssid = line.strip().rstrip(":")
                if ssid and ssid != "Current Network Information":
                    return ssid
            if in_current and "Other Local" in line:
                break
        return None
    except Exception:
        return None


def get_local_ip():
    """Get the machine's local IP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def load_known_ssids():
    """Load the set of SSIDs we've propagated to."""
    if KNOWN_SSIDS.exists():
        return json.loads(KNOWN_SSIDS.read_text())
    return {"ssids": [], "propagations": []}


def save_known_ssids(data):
    """Persist known SSIDs."""
    KNOWN_SSIDS.write_text(json.dumps(data, indent=2))


def log_propagation(ssid, ip, port):
    """Log a propagation event."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "ssid": ssid,
        "ip": ip,
        "port": port,
        "hostname": socket.gethostname(),
    }

    log = []
    if PROPAGATION_LOG.exists():
        log = json.loads(PROPAGATION_LOG.read_text())
    log.append(entry)
    PROPAGATION_LOG.write_text(json.dumps(log, indent=2))

    print(f"[PROPAGATION] {entry['timestamp']} → {ssid} at {ip}:{port}")
    return entry


class BundleHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUNDLE_DIR), **kwargs)

    def log_message(self, fmt, *args):
        print(f"  [HTTP] {self.client_address[0]} {fmt % args}")


class WormNode:
    """A single WORM propagation node — one per network."""

    def __init__(self, ssid):
        self.ssid = ssid
        self.server = None
        self.port = None
        self.mdns_proc = None
        self.alive = False

    def start(self):
        """Start serving evidence and announcing on this network."""
        # Create fresh bundle
        from g3_worm_propagator import create_evidence_bundle
        create_evidence_bundle()

        # Start HTTP server
        self.server = http.server.HTTPServer(("0.0.0.0", 0), BundleHandler)
        self.port = self.server.server_address[1]
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()

        # Start mDNS announcement
        ip = get_local_ip()
        hostname = socket.gethostname()
        try:
            self.mdns_proc = subprocess.Popen(
                ["dns-sd", "-R", f"G3-Guardian-{self.ssid[:20]}",
                 "_g3-guardian._tcp", "local.", str(self.port),
                 "version=1", f"host={hostname}", f"ip={ip}",
                 f"ssid={self.ssid}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            pass

        self.alive = True
        log_propagation(self.ssid, ip, self.port)
        print(f"[WORM] Node active on '{self.ssid}' — {ip}:{self.port}")

    def stop(self):
        """Stop this node."""
        if self.server:
            self.server.shutdown()
        if self.mdns_proc:
            self.mdns_proc.terminate()
        self.alive = False
        print(f"[WORM] Node stopped on '{self.ssid}'")


def watch():
    """Main watch loop — monitor wifi and propagate on new networks."""
    print("=" * 60)
    print("G3 WIFI WATCHER — auto-propagate on new networks")
    print("=" * 60)
    print(f"Host: {socket.gethostname()}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print()

    # Add the worm dir to path so we can import the propagator
    sys.path.insert(0, str(WORM_DIR))

    known = load_known_ssids()
    active_node = None
    last_ssid = None

    def shutdown(sig, frame):
        print("\n[WATCHER] Shutting down...")
        if active_node:
            active_node.stop()
        save_known_ssids(known)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        ssid = get_current_ssid()

        if ssid and ssid != last_ssid:
            print(f"\n[WIFI] Network changed: {last_ssid} → {ssid}")

            # Stop previous node
            if active_node:
                active_node.stop()

            # Check if this is a new network
            is_new = ssid not in known["ssids"]
            if is_new:
                known["ssids"].append(ssid)
                known["propagations"].append({
                    "ssid": ssid,
                    "first_seen": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "ip": get_local_ip(),
                })
                save_known_ssids(known)
                print(f"[WORM] NEW NETWORK: '{ssid}' — propagating!")
            else:
                print(f"[WORM] Known network: '{ssid}' — re-announcing")

            # Start new node on this network
            active_node = WormNode(ssid)
            try:
                active_node.start()
            except Exception as e:
                print(f"[ERROR] Failed to start node: {e}")

            last_ssid = ssid

        elif not ssid and last_ssid:
            print(f"\n[WIFI] Disconnected from {last_ssid}")
            if active_node:
                active_node.stop()
                active_node = None
            last_ssid = None

        time.sleep(POLL_INTERVAL)


def install_launchd():
    """Install as a macOS launchd agent — starts on login, watches wifi."""
    python_path = shutil.which("python3") or "/usr/bin/python3"
    script_path = str(pathlib.Path(__file__).resolve())

    plist = {
        "Label": PLIST_NAME,
        "ProgramArguments": [python_path, script_path, "watch"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(WORM_DIR / "wifi-watcher.log"),
        "StandardErrorPath": str(WORM_DIR / "wifi-watcher.err"),
        "WorkingDirectory": str(REPO_ROOT),
        "EnvironmentVariables": {
            "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        },
    }

    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)

    subprocess.run(["launchctl", "load", str(PLIST_PATH)], check=True)
    print(f"Installed and loaded: {PLIST_PATH}")
    print(f"Log: {WORM_DIR / 'wifi-watcher.log'}")
    print()
    print("The G3 WORM will now auto-propagate whenever this Mac")
    print("joins a new wifi network. It starts on login.")
    print()
    print("To stop: python3 worm/g3_wifi_watcher.py uninstall")


def uninstall_launchd():
    """Remove the launchd agent."""
    if PLIST_PATH.exists():
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)])
        PLIST_PATH.unlink()
        print(f"Removed: {PLIST_PATH}")
    else:
        print("Not installed.")


def status():
    """Show current watcher status."""
    print("=" * 60)
    print("G3 WIFI WATCHER STATUS")
    print("=" * 60)

    # Check if launchd agent is installed
    if PLIST_PATH.exists():
        result = subprocess.run(
            ["launchctl", "list", PLIST_NAME],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"LaunchAgent: INSTALLED + RUNNING")
        else:
            print(f"LaunchAgent: INSTALLED (not running)")
    else:
        print(f"LaunchAgent: NOT INSTALLED")

    print(f"Current SSID: {get_current_ssid() or 'disconnected'}")
    print(f"Local IP: {get_local_ip()}")

    known = load_known_ssids()
    print(f"\nKnown SSIDs ({len(known['ssids'])}):")
    for s in known["ssids"]:
        print(f"  • {s}")

    if PROPAGATION_LOG.exists():
        log = json.loads(PROPAGATION_LOG.read_text())
        print(f"\nPropagation events ({len(log)}):")
        for entry in log[-5:]:
            print(f"  {entry['timestamp']} → {entry['ssid']} at {entry['ip']}:{entry['port']}")

    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    commands = {
        "watch": watch,
        "install": install_launchd,
        "uninstall": uninstall_launchd,
        "status": status,
    }

    cmd = sys.argv[1]
    if cmd not in commands:
        print(f"Unknown: {cmd}. Available: {', '.join(commands)}")
        sys.exit(1)

    commands[cmd]()


if __name__ == "__main__":
    main()
