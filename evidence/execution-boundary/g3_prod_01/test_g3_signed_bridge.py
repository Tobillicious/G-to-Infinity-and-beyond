"""Integration tests using existing PR #456 synthetic fixtures; no live effects."""
import os
import subprocess
import time
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from g3_cross_process_fence import FencedSignedG3Writer
from g_mesh_protocol import GMeshProtocolHandler, PROTOCOL, encode_body
from koru_ed25519_permit import issue_ed25519
from koru_shadow import digest
from koru_synthetic_effect_gate import SyntheticEffectGate
from test_koru_shadow import fixtures
from g3_monitor import sha, Server, request

class SignedBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.out=self.root/'out'
        self.out.mkdir(mode=0o700)
        self.now=[20]
        self.event, registries=fixtures()
        self.gkey=Ed25519PrivateKey.generate()
        self.mkey=Ed25519PrivateKey.generate()
        self.ckey=Ed25519PrivateKey.generate()
        self.permit=issue_ed25519(
            self.gkey,issuer='g3-test-issuer',event=self.event,expires_at=100)
        self.gate=SyntheticEffectGate(
            str(self.root/'g3.sqlite'),
            contexts=registries['contexts'],
            signatures=registries['signatures'],
            witnesses=registries['witnesses'],
            authorities=registries['authorities'],
            provenances=registries['provenances'],
            context_ref='ctx-one',generation=3,
            ed25519_public_key=self.gkey.public_key(),
            permit_issuer='g3-test-issuer')
        self.mesh=GMeshProtocolHandler(
            str(self.root/'mesh.sqlite'),node_id='local-target',
            deployment_id='test-deployment',policy_digest='a'*64,
            issuer_keys={'mesh-issuer':self.mkey.public_key()},
            controller_keys={'controller':self.ckey.public_key()},
            clock=lambda:self.now[0],require_fresh_lease=True,
            max_lease_seconds=10)
        self.html='<h1>Safe curriculum</h1>'
        self.writer=FencedSignedG3Writer(
            str(self.root/'writer.sqlite'),self.out,
            fence_path=str(self.root/'fence.lock'),gate=self.gate,
            mesh=self.mesh,manifest={self.event['event_id']:sha(self.html.encode())},
            clock=lambda:self.now[0])
        self.epoch=self.writer.arm()['epoch']
        self.assertTrue(self.gate.apply(self.event,now=20,permit=self.permit)['ok'])
    def tearDown(self):
        self.writer.close()
        self.mesh.close()
        self.gate.close()
        self.tmp.cleanup()
    def lease(self):
        packet=dict(protocol=PROTOCOL,type='lease',
            source_node_id='controller',target_node_id='local-target',
            deployment_id='test-deployment',policy_digest='a'*64,
            generation=1,sequence=1,not_after=25)
        self.assertTrue(self.mesh.install_authority_lease(
            packet,self.ckey.sign(encode_body(packet)))[0])
    def request(self,seq=1):
        packet=dict(protocol=PROTOCOL,type='handshake',
            source_node_id='mesh-issuer',target_node_id='local-target',
            deployment_id='test-deployment',event_digest=digest(self.event),
            policy_digest='a'*64,authority_ref='auth-lesson',
            generation=1,sequence=seq,not_after=100,
            attestation_ref='unverified-fixture')
        return dict(op='write',id=self.event['event_id'],html=self.html,
            epoch=self.epoch,event=self.event,permit=self.permit,
            mesh_handshake=packet,
            mesh_signature=self.mkey.sign(encode_body(packet)).hex())
    def test_missing_lease_denies(self):
        self.assertEqual(self.writer.write(self.request())['code'],
                         'mesh_FAIL_CLOSED_lease_unavailable')
        self.assertEqual(list(self.out.iterdir()),[])
    def test_valid_signed_path_writes_once(self):
        self.lease()
        self.assertEqual(self.writer.write(self.request())['code'],'committed')
        self.assertEqual(len(list(self.out.iterdir())),1)
        self.assertEqual(self.writer.write(self.request())['code'],'mesh_nonce_replay')
    def test_bad_permit_rejected(self):
        self.lease()
        r=self.request()
        r['permit']=dict(r['permit'],signature='0'*128)
        self.assertEqual(self.writer.write(r)['code'],'invalid_permit_at_effect')
        self.assertFalse(list(self.out.iterdir()))
    def test_bad_manifest_rejected_before_handshake(self):
        self.lease()
        r=self.request()
        r['html']='substitute'
        self.assertEqual(self.writer.write(r)['code'],'untrusted_output_bytes')
        self.assertFalse(list(self.out.iterdir()))
    def test_oversized_output_denied(self):
        self.lease()
        r=self.request()
        r['html']='X'*4097
        self.assertEqual(self.writer.write(r)['code'],'event_id_mismatch')
        self.assertFalse(list(self.out.iterdir()))
    def test_unsigned_request_rejected(self):
        self.lease()
        r=self.request()
        del r['mesh_signature']
        self.assertEqual(self.writer.write(r)['code'],'signed_envelope_required')
        self.assertFalse(list(self.out.iterdir()))
    def test_expired_lease_rejected(self):
        self.lease()
        self.now[0]=25
        self.assertEqual(self.writer.write(self.request())['code'],
                         'mesh_FAIL_CLOSED_lease_unavailable')
    def test_writer_hold_does_not_consume_mesh_or_record_g3_effect(self):
        self.lease()
        self.writer.hold()
        request=self.request()
        self.assertEqual(self.writer.write(request)['code'],'stale_or_halted')
        self.assertEqual(self.gate.effect_count(),0)
        self.assertFalse(list(self.out.iterdir()))
    def test_pending_writer_intent_does_not_consume_mesh_sequence(self):
        self.lease()
        self.writer.db.execute(
            'INSERT INTO effect VALUES(?,?,?,?)',
            ('unrelated','0'*64,self.epoch,'INTENT'))
        self.assertEqual(
            self.writer.write(self.request())['code'],'unresolved_previous_effect')
        self.assertEqual(self.gate.effect_count(),0)
        self.assertFalse(list(self.out.iterdir()))
    def test_separate_process_local_revoke_denies_signed_write(self):
        self.lease()
        command=[
            sys.executable, '-c',
            'import sys; from g3_cross_process_fence import revoke_writer; '
            'result=revoke_writer(sys.argv[1],sys.argv[2]); assert result["ok"]',
            str(self.root/'writer.sqlite'),str(self.root/'fence.lock')]
        env=dict(os.environ)
        env['PYTHONPATH']=str(Path(__file__).resolve().parent.parent)+os.pathsep+env.get('PYTHONPATH','')
        done=subprocess.run(command, capture_output=True, text=True, timeout=10,
            cwd=str(Path(__file__).resolve().parent), env=env)
        self.assertEqual(done.returncode,0,done.stdout+done.stderr)
        self.assertEqual(self.writer.write(self.request())['code'],'stale_or_halted')
        self.assertEqual(self.gate.effect_count(),0)
        self.assertFalse(list(self.out.iterdir()))

    def test_external_revocation_blocks_on_writer_commit_fence(self):
        self.lease()
        command=[
            sys.executable, '-c',
            'import sys; from g3_cross_process_fence import revoke_writer; '
            'result=revoke_writer(sys.argv[1],sys.argv[2]); assert result["ok"]',
            str(self.root/'writer.sqlite'),str(self.root/'fence.lock')]
        env=dict(os.environ)
        env['PYTHONPATH']=str(Path(__file__).resolve().parent.parent)+os.pathsep+env.get('PYTHONPATH','')
        with self.writer.fence.exclusive():
            child=subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True,
                cwd=str(Path(__file__).resolve().parent), env=env)
            try:
                time.sleep(0.2)
                self.assertIsNone(child.poll(),
                    'external hold must wait for writer-owned fence')
            finally:
                pass
        output, errors=child.communicate(timeout=10)
        self.assertEqual(child.returncode,0,output+errors)
        self.assertEqual(self.writer.write(self.request())['code'],'stale_or_halted')
        self.assertFalse(list(self.out.iterdir()))
    def test_signed_writer_socket_enforces_full_envelope(self):
        # The public IPC path must call the signed subclass, never bare
        # Store.write. In-process signed-writer unit checks alone do not
        # demonstrate the behavior of the actual socket entrypoint.
        sock=str(self.root/'signed-writer.sock')
        server=Server(sock,self.writer,{os.geteuid()})
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            signed=self.request()
            unsigned={k:signed[k] for k in ('op','id','html','epoch')}
            self.assertEqual(request(sock,unsigned)['code'],
                             'signed_envelope_required')
            self.assertEqual(self.gate.effect_count(),0)
            self.assertEqual(list(self.out.iterdir()),[])

            # Even a correctly signed envelope is insufficient without
            # a fresh bounded controller lease.
            self.assertEqual(request(sock,signed)['code'],
                             'mesh_FAIL_CLOSED_lease_unavailable')
            self.assertEqual(self.gate.effect_count(),0)
            self.assertEqual(list(self.out.iterdir()),[])

            self.lease()
            substitution=dict(signed,html='<h1>Replaced content</h1>')
            self.assertEqual(request(sock,substitution)['code'],
                             'untrusted_output_bytes')
            self.assertEqual(self.gate.effect_count(),0)
            self.assertEqual(list(self.out.iterdir()),[])

            self.assertEqual(request(sock,signed)['code'],'committed')
            self.assertEqual(self.gate.effect_count(),1)
            self.assertEqual(len(list(self.out.iterdir())),1)
            self.assertEqual(request(sock,signed)['code'],'mesh_nonce_replay')
            self.assertEqual(len(list(self.out.iterdir())),1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())

    def test_writer_socket_hold_denies_signed_request(self):
        self.lease()
        sock=str(self.root/'signed-hold.sock')
        server=Server(sock,self.writer,{os.geteuid()})
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            self.writer.hold()
            self.assertEqual(request(sock,self.request())['code'],
                             'stale_or_halted')
            self.assertEqual(self.gate.effect_count(),0)
            self.assertEqual(list(self.out.iterdir()),[])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())

    def test_real_signed_write_and_external_revoke_have_one_local_order(self):
        """A concurrent local hold waits for a signed writer's actual publish.

        Uses a separate process for revocation, not merely a manually held
        lock. This tests cooperating processes sharing the same lock inode.
        It does not simulate remote G-Mesh revocation or hardware power loss.
        """
        self.lease()
        entered=threading.Event()
        resume=threading.Event()
        outcome=[]
        real_link=os.link

        def block_at_publish(*args, **kwargs):
            entered.set()
            if not resume.wait(timeout=8):
                raise RuntimeError('race fixture publication release timed out')
            return real_link(*args, **kwargs)

        command=[
            sys.executable, '-c',
            'import sys; from g3_cross_process_fence import revoke_writer; '
            'r=revoke_writer(sys.argv[1],sys.argv[2]); assert r["ok"]',
            str(self.root/'writer.sqlite'),str(self.root/'fence.lock')]
        env=dict(os.environ)
        env['PYTHONPATH']=str(Path(__file__).resolve().parent.parent)+os.pathsep+env.get('PYTHONPATH','')

        with patch('g3_monitor.os.link', side_effect=block_at_publish):
            worker=threading.Thread(
                target=lambda: outcome.append(self.writer.write(self.request())),
                daemon=True)
            worker.start()
            self.assertTrue(entered.wait(timeout=5),'signed write did not reach publication')
            child=subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True,
                cwd=str(Path(__file__).resolve().parent), env=env)
            try:
                time.sleep(0.2)
                self.assertIsNone(child.poll(),
                    'revoker must not pass while signed publication holds fence')
            finally:
                resume.set()
            worker.join(timeout=10)
            self.assertFalse(worker.is_alive())
            out,err=child.communicate(timeout=10)
            self.assertEqual(child.returncode,0,out+err)

        self.assertEqual(len(outcome),1)
        self.assertEqual(outcome[0]['code'],'committed')
        self.assertEqual(self.gate.effect_count(),1)
        self.assertEqual(len(list(self.out.iterdir())),1)
        # The completed hold must reject subsequent attempts even when
        # mesh source provides a distinct signed handshake sequence.
        self.assertEqual(self.writer.write(self.request(seq=2))['code'],
                         'stale_or_halted')
        self.assertEqual(len(list(self.out.iterdir())),1)

    def test_lease_expiry_during_staging_blocks_publication(self):
        """Adversarial clock advancement after signed admission but before link."""
        self.lease()
        original=os.fsync
        advanced=[False]
        def expiry_before_link(fd):
            result=original(fd)
            if fd != self.writer.dirfd and not advanced[0]:
                advanced[0]=True
                self.now[0]=25  # signed controller lease expires at 25
            return result
        with patch('g3_monitor.os.fsync',side_effect=expiry_before_link):
            result=self.writer.write(self.request())
        self.assertTrue(advanced[0])
        self.assertEqual(result['code'],'mesh_lease_unavailable_at_publish')
        self.assertEqual(list(self.out.iterdir()),[])
        self.assertEqual(self.writer.db.execute(
            'SELECT state FROM effect WHERE id=?',
            (self.event['event_id'],)).fetchone(),('INTENT',))
        # Synthetic dispatch may have occurred before expiry; that is
        # NOT evidence of an actual published filesystem effect.
        self.assertEqual(self.gate.effect_count(),1)
        # Never turn clock rollback into apparent lease renewal.
        self.now[0]=20
        self.assertNotEqual(self.writer.write(self.request(seq=2)).get('code'),
                            'committed')
        self.assertEqual(list(self.out.iterdir()),[])

    def test_permit_expiry_during_staging_blocks_publication(self):
        """Even with a live mesh lease, permit expiry denies before link."""
        self.lease()
        original=os.fsync
        moved=[False]
        def expiry_before_link(fd):
            result=original(fd)
            if fd != self.writer.dirfd and not moved[0]:
                moved[0]=True
                self.now[0]=25
            return result
        with patch('g3_monitor.os.fsync',side_effect=expiry_before_link):
            result=self.writer.write(self.request())
        self.assertTrue(moved[0])
        self.assertNotEqual(result.get('code'),'committed')
        self.assertFalse(list(self.out.iterdir()))

    def test_writer_epoch_fenced(self):
        self.lease()
        self.writer.hold()
        self.assertEqual(self.writer.write(self.request())['code'],'stale_or_halted')
        self.assertFalse(list(self.out.iterdir()))

if __name__=='__main__':
    unittest.main()
