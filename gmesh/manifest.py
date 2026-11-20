"""WORM manifest integrity checker.

Loads worm_manifest.json and worm_manifest.sha256, verifies the manifest
hash, and spot-checks file integrity against stored SHA256 digests.

Reports honestly: "local integrity check", never "universal verification".
"""
import hashlib
import json
import os
import random
from pathlib import Path


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(repo_root):
    manifest_path = Path(repo_root) / "worm_manifest.json"
    sha_path = Path(repo_root) / "worm_manifest.sha256"

    if not manifest_path.exists() or not sha_path.exists():
        return None, "manifest files not found"

    manifest_text = manifest_path.read_text()
    manifest = json.loads(manifest_text)

    stored_line = sha_path.read_text().strip()
    stored_sha = stored_line.split()[0]

    computed_sha = hashlib.sha256(manifest_text.encode()).hexdigest()
    sha_ok = computed_sha == stored_sha

    return manifest, {
        "files_tracked": len(manifest),
        "lean_files": sum(1 for k in manifest if k.endswith(".lean")),
        "manifest_sha256": computed_sha,
        "stored_sha256": stored_sha,
        "manifest_integrity": sha_ok,
    }


def spot_check(repo_root, manifest, n=20):
    files = list(manifest.keys())
    sample = random.sample(files, min(n, len(files)))

    checked = 0
    passed = 0
    failed = []
    missing = []

    for rel_path in sample:
        full = Path(repo_root) / rel_path
        if not full.exists():
            missing.append(rel_path)
            checked += 1
            continue
        actual = _sha256_file(full)
        expected = manifest[rel_path]["sha256"]
        checked += 1
        if actual == expected:
            passed += 1
        else:
            failed.append(rel_path)

    return {
        "files_sampled": checked,
        "passed": passed,
        "failed": failed,
        "missing": missing,
        "integrity": len(failed) == 0 and len(missing) == 0,
    }


def full_report(repo_root):
    manifest, info = load_manifest(repo_root)
    if manifest is None:
        return {"status": "ERROR", "detail": info}

    check = spot_check(repo_root, manifest)

    return {
        "schema": "gmesh-worm-check-v1",
        "status": "VERIFIED_LOCAL" if (info["manifest_integrity"] and check["integrity"]) else "INTEGRITY_MISMATCH",
        "manifest": info,
        "spot_check": check,
        "scope": "local file integrity only — not independent or universal verification",
    }
