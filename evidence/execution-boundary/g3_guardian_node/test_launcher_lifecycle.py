"""Docker-free controls for first-start failure and persistent restart policy.

These exercise launcher lifecycle decisions, not kernel/effect enforcement.
No Docker daemon or running node is contacted.
"""
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("guardian_launcher",
    Path(__file__).with_name("launcher.py"))
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


def owned(bundle="reviewed", running=True):
    return {"Config": {"Labels": {launcher.ROLE: "guardian-node",
                                   launcher.BUNDLE: bundle}},
            "State": {"Running": running},
            "HostConfig": {"RestartPolicy": {"Name": "no"}}}


class FirstStartLifecycleTests(unittest.TestCase):
    def test_remote_context_cannot_pass_local_socket_check(self):
        values = [SimpleNamespace(stdout="remote"), SimpleNamespace(stdout=json.dumps([
            {"Endpoints": {"docker": {"Host": "ssh://remote.example"}}}]))]
        with patch.object(launcher, "PINNED_CONTEXT", None), \
             patch.object(launcher, "docker", side_effect=values) as docker, \
             patch.dict(os.environ, {"DOCKER_HOST": "unix:///local-looking.sock"}):
            with self.assertRaisesRegex(RuntimeError, "local Docker socket"):
                launcher.local_context()
        self.assertEqual(docker.call_count, 2)

    def test_selected_local_context_is_explicit_on_every_daemon_call(self):
        result = SimpleNamespace(returncode=0, stdout="", stderr="")
        with patch.object(launcher, "PINNED_CONTEXT", "desktop-linux"), \
             patch.object(launcher.shutil, "which", return_value="/docker"), \
             patch.object(launcher.subprocess, "run", return_value=result) as run, \
             patch.dict(os.environ, {"DOCKER_HOST": "tcp://remote.example:2375",
                                    "DOCKER_CONTEXT": "remote"}):
            launcher.docker("container", "inspect", launcher.CONTAINER)
        self.assertEqual(run.call_args.args[0], ["/docker", "--context", "desktop-linux",
            "container", "inspect", launcher.CONTAINER])

    def test_failed_initialization_stops_own_node_and_retains_state(self):
        seen = []
        def fake_docker(*args, **kwargs):
            seen.append(args)
            return SimpleNamespace(returncode=0, stdout="import failed", stderr="")
        with patch.object(launcher, "node_container", side_effect=[None, owned()]), \
             patch.object(launcher, "ensure_image", return_value="reviewed-image"), \
             patch.object(launcher, "ensure_volume"), \
             patch.object(launcher, "docker", side_effect=fake_docker), \
             patch.object(launcher, "run_control", side_effect=RuntimeError("not ready")):
            with self.assertRaisesRegex(RuntimeError, "not ready: import failed"):
                launcher.start({"engine_source_commit": "pinned"}, "reviewed")
        run = next(args for args in seen if args[0] == "run")
        self.assertEqual(run[run.index("--restart") + 1], "no")
        self.assertIn(("update", "--restart", "no", launcher.CONTAINER), seen)
        self.assertIn(("stop", "--time", "12", launcher.CONTAINER), seen)
        self.assertNotIn(("update", "--restart", "unless-stopped", launcher.CONTAINER), seen)
        self.assertFalse(any(args[0] in {"rm", "volume"} for args in seen))

    def test_persistence_enabled_only_after_ready_status(self):
        order = []
        def fake_docker(*args, **kwargs):
            order.append(args[0])
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        def ready(*args, **kwargs):
            order.append("ready")
            return {"ready": True, "held": True}
        with patch.object(launcher, "node_container", return_value=None), \
             patch.object(launcher, "ensure_image", return_value="reviewed-image"), \
             patch.object(launcher, "ensure_volume"), \
             patch.object(launcher, "docker", side_effect=fake_docker), \
             patch.object(launcher, "run_control", side_effect=ready):
            result = launcher.start({"engine_source_commit": "pinned"}, "reviewed")
        self.assertTrue(result["held"])
        self.assertEqual(order, ["run", "ready", "update"])

    def test_existing_different_bundle_is_never_replaced(self):
        with patch.object(launcher, "node_container", return_value=owned("older")), \
             patch.object(launcher, "docker") as docker:
            with self.assertRaisesRegex(RuntimeError, "another bundle"):
                launcher.start({"engine_source_commit": "pinned"}, "reviewed")
        docker.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
