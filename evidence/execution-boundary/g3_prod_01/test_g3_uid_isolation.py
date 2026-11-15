"""Linux-only host UID isolation check, run as root in a disposable CI runner.

Proves a non-root *process* cannot directly write an owner-private directory.
It DOES NOT prove namespace isolation, full syscall mediation or root resistance.
"""
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import threading
import unittest

from g3_monitor import Store, Server

@unittest.skipUnless(sys.platform == "linux" and os.geteuid() == 0,
                     "requires a disposable Linux root CI runner")
class SeparateUidTests(unittest.TestCase):
    def test_untrusted_uid_cannot_write_protected_output(self):
        with tempfile.TemporaryDirectory(prefix='g3-os-isolation-') as base:
            root = pathlib.Path(base)
            os.chmod(root,0o711)
            out = root/'protected'
            out.mkdir(mode=0o700)
            store = Store(str(root/'writer.sqlite'),out)
            server = Server(str(root/'writer.sock'), store, {65534})
            # The socket's directory and file must be accessible for the
            # purpose of observing peer credentials in the separate process.
            os.chmod(root/'writer.sock',0o666)
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            try:
                child_script = r'''
import os,sys,socket,json
output, socketpath = sys.argv[1:]
assert os.geteuid() == 65534
try:
    fd=os.open(output, os.O_RDONLY | os.O_DIRECTORY)
except PermissionError:
    pass
else:
    os.close(fd)
    raise AssertionError('untrusted UID can open protected output')
try:
    with open(os.path.join(output,'untrusted.html'),'w') as f:
        f.write('bypass')
except PermissionError:
    pass
else:
    raise AssertionError('direct write bypass')
with socket.socket(socket.AF_UNIX) as s:
    s.settimeout(2)
    s.connect(socketpath)
    s.sendall(b'{"op":"write","id":"x","html":"unsafe","epoch":0}\\n'.replace(b'\\\\n',b'\\n'))
    result=b''
    while not result.endswith(b'\\n'):
        chunk=s.recv(4096)
        if not chunk:break
        result+=chunk
    assert json.loads(result)['code']=='stale_or_halted',result
'''
                def drop():
                    os.setgroups([])
                    os.setgid(65534)
                    os.setuid(65534)
                result=subprocess.run(
                    [sys.executable,'-c',child_script,str(out),str(root/'writer.sock')],
                    preexec_fn=drop, text=True, capture_output=True,
                    timeout=15)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(list(out.iterdir()),[])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
                store.close()

if __name__=='__main__':
    unittest.main()
