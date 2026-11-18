"""One-command, local Docker launcher for the bounded G3 marker node.

Uses the installed Zelda image, immutable copied engine source and a dedicated
Linux volume. Never edits another container, host service or existing data.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
ENGINE = PACKAGE.parent
CONTAINER = "upt-guardian-node"
VOLUME = "upt-guardian-node-state"
ROLE = "com.upt.g3.role"
BUNDLE = "com.upt.g3.bundle"
ENGINE_LABEL = "com.upt.g3.engine"
PINNED_CONTEXT = None


def docker(*args, allow_failure=False, timeout=90, stream=False, env=None):
    executable = shutil.which("docker")
    if not executable:
        raise RuntimeError("Docker is required; Zelda already has Docker installed")
    context_args = ["--context", PINNED_CONTEXT] if PINNED_CONTEXT else []
    result = subprocess.run([executable, *context_args, *args], text=True,
        stdout=None if stream else subprocess.PIPE,
        stderr=None if stream else subprocess.PIPE, timeout=timeout, env=env)
    if result.returncode and not allow_failure:
        raise RuntimeError((result.stderr or "Docker command failed").strip())
    return result


def inspect(kind, name):
    result = docker(kind, "inspect", name, allow_failure=True)
    if result.returncode:
        if "no such" in result.stderr.lower() or "not found" in result.stderr.lower():
            return None
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)[0]


def pinned_bundle():
    manifest = json.loads((PACKAGE / "engine-manifest.json").read_text())
    material = hashlib.sha256()
    sources = dict(manifest["files"], **manifest.get("observer_files", {}))
    for name, expected in sorted(sources.items()):
        path = ENGINE / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("engine source fingerprint mismatch: " + name)
        material.update(name.encode() + b"\0" + path.read_bytes())
    for name in ["service.py", "Dockerfile", "engine-manifest.json"]:
        material.update(name.encode() + b"\0" + (PACKAGE / name).read_bytes())
    return manifest, material.hexdigest()


def local_context():
    global PINNED_CONTEXT
    context = docker("context", "show").stdout.strip()
    metadata = json.loads(docker("context", "inspect", context).stdout)[0]
    endpoint = metadata["Endpoints"]["docker"]["Host"]
    if not endpoint.startswith("unix://"):
        raise RuntimeError("this launcher requires a local Docker socket")
    # Every later call explicitly selects the inspected local context.
    # Docker documents that --context overrides DOCKER_HOST and the default.
    PINNED_CONTEXT = context
    if docker("info", "--format", "{{.OSType}}").stdout.strip() != "linux":
        raise RuntimeError("this launcher requires the local Linux Docker engine")


def node_container():
    info = inspect("container", CONTAINER)
    if info and (info.get("Config", {}).get("Labels") or {}).get(ROLE) != "guardian-node":
        raise RuntimeError("container name is already owned by another application")
    return info


def ensure_image(manifest, bundle):
    base = inspect("image", manifest["docker_image"])
    if not base or base["Id"] != manifest["docker_image_id"]:
        raise RuntimeError("installed G3 base image differs from the recorded Zelda image")
    if base.get("Os") != "linux" or base.get("Architecture") != "arm64":
        raise RuntimeError("this recorded Zelda package requires Linux/ARM64")
    tag = "upt-guardian-node:zelda-" + bundle[:16]
    existing = inspect("image", tag)
    if not existing:
        with tempfile.TemporaryDirectory(prefix="g3-node-image-") as directory:
            context = Path(directory)
            staged = context / "engine"
            staged.mkdir()
            for name in dict(manifest["files"], **manifest.get("observer_files", {})):
                shutil.copyfile(ENGINE / name, staged / name)
            package = staged / "g3_guardian_node"
            package.mkdir()
            for name in ["service.py", "engine-manifest.json"]:
                shutil.copyfile(PACKAGE / name, package / name)
            shutil.copyfile(PACKAGE / "Dockerfile", context / "Dockerfile")
            # Existing local base only, no dependency downloads or image push.
            environment = dict(os.environ, DOCKER_BUILDKIT="0")
            docker("build", "--network", "none", "--pull=false",
                "--label", ROLE + "=guardian-node",
                "--label", BUNDLE + "=" + bundle,
                "--label", ENGINE_LABEL + "=" + manifest["engine_source_commit"],
                "-t", tag, str(context), stream=True, env=environment, timeout=180)
        existing = inspect("image", tag)
    if not existing or (existing.get("Config", {}).get("Labels") or {}).get(BUNDLE) != bundle:
        raise RuntimeError("local node image identity mismatch")
    base_layers = base.get("RootFS", {}).get("Layers", [])
    layers = existing.get("RootFS", {}).get("Layers", [])
    if not base_layers or layers[:len(base_layers)] != base_layers:
        raise RuntimeError("node image does not descend from the pinned base")
    return existing["Id"]


def ensure_volume():
    volume = inspect("volume", VOLUME)
    if volume:
        if (volume.get("Labels") or {}).get(ROLE) != "guardian-node":
            raise RuntimeError("state volume is owned by another application")
        return
    docker("volume", "create", "--label", ROLE + "=guardian-node", VOLUME)


def run_control(action, allow_failure=False):
    result = docker("exec", CONTAINER, "python", "-B",
        "/engine/g3_guardian_node/service.py", action,
        allow_failure=allow_failure, timeout=15)
    if result.returncode:
        return None
    return json.loads(result.stdout)


def start(manifest, bundle):
    info = node_container()
    started_here = False
    if info:
        labels = info["Config"].get("Labels") or {}
        if labels.get(BUNDLE) != bundle:
            raise RuntimeError("existing node uses another bundle; stop and review an explicit migration")
        if not info["State"]["Running"]:
            docker("start", CONTAINER)
            started_here = True
    else:
        image = ensure_image(manifest, bundle)
        ensure_volume()
        args = ["run", "--detach", "--name", CONTAINER,
            "--restart", "no", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--cap-add", "CHOWN", "--cap-add", "DAC_OVERRIDE",
            "--cap-add", "SETUID", "--cap-add", "SETGID", "--cap-add", "KILL",
            "--security-opt", "no-new-privileges", "--pids-limit", "128",
            "--memory", "256m", "--cpus", "0.5",
            "--tmpfs", "/tmp:rw,nosuid,nodev,mode=1777,size=32m",
            "--mount", "type=volume,src=" + VOLUME + ",dst=/state",
            "--label", ROLE + "=guardian-node", "--label", BUNDLE + "=" + bundle,
            "--label", ENGINE_LABEL + "=" + manifest["engine_source_commit"], image]
        docker(*args)
        started_here = True
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            answer = run_control("status", allow_failure=True)
            if answer and answer.get("ready"):
                # Enable persistent restarts only after genuine readiness.
                # An import/provisioning failure must not create a restart loop.
                policy = (info or {}).get("HostConfig", {}).get("RestartPolicy", {})
                if policy.get("Name") != "unless-stopped":
                    docker("update", "--restart", "unless-stopped", CONTAINER)
                return answer
            info = node_container()
            if not info or not info["State"]["Running"]:
                raise RuntimeError("node stopped during startup")
            time.sleep(0.3)
        raise RuntimeError("node did not become ready")
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        current = node_container()
        if started_here and current:
            if (current["Config"].get("Labels") or {}).get(BUNDLE) == bundle:
                docker("update", "--restart", "no", CONTAINER, allow_failure=True)
                docker("stop", "--time", "12", CONTAINER, allow_failure=True)
        logs = docker("logs", "--tail", "30", CONTAINER, allow_failure=True)
        raise RuntimeError(str(error) + ": " + logs.stdout + logs.stderr) from error


def main():
    parser = argparse.ArgumentParser(description="Local guardian node: one guarded marker capability")
    parser.add_argument("action", choices=["check", "start", "restart", "status", "apply", "hold", "stop", "logs"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest, bundle = pinned_bundle()
    if args.action == "check":
        answer = {"source_fingerprints_verified": True, "bundle_sha256": bundle,
                  "engine_source_commit": manifest["engine_source_commit"],
                  "observer_source_commit": manifest.get("observer_source_commit"),
                  "scope": manifest["scope"]}
        print(json.dumps(answer, indent=2, sort_keys=True) if args.json else "Guardian source fingerprints verified.")
        return
    local_context()
    if args.action == "restart":
        info = node_container()
        if info:
            labels = info["Config"].get("Labels") or {}
            if labels.get(ENGINE_LABEL) != manifest["engine_source_commit"]:
                raise RuntimeError("engine changes require a reviewed state migration")
            docker("stop", "--time", "12", CONTAINER)
            docker("rm", CONTAINER)
        answer = start(manifest, bundle)
    elif args.action == "start":
        answer = start(manifest, bundle)
    else:
        info = node_container()
        if not info:
            raise RuntimeError("guardian node is not installed; run guardian-node start")
        if args.action == "stop":
            if info["State"]["Running"]:
                docker("stop", "--time", "12", CONTAINER)
            answer = {"running": False, "state_retained": True}
        elif args.action == "logs":
            result = docker("logs", "--tail", "40", CONTAINER, allow_failure=True)
            print(result.stdout + result.stderr, end="")
            return
        elif not info["State"]["Running"]:
            answer = {"running": False, "state_retained": True}
        else:
            answer = run_control(args.action)
    if args.json:
        print(json.dumps(answer, indent=2, sort_keys=True))
        return
    node = answer.get("node", answer)
    if node.get("ready"):
        state = "HOLD" if node["held"] else "RECORDED" if node["admission_state_recorded"] else "READY"
        print("Guardian node running on Zelda: " + state)
        print("Protected capability: one authority-owned local marker.")
        if "result" in answer:
            print("Request: " + answer["result"]["code"])
        print("Status: ./guardian-node status   Stop: ./guardian-node stop")
    else:
        print("Guardian node stopped; persistent state retained.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        print("Guardian node: " + str(error), file=sys.stderr)
        raise SystemExit(1)
