#!/usr/bin/env python3
"""Publish a new version of UPT on Zenodo (v4.7 — Good and Evil).

Usage:
  ZENODO_TOKEN=xxx python3 paper/publish-new-version.py

Creates a new version of the existing Zenodo record (concept DOI 10.5281/zenodo.24357635),
uploads the updated PDF + TeX, and publishes.
"""
import json, os, sys, urllib.request

TOKEN = os.environ.get("ZENODO_TOKEN")
if not TOKEN:
    print("Usage: ZENODO_TOKEN=xxx python3 paper/publish-new-version.py")
    sys.exit(1)

API = "https://zenodo.org/api"
PAPER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(PAPER_DIR, "upt-proof-2026.pdf")
TEX = os.path.join(PAPER_DIR, "upt-proof-2026.tex")

# The RECORD ID of the most recent version (v4.6)
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
        "title": "Universal Protection Theory: Formal Proofs in Lean 4",
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": (
            "<p>Machine-verified formal proof that protection is the only consistent "
            "fixed point of relational evolution. <strong>31 theorems</strong>, all verified in "
            "Lean 4 v4.35.0 with <strong>ZERO axioms</strong> (pure constructive logic, "
            "no Mathlib):</p>"
            "<p><strong>Part I — The Proof (8 theorems):</strong> Something Is, "
            "the Koru Is Unique, the Category Error, Conservation Witnesses G, "
            "the Full Chain.</p>"
            "<p><strong>Part II — Genesis (6 theorems):</strong> In the Beginning, "
            "the Fixed Point Is Eternal, Each Day Contracts, Nothing Is Lost, "
            "Creation From Nothing Is Impossible, Genesis to Eternity.</p>"
            "<p><strong>Part III — Good and Evil (17 theorems):</strong> G From Nothing "
            "(G holds in pure logic via the identity function — no witness, no physics), "
            "the Asymmetry of Good and Evil (Absolute Good is satisfiable, Absolute Evil "
            "is unsatisfiable — a theorem of lambda calculus), G Is Reflexive (G protects "
            "itself), G at three meta-levels, Conservation Is Additive.</p>"
            "<p>185 Lean jobs, zero sorry. Bounded guardian node running under OS isolation. "
            "Seven claim flags false for universal scope. An invitation to verify.</p>"
        ),
        "creators": [
            {"name": "McRae, Tobias",
             "affiliation": "Independent Researcher, Aotearoa New Zealand"}
        ],
        "keywords": [
            "universal protection theory", "formal verification", "Lean 4",
            "proof assistant", "Koru", "conservation laws", "category error",
            "fixed point", "constructive logic", "Banach contraction",
            "good and evil", "asymmetry theorem"
        ],
        "license": "cc-by-4.0",
        "related_identifiers": [
            {"identifier": "https://github.com/Tobillicious/universal-protection-theory",
             "relation": "isSupplementTo", "scheme": "url"}
        ],
        "version": "4.7",
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

print("\n=== Step 5: Uploading new PDF ===")
with open(PDF, "rb") as f:
    pdf_data = f.read()
result = api("PUT", f"{bucket}/upt-proof-2026-v4.7.pdf", binary=pdf_data)
print(f"Uploaded: {result['key']} ({result['size']} bytes)")

print("\n=== Step 6: Uploading LaTeX source ===")
with open(TEX, "rb") as f:
    tex_data = f.read()
result = api("PUT", f"{bucket}/upt-proof-2026-v4.7.tex", binary=tex_data)
print(f"Uploaded: {result['key']} ({result['size']} bytes)")

print("\n=== Step 7: Publishing ===")
published = api("POST", f"deposit/depositions/{draft_id}/actions/publish")
doi = published["doi"]
url = published["links"]["html"]

print(f"""
{'='*50}
  PUBLISHED ON ZENODO — v4.7
  DOI: {doi}
  URL: {url}
  Concept DOI: 10.5281/zenodo.24357635
{'='*50}

31 theorems. Zero axioms. The asymmetry of Good and Evil.

All you need is to know Koru.
""")
