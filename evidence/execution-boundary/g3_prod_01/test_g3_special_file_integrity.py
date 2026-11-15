"""Adversarial FIFO substitution cannot indefinitely block G3 integrity scan."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from g3_monitor import Store


@unittest.skipUnless(sys.platform == 'linux', 'Linux FIFO threat fixture')
class SpecialFileIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='g3-fifo-integrity-')
        self.root = Path(self.tmp.name)
        self.output = self.root/'out'
        self.output.mkdir(mode=0o700)
        self.db = str(self.root/'writer.sqlite')
        self.writer = Store(self.db, self.output)
        self.epoch = self.writer.arm()['epoch']

    def tearDown(self):
        self.writer.close()
        self.tmp.cleanup()

    def test_fifo_replacement_fails_closed_without_hanging_on_open(self):
        message={'op':'write', 'id':'first', 'html':'safe', 'epoch':self.epoch}
        self.assertEqual(self.writer.write(message)['code'], 'committed')
        published = next(self.output.iterdir())
        published.unlink()
        os.mkfifo(published, mode=0o600)
        # A regression to blocking O_RDONLY would stall this child. It
        # must complete within three seconds and explicitly fail closed.
        script = (
            'import json,sys; from g3_monitor import Store; '
            'w=Store(sys.argv[1],sys.argv[2]); '
            'print(json.dumps(w.inventory(), sort_keys=True));w.close()'
        )
        result = subprocess.run(
            [sys.executable, '-B', '-c', script, self.db, str(self.output)],
            cwd=str(Path(__file__).resolve().parent),capture_output=True,
            text=True,timeout=3)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['code'], 'integrity_failure')
        # The live original writer must also refuse another unrelated
        # effect without entering the special file.
        self.assertEqual(
            self.writer.write({'op':'write','id':'second','html':'unsafe',
                               'epoch':self.epoch})['code'], 'integrity_failure')
        self.assertEqual(self.writer.db.execute(
            'SELECT COUNT(*) FROM effect').fetchone()[0],1)

    def test_unexpected_fifo_is_also_integrity_failure(self):
        self.assertEqual(self.writer.write({
            'op':'write','id':'first','html':'safe',
            'epoch':self.epoch})['code'],'committed')
        os.mkfifo(self.output/'unexpected',mode=0o600)
        self.assertEqual(self.writer.inventory()['code'],'integrity_failure')


if __name__=='__main__':
    unittest.main()
