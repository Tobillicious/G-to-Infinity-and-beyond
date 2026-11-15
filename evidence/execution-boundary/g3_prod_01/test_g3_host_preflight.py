"""Adversarial local preflight checks; non-root CI only for positive cases."""
import os
from pathlib import Path
import tempfile
import unittest
from g3_host_preflight import inspect_writer_host

class HostPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='g3-host-preflight-')
        self.root=Path(self.tmp.name).resolve()
        self.output=self.root/'effects'
        self.output.mkdir(mode=0o700)
        self.state=self.root/'state'
        self.state.mkdir(mode=0o700)
        self.paths=[self.state/p for p in
                    ('writer.sqlite','fence.lock','gate.sqlite','mesh.sqlite')]
        for p in self.paths:
            p.write_bytes(b'fixture')
            p.chmod(0o600)
        self.kw=dict(output_dir=str(self.output),writer_db=str(self.paths[0]),
                     fence_file=str(self.paths[1]),gate_db=str(self.paths[2]),
                     mesh_db=str(self.paths[3]))
    def tearDown(self):
        self.tmp.cleanup()
    def check(self):
        return inspect_writer_host(**self.kw)

    @unittest.skipIf(os.geteuid()==0, 'positive case needs dedicated nonroot writer')
    def test_private_owned_resources_are_accepted_but_not_certified(self):
        result=self.check()
        self.assertTrue(result['ok'],result)
        self.assertFalse(result['certified'])
        self.assertFalse(result['all_capabilities_mediated'])

    def test_reject_accessible_effect_directory(self):
        self.output.chmod(0o755)
        self.assertFalse(self.check()['ok'])

    def test_reject_writable_authority_root(self):
        self.state.chmod(0o777)
        self.assertFalse(self.check()['ok'])

    def test_reject_writable_database(self):
        self.paths[0].chmod(0o666)
        self.assertFalse(self.check()['ok'])

    def test_reject_hardlinked_fence(self):
        alias=self.state/'duplicate-fence'
        os.link(self.paths[1],alias)
        self.assertFalse(self.check()['ok'])

    def test_reject_symlinked_database(self):
        self.paths[2].unlink()
        self.paths[2].symlink_to(self.paths[0])
        self.assertFalse(self.check()['ok'])

    def test_reject_symlinked_intermediate_state_root(self):
        real=self.root/'real-parent'
        real.mkdir(mode=0o700)
        alt=real/'state'
        alt.mkdir(mode=0o700)
        alias=self.root/'alias-parent'
        alias.symlink_to(real,target_is_directory=True)
        # Move the existing private files to the alternate directory;
        # final files themselves are ordinary regular owned inodes.
        for p in self.paths:
            p.rename(alt/p.name)
        self.kw.update(writer_db=str(alias/'state'/'writer.sqlite'),
                       fence_file=str(alias/'state'/'fence.lock'),
                       gate_db=str(alias/'state'/'gate.sqlite'),
                       mesh_db=str(alias/'state'/'mesh.sqlite'))
        result=self.check()
        self.assertEqual(result['code'],'unsafe_ancestor')
        self.assertEqual(result['reason'],'ancestor_not_directory')

    def test_reject_writable_intermediate_state_root(self):
        middle=self.root/'writable-middle'
        middle.mkdir(mode=0o700)
        inner=middle/'private'
        inner.mkdir(mode=0o700)
        for p in self.paths:
            p.rename(inner/p.name)
        self.kw.update(writer_db=str(inner/'writer.sqlite'),
                       fence_file=str(inner/'fence.lock'),
                       gate_db=str(inner/'gate.sqlite'),
                       mesh_db=str(inner/'mesh.sqlite'))
        os.chmod(middle,0o777)
        try:
            result=self.check()
            self.assertEqual(result['code'],'unsafe_ancestor')
            self.assertEqual(result['reason'],'ancestor_writable')
        finally:
            os.chmod(middle,0o700)

    def test_reject_relative_paths(self):
        self.kw['writer_db']='relative.sqlite'
        self.assertEqual(self.check()['code'],'invalid_path')

    def test_reject_duplicated_authority_path(self):
        self.kw['gate_db']=self.kw['writer_db']
        self.assertEqual(self.check()['code'],'resource_path_collision')

    def test_reject_db_under_effect_output(self):
        p=self.output/'gate.sqlite'
        p.write_bytes(b'fixture')
        p.chmod(0o600)
        self.kw['gate_db']=str(p)
        self.assertFalse(self.check()['ok'])

    def test_root_identity_is_not_certifiable(self):
        if os.geteuid()==0:
            self.assertEqual(self.check()['code'],'root_writer_forbidden')
        else:
            self.assertNotEqual(self.check()['code'],'root_writer_forbidden')

if __name__=='__main__':
    unittest.main()
