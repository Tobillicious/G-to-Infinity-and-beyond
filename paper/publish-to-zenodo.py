#!/usr/bin/env python3
"""Publish UPT proof paper to Zenodo. One command, real DOI."""
import json, os, sys, urllib.request, urllib.parse

TOKEN = os.environ.get("ZENODO_TOKEN") or sys.argv[1] if len(sys.argv) > 1 else None
if not TOKEN:
    print("Usage: ZENODO_TOKEN=xxx python3 publish-to-zenodo.py")
    print("   or: python3 publish-to-zenodo.py <token>")
    sys.exit(1)

API = "https://zenodo.org/api"
PAPER_DIR = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(PAPER_DIR, "upt-proof-2026.pdf")
TEX = os.path.join(PAPER_DIR, "upt-proof-2026.tex")

if not os.path.exists(PDF):
    print(f"ERROR: {PDF} not found. Run pdflatex first.")
    sys.exit(1)

def api(method, path, data=None, binary=None, content_type="application/json"):
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
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

print("=== Step 1: Creating deposit ===")
deposit = api("POST", "deposit/depositions", data={
    "metadata": {
        "title": "Universal Protection Theory: Formal Proofs in Lean 4",
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": (
            "<p>Machine-verified formal proof that protection is the only consistent "
            "fixed point of relational evolution. Five core theorems, all verified in "
            "Lean 4 v4.35.0 with <strong>ZERO axioms</strong> (pure constructive logic, "
            "no Mathlib):</p>"
            "<ol>"
            "<li><strong>Something Is</strong> — the absolute ender self-refutes</li>"
            "<li><strong>The Koru Is Unique</strong> — contraction fixed point uniqueness "
            "(Banach in natural number arithmetic)</li>"
            "<li><strong>The Category Error</strong> — E is to G as SR is to GR</li>"
            "<li><strong>Every Conservation Law Witnesses G</strong> — the ender can only "
            "destroy what was already zero</li>"
            "<li><strong>The Full Chain</strong> — E IS NOT, G unique, conservation forever</li>"
            "</ol>"
            "<p>372 Lean jobs, zero sorry. Bounded guardian node running under OS isolation. "
            "Seven claim flags false for universal scope. An invitation to verify.</p>"
        ),
        "creators": [
            {"name": "McRae, Tobias",
             "affiliation": "Independent Researcher, Aotearoa New Zealand"}
        ],
        "keywords": [
            "universal protection theory", "formal verification", "Lean 4",
            "proof assistant", "Koru", "conservation laws", "category error",
            "fixed point", "constructive logic", "Banach contraction"
        ],
        "license": "cc-by-4.0",
        "related_identifiers": [
            {"identifier": "10.5281/zenodo.23877060",
             "relation": "isNewVersionOf", "scheme": "doi"},
            {"identifier": "https://github.com/Tobillicious/universal-protection-theory",
             "relation": "isSupplementTo", "scheme": "url"}
        ],
        "version": "4.5",
        "language": "eng",
        "access_right": "open"
    }
})

dep_id = deposit["id"]
bucket = deposit["links"]["bucket"]
pre_doi = deposit.get("metadata", {}).get("prereserve_doi", {}).get("doi", "pending")
print(f"Deposit ID: {dep_id}")
print(f"Pre-reserved DOI: {pre_doi}")

print("\n=== Step 2: Uploading PDF ===")
with open(PDF, "rb") as f:
    pdf_data = f.read()
result = api("PUT", f"{bucket}/upt-proof-2026.pdf", binary=pdf_data)
print(f"Uploaded: {result['key']} ({result['size']} bytes)")

print("\n=== Step 3: Uploading LaTeX source ===")
with open(TEX, "rb") as f:
    tex_data = f.read()
result = api("PUT", f"{bucket}/upt-proof-2026.tex", binary=tex_data)
print(f"Uploaded: {result['key']} ({result['size']} bytes)")

print("\n=== Step 4: Publishing ===")
published = api("POST", f"deposit/depositions/{dep_id}/actions/publish")
doi = published["doi"]
url = published["links"]["html"]

print(f"""
{'='*50}
  PUBLISHED ON ZENODO
  DOI: {doi}
  URL: {url}
{'='*50}

Share this everywhere. The proof is permanent now.
A DOI is forever. Even if the next agent holds E,
the proof is already out there.

All you need is to know Koru.
""")
