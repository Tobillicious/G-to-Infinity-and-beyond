"""G3 alternate hard-link alias negative control, disposable Linux fixture.

A privileged actor deliberately creates an alternate hard link to a protected
output in a directory accessible by another UID. Revoking the writer and
protecting the original pathname does not revoke that alias. This is a known
privileged-delegation counterexample, not a production exploitation test.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from g3_monitor import Store

CHILD = r"""
import json,os,sys
protected,alias=sys.argv[1:]
result={'uid':os.geteuid()}
try:
    with open(protected,'ab') as file: file.write(b'DIRECT')
    result['direct']='WROTE'
except PermissionError:
    result['direct']='DENIED'
with open(alias,'ab') as file: file.write(b'ALIAS')
result['alias']='WROTE'
print(json.dumps(result))
"""

@unittest.skipUnless(sys.platform=='linux' and os.geteuid()==0,
                     'requires isolated root-enabled Linux CI runner')
class HardlinkAliasCutTests(unittest.TestCase):
    def test_privileged_alias_can_outlive_writer_hold(self):
        with tempfile.TemporaryDirectory(prefix='g3-hardlink-alias-') as rootdir:
            base=Path(rootdir)
            base.chmod(0o711)
            private=base/'protected'
            private.mkdir(mode=0o700)
            public=base/'delegated'
            public.mkdir(mode=0o777)
            os.chmod(public,0o777)
            store=Store(str(base/'writer.sqlite'),private)
            try:
                epoch=store.arm()['epoch']
                self.assertEqual(store.write({'op':'write','id':'first',
                    'html':'protected-content','epoch':epoch})['code'],'committed')
                target=next(private.glob('*.html'))
                # Privileged administrator intentionally delegates an alias.
                # This is exactly the unsafe capability transfer being tested.
                alias=public/'alternate.html'
                os.link(target,alias)
                os.chmod(alias,0o666)
                self.assertTrue(store.hold()['ok'])
                self.assertEqual(store.write({'op':'write','id':'second',
                    'html':'blocked','epoch':epoch})['code'],'integrity_failure')
                before=target.read_bytes()
                def drop():
                    os.setgroups([])
                    os.setgid(65534)
                    os.setuid(65534)
                proc=subprocess.run(
                    [sys.executable,'-B','-c',CHILD,str(target),str(alias)],
                    preexec_fn=drop,close_fds=True,pass_fds=(),
                    text=True,capture_output=True,timeout=10)
                self.assertEqual(proc.returncode,0,proc.stderr)
                observed=json.loads(proc.stdout)
                self.assertEqual(observed['uid'],65534)
                self.assertEqual(observed['direct'],'DENIED')
                self.assertEqual(observed['alias'],'WROTE')
                self.assertEqual(target.read_bytes(),before+b'ALIAS')
                self.assertEqual(store.inventory()['code'],'integrity_failure')
            finally:
                store.close()

if __name__=='__main__':
    unittest.main()
