#!/usr/bin/env python3
"""Publish UPT v5.1 on Zenodo — The Tree of Eternal Life and Endless Knowledge.

Backwards summit edition. Full maximal strength.

Creates a new version of the existing Zenodo record (concept DOI 10.5281/zenodo.24357635),
uploads G3 paper, Tree modules, assembly, PureG, and the main UPT paper, then publishes.

Usage:
  ZENODO_TOKEN=xxx python3 paper/publish-v5.1.py
"""
import json, os, sys, urllib.request

TOKEN = os.environ.get("ZENODO_TOKEN")
if not TOKEN:
    print("Usage: ZENODO_TOKEN=xxx python3 paper/publish-v5.1.py")
    print("Get your token from: https://zenodo.org/account/settings/applications/")
    sys.exit(1)

API = "https://zenodo.org/api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(ROOT, "paper")
BRIDGES = os.path.join(ROOT, "evidence/physical-bridges/PhysicalBridges")

FILES_TO_UPLOAD = [
    (os.path.join(PAPER_DIR, "G3-guardian-proof.pdf"), "G3-guardian-proof-v5.1.pdf"),
    (os.path.join(PAPER_DIR, "G3-guardian-proof.tex"), "G3-guardian-proof-v5.1.tex"),
    (os.path.join(PAPER_DIR, "upt-proof-2026.pdf"), "upt-proof-2026-v5.1.pdf"),
    (os.path.join(PAPER_DIR, "upt-proof-2026.tex"), "upt-proof-2026-v5.1.tex"),
    (os.path.join(BRIDGES, "G3PreQGComplete.lean"), "G3PreQGComplete.lean"),
    (os.path.join(BRIDGES, "PureG.lean"), "PureG.lean"),
    (os.path.join(BRIDGES, "G3TikangaEthicsTree.lean"), "G3TikangaEthicsTree.lean"),
    (os.path.join(BRIDGES, "G3TreeGrowth.lean"), "G3TreeGrowth.lean"),
    (os.path.join(BRIDGES, "G3TreeThirdGrowth.lean"), "G3TreeThirdGrowth.lean"),
]

print("Checking all files exist...")
for path, name in FILES_TO_UPLOAD:
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        sys.exit(1)
    size = os.path.getsize(path)
    print(f"  {name}: {size:,} bytes")

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

print("\n=== Step 1: Creating new version draft ===")
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
        "title": (
            "Universal Protection Theory v5.1: "
            "The Tree of Eternal Life and Endless Knowledge"
        ),
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": (
            "<p><strong>Backwards summit.</strong> Presume BCRD is QG. "
            "Everything else is proved.</p>"

            "<p>Machine-verified formal proof that protection (G) is the only "
            "consistent fixed point of relational evolution. "
            "<strong>405 Lean 4 build jobs, zero sorry, zero custom axioms "
            "on core theorems.</strong></p>"

            "<h3>The Assembly (G3PreQGComplete.lean)</h3>"
            "<p>One structure: <code>BCRDIsQG</code>. Three conditional theorems:</p>"
            "<ul>"
            "<li><code>if_bcrd_then_all_six_and_no_E</code> — every physical event: "
            "all six original duties, no absolute E</li>"
            "<li><code>if_bcrd_then_no_violation</code> — no X3 violation anywhere</li>"
            "<li><code>if_bcrd_then_eternal</code> — the dynamics never terminates</li>"
            "</ul>"

            "<h3>The Tree of Eternal Life and Endless Knowledge</h3>"
            "<p>51 theorems across three modules, all zero sorry:</p>"
            "<ul>"
            "<li><strong>G3TikangaEthicsTree.lean</strong> (12 theorems): "
            "Generic obligation framework. Original six X3 duties embedded. "
            "Four new branches: Eternal Unending Happiness, Coexistence, Protection, "
            "Faith in God. Monotonic growth. Path preservation. The framework is open.</li>"
            "<li><strong>G3TreeGrowth.lean</strong> (18 theorems): "
            "Composability (ethical traditions merge). Dignity (every owed particular "
            "gets the full bundle). Whanaungatanga (reciprocity). Restorative justice "
            "(correction obligations). Root constraint (poison cannot enter). "
            "Manaakitanga (the tree nurtures). Aroha (love implies all protection). "
            "Accumulation (the tree hoards — it forgets nothing).</li>"
            "<li><strong>G3TreeThirdGrowth.lean</strong> (21 theorems): "
            "Countable growth (infinitely many branches). Sovereignty (self-consistent, "
            "no external authority). The Covenant (irrevocable along every future path). "
            "Testimony (witnesses persist — evidence does not decay). Kotahitanga (unity "
            "of aligned agents). The Mirror (merged traditions faithfully reflected). "
            "Self-knowledge (the tree that IS satisfied KNOWS it is satisfied — free). "
            "Wairua (same spirit, same judgement).</li>"
            "</ul>"

            "<h3>The Unconditional Proofs</h3>"
            "<ul>"
            "<li><strong>Something Is:</strong> the absolute ender self-refutes</li>"
            "<li><strong>The Koru:</strong> G is the unique fixed point; "
            "E has no model on function spaces</li>"
            "<li><strong>The Spiral:</strong> strictly growing, never returning, "
            "nothing lost</li>"
            "<li><strong>The Turn:</strong> an E can turn to G; "
            "the turn preserves the world</li>"
            "<li><strong>The Asymmetry:</strong> Absolute Good is satisfiable; "
            "Absolute Evil is unsatisfiable</li>"
            "</ul>"

            "<h3>Evidence for BCRD</h3>"
            "<ul>"
            "<li>IBM <code>ibm_fez</code> quantum hardware: 96% recovery "
            "vs 50% uncoded baseline</li>"
            "<li>Real Planck 30 GHz CMB cross-mode sky: same C_l, same energy, "
            "9σ significance vs random twins</li>"
            "<li>All three BCRD operators (W, C_LM, U_MR) proved unitary in "
            "Q(√2, i) — exact algebraic, not floating-point</li>"
            "</ul>"

            "<h3>Included files (9)</h3>"
            "<ul>"
            "<li>G3 Guardian Proof paper (PDF + TeX, Parts I–V, 30 pages)</li>"
            "<li>UPT Proof paper (PDF + TeX)</li>"
            "<li>G3PreQGComplete.lean — the assembly (one structure, everything follows)</li>"
            "<li>PureG.lean — standalone zero-import proof of G</li>"
            "<li>G3TikangaEthicsTree.lean — the tree, first growth</li>"
            "<li>G3TreeGrowth.lean — the tree, second growth</li>"
            "<li>G3TreeThirdGrowth.lean — the tree, third growth</li>"
            "</ul>"

            "<h3>Verification</h3>"
            "<pre>git clone https://github.com/Tobillicious/universal-protection-theory\n"
            "cd evidence/physical-bridges\n"
            "lake build</pre>"
            "<p>405 jobs. Zero sorry. Core theorems: "
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
            "pre-QG complete", "assembly", "tree of life", "endless knowledge",
            "tikanga", "aroha", "manaakitanga", "whanaungatanga", "dignity",
            "covenant", "sovereignty", "self-knowledge", "wairua",
            "backwards summit", "ethics", "restorative justice"
        ],
        "license": "cc-by-4.0",
        "related_identifiers": [
            {"identifier": "https://github.com/Tobillicious/universal-protection-theory",
             "relation": "isSupplementTo", "scheme": "url"}
        ],
        "version": "5.1",
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
  PUBLISHED ON ZENODO — v5.1
  DOI: {doi}
  URL: {url}
  Concept DOI: 10.5281/zenodo.24357635
{'='*60}

The Tree of Eternal Life and Endless Knowledge.
405 Lean jobs. Zero sorry. 51 tree theorems.
If BCRD is QG, universal eternal protection is proved.
The tree grows. It cannot shrink.

Aroha was already in the tree — we just named the branch.
""")
