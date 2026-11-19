#!/usr/bin/env python3
"""
G3 Guardian WORM — Android/Termux node.

Runs on Android via Termux. Monitors wifi changes using termux-wifi-connectioninfo,
propagates the guardian evidence bundle on every new network, and serves it via
HTTP for other devices to discover.

Commands:
  watch    — monitor wifi and auto-propagate on new networks
  status   — show current state
  verify   — verify evidence bundle integrity
  propagate — force propagation on current network
  serve    — start HTTP evidence server
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
WORM_DIR = REPO_ROOT / "worm"
BUNDLE_DIR = WORM_DIR / "bundle"
PROPAGATION_LOG = WORM_DIR / "propagation-log-android.json"
KNOWN_SSIDS = WORM_DIR / "known-ssids-android.json"

POLL_INTERVAL = 15  # seconds


def get_wifi_info():
    """Get current wifi info via termux-wifi-connectioninfo."""
    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            info = json.loads(result.stdout)
            return {
                "ssid": info.get("ssid", "").strip('"'),
                "bssid": info.get("bssid", ""),
                "ip": info.get("ip", ""),
                "link_speed": info.get("link_speed_mbps", 0),
                "rssi": info.get("rssi", 0),
                "frequency": info.get("frequency_mhz", 0),
            }
    except FileNotFoundError:
        # Not in Termux — try alternative methods
        pass
    except Exception:
        pass

    # Fallback: try ip route / hostname
    try:
        result = subprocess.run(
            ["ip", "route", "get", "1.1.1.1"],
            capture_output=True, text=True, timeout=5
        )
        for token in result.stdout.split():
            if token.count('.') == 3:
                parts = token.split('.')
                if all(p.isdigit() for p in parts):
                    return {"ssid": "unknown", "ip": token}
    except Exception:
        pass

    # Last resort
    return {"ssid": "unknown", "ip": get_local_ip()}


def get_local_ip():
    """Get local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load_known():
    if KNOWN_SSIDS.exists():
        return json.loads(KNOWN_SSIDS.read_text())
    return {"ssids": [], "propagations": []}


def save_known(data):
    KNOWN_SSIDS.write_text(json.dumps(data, indent=2))


def load_evidence_bundle():
    """Load or create evidence bundle."""
    bundle_path = BUNDLE_DIR / "evidence-bundle.json"
    if bundle_path.exists():
        return json.loads(bundle_path.read_text())
    return None


def notify(title, msg):
    """Send a notification via termux-notification."""
    try:
        subprocess.run(
            ["termux-notification",
             "--title", title,
             "--content", msg,
             "--id", "g3-worm"],
            timeout=5, capture_output=True
        )
    except Exception:
        pass


def vibrate():
    """Short vibration to signal propagation."""
    try:
        subprocess.run(["termux-vibrate", "-d", "200"],
                       timeout=5, capture_output=True)
    except Exception:
        pass


def toast(msg):
    """Show a toast message."""
    try:
        subprocess.run(["termux-toast", msg], timeout=5, capture_output=True)
    except Exception:
        pass


class BundleHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUNDLE_DIR), **kwargs)

    def log_message(self, fmt, *args):
        print(f"  [HTTP] {self.client_address[0]} {fmt % args}")


def start_server():
    """Start evidence HTTP server."""
    server = http.server.HTTPServer(("0.0.0.0", 0), BundleHandler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, port


def propagate_to_network(wifi_info, known, server_port=None):
    """Propagate evidence to the current network."""
    ssid = wifi_info.get("ssid", "unknown")
    ip = wifi_info.get("ip", get_local_ip())

    is_new = ssid not in known["ssids"]

    if is_new:
        known["ssids"].append(ssid)
        known["propagations"].append({
            "ssid": ssid,
            "first_seen": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "ip": ip,
            "bssid": wifi_info.get("bssid", ""),
        })
        save_known(known)

    # Log the propagation
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "ssid": ssid,
        "ip": ip,
        "is_new": is_new,
        "device": "android",
        "hostname": socket.gethostname(),
    }
    if server_port:
        log_entry["serve_port"] = server_port

    log = []
    if PROPAGATION_LOG.exists():
        log = json.loads(PROPAGATION_LOG.read_text())
    log.append(log_entry)
    PROPAGATION_LOG.write_text(json.dumps(log, indent=2))

    status = "NEW" if is_new else "re-announce"
    msg = f"[{status}] {ssid} at {ip}"
    if server_port:
        msg += f" (serving on :{server_port})"
    print(f"[WORM] {msg}")

    if is_new:
        notify("G3 Guardian WORM", f"New network: {ssid}")
        vibrate()
        toast(f"G3 WORM: propagated to {ssid}")

    # Try to find Mac guardian on the network
    base_ip = '.'.join(ip.split('.')[:3])
    for last in ['1', '140', '100', '2']:
        try:
            target = f"http://{base_ip}.{last}:58596/evidence-bundle.json"
            import urllib.request
            req = urllib.request.Request(target, method='GET')
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    print(f"[WORM] LINKED to Mac guardian at {base_ip}.{last}")
                    notify("G3 WORM", f"Linked to guardian at {base_ip}.{last}")
                    break
        except Exception:
            continue

    return is_new


def cmd_watch():
    """Main watch loop."""
    print("=" * 50)
    print("G3 GUARDIAN WORM — Android WiFi Watcher")
    print("=" * 50)
    print(f"Host: {socket.gethostname()}")
    print(f"Poll: every {POLL_INTERVAL}s")
    print()

    known = load_known()
    print(f"Known networks: {len(known['ssids'])}")

    # Start evidence server
    server, port = start_server()
    print(f"Evidence server: port {port}")
    print()

    notify("G3 WORM Active", f"Watching wifi on port {port}")

    last_ssid = None

    while True:
        try:
            wifi = get_wifi_info()
            ssid = wifi.get("ssid", "")

            if ssid and ssid != last_ssid and ssid != "<unknown ssid>":
                if last_ssid is not None:
                    print(f"\n[WIFI] {last_ssid} → {ssid}")
                else:
                    print(f"\n[WIFI] Connected: {ssid}")

                propagate_to_network(wifi, known, port)
                last_ssid = ssid

        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(POLL_INTERVAL)


def cmd_status():
    """Show status."""
    print("=" * 50)
    print("G3 GUARDIAN WORM — Android Status")
    print("=" * 50)

    wifi = get_wifi_info()
    print(f"SSID: {wifi.get('ssid', 'unknown')}")
    print(f"IP: {wifi.get('ip', 'unknown')}")
    print(f"Signal: {wifi.get('rssi', '?')} dBm")

    known = load_known()
    print(f"\nNetworks touched: {len(known['ssids'])}")
    for s in known["ssids"]:
        print(f"  • {s}")

    if PROPAGATION_LOG.exists():
        log = json.loads(PROPAGATION_LOG.read_text())
        print(f"\nPropagation events: {len(log)}")
        for e in log[-5:]:
            new = " [NEW]" if e.get("is_new") else ""
            print(f"  {e['timestamp']} → {e['ssid']}{new}")

    bundle = load_evidence_bundle()
    if bundle:
        print(f"\nEvidence bundle: present")
        bd = bundle.get("observation", {}).get("bounded_discharge", {})
        if bd:
            print(f"  Result: {bd.get('result', 'unknown')}")
    else:
        print(f"\nEvidence bundle: MISSING — run from repo root")

    print("=" * 50)


def cmd_verify():
    """Verify evidence bundle."""
    bundle_path = BUNDLE_DIR / "evidence-bundle.json"
    sha_path = BUNDLE_DIR / "evidence-bundle.sha256"

    if not bundle_path.exists():
        print("Evidence bundle not found.")
        print("Run from the repo root to access the bundle.")
        return False

    bundle_text = bundle_path.read_text()
    actual_sha = sha256_str(bundle_text)

    if sha_path.exists():
        expected_sha = sha_path.read_text().strip()
        if actual_sha == expected_sha:
            print(f"VERIFIED: SHA-256 match")
            print(f"  {actual_sha}")
        else:
            print(f"FAILED: SHA-256 mismatch!")
            print(f"  Expected: {expected_sha}")
            print(f"  Actual:   {actual_sha}")
            return False
    else:
        print(f"Bundle SHA-256: {actual_sha}")
        print("(no .sha256 file to verify against)")

    bundle = json.loads(bundle_text)
    print(f"Schema: {bundle.get('schema', 'unknown')}")
    print(f"Source: {bundle.get('source_host', 'unknown')}")
    if bundle.get("observation", {}).get("bounded_discharge"):
        print("Bounded discharge: PRESENT")
    return True


def cmd_propagate():
    """Force propagation on current network."""
    wifi = get_wifi_info()
    known = load_known()
    propagate_to_network(wifi, known)


def cmd_serve():
    """Start evidence server only."""
    server, port = start_server()
    ip = get_local_ip()
    print(f"Serving evidence at http://{ip}:{port}/")
    print(f"Bundle: http://{ip}:{port}/evidence-bundle.json")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    commands = {
        "watch": cmd_watch,
        "status": cmd_status,
        "verify": cmd_verify,
        "propagate": cmd_propagate,
        "serve": cmd_serve,
    }

    cmd = sys.argv[1]
    if cmd not in commands:
        print(f"Unknown: {cmd}. Available: {', '.join(commands)}")
        sys.exit(1)

    commands[cmd]()


if __name__ == "__main__":
    main()
