import tempfile,unittest,threading,os,socket,json,hashlib
from pathlib import Path
from g3_monitor import Store,Server,request

class MonitorTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.root=Path(self.temp.name)
  self.out=self.root/'out';self.out.mkdir(mode=0o700)
  self.db=str(self.root/'db.sqlite')
  self.s=Store(self.db,self.out)
  self.msg=lambda epoch,event='a',html='safe':{'op':'write','id':event,'html':html,'epoch':epoch}
 def tearDown(self):self.s.close();self.temp.cleanup()
 def test_disarmed_default(self):
  self.assertEqual(self.s.write(self.msg(1))['code'],'stale_or_halted')
 def test_fenced_revocation(self):
  e=self.s.arm()['epoch'];self.assertTrue(self.s.write(self.msg(e))['ok'])
  self.s.hold();self.assertEqual(self.s.write(self.msg(e,event='b'))['code'],'stale_or_halted')
 def test_crash_reboot_fences(self):
  e=self.s.arm()['epoch'];self.s.close();self.s=Store(self.db,self.out)
  self.assertEqual(self.s.write(self.msg(e))['code'],'stale_or_halted')
 def test_recovery_pending_blocks_other_effect(self):
  e=self.s.arm()['epoch'];self.s.db.execute('INSERT INTO effect VALUES(?,?,?,?)',('a',hashlib.sha256(b'safe').hexdigest(),e,'INTENT'))
  self.assertEqual(self.s.write(self.msg(e,event='b'))['code'],'unresolved_previous_effect')
  self.assertTrue(self.s.write(self.msg(e))['ok'])
 def test_existing_file_integrity(self):
  e=self.s.arm()['epoch'];self.assertTrue(self.s.write(self.msg(e))['ok'])
  f=next(self.out.iterdir());f.write_text('tampered')
  self.assertEqual(self.s.write(self.msg(e,event='other'))['code'],'integrity_failure')
 def test_no_staging_artifacts_after_success(self):
  e=self.s.arm()['epoch']
  self.assertTrue(self.s.write(self.msg(e))['ok'])
  self.assertEqual(len(list(self.out.iterdir())),1)
  self.assertTrue(next(self.out.iterdir()).name.endswith('.html'))
 def test_orphan_stage_fails_closed(self):
  e=self.s.arm()['epoch']
  (self.out/'.stage-orphan').write_text('interrupted')
  self.assertEqual(self.s.write(self.msg(e))['code'],'integrity_failure')
 def test_malformed_request_denied(self):
  e=self.s.arm()['epoch']
  self.assertEqual(self.s.write({'op':'write','id':'a','html':'ok','epoch':e,'path':'/tmp/unsafe'})['code'],'schema')
 def test_collision(self):
  e=self.s.arm()['epoch'];self.assertTrue(self.s.write(self.msg(e))['ok'])
  self.assertEqual(self.s.write(self.msg(e,html='different'))['code'],'collision')
 def test_socket_requires_peer_uid_and_never_exposes_arm(self):
  e=self.s.arm()['epoch'];sock=str(self.root/'broker.sock')
  srv=Server(sock,self.s,{os.geteuid()});t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
  try:
   self.assertTrue(request(sock,self.msg(e))['ok'])
   self.assertEqual(request(sock,{'op':'arm'})['code'],'schema')
  finally:srv.shutdown();srv.server_close();t.join()
 def test_socket_denies_other_uid(self):
  sock=str(self.root/'broker.sock');srv=Server(sock,self.s,{os.geteuid()+1000});t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
  try:self.assertEqual(request(sock,self.msg(1))['code'],'peer_denied')
  finally:srv.shutdown();srv.server_close();t.join()

if __name__=='__main__':unittest.main()
