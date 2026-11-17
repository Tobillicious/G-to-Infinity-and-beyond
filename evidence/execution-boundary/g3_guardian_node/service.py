"""Persistent local launcher for the existing bounded G3 marker authority.

One Linux volume, distinct authority/executor/controller principals, existing
HOLD/effect transaction and fixed confined executor. This is not whole-host
enforcement or independently administered custody. No restart reprovisioning.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import socket
import stat
import subprocess
import sys
import time
import uuid

ENGINE = Path(__file__).resolve().parents[1]
STATE = Path("/state")
AUTH, EXECUTOR, CONTROLLER = 65533, 65532, 65530
DATABASE = STATE / "authority" / "authority.sqlite"
SOCKET = STATE / "socket" / "authority.sock"
MARKERS = STATE / "markers"
CONFIG = STATE / "node.json"
LIVE = STATE / "authority-live.json"
MANIFEST = Path(__file__).with_name("engine-manifest.json")


def verify_engine():
    manifest = json.loads(MANIFEST.read_text())
    sources = dict(manifest["files"], **manifest.get("observer_files", {}))
    for name, expected in sources.items():
        path = ENGINE / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("pinned engine source mismatch: " + name)
    return manifest


def write_json(path, data):
    temporary = path.with_name(path.name + ".new-" + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        os.write(fd, (json.dumps(data, sort_keys=True) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def event(kind, details):
    record = {"time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "event": kind, "details": details}
    fd = os.open(STATE / "events.jsonl", os.O_WRONLY | os.O_APPEND |
                 os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        os.write(fd, (json.dumps(record, sort_keys=True) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def identity(uid):
    def drop():
        os.setgroups([])
        os.setgid(uid)
        os.setuid(uid)
    return drop


def provision_or_load(manifest):
    from koru_authority_admission_journal import AuthorityAdmissionJournal
    from koru_transactional_hold_witness import TransactionalHoldWitness
    if CONFIG.exists():
        if CONFIG.is_symlink() or CONFIG.stat().st_uid != 0:
            raise RuntimeError("node configuration identity invalid")
        config = json.loads(CONFIG.read_text())
        if config.get("engine_source_commit") != manifest["engine_source_commit"]:
            raise RuntimeError("existing node uses another engine; no automatic migration")
        # Missing or corrupt state must fail, never become fresh/unheld.
        TransactionalHoldWitness(str(DATABASE)).read()
        AuthorityAdmissionJournal(TransactionalHoldWitness(str(DATABASE))).unresolved()
        return config
    if any(STATE.iterdir()):
        raise RuntimeError("incomplete or unknown existing state; refusing reprovisioning")
    os.chmod(STATE, 0o755)
    for name, mode in [("authority", 0o700), ("markers", 0o700), ("socket", 0o711)]:
        path = STATE / name
        path.mkdir(mode=mode)
        path.chmod(mode)
        os.chown(path, AUTH, AUTH)
    expected = {"generation": 1, "event_id": "guardian-" + uuid.uuid4().hex,
                "authority_ref": "g3-" + manifest["engine_source_commit"]}
    witness = TransactionalHoldWitness.provision(str(DATABASE), dict(expected, held=False))
    AuthorityAdmissionJournal.provision(witness)
    os.chown(DATABASE, AUTH, AUTH)
    config = {"engine_source_commit": manifest["engine_source_commit"],
              "expected": expected, "scope": "one authority-owned fixed marker"}
    write_json(CONFIG, config)
    return config


def process_start(pid):
    # After the final ')' the array begins at Linux proc field 3.
    text = Path(f"/proc/{pid}/stat").read_text()
    return int(text.rsplit(")", 1)[1].split()[19])


def authority(expected):
    from koru_authority_owned_marker_service import AuthorityOwnedMarkerService
    service = AuthorityOwnedMarkerService(str(SOCKET), str(DATABASE), str(MARKERS),
        executor_uid=EXECUTOR, controller_uid=CONTROLLER, expected=expected)
    service.timeout = 0.2
    print("READY", flush=True)
    try:
        while True:
            readable, _, _ = select.select([sys.stdin], [], [], 0)
            if readable:
                line = sys.stdin.readline()
                if not line or line.strip() == "stop":
                    break
            service.handle_request()
    finally:
        service.server_close()


def serve(manifest):
    config = provision_or_load(manifest)
    if os.path.lexists(SOCKET):
        info = os.lstat(SOCKET)
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != AUTH:
            raise RuntimeError("unexpected existing socket identity")
        os.unlink(SOCKET)
    child = subprocess.Popen([sys.executable, "-B", __file__, "authority",
        "--expected", json.dumps(config["expected"])], preexec_fn=identity(AUTH),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, text=True,
        close_fds=True, cwd="/engine",
        env={"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONPATH": "/engine",
             "PYTHONDONTWRITEBYTECODE": "1"})
    stopped = False
    def stop(_signal, _frame):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        ready, _, _ = select.select([child.stdout], [], [], 10)
        if not ready or child.stdout.readline().strip() != "READY":
            raise RuntimeError("authority did not become ready")
        write_json(LIVE, {"pid": child.pid, "uid": AUTH,
                          "process_start": process_start(child.pid)})
        event("started", {"authority_pid": child.pid,
            "engine_source_commit": manifest["engine_source_commit"]})
        print(json.dumps({"ready": True, "scope": config["scope"]}), flush=True)
        while not stopped and child.poll() is None:
            time.sleep(0.2)
        if not stopped:
            raise RuntimeError("authority exited unexpectedly")
    finally:
        if child.poll() is None:
            try:
                child.stdin.write("stop\n")
                child.stdin.flush()
                child.wait(timeout=6)
            except (BrokenPipeError, subprocess.TimeoutExpired):
                child.terminate()
                child.wait(timeout=4)
        child.stdin.close()
        child.stdout.close()


def live_identity():
    record = json.loads(LIVE.read_text())
    if record["uid"] != AUTH or process_start(record["pid"]) != record["process_start"]:
        raise RuntimeError("authority live-process identity mismatch")
    lines = Path(f"/proc/{record['pid']}/status").read_text().splitlines()
    uid = next(line.split()[1] for line in lines if line.startswith("Uid:"))
    if int(uid) != AUTH:
        raise RuntimeError("authority UID mismatch")
    return record


def status(manifest):
    from koru_authority_admission_journal import AuthorityAdmissionJournal
    from koru_transactional_hold_witness import TransactionalHoldWitness
    from koru_r6_marker_readonly_observer import observe
    live = live_identity()
    witness = TransactionalHoldWitness(str(DATABASE))
    state = witness.read()
    unresolved = AuthorityAdmissionJournal(witness).unresolved()
    marker = observe(str(MARKERS), expected_uid=AUTH)
    return {"ready": True, "engine_source_commit": manifest["engine_source_commit"],
            "observer_source_commit": manifest.get("observer_source_commit"),
            "scope": "one authority-owned zero-byte marker",
            "held": state["held"], "generation": state["generation"],
            "admission_state_recorded": bool(unresolved), "marker": marker,
            "authority_pid": live["pid"], "authority_uid": AUTH,
            "executor_uid": EXECUTOR, "controller_uid": CONTROLLER,
            "custody": "same-administrator local Docker volume",
            "whole_machine_enforcement": False, "independent_custody_verified": False}


CLIENT = r'''
import json,socket,sys
with socket.socket(socket.AF_UNIX) as connection:
    connection.settimeout(4)
    connection.connect(sys.argv[1])
    connection.sendall(b'{"op":"hold"}\n')
    reply=bytearray()
    while not reply.endswith(b"\n"):
        part=connection.recv(1024)
        if not part or len(reply)+len(part)>2048:
            raise ValueError("incomplete HOLD response")
        reply.extend(part)
print(json.dumps(json.loads(reply)),flush=True)
'''


def control(command, manifest):
    live = live_identity()
    if command == "apply":
        from koru_no_inherited_fd_executor import launch_fixed_executor_client
        # Only the existing fixed, confined client can request this effect.
        result = launch_fixed_executor_client(str(SOCKET), executor_uid=EXECUTOR,
            authority_uid=AUTH, authority_pid=live["pid"])
    else:
        process = subprocess.run([sys.executable, "-B", "-c", CLIENT, str(SOCKET)],
            preexec_fn=identity(CONTROLLER), close_fds=True,
            capture_output=True, text=True, timeout=8,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"})
        if process.returncode:
            raise RuntimeError("HOLD was not acknowledged: " + process.stderr.strip())
        result = json.loads(process.stdout)
    event(command, result)
    return {"result": result, "node": status(manifest)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["serve", "authority", "status", "apply", "hold"])
    parser.add_argument("--expected")
    args = parser.parse_args()
    manifest = verify_engine()
    if args.command == "authority":
        authority(json.loads(args.expected))
    elif args.command == "serve":
        if os.geteuid() != 0:
            raise RuntimeError("supervisor requires isolated container root")
        serve(manifest)
    else:
        answer = status(manifest) if args.command == "status" else control(args.command, manifest)
        print(json.dumps(answer, sort_keys=True))


if __name__ == "__main__":
    main()
