"""G3 positive control: no delegated writable capability, no post-HOLD write.

This is an isolated Linux root-provisioned fixture, not proof that every
production process or descriptor-transfer path has been enumerated.
"""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from g3_monitor import Store

CHILD = r"""
import json,os,stat,sys
target,parent_pid,parent_fd=sys.argv[1:]
out={'uid':os.geteuid()}
for name,path in [('direct',target),('proc_fd',f'/proc/{parent_pid}/fd/{parent_fd}')]:
    try:
        fd=os.open(path,os.O_WRONLY|os.O_APPEND)
    except PermissionError:
        out[name]='DENIED'
    except FileNotFoundError:
        out[name]='UNAVAILABLE'
    else:
        try: os.write(fd,b'BYPASS')
        finally: os.close(fd)
        out[name]='WROTE'
# Enumerate own inherited FDs, rather than assuming subprocess defaults
# suffice. A child can create pipes/sockets, but must not hold the target inode.
st=os.stat(target) if os.access(target,os.R_OK) else None
leaked=False
if os.path.isdir('/proc/self/fd'):
    for entry in os.listdir('/proc/self/fd'):
        try:
            fd=int(entry)
            s=os.fstat(fd)
        except (ValueError,OSError): continue
        if stat.S_ISREG(s.st_mode) and s.st_dev==int(sys.argv[4]) and s.st_ino==int(sys.argv[5]):
            leaked=True
out['inherited_target_inode']=leaked
print(json.dumps(out))
"""

@unittest.skipUnless(sys.platform=='linux' and os.geteuid()==0,
                     'disposable root Linux CI required')
class NoDelegatedCapabilityTests(unittest.TestCase):
    def test_separate_uid_without_fd_cannot_mutate_after_hold(self):
        with tempfile.TemporaryDirectory(prefix='g3-no-leak-') as temp:
            root=Path(temp)
            root.chmod(0o711)
            protected=root/'protected'
            protected.mkdir(mode=0o700)
            store=Store(str(root/'writer.sqlite'),protected)
            try:
                epoch=store.arm()['epoch']
                result=store.write({'op':'write','id':'one','html':'safe','epoch':epoch})
                self.assertTrue(result['ok'])
                target=next(protected.glob('*.html'))
                holder=os.open(target,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW|os.O_CLOEXEC)
                try:
                    self.assertTrue(store.hold()['ok'])
                    before=target.read_bytes()
                    stat_info=os.fstat(holder)
                    def drop():
                        os.setgroups([])
                        os.setgid(65534)
                        os.setuid(65534)
                    child=subprocess.run(
                        [sys.executable,'-B','-c',CHILD,str(target),str(os.getpid()),
                         str(holder),str(stat_info.st_dev),str(stat_info.st_ino)],
                        preexec_fn=drop,close_fds=True,pass_fds=(),
                        capture_output=True,text=True,timeout=10)
                    self.assertEqual(child.returncode,0,child.stderr)
                    seen=json.loads(child.stdout)
                    self.assertEqual(seen['uid'],65534)
                    self.assertEqual(seen['direct'],'DENIED')
                    self.assertIn(seen['proc_fd'],('DENIED','UNAVAILABLE'))
                    self.assertFalse(seen['inherited_target_inode'])
                    self.assertEqual(target.read_bytes(),before)
                    self.assertTrue(store.inventory()['ok'])
                finally: os.close(holder)
            finally: store.close()

if __name__=='__main__':
    unittest.main()
