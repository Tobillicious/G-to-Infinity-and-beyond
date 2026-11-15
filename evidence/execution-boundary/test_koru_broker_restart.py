"""Local broker restart and persistent-clock rollback controls (synthetic)."""
import os
import pathlib
import sys
import tempfile
import threading
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from koru_broker import SyntheticBroker, send_request
from koru_ed25519_permit import issue_ed25519
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures


@unittest.skipUnless(
    sys.platform == "linux" and hasattr(os, "getuid") and os.getuid() > 0,
    "requires Linux non-root user for broker peer-credential test")
class TestBrokerRestart(unittest.TestCase):
    def test_restart_preserves_time_floor_and_effect_controls(self):
        event, trusted = fixtures()
        private = Ed25519PrivateKey.generate()
        with tempfile.TemporaryDirectory(prefix="g3-restart-") as folder:
            database = str(pathlib.Path(folder) / "gate.sqlite")
            options = dict(
                contexts=trusted["contexts"],
                signatures=trusted["signatures"],
                witnesses=trusted["witnesses"],
                authorities=trusted["authorities"],
                provenances=trusted["provenances"],
                context_ref="ctx-one", generation=3,
                ed25519_public_key=private.public_key(),
                permit_issuer="fixture-issuer")
            permit = issue_ed25519(
                private, issuer="fixture-issuer", event=event, expires_at=35)
            first = SyntheticEffectGate(database, **options)
            socket_a = str(pathlib.Path(folder) / "broker-a.sock")
            broker = SyntheticBroker(
                socket_a, first, allowed_client_uids={os.getuid()},
                clock=lambda: 30)
            thread = threading.Thread(target=broker.serve_forever, daemon=True)
            thread.start()
            try:
                admission = send_request(socket_a, "admit", event, permit, 0)
                self.assertEqual(admission["code"], "durable_synthetic_record")
                self.assertEqual(first.effect_count(), 0)
            finally:
                broker.shutdown()
                broker.server_close()
                thread.join(timeout=5)
                first.close()

            second = SyntheticEffectGate(database, **options)
            clock = [20]
            socket_b = str(pathlib.Path(folder) / "broker-b.sock")
            broker = SyntheticBroker(
                socket_b, second, allowed_client_uids={os.getuid()},
                clock=lambda: clock[0])
            thread = threading.Thread(target=broker.serve_forever, daemon=True)
            thread.start()
            try:
                rollback = send_request(socket_b, "dispatch", event, permit, 0)
                self.assertEqual(rollback["code"], "clock_rollback")
                self.assertEqual(second.effect_count(), 0)

                clock[0] = 35
                expired = send_request(socket_b, "dispatch", event, permit, 0)
                self.assertEqual(expired["code"], "invalid_permit_at_effect")
                self.assertEqual(second.effect_count(), 0)

                # An expired permit cannot be revived by rolling backward
                # after the broker observed time 35.
                clock[0] = 31
                self.assertEqual(
                    send_request(socket_b, "dispatch", event, permit, 0)["code"],
                    "clock_rollback")
                self.assertEqual(second.effect_count(), 0)
            finally:
                broker.shutdown()
                broker.server_close()
                thread.join(timeout=5)
                second.close()


if __name__ == "__main__":
    unittest.main()
