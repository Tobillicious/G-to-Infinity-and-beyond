"""Failure injection through the actual signed PR #456/G-Mesh to G3 writer path.

These are in-process simulated I/O failures, NOT OS power-cut certification.
They distinguish durable synthetic G3 dispatch from physical HTML publication.
"""
import os
import unittest
from unittest.mock import patch
from test_g3_signed_bridge import SignedBridgeTests


class SignedPublicationFaultTests(unittest.TestCase):
    setUp = SignedBridgeTests.setUp
    tearDown = SignedBridgeTests.tearDown
    lease = SignedBridgeTests.lease
    request = SignedBridgeTests.request

    def test_link_failure_then_hold_never_republishes(self):
        self.lease()
        with patch('g3_monitor.os.link',
                   side_effect=OSError('injected no-overwrite link failure')):
            with self.assertRaises(OSError):
                self.writer.write(self.request())
        # Signed synthetic G3 dispatch is separately durable; never
        # conflate it with actually published HTML.
        self.assertEqual(self.gate.effect_count(), 1)
        row=self.writer.db.execute(
            'SELECT state FROM effect WHERE id=?',
            (self.event['event_id'],)).fetchone()
        self.assertEqual(row,('INTENT',))
        self.assertEqual(list(self.out.iterdir()),[])
        # A subsequent hold must block recovery *before* any new publication,
        # even with a new valid signed mesh handshake sequence.
        self.writer.hold()
        result=self.writer.write(self.request(seq=2))
        self.assertEqual(result['code'],'stale_or_halted')
        self.assertEqual(self.gate.effect_count(),1)
        self.assertEqual(list(self.out.iterdir()),[])

    def test_staging_file_sync_failure_needs_new_signed_handshake(self):
        self.lease()
        original=os.fsync
        hit=[False]
        def inject_once(fd):
            if fd != self.writer.dirfd and not hit[0]:
                hit[0]=True
                raise OSError('injected staging fsync failure')
            return original(fd)
        with patch('g3_monitor.os.fsync',side_effect=inject_once):
            with self.assertRaises(OSError):
                self.writer.write(self.request())
        self.assertTrue(hit[0])
        self.assertEqual(self.gate.effect_count(),1)
        self.assertEqual(self.writer.db.execute(
            'SELECT state FROM effect WHERE id=?',
            (self.event['event_id'],)).fetchone(),('INTENT',))
        self.assertEqual(list(self.out.iterdir()),[])
        # A replay of the consumed handshake is rejected, not silently
        # turned into retry permission.
        self.assertEqual(self.writer.write(self.request())['code'],
                         'mesh_nonce_replay')
        self.assertEqual(list(self.out.iterdir()),[])
        # With a new signed sequence, current authority is rechecked and
        # pending, matching bytes may be completed exactly once.
        self.assertEqual(self.writer.write(self.request(seq=2))['code'],
                         'committed')
        self.assertEqual(self.gate.effect_count(),1)
        self.assertEqual(len(list(self.out.iterdir())),1)

    def test_directory_sync_failure_preserves_uncertain_outcome(self):
        self.lease()
        original=os.fsync
        hit=[False]
        def inject_once(fd):
            if fd==self.writer.dirfd and not hit[0]:
                hit[0]=True
                raise OSError('injected publication directory fsync failure')
            return original(fd)
        with patch('g3_monitor.os.fsync',side_effect=inject_once):
            with self.assertRaises(OSError):
                self.writer.write(self.request())
        self.assertTrue(hit[0])
        self.assertEqual(self.gate.effect_count(),1)
        self.assertEqual(self.writer.db.execute(
            'SELECT state FROM effect WHERE id=?',
            (self.event['event_id'],)).fetchone(),('INTENT',))
        # Publication may already be visible even though durable directory
        # sync failed. Never assert rollback of an external effect.
        self.assertEqual(len(list(self.out.iterdir())),1)
        self.assertTrue(self.writer.inventory()['ok'])
        self.writer.hold()
        self.assertEqual(self.writer.write(self.request(seq=2))['code'],
                         'stale_or_halted')
        self.assertEqual(len(list(self.out.iterdir())),1)


if __name__=='__main__':
    unittest.main()
