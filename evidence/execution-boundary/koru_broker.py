"""Local UNIX-socket front end for the isolated synthetic G3 effect store.

RESEARCH FIXTURE ONLY. Does not handle actual external effects. The process
owning this server MUST run as a distinct OS identity from untrusted callers,
and its private SQLite directory MUST NOT be writable/traversable by callers.
Only admission and a configured effect route are exposed when a real marker
sink is attached; synthetic dispatch is available only without that sink.
Hold/revoke/release remain outside the untrusted socket API. The client cannot supply trusted registries or keys.
"""
import json
import os
import socket
import socketserver
import struct
import sys
import time

from koru_bounded_server import BoundedThreadingMixIn

MAX_REQUEST = 32768


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(self.server.request_timeout)
        # Verify kernel-supplied Linux peer identity BEFORE parsing any request.
        try:
            raw_cred = self.request.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
            _pid, uid, _gid = struct.unpack("3i", raw_cred)
        except (AttributeError, OSError, struct.error):
            self._send({"ok": False, "code": "peer_unverifiable"})
            return
        if uid not in self.server.allowed_client_uids:
            self._send({"ok": False, "code": "peer_denied"})
            return
        # Strict one-request-per-connection, input bounded before JSON parse.
        try:
            raw = self.rfile.readline(MAX_REQUEST + 1)
        except (TimeoutError, OSError):
            # Slow/incomplete senders lose the connection without an effect.
            return
        if not raw or len(raw) > MAX_REQUEST or not raw.endswith(b"\n"):
            self._send({"ok": False, "code": "bad_request"})
            return
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            self._send({"ok": False, "code": "bad_request"})
            return
        if type(data) is not dict:
            self._send({"ok": False, "code": "bad_request"})
            return
        # Lease-mode marker gateway accepts a *separately signed* mesh
        # handshake; all other routes retain the narrower original schema.
        leased_marker = (
            data.get("op") == "effect_marker" and
            self.server.effect_sink is not None and
            getattr(self.server.effect_sink, "requires_mesh_handshake", False))
        expected = ({"op", "event", "permit", "mesh_handshake", "mesh_signature"}
                    if leased_marker else {"op", "event", "permit"})
        if set(data) != expected:
            self._send({"ok": False, "code": "bad_request"})
            return
        if data["op"] not in ("admit", "dispatch", "effect_marker"):
            self._send({"ok": False, "code": "unsupported_operation"})
            return
        if data["op"] == "effect_marker" and self.server.effect_sink is None:
            self._send({"ok": False, "code": "unsupported_operation"})
            return
        if data["op"] == "dispatch" and self.server.effect_sink is not None:
            # A live marker sink must be the *only* dispatch route exposed
            # to untrusted clients. Allowing SQLite-only dispatch would
            # journal a side effect without creating its corresponding
            # marker, stranding the recovery queue and blocking later work.
            self._send({"ok": False, "code": "effect_route_required"})
            return
        # Time MUST come from the trusted broker, never a client-supplied value.
        try:
            now = self.server.clock()
            if type(now) is not int or now < 0:
                raise ValueError("invalid trusted clock")
        except (TypeError, ValueError, OverflowError):
            self._send({"ok": False, "code": "clock_unavailable"})
            return
        # Persist the clock floor BEFORE evaluating any permit. A broker
        # restart or system clock rollback cannot revive an old permit below
        # the last time observed by this protected store.
        time_check = self.server.gate.accept_broker_time(now)
        if not time_check["ok"]:
            self._send(time_check)
            return
        try:
            if data["op"] == "admit":
                result = self.server.gate.apply(
                    data["event"], now=now, permit=data["permit"])
            elif data["op"] == "effect_marker":
                # Target path and effect type are provisioned independently,
                # NEVER selected from client-controlled event or socket JSON.
                if leased_marker:
                    # Hex decoding is strictly canonical; the mesh handler
                    # authenticates the bytes and exact event digest.
                    hex_signature = data["mesh_signature"]
                    if (type(hex_signature) is not str or
                            len(hex_signature) != 128 or
                            any(c not in "0123456789abcdef" for c in hex_signature)):
                        result = {"ok": False, "code": "invalid_mesh_signature"}
                    else:
                        result = self.server.effect_sink.apply_marker(
                            data["event"], now=now, permit=data["permit"],
                            mesh_handshake=data["mesh_handshake"],
                            mesh_signature=bytes.fromhex(hex_signature))
                else:
                    result = self.server.effect_sink.apply_marker(
                        data["event"], now=now, permit=data["permit"])
            else:
                result = self.server.gate.dispatch_synthetic(
                    data["event"], now=now, permit=data["permit"])
        except (TypeError, ValueError, KeyError):
            result = {"ok": False, "code": "bad_request"}
        self._send(result)

    def _send(self, value):
        self.wfile.write((json.dumps(value, sort_keys=True) + "\n").encode("utf-8"))


class SyntheticBroker(BoundedThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, socket_path, gate, *, allowed_client_uids, clock=None,
                 effect_sink=None, max_connections=16, request_timeout=2.0):
        if sys.platform != "linux" or not hasattr(socket, "SO_PEERCRED"):
            raise RuntimeError("secure broker requires Linux SO_PEERCRED")
        if (type(allowed_client_uids) not in (set, frozenset) or
                not allowed_client_uids or
                any(type(u) is not int or u < 1 for u in allowed_client_uids)):
            raise ValueError("explicit non-root client UID allowlist required")
        self.configure_bounds(max_connections=max_connections, request_timeout=request_timeout)
        self.allowed_client_uids = frozenset(allowed_client_uids)
        self.clock = clock if clock is not None else lambda: int(time.time())
        if not callable(self.clock):
            raise ValueError("trusted clock callback required")
        if effect_sink is not None and effect_sink.gate is not gate:
            raise ValueError("filesystem sink must use this protected gate")
        self.effect_sink = effect_sink
        self.gate = gate
        super().__init__(socket_path, _Handler)
        # Mode is set only after bind. Containing directory must be protected
        # by trusted deployment provisioning; permissions alone do not protect
        # against a caller with the SAME Unix UID as the broker.
        os.chmod(socket_path, 0o666)


def send_request(socket_path, op, event, permit, now):
    """Untrusted client helper, no secrets and no DB handle."""
    # Keep caller's legacy "now" argument for test-client compatibility,
    # but NEVER send it to the trusted server.
    message = json.dumps(dict(op=op, event=event, permit=permit),
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
