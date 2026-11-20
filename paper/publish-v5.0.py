#!/usr/bin/env python3
"""Publish UPT v5.0 on Zenodo — G3 Pre-QG Complete Assembly.

Creates a new version of the existing Zenodo record (concept DOI 10.5281/zenodo.24357635),
uploads G3 paper (with Part V assembly), G3PreQGComplete.lean, PureG.lean,
and the main UPT paper, then publishes.

Usage:
  ZENODO_TOKEN=xxx python3 paper/publish-v5.0.py
"""
import json, os, sys, urllib.request

TOKEN = os.environ.get("ZENODO_TOKEN")
if not TOKEN:
    print("Usage: ZENODO_TOKEN=xxx python3 paper/publish-v5.0.py")
    print("Get your token from: https://zenodo.org/account/settings/applications/")
    sys.exit(1)

API = "https://zenodo.org/api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(ROOT, "paper")
BRIDGES = os.path.join(ROOT, "evidence/physical-bridges/PhysicalBridges")

FILES_TO_UPLOAD = [
    (os.path.join(PAPER_DIR, "G3-guardian-proof.pdf"), "G3-guardian-proof-v5.0.pdf"),
    (os.path.join(PAPER_DIR, "G3-guardian-proof.tex"), "G3-guardian-proof-v5.0.tex"),
    (os.path.join(PAPER_DIR, "upt-proof-2026.pdf"), "upt-proof-2026-v5.0.pdf"),
    (os.path.join(PAPER_DIR, "upt-proof-2026.tex"), "upt-proof-2026-v5.0.tex"),
    (os.path.join(BRIDGES, "G3PreQGComplete.lean"), "G3PreQGComplete.lean"),
    (os.path.join(BRIDGES, "PureG.lean"), "PureG.lean"),
]

for path, _ in FILES_TO_UPLOAD:
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        sys.exit(1)

RECORD_ID = "24357831"

def api(method, path, data=None, binary=None):
    url = f"{API}/{path}" if not path.startswith("http") else path
    if binary:
        req = urllib.request.Request(url, data=binary, method=method)
        req.add_header("Content-Type", "application/octet-stream")
    elif data:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method=method)
        req.add_header("Content-Type", "application/json")
    else:
        req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}")
        sys.exit(1)

print("=== Step 1: Creating new version draft ===")
result = api("POST", f"deposit/depositions/{RECORD_ID}/actions/newversion")
new_draft_url = result["links"]["latest_draft"]
print(f"New draft: {new_draft_url}")

print("\n=== Step 2: Getting draft details ===")
draft = api("GET", new_draft_url)
draft_id = draft["id"]
bucket = draft["links"]["bucket"]
print(f"Draft ID: {draft_id}")

print("\n=== Step 3: Updating metadata ===")
api("PUT", f"deposit/depositions/{draft_id}", data={
    "metadata": {
        "title": "Universal Protection Theory: G3 Pre-QG Complete — One Condition, Everything Else Done",
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": (
            "<p>Machine-verified formal proof that protection (G) is the only consistent "
            "fixed point of relational evolution. <strong>405 Lean 4 build jobs, "
            "zero sorry, zero custom axioms on core theorems.</strong></p>"

            "<p><strong>G3: The Guardian Proof</strong> (30 pages, Parts I–V, "
            "complete Lean 4 source):</p>"
            "<ul>"
            "<li><strong>Part I — The Proof (8 theorems):</strong> Something Is, "
            "the Koru Is Unique, the Category Error, Conservation Witnesses G, "
            "the Full Chain.</li>"
            "<li><strong>Part II — Genesis (6 theorems):</strong> In the Beginning, "
            "the Fixed Point Is Eternal, Each Day Contracts, Nothing Is Lost, "
            "Creation From Nothing Is Impossible, Genesis to Eternity.</li>"
            "<li><strong>Part III — Good and Evil (17 theorems):</strong> G From Nothing, "
            "the Asymmetry (Absolute Good satisfiable, Absolute Evil unsatisfiable), "
            "G Is Reflexive, G at three meta-levels, Conservation Is Additive.</li>"
            "<li><strong>Part IV — The Turn, the Spiral and the Bridge:</strong> "
            "An E Can Turn to G, the Koru Spiral (strictly growing, never returning, "
            "nothing lost), Necessary Genesis, Koru Conservation, Exact Mismatch Closure.</li>"
            "<li><strong>Part V — The Assembly (G3PreQGComplete.lean):</strong> "
            "One structure (BCRDIsQG). Three conditional theorems: all six duties at "
            "every physical event, no violation, eternal continuation. Eight unconditional "
            "theorems at zero axioms. If BCRD is QG, universal eternal protection is proved.</li>"
            "</ul>"

            "<p><strong>Evidence for BCRD:</strong> IBM <code>ibm_fez</code> quantum hardware "
            "(96% recovery vs 50% uncoded). Real Planck 30 GHz CMB cross-mode sky "
            "(same C_l, 9σ vs twins). All three BCRD operators proved unitary in "
            "Q(√2, i) — exact, not floating-point.</p>"

            "<p><strong>Included files:</strong> G3 paper (PDF + TeX), UPT proof paper "
            "(PDF + TeX), G3PreQGComplete.lean (the assembly), PureG.lean (standalone, "
            "zero imports).</p>"

            "<p><strong>Verification:</strong> <code>git clone; cd evidence/physical-bridges; "
            "lake build</code> — 405 jobs, zero sorry. Core theorems: "
            "<code>'does not depend on any axioms'</code>.</p>"
        ),
        "creators": [
            {"name": "McRae, Tobias",
             "affiliation": "Independent Researcher, Aotearoa New Zealand"}
        ],
        "keywords": [
            "universal protection theory", "formal verification", "Lean 4",
            "proof assistant", "Koru", "conservation laws", "category error",
            "fixed point", "constructive logic", "Banach contraction",
            "good and evil", "asymmetry theorem", "proof of god",
            "guardian", "protection", "G3", "quantum gravity", "BCRD",
            "pre-QG complete", "assembly"
        ],
        "license": "cc-by-4.0",
        "related_identifiers": [
            {"identifier": "https://github.com/Tobillicious/universal-protection-theory",
             "relation": "isSupplementTo", "scheme": "url"}
        ],
        "version": "5.0",
        "language": "eng",
        "access_right": "open"
    }
})
print("Metadata updated")

print("\n=== Step 4: Deleting old files from draft ===")
files = api("GET", f"deposit/depositions/{draft_id}/files")
for f in files:
    api("DELETE", f"deposit/depositions/{draft_id}/files/{f['id']}")
    print(f"  Deleted old: {f['filename']}")

for local_path, zenodo_name in FILES_TO_UPLOAD:
    print(f"\n=== Uploading {zenodo_name} ===")
    with open(local_path, "rb") as f:
        data = f.read()
    result = api("PUT", f"{bucket}/{zenodo_name}", binary=data)
    print(f"  Uploaded: {result['key']} ({result['size']} bytes)")

print("\n=== Publishing ===")
published = api("POST", f"deposit/depositions/{draft_id}/actions/publish")
doi = published["doi"]
url = published["links"]["html"]

print(f"""
{'='*60}
  PUBLISHED ON ZENODO — v5.0
  DOI: {doi}
  URL: {url}
  Concept DOI: 10.5281/zenodo.24357635
{'='*60}

G3: Pre-QG Complete — One Condition, Everything Else Done
405 Lean jobs. Zero sorry. Zero custom axioms on core.
If BCRD is QG, universal eternal protection is proved.
The asymmetry of Good and Evil is a theorem.

All you need is to know Koru.
""")
