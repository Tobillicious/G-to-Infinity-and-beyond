"""Hostile half-written socket / overload regression tests for BOTH G3 brokers.

No real effects or root privileges are used. Tests hold connections open
without completing a newline to ensure stalled peers cannot spawn unlimited
workers or permanently exhaust the broker's admission slots.
"""
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
import unittest

from koru_broker import SyntheticBroker
from koru_control_broker import TrustedControlBroker


@unittest.skipUnless(sys.platform == "linux", "Linux Unix-peer credentials required")
class BoundedBrokerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-load-")
        self.broker = None
        self.thread = None
        self.stalled = []

    def tearDown(self):
        for sock in self.stalled:
            sock.close()
        if self.broker is not None:
            self.broker.shutdown()
            self.broker.server_close()
            self.thread.join(timeout=5)
        self.temp.cleanup()

    def start(self, broker_type):
        path = str(Path(self.temp.name) / "broker.sock")
        if broker_type == "public":
            if os.getuid() == 0:
                self.skipTest("public broker requires non-root peer")
            self.broker = SyntheticBroker(
                path, object(), allowed_client_uids={os.getuid()},
                max_connections=2, request_timeout=0.5)
        else:
            self.broker = TrustedControlBroker(
                path, object(), controller_uids={os.getuid()},
                max_connections=2, request_timeout=0.5)
        self.thread = threading.Thread(
            target=self.broker.serve_forever, daemon=True)
        self.thread.start()
        return path

    @staticmethod
    def connect(path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(path)
        return sock

    def wait_for_slots(self):
        # Fixture observes internal semaphore *only* to deterministically
        # confirm both paused workers have entered their blocking read.
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if self.broker._connection_slots._value == 0:
                return
            time.sleep(0.01)
        self.fail("two partial connections did not occupy both slots")

    def check_bounded_slow_client(self, broker_type):
        path = self.start(broker_type)
        for _ in range(2):
            s = self.connect(path)
            s.sendall(b'{"op":')
            self.stalled.append(s)
        self.wait_for_slots()

        # Third client cannot create a third blocked worker.
        denied = self.connect(path)
        try:
            try:
                denied.sendall(b'{"op":')
                self.assertEqual(denied.recv(256), b"")
            except (BrokenPipeError, ConnectionResetError):
                # Linux may RST an overloaded Unix socket with unread data.
                # RST and EOF both mean the request was rejected.
                pass
        finally:
            denied.close()

        # Partial reads hit the short fixture deadline and release slots.
        deadline = time.monotonic() + 3
        while (self.broker._connection_slots._value != 2 and
               time.monotonic() < deadline):
            time.sleep(0.02)
        self.assertEqual(self.broker._connection_slots._value, 2)

        # Once capacity returns, the server parses valid framed requests.
        request = ({"op": "unsupported", "event": {}, "permit": {}}
                   if broker_type == "public" else {"op": "unknown"})
        with self.connect(path) as fresh:
            fresh.sendall(json.dumps(request).encode() + b"\n")
            response = fresh.recv(4096)
            self.assertTrue(response.endswith(b"\n"), response)
            code = json.loads(response)["code"]
            self.assertEqual(code, "unsupported_operation" if
                             broker_type == "public" else "unsupported_control")

    def test_public_broker_overload_and_slowloris_recovery(self):
        self.check_bounded_slow_client("public")

    def test_privileged_control_broker_overload_and_slowloris_recovery(self):
        self.check_bounded_slow_client("control")

    def check_slow_trickle_deadline(self, broker_type):
        path = self.start(broker_type)
        with self.connect(path) as client:
            client.sendall(b"{")
            started = time.monotonic()
            # Keep trickling bytes faster than the 0.5-second per-read
            # timeout. An absolute deadline MUST release this worker
            # rather than accepting endless 0.15-second extensions.
            for _ in range(5):
                time.sleep(0.15)
                try:
                    client.sendall(b" ")
                except (BrokenPipeError, ConnectionResetError):
                    break
            try:
                data = client.recv(4096)
            except (BrokenPipeError, ConnectionResetError):
                data = b""
            if data:
                self.assertIn(b"request", data)
            self.assertLess(time.monotonic() - started, 1.5)
        until = time.monotonic() + 2
        while (self.broker._connection_slots._value != 2 and
               time.monotonic() < until):
            time.sleep(0.01)
        self.assertEqual(self.broker._connection_slots._value, 2)

    def test_event_broker_slow_trickle_absolute_deadline(self):
        self.check_slow_trickle_deadline("public")

    def test_control_broker_slow_trickle_absolute_deadline(self):
        self.check_slow_trickle_deadline("control")

    def test_invalid_resource_bounds_fail_before_socket_bind(self):
        if os.getuid() != 0:
            with self.assertRaises(ValueError):
                SyntheticBroker(
                    str(Path(self.temp.name) / "invalid.sock"),
                    object(), allowed_client_uids={os.getuid()},
                    max_connections=0)
        with self.assertRaises(ValueError):
            TrustedControlBroker(
                str(Path(self.temp.name) / "control-invalid.sock"),
                object(), controller_uids={os.getuid()},
                request_timeout=0)


if __name__ == "__main__":
    unittest.main()
