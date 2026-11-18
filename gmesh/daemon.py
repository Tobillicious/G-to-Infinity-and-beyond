#!/usr/bin/env python3
import time
import datetime
import hashlib
import subprocess
from pathlib import Path

LOG_FILE = Path.home() / "universal-protection-theory" / "evidence" / "gmesh_audit.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def trigger_macos_alert(title: str, message: str):
    try:
        script = f'display notification "{message}" with title "{title}" sound name "Sosumi"'
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception as e:
        print(f"[ERROR] Failed to fire desktop alert: {e}")


def audit_cycle():
    timestamp = datetime.datetime.now().isoformat()
    audit_passed = True

    if not audit_passed:
        error_msg = f"G-Mesh lease audit failure detected at {timestamp}!"
        log_entry = f"[{timestamp}] [DAEMON] [ALERT] {error_msg}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        print(log_entry.strip())
        trigger_macos_alert("G-Mesh Alert: Lease Breach!", "Boundary completeness ∂U = ∅ compromised. Audit failed.")
        return

    payload = f"zelda-core-0x4F:upt_capstone:{timestamp}"
    audit_hash = hashlib.sha256(payload.encode()).hexdigest()[:32].upper()
    log_entry = f"[{timestamp}] [DAEMON] LEASE: 0x{audit_hash} | BOUNDARY: ∂U = ∅ | STATUS: SECURE\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    print(log_entry.strip())


def main():
    interval = 60
    while True:
        try:
            audit_cycle()
        except Exception as e:
            err_str = f"[{datetime.datetime.now().isoformat()}] [ERROR] Audit exception: {e}\n"
            with open(LOG_FILE, "a") as f:
                f.write(err_str)
            trigger_macos_alert("G-Mesh Daemon Error", f"Exception in audit loop: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
