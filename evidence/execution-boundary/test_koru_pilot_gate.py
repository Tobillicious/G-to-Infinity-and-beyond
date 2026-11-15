"""Controlled pilot negative controls. Run with:
python3 -B -m unittest discover -s evidence/execution-boundary -p 'test_koru_pilot_gate.py' -v
"""
import copy
import tempfile
import threading
import unittest
from pathlib import Path
from koru_shadow import digest
from koru_pilot_gate import PilotGate
from test_koru_shadow import fixtures


class TestKoruPilotGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.event, self.trusted = fixtures()
        self.db_path = str(Path(self.tmp.name) / "pilot.sqlite")
        self.gate = PilotGate(self.db_path, contexts=self.trusted["contexts"],
                              signatures=self.trusted["signatures"],
                              witnesses=self.trusted["witnesses"],
                              authorities=self.trusted["authorities"],
                              provenances=self.trusted["provenances"],
                              context_ref="ctx-one", generation=3)

    def tearDown(self):
        self.gate.close()
        self.tmp.cleanup()

    def test_valid_commit_and_durable_replay_refusal(self):
        result = self.gate.apply(copy.deepcopy(self.event), now=20)
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(result["receipt"]), 64)
        self.assertEqual(self.gate.record_count(), 1)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "replay")
        self.gate.close()
        self.gate = PilotGate(self.db_path, contexts=self.trusted["contexts"],
                              signatures=self.trusted["signatures"],
                              witnesses=self.trusted["witnesses"],
                              authorities=self.trusted["authorities"],
                              provenances=self.trusted["provenances"],
                              context_ref="ctx-one", generation=1)
        self.assertEqual(self.gate.record_count(), 1)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "replay")

    def test_revoked_authority_cannot_commit(self):
        self.trusted["authorities"]["auth-lesson"]["active"] = False
        result = self.gate.apply(self.event, now=20)
        self.assertEqual(result["code"], "independent_authority")
        self.assertEqual(self.gate.record_count(), 0)

    def test_changed_whole_context_and_payload_cannot_commit(self):
        event = copy.deepcopy(self.event)
        event["action_expr"] = {"op": "identity", "args": [{"atom": "p1"}]}
        self.assertEqual(self.gate.apply(event, now=20)["code"], "trusted_witness")
        context = self.trusted["contexts"]["ctx-one"]
        context["positions"][5]["value"] += 1
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "whole_context_mismatch")
        self.assertEqual(self.gate.record_count(), 0)

    def test_hold_and_released_generation(self):
        self.gate.hold(4)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "held")
        self.gate.release(5)
        self.assertEqual(self.gate.apply(self.event, now=20)["code"], "stale_generation")
        self.assertEqual(self.gate.record_count(), 0)

    def test_stale_context_and_lineage(self):
        event = copy.deepcopy(self.event)
        event["context_version"] = 3
        self.assertEqual(self.gate.apply(event, now=20)["code"], "stale_context")
        event = copy.deepcopy(self.event)
        event["predecessor_ref"] = "wrong"
        self.assertEqual(self.gate.apply(event, now=20)["code"], "lineage_mismatch")
        self.assertEqual(self.gate.record_count(), 0)

    def test_concurrent_duplicate_only_once(self):
        results = []
        def worker():
            results.append(self.gate.apply(copy.deepcopy(self.event), now=20))
        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(sum(r["ok"] for r in results), 1)
        self.assertEqual(self.gate.record_count(), 1)

    def test_bad_witness_and_unknown_event(self):
        event = copy.deepcopy(self.event)
        event["witness_ref"] = "fabricated"
        self.assertEqual(self.gate.apply(event, now=20)["code"], "trusted_witness")
        self.assertEqual(self.gate.apply({}, now=20)["code"], "wrong_context")
        self.assertEqual(self.gate.record_count(), 0)


if __name__ == "__main__":
    unittest.main()
