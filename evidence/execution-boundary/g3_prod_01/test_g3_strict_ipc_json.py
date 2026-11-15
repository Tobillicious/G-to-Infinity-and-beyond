"""Adversarial strict-JSON tests on actual G3-PROD-01 Unix socket.

The parser must deny ambiguous wire bytes before invoking the writer.
These tests do not constitute complete production authorization review.
"""
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from g3_monitor import Server, Store, strict_request_json


class StrictIpcJsonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="g3-strict-ipc-")
        self.root = Path(self.temp.name)
        self.output = self.root / "protected"
        self.output.mkdir(mode=0o700)
        self.store = Store(str(self.root / "journal.sqlite"), self.output)
        self.socket_path = str(self.root / "broker.sock")
        self.server = Server(self.socket_path, self.store, {os.geteuid()})
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.store.close()
        self.temp.cleanup()

    def send_wire(self, payload):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(3)
            client.connect(self.socket_path)
            client.sendall(payload + bytes([10]))
            response = bytearray()
            while not response.endswith(bytes([10])):
                part = client.recv(4096)
                if not part:
                    break
                response.extend(part)
        self.assertTrue(response, "server must reject invalid input explicitly")
        import json
        return json.loads(response)

    def test_reject_duplicate_top_level_operation(self):
        response = self.send_wire(
            b'{"op":"write","op":"read","id":"a","html":"safe","epoch":1}')
        self.assertEqual(response["code"], "invalid_request")
        self.assertEqual(list(self.output.iterdir()), [])

    def test_reject_nested_duplicate_fields(self):
        response = self.send_wire(
            b'{"op":"write","id":"a","html":"safe","epoch":1,'
            b'"event":{"subject":"first","subject":"other"}}')
        self.assertEqual(response["code"], "invalid_request")
        self.assertEqual(list(self.output.iterdir()), [])

    def test_reject_nonfinite_constants(self):
        for constant in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(constant=constant):
                response = self.send_wire(
                    b'{"op":"write","id":"a","html":"safe","epoch":'
                    + constant + b'}')
                self.assertEqual(response["code"], "invalid_request")
        self.assertEqual(list(self.output.iterdir()), [])

    def test_unambiguous_valid_json_still_reaches_denying_store(self):
        response = self.send_wire(
            b'{"op":"write","id":"a","html":"safe","epoch":1}')
        self.assertEqual(response["code"], "stale_or_halted")

    def test_direct_parser_refuses_duplicate_nested_keys(self):
        with self.assertRaises(ValueError):
            strict_request_json(b'{"outer":{"x":1,"x":2}}')


if __name__ == "__main__":
    unittest.main()
