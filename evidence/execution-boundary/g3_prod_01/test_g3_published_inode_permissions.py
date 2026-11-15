"""Post-publication writable-handle checks for a bounded G3 research writer.

These verify *ordinary writer-process hygiene*, not immutable files: privileged
actors, an owner changing mode, external hardlinks or previously delegated
writable descriptors are explicitly outside this narrow positive test.
"""
import fcntl
import os
from pathlib import Path
import stat
import tempfile
import unittest

from g3_monitor import Store


class PublishedInodePermissionsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='g3-inode-')
        self.root = Path(self.temp.name)
        self.output = self.root / 'out'
        self.output.mkdir(mode=0o700)
        self.store = Store(str(self.root / 'writer.sqlite'), self.output)
        self.epoch = self.store.arm()['epoch']

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_published_inode_is_readonly_before_it_becomes_visible(self):
        self.assertEqual(
            self.store.write({'op':'write','id':'sample','html':'harmless',
                              'epoch':self.epoch})['code'], 'committed')
        files = list(self.output.iterdir())
        self.assertEqual(len(files), 1)
        target = files[0]
        state = target.stat()
        self.assertEqual(stat.S_IMODE(state.st_mode), 0o400)
        self.assertEqual(state.st_nlink, 1)
        self.assertEqual(target.read_text(), 'harmless')
        self.assertTrue(self.store.inventory()['ok'])
        self.assertEqual(self.store.inventory()['committed'], 1)

        # The writer should close its staging O_WRONLY descriptor before
        # linking the published inode. Inspect the process's own FD table;
        # this cannot enumerate descriptors delegated to other processes.
        fd_root = Path('/proc/self/fd')
        if fd_root.is_dir():
            for entry in fd_root.iterdir():
                try:
                    fd = int(entry.name)
                    opened = os.fstat(fd)
                    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                except (OSError, ValueError):
                    continue
                if (opened.st_dev, opened.st_ino) == (state.st_dev, state.st_ino):
                    self.assertEqual(flags & os.O_ACCMODE, os.O_RDONLY)

    @unittest.skipIf(os.geteuid() == 0,
                     'ordinary DAC denial requires a non-root writer UID')
    def test_nonroot_writer_cannot_reopen_published_file_writable_without_chmod(self):
        self.assertEqual(
            self.store.write({'op':'write','id':'sample','html':'safe',
                              'epoch':self.epoch})['code'], 'committed')
        target = next(self.output.iterdir())
        with self.assertRaises(PermissionError):
            fd = os.open(target, os.O_WRONLY | os.O_NOFOLLOW)
            os.close(fd)
        self.assertEqual(target.read_text(), 'safe')

    def test_owner_write_bit_restoration_is_detected_before_new_effect(self):
        self.assertEqual(
            self.store.write({'op':'write','id':'first','html':'safe',
                              'epoch':self.epoch})['code'], 'committed')
        target = next(self.output.iterdir())
        original = target.read_bytes()
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o400)
        # A trusted owner (or compromised service owner) can change DAC
        # without altering the content hash. This must be an integrity alert,
        # not accepted as a safe unchanged artifact.
        target.chmod(0o600)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(self.store.inventory()['code'], 'integrity_failure')
        denied = self.store.write({'op':'write','id':'second','html':'other',
                                   'epoch':self.epoch})
        self.assertEqual(denied['code'], 'integrity_failure')
        self.assertEqual(len(list(self.output.iterdir())), 1)
        self.assertEqual(self.store.db.execute(
            'SELECT COUNT(*) FROM effect').fetchone()[0], 1)
        # Recovery is not permission to publish a different event.
        target.chmod(0o400)
        self.assertTrue(self.store.inventory()['ok'])
        self.assertEqual(self.store.inventory()['committed'], 1)

    def test_world_readability_relaxation_is_integrity_failure(self):
        self.assertEqual(
            self.store.write({'op':'write','id':'first','html':'safe',
                              'epoch':self.epoch})['code'], 'committed')
        target = next(self.output.iterdir())
        target.chmod(0o444)
        self.assertEqual(self.store.inventory()['code'], 'integrity_failure')
        self.assertEqual(self.store.write(
            {'op':'write','id':'second','html':'other',
             'epoch':self.epoch})['code'], 'integrity_failure')

    def test_denied_or_unpublished_intent_never_becomes_visible(self):
        self.store.hold()
        self.assertEqual(
            self.store.write({'op':'write','id':'stale','html':'unsafe',
                              'epoch':self.epoch})['code'], 'stale_or_halted')
        self.assertEqual(list(self.output.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
