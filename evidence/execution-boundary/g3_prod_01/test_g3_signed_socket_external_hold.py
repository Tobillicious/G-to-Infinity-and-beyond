"""Integrated G3 research acceptance: distinct guest UID + signed socket + local hold.

A separate guest process communicates only through SignedFencedServer. Another
trusted process records a durable local writer hold while the socket stays up.
Freshly signed requests must then fail without publishing or consuming a G3
synthetic effect. No live service, remote revocation or real-world X3 claims.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest

from g3_secure_socket import SignedFencedServer
from test_g3_signed_bridge import SignedBridgeTests

GUEST = r"""
import json,os,socket,sys
path=sys.argv[1]
assert os.geteuid()==65534
data=json.loads(sys.stdin.read())
with socket.socket(socket.AF_UNIX) as client:
    client.settimeout(4)
    client.connect(path)
    client.sendall(json.dumps(data,sort_keys=True,separators=(',',':')).encode()+b'\n')
    answer=bytearray()
    while not answer.endswith(b'\n'):
        part=client.recv(4096)
        if not part: break
        answer.extend(part)
print(answer.decode().strip())
"""

@unittest.skipUnless(sys.platform == 'linux' and os.geteuid() == 0,
                     'disposable privileged Linux CI runner required')
class SignedSocketExternalHoldTests(unittest.TestCase):
    setUp = SignedBridgeTests.setUp
    tearDown = SignedBridgeTests.tearDown
    lease = SignedBridgeTests.lease
    request = SignedBridgeTests.request

    def test_external_hold_blocks_new_signed_guest_socket_request(self):
        self.lease()
        # The private SQLite/fence parent remains mode 0700. Only the public
        # socket parent is traversable by the untrusted separate-UID child.
        with tempfile.TemporaryDirectory(prefix='g3-public-ipc-') as public:
            os.chmod(public,0o711)
            sock=str(Path(public)/'signed.sock')
            server=SignedFencedServer(sock,self.writer,{65534})
            os.chown(sock,-1,65534)
            os.chmod(sock,0o660)
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()

            def guest(payload):
                def drop():
                    os.setgroups([])
                    os.setgid(65534)
                    os.setuid(65534)
                process=subprocess.run(
                    [sys.executable,'-B','-c',GUEST,sock],
                    input=json.dumps(payload),capture_output=True,text=True,
                    preexec_fn=drop,close_fds=True,timeout=12)
                self.assertEqual(process.returncode,0,process.stderr)
                return json.loads(process.stdout)

            try:
                initial=guest(self.request())
                self.assertEqual(initial['code'],'committed')
                self.assertEqual(self.gate.effect_count(),1)
                snapshot={p.name:p.read_bytes() for p in self.out.iterdir()}
                self.assertEqual(len(snapshot),1)

                # Trusted controller is a distinct operating-system process,
                # fenced against the same local lock and authority DB.
                controller = (
                    'import sys; from g3_cross_process_fence import revoke_writer; '
                    'x=revoke_writer(sys.argv[1],sys.argv[2]); '
                    'assert x["ok"] and x["code"]=="local_writer_revoked"'
                )
                root=str(self.root)
                env=dict(os.environ)
                parent=str(Path(__file__).resolve().parent)
                env['PYTHONPATH']=str(Path(parent).parent)+os.pathsep+env.get('PYTHONPATH','')
                held=subprocess.run(
                    [sys.executable,'-B','-c',controller,
                     str(self.root/'writer.sqlite'),str(self.root/'fence.lock')],
                    cwd=parent,env=env,capture_output=True,text=True,timeout=12)
                self.assertEqual(held.returncode,0,held.stderr)

                # Fresh mesh sequence cannot override durable writer hold.
                denied=guest(self.request(seq=2))
                self.assertEqual(denied['code'],'stale_or_halted')
                self.assertEqual(self.gate.effect_count(),1)
                self.assertEqual(
                    {p.name:p.read_bytes() for p in self.out.iterdir()},
                    snapshot)
                self.assertTrue(self.writer.inventory()['ok'])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())


if __name__ == '__main__':
    unittest.main()
