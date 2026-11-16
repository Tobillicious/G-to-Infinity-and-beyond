"""Bounded G3 signed-writer/withdrawal tests, including a forced publication race.

The synthetic event fixture is not human consent or universal protection.
Unlike PR #505's old negative control, this suite exercises the NEW opt-in
rights-bound writer and verifies that prior withdrawals stop publication.
"""
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "g3_prod_01"))

from g3_prod_01.test_g3_signed_bridge import SignedBridgeTests
from g3_cross_process_fence import FileFence, VetoBoundFencedSignedG3Writer
from g3_rights_veto.rights_veto import RightsVetoJournal
from g3_monitor import sha


class EffectTimeRightsTests(unittest.TestCase):
    def setUp(self):
        fixture = SignedBridgeTests(methodName="test_valid_signed_path_writes_once")
        fixture.setUp()
        self.fixture = fixture
        old = fixture.writer
        old.close()
        self.fence_path = str(fixture.root / "fence.lock")
        self.journal_path = fixture.root / "rights.sqlite"
        self.guard = FileFence(self.fence_path)
        self.rights = RightsVetoJournal(
            self.journal_path, initialize=True, publication_fence=self.guard)
        self.subject = "synthetic-owed-subject"
        fixture.writer = VetoBoundFencedSignedG3Writer(
            str(fixture.root / "writer.sqlite"), fixture.out,
            fence_path=self.fence_path, veto_journal=self.rights,
            trusted_subjects={fixture.event["event_id"]: self.subject},
            trusted_authority_refs={fixture.event["event_id"]: fixture.event["authority_ref"]},
            gate=fixture.gate, mesh=fixture.mesh,
            manifest={fixture.event["event_id"]: sha(fixture.html.encode())},
            clock=lambda: fixture.now[0])
        fixture.epoch = fixture.writer.arm()["epoch"]
        self.addCleanup(self.cleanup_fixture)

    def cleanup_fixture(self):
        self.fixture.tearDown()
        self.rights.close()
        self.guard.close()

    def withdraw(self):
        f = self.fixture
        return self.rights.record_withdrawal(
            record_ref=f.event["authority_ref"], subject=self.subject,
            action="publish", effect_digest=sha(f.html.encode()),
            generation=1)

    def test_new_writable_output_fd_after_initialization_denies_effect(self):
        """A live writer must not trust only an earlier startup FD check."""
        f = self.fixture
        f.lease()
        stage = f.out / ".unexpected-live-writable-stage"
        fd = os.open(stage, os.O_CREAT | os.O_EXCL | os.O_WRONLY |
                     os.O_CLOEXEC, 0o600)
        try:
            response = f.writer.write(f.request())
            self.assertFalse(response["ok"], response)
            self.assertEqual(
                response["code"], "effect_time_writable_fd_or_unavailable")
            self.assertEqual(f.gate.effect_count(), 0)
            self.assertEqual(list(f.out.glob("*.html")), [])
        finally:
            os.close(fd)
            stage.unlink()
        # Releasing the unexpected capability permits the usual
        # independently authorized synthetic request.
        self.assertEqual(f.writer.write(f.request())["code"], "committed")

    def test_prior_withdrawal_denies_real_publish(self):
        self.assertTrue(self.withdraw()["ok"])
        self.fixture.lease()
        response = self.fixture.writer.write(self.fixture.request())
        self.assertEqual(response["code"], "rights_veto_or_unavailable")
        self.assertEqual(self.fixture.gate.effect_count(), 0)
        self.assertEqual(list(self.fixture.out.iterdir()), [])

    def test_no_veto_alone_is_never_consent_but_existing_signed_gate_can_commit(self):
        f = self.fixture
        inspect = self.rights.inspect(
            record_ref=f.event["authority_ref"], subject=self.subject,
            action="publish", effect_digest=sha(f.html.encode()),
            expected_generation=0)
        self.assertFalse(inspect["authorizes_effect"])
        self.assertFalse(inspect["authentic_consent_proved"])
        self.assertFalse(inspect["original_six_x3_proved"])
        f.lease()
        self.assertEqual(f.writer.write(f.request())["code"], "committed")
        self.assertEqual(len(list(f.out.glob("*.html"))), 1)
        # A later withdrawal cannot undo a previously completed publication.
        self.assertTrue(self.withdraw()["ok"])
        self.assertEqual(f.writer.write(f.request(seq=2))["code"],
                         "rights_veto_or_unavailable")

    def test_protected_ipc_requires_veto_bound_writer(self):
        from g3_secure_socket import VetoBoundSignedFencedServer
        from g3_bound_host_server import PreflightedVetoBoundSignedFencedServer
        with self.assertRaises(TypeError):
            VetoBoundSignedFencedServer(
                str(self.fixture.root / "untrusted.sock"), object(), {65534})
        with self.assertRaises(TypeError):
            PreflightedVetoBoundSignedFencedServer(
                str(self.fixture.root / "untrusted-host.sock"),
                object(), {65534}, output_dir=str(self.fixture.out),
                writer_db=str(self.fixture.root / "writer.sqlite"),
                fence_file=self.fence_path,
                gate_db=str(self.fixture.root / "g3.sqlite"),
                mesh_db=str(self.fixture.root / "mesh.sqlite"))

    def test_substituted_authority_ref_cannot_redirect_rights_lookup(self):
        f = self.fixture
        f.lease()
        req = f.request()
        req["event"] = dict(req["event"], authority_ref="replacement-authority")
        result = f.writer.write(req)
        self.assertEqual(result["code"], "rights_event_mapping_unavailable")
        self.assertEqual(list(f.out.iterdir()), [])

    def test_closed_rights_journal_fails_closed_before_publish(self):
        self.rights.close()
        self.fixture.lease()
        result = self.fixture.writer.write(self.fixture.request())
        self.assertEqual(result["code"], "rights_evidence_unavailable")
        self.assertEqual(list(self.fixture.out.iterdir()), [])

    def test_swapped_rights_path_fails_closed(self):
        self.journal_path.rename(self.journal_path.with_suffix(".backup"))
        self.journal_path.write_bytes(b"untrusted substitute")
        self.journal_path.chmod(0o600)
        self.fixture.lease()
        result = self.fixture.writer.write(self.fixture.request())
        self.assertEqual(result["code"], "rights_evidence_unavailable")
        self.assertEqual(list(self.fixture.out.iterdir()), [])

    def test_unbound_rights_journal_rejected(self):
        f = self.fixture
        unbound = RightsVetoJournal(f.root / "unbound.sqlite", initialize=True)
        try:
            with self.assertRaises(PermissionError):
                VetoBoundFencedSignedG3Writer(
                    str(f.root / "other-writer.sqlite"), f.out,
                    fence_path=self.fence_path, veto_journal=unbound,
                    trusted_subjects={f.event["event_id"]: self.subject},
                    trusted_authority_refs={f.event["event_id"]: f.event["authority_ref"]},
                    gate=f.gate, mesh=f.mesh,
                    manifest={f.event["event_id"]: sha(f.html.encode())},
                    clock=lambda: f.now[0])
        finally:
            unbound.close()

    def test_fence_inode_mismatch_rejected(self):
        f = self.fixture
        other_fence = FileFence(str(f.root / "unrelated.lock"))
        other = RightsVetoJournal(f.root / "other-rights.sqlite",
                                  initialize=True, publication_fence=other_fence)
        try:
            with self.assertRaises(PermissionError):
                VetoBoundFencedSignedG3Writer(
                    str(f.root / "other-writer.sqlite"), f.out,
                    fence_path=self.fence_path, veto_journal=other,
                    trusted_subjects={f.event["event_id"]: self.subject},
                    trusted_authority_refs={f.event["event_id"]: f.event["authority_ref"]},
                    gate=f.gate, mesh=f.mesh,
                    manifest={f.event["event_id"]: sha(f.html.encode())},
                    clock=lambda: f.now[0])
        finally:
            other.close()
            other_fence.close()

    def test_separate_process_withdrawal_is_serialized_with_publication(self):
        """Independent controller process cannot pass the writer's flock."""
        f = self.fixture
        f.lease()
        entered = threading.Event()
        proceed = threading.Event()
        outcome = []
        real_link = os.link

        def stop_at_link(*args, **kwargs):
            entered.set()
            if not proceed.wait(8):
                raise RuntimeError("link release timed out")
            return real_link(*args, **kwargs)

        script = (
            "import sys; "
            "from g3_cross_process_fence import FileFence; "
            "from g3_rights_veto.rights_veto import RightsVetoJournal; "
            "guard=FileFence(sys.argv[1]); "
            "j=RightsVetoJournal(sys.argv[2],publication_fence=guard); "
            "r=j.record_withdrawal(record_ref=sys.argv[3], "
            "subject=sys.argv[4],action='publish',"
            "effect_digest=sys.argv[5],generation=1); "
            "assert r['ok'],r; print(r['code']); "
            "j.close(); guard.close()")
        cmd = [
            sys.executable, "-c", script, self.fence_path,
            str(self.journal_path), f.event["authority_ref"], self.subject,
            sha(f.html.encode())]
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(ROOT), str(ROOT / "g3_prod_01"), env.get("PYTHONPATH", "")])
        with patch("g3_monitor.os.link", side_effect=stop_at_link):
            worker = threading.Thread(
                target=lambda: outcome.append(f.writer.write(f.request())),
                daemon=True)
            worker.start()
            self.assertTrue(entered.wait(5), "writer did not reach publication")
            child = subprocess.Popen(
                cmd, cwd=str(ROOT), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                time.sleep(0.2)
                self.assertIsNone(child.poll(),
                    "trusted controller must wait for publication fence")
            finally:
                proceed.set()
            worker.join(timeout=10)
            stdout, stderr = child.communicate(timeout=10)
        self.assertFalse(worker.is_alive())
        self.assertEqual(child.returncode, 0, stdout + stderr)
        self.assertIn("withdrawal_recorded", stdout)
        self.assertEqual(outcome[0]["code"], "committed")
        self.assertEqual(
            f.writer.write(f.request(seq=2))["code"],
            "rights_veto_or_unavailable")

    def test_withdrawal_waits_while_publication_owns_fence(self):
        f = self.fixture
        f.lease()
        at_link = threading.Event()
        resume_link = threading.Event()
        completed = []
        withdrawal = []
        real_link = os.link

        def hold_link(*args, **kwargs):
            at_link.set()
            if not resume_link.wait(timeout=8):
                raise RuntimeError("link fixture timed out")
            return real_link(*args, **kwargs)

        with patch("g3_monitor.os.link", side_effect=hold_link):
            writer_thread = threading.Thread(
                target=lambda: completed.append(f.writer.write(f.request())),
                daemon=True)
            writer_thread.start()
            self.assertTrue(at_link.wait(5), "real writer never reached link")
            revoker = threading.Thread(
                target=lambda: withdrawal.append(self.withdraw()), daemon=True)
            revoker.start()
            time.sleep(0.2)
            self.assertTrue(revoker.is_alive(),
                            "withdrawal must wait for the same fence")
            self.assertEqual(withdrawal, [])
            resume_link.set()
            writer_thread.join(timeout=10)
            revoker.join(timeout=10)

        self.assertFalse(writer_thread.is_alive())
        self.assertFalse(revoker.is_alive())
        self.assertEqual(completed[0]["code"], "committed")
        self.assertTrue(withdrawal[0]["ok"])
        self.assertEqual(
            f.writer.write(f.request(seq=2))["code"],
            "rights_veto_or_unavailable")


if __name__ == "__main__":
    unittest.main()
