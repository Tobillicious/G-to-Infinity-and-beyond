"""Separate Linux-only trusted control socket for the G3 synthetic pilot.

Only the independently allowlisted controller OS principal may hold, revoke
or release. No untrusted agent-facing operations, no external actuators.
This fixture relies on OS peer credentials and socket directory ownership;
it is NOT authorization of real human subjects or a production controller.
"""
import json
import os
import socket
import socketserver
import struct
import sys

from koru_bounded_server import BoundedThreadingMixIn

MAX_CONTROL_REQUEST = 4096


class _ControlHandler(socketserver.StreamRequestHandler):
    def _reply(self, payload):
        self.wfile.write((json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))

    def handle(self):
        self.request.settimeout(self.server.request_timeout)
        try:
            cred = self.request.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
            _pid, uid, _gid = struct.unpack("3i", cred)
        except (AttributeError, OSError, struct.error):
            self._reply({"ok": False, "code": "peer_unverifiable"})
            return
        if uid not in self.server.controller_uids:
            self._reply({"ok": False, "code": "controller_denied"})
            return
        try:
            raw = self.rfile.readline(MAX_CONTROL_REQUEST + 1)
        except (TimeoutError, OSError):
            return
        if not raw or len(raw) > MAX_CONTROL_REQUEST or not raw.endswith(b"\n"):
            self._reply({"ok": False, "code": "invalid_control_request"})
            return
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            self._reply({"ok": False, "code": "invalid_control_request"})
            return
        if type(data) is not dict or type(data.get("op")) is not str:
            self._reply({"ok": False, "code": "invalid_control_request"})
            return
        op = data["op"]
        try:
            if op == "hold" and set(data) == {"op", "minimum_generation"}:
                value = data["minimum_generation"]
                if type(value) is not int or value < 1 or value >= 2**63:
                    raise ValueError("bad generation")
                self.server.gate.hold(value)
                result = {"ok": True, "code": "held"}
            elif op == "release" and set(data) == {"op", "generation"}:
                value = data["generation"]
                if type(value) is not int or value < 1 or value >= 2**63:
                    raise ValueError("bad generation")
                self.server.gate.release(value)
                result = {"ok": True, "code": "released"}
            elif op == "revoke" and set(data) == {"op", "authority_ref"}:
                authority = data["authority_ref"]
                if type(authority) is not str or not authority or len(authority) > 200:
                    raise ValueError("invalid authority")
                self.server.gate.revoke_authority(authority)
                result = {"ok": True, "code": "revoked"}
            else:
                result = {"ok": False, "code": "unsupported_control"}
        except (ValueError, OverflowError, TypeError):
            result = {"ok": False, "code": "invalid_control_request"}
        self._reply(result)


class TrustedControlBroker(BoundedThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, socket_path, gate, *, controller_uids,
                 max_connections=8, request_timeout=2.0):
        if sys.platform != "linux" or not hasattr(socket, "SO_PEERCRED"):
            raise RuntimeError("control socket requires Linux peer credentials")
        if (type(controller_uids) not in (set, frozenset) or
                not controller_uids or
                any(type(uid) is not int or uid < 0 for uid in controller_uids)):
            raise ValueError("explicit controller UID allowlist required")
        self.configure_bounds(max_connections=max_connections, request_timeout=request_timeout)
        self.controller_uids = frozenset(controller_uids)
        self.gate = gate
        super().__init__(socket_path, _ControlHandler)
        os.chmod(socket_path, 0o600)


def send_control(socket_path, payload):
    """Test/developer helper only; OS credentials are checked by the server."""
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(body) >= MAX_CONTROL_REQUEST:
        raise ValueError("control request too large")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect(socket_path)
        sock.sendall(body + b"\n")
        raw = bytearray()
        while not raw.endswith(b"\n"):
            chunk = sock.recv(4096)
            if not chunk or len(raw) + len(chunk) > MAX_CONTROL_REQUEST:
                raise ValueError("control reply truncated")
            raw.extend(chunk)
        return json.loads(raw)
