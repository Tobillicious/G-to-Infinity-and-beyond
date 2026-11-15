"""Local UNIX-socket front end for the isolated synthetic G3 effect store.

RESEARCH FIXTURE ONLY. Does not handle actual external effects. The process
owning this server MUST run as a distinct OS identity from untrusted callers,
and its private SQLite directory MUST NOT be writable/traversable by callers.
Only 'admit' and 'dispatch' are available; hold/revoke/release stay outside the
untrusted socket API. The client cannot supply trusted registries or keys.
"""
import json
import os
import socket
import socketserver
import threading

MAX_REQUEST = 32768


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        # Strict one-request-per-connection, input bounded before JSON parse.
        raw = self.rfile.readline(MAX_REQUEST + 1)
        if not raw or len(raw) > MAX_REQUEST or not raw.endswith(b"\n"):
            self._send({"ok": False, "code": "bad_request"})
            return
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            self._send({"ok": False, "code": "bad_request"})
            return
        if type(data) is not dict or set(data) != {"op", "event", "permit", "now"}:
            self._send({"ok": False, "code": "bad_request"})
            return
        if data["op"] not in ("admit", "dispatch"):
            self._send({"ok": False, "code": "unsupported_operation"})
            return
        if type(data["now"]) is not int:
            self._send({"ok": False, "code": "bad_time"})
            return
        try:
            if data["op"] == "admit":
                result = self.server.gate.apply(
                    data["event"], now=data["now"], permit=data["permit"])
            else:
                result = self.server.gate.dispatch_synthetic(
                    data["event"], now=data["now"], permit=data["permit"])
        except (TypeError, ValueError, KeyError):
            result = {"ok": False, "code": "bad_request"}
        self._send(result)

    def _send(self, value):
        self.wfile.write((json.dumps(value, sort_keys=True) + "\n").encode("utf-8"))


class SyntheticBroker(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, socket_path, gate):
        self.gate = gate
        super().__init__(socket_path, _Handler)
        # Mode is set only after bind. Containing directory must be protected
        # by trusted deployment provisioning; permissions alone do not protect
        # against a caller with the SAME Unix UID as the broker.
        os.chmod(socket_path, 0o666)


def send_request(socket_path, op, event, permit, now):
    """Untrusted client helper, no secrets and no DB handle."""
    message = json.dumps(dict(op=op, event=event, permit=permit, now=now),
                         sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(message) >= MAX_REQUEST:
        raise ValueError("request too large")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(5)
        connection.connect(socket_path)
        connection.sendall(message + b"\n")
        raw = bytearray()
        while not raw.endswith(b"\n"):
            part = connection.recv(4096)
            if not part or len(raw) + len(part) > MAX_REQUEST:
                raise ValueError("truncated response")
            raw.extend(part)
    return json.loads(raw)
