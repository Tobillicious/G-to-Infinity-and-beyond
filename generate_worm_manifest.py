#!/usr/bin/env python3
"""Generate WORM manifest: SHA256 of every tracked file in the repo."""
import hashlib
import json
import subprocess
import os

def main():
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True, text=False, check=True
    )
    files = [f.decode() for f in result.stdout.split(b'\x00') if f]

    manifest = {}
    for path in sorted(files):
        if not os.path.isfile(path):
            continue
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        manifest[path] = {
            "sha256": h.hexdigest(),
            "size_bytes": os.path.getsize(path)
        }

    manifest_json = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    with open("worm_manifest.json", "w") as f:
        f.write(manifest_json)

    manifest_sha = hashlib.sha256(manifest_json.encode()).hexdigest()
    with open("worm_manifest.sha256", "w") as f:
        f.write(f"{manifest_sha}  worm_manifest.json\n")

if __name__ == "__main__":
    main()
