"""G3 SCM_RIGHTS descriptor-transfer counterexample (disposable Linux root CI).

Negative control: a privileged participant can delegate a pre-open writable
descriptor AFTER HOLD, so path DAC and broker revocation alone do not establish
complete mediation. No production targets or network are used.
"""
import array
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from g3_monitor import Store

CHILD = r"""
import array,json,os,socket,sys
path, sockfd = sys.argv[1:]
s=socket.socket(fileno=int(sockfd))
out={'uid':os.geteuid()}
try:
    with open(path,'ab') as f: f.write(b'PATH')
    out['path']='ALLOWED'
except PermissionError:
    out['path']='DENIED'
_,anc,_,_=s.recvmsg(1,socket.CMSG_SPACE(array.array('i').itemsize))
fds=[]
for level,kind,data in anc:
    if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
        a=array.array('i')
        a.frombytes(data[:len(data)-len(data)%a.itemsize])
        fds.extend(a)
assert len(fds)==1, fds
try:
    os.write(fds[0],b'UNAUTHORIZED-FD')
    os.fsync(fds[0])
finally: os.close(fds[0])
out['delegated_fd']='WROTE'
print(json.dumps(out))
"""

@unittest.skipUnless(sys.platform=='linux' and os.geteuid()==0,
                     'disposable root-enabled Linux CI only')
class DescriptorTransferCut(unittest.TestCase):
    def test_post_hold_scm_rights_can_bypass_dac(self):
        with tempfile.TemporaryDirectory(prefix='g3-scm-rights-') as tmp:
            root=Path(tmp); root.chmod(0o711)
            output=root/'output'; output.mkdir(mode=0o700)
            store=Store(str(root/'writer.sqlite'),output)
            try:
                epoch=store.arm()['epoch']
                result=store.write({'op':'write','id':'one','html':'authorized','epoch':epoch})
                self.assertTrue(result['ok'],result)
                target=next(output.glob('*.html'))
                writable=os.open(target,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW)
                try:
                    self.assertTrue(store.hold()['ok'])
                    self.assertEqual(store.write({'op':'write','id':'two',
                        'html':'denied','epoch':epoch})['code'],'stale_or_halted')
                    before=target.read_bytes()
                    a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM)
                    try:
                        def drop():
                            os.setgroups([])
                            os.setgid(65534)
                            os.setuid(65534)
                        proc=subprocess.Popen(
                            [sys.executable,'-B','-c',CHILD,str(target),str(b.fileno())],
                            pass_fds=(b.fileno(),),preexec_fn=drop,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                        b.close()
                        a.sendmsg([b'X'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,
                            array.array('i',[writable]).tobytes())])
                        stdout,stderr=proc.communicate(timeout=10)
                        self.assertEqual(proc.returncode,0,stderr)
                        observed=json.loads(stdout)
                        self.assertEqual(observed['uid'],65534)
                        self.assertEqual(observed['path'],'DENIED')
                        self.assertEqual(observed['delegated_fd'],'WROTE')
                        self.assertEqual(target.read_bytes(),before+b'UNAUTHORIZED-FD')
                        self.assertEqual(store.inventory()['code'],'integrity_failure')
                    finally: a.close()
                finally: os.close(writable)
            finally: store.close()

if __name__=='__main__':
    unittest.main()
