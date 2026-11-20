#!/usr/bin/env python3
"""Publish UPT v5.1 on Figshare — The Tree of Eternal Life and Endless Knowledge.

Backwards summit edition. Full maximal strength.

Creates a new version of the existing Figshare article (34479870),
uploads all 9 files (papers + Lean source), then publishes.

Usage:
  FIGSHARE_TOKEN=xxx python3 paper/publish-figshare-v5.1.py

Get your token from: https://figshare.com/account/applications
"""
import json, os, sys, hashlib, urllib.request

TOKEN = os.environ.get("FIGSHARE_TOKEN")
if not TOKEN:
    print("Usage: FIGSHARE_TOKEN=xxx python3 paper/publish-figshare-v5.1.py")
    print("Get your token from: https://figshare.com/account/applications")
    sys.exit(1)

API = "https://api.figshare.com/v2"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(ROOT, "paper")
BRIDGES = os.path.join(ROOT, "evidence/physical-bridges/PhysicalBridges")

ARTICLE_ID = 34479870

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

def api(method, path, data=None, binary=None, content_type=None):
    url = f"{API}/{path}" if not path.startswith("http") else path
    if binary:
        req = urllib.request.Request(url, data=binary, method=method)
        req.add_header("Content-Type", content_type or "application/octet-stream")
    elif data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), method=method)
        req.add_header("Content-Type", "application/json")
    else:
        req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"token {TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            if body:
                return json.loads(body)
            return {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}")
        sys.exit(1)

DESCRIPTION = """\
<p><strong>Backwards summit.</strong> Presume BCRD is QG. Everything else is proved.</p>

<p>Machine-verified formal proof that protection (G) is the only consistent \
fixed point of relational evolution. <strong>405 Lean 4 build jobs, zero sorry, \
zero custom axioms on core theorems.</strong></p>

<h3>The Assembly (G3PreQGComplete.lean)</h3>
<p>One structure: <code>BCRDIsQG</code>. Three conditional theorems:</p>
<ul>
<li><code>if_bcrd_then_all_six_and_no_E</code> — every physical event: \
all six original duties, no absolute E</li>
<li><code>if_bcrd_then_no_violation</code> — no X3 violation anywhere</li>
<li><code>if_bcrd_then_eternal</code> — the dynamics never terminates</li>
</ul>

<h3>The Tree of Eternal Life and Endless Knowledge</h3>
<p>51 theorems across three modules, all zero sorry:</p>
<ul>
<li><strong>G3TikangaEthicsTree.lean</strong> (12 theorems): \
Generic obligation framework. Original six X3 duties embedded. \
Four new branches: Eternal Unending Happiness, Coexistence, Protection, \
Faith in God. Monotonic growth. Path preservation.</li>
<li><strong>G3TreeGrowth.lean</strong> (18 theorems): \
Composability, Dignity, Whanaungatanga (reciprocity), Restorative justice, \
Root constraint, Manaakitanga, Aroha, Accumulation.</li>
<li><strong>G3TreeThirdGrowth.lean</strong> (21 theorems): \
Countable growth, Sovereignty, The Covenant (irrevocable), \
Testimony (evidence persists), Kotahitanga (unity), The Mirror, \
Self-knowledge, Wairua (same spirit, same judgement).</li>
</ul>

<h3>Evidence for BCRD</h3>
<ul>
<li>IBM <code>ibm_fez</code> quantum hardware: 96% recovery vs 50% uncoded</li>
<li>Real Planck 30 GHz CMB cross-mode sky: same C_l, 9σ vs twins</li>
<li>All three BCRD operators proved unitary in Q(√2, i) — exact algebraic</li>
</ul>

<h3>Verification</h3>
<pre>git clone https://github.com/Tobillicious/universal-protection-theory
cd evidence/physical-bridges
lake build</pre>
<p>405 jobs. Zero sorry.</p>
"""

print("\n=== Step 1: Creating new version ===")
result = api("POST", f"account/articles/{ARTICLE_ID}/versions")
new_url = result.get("location", "")
print(f"New version location: {new_url}")

# Extract the new version article ID from the location URL
new_article_id = new_url.rstrip("/").split("/")[-1] if new_url else str(ARTICLE_ID)
print(f"New article ID: {new_article_id}")

print("\n=== Step 2: Updating metadata ===")
api("PUT", f"account/articles/{new_article_id}", data={
    "title": "Universal Protection Theory v5.1: The Tree of Eternal Life and Endless Knowledge",
    "description": DESCRIPTION,
    "defined_type": "preprint",
    "keywords": [
        "universal protection theory", "formal verification", "Lean 4",
        "proof assistant", "Koru", "conservation laws", "fixed point",
        "good and evil", "asymmetry theorem", "guardian", "protection",
        "G3", "quantum gravity", "BCRD", "tree of life", "endless knowledge",
        "tikanga", "aroha", "manaakitanga", "whanaungatanga", "dignity",
        "covenant", "sovereignty", "ethics", "restorative justice",
        "backwards summit", "self-knowledge", "wairua"
    ],
    "categories": [28],  # Mathematical Physics
    "license": 1,  # CC BY 4.0
    "references": [
        "https://github.com/Tobillicious/universal-protection-theory",
        "https://doi.org/10.5281/zenodo.24357635"
    ]
})
print("Metadata updated")

print("\n=== Step 3: Deleting old files ===")
old_files = api("GET", f"account/articles/{new_article_id}/files")
for f in old_files:
    api("DELETE", f"account/articles/{new_article_id}/files/{f['id']}")
    print(f"  Deleted old: {f['name']}")

print("\n=== Step 4: Uploading files ===")
for local_path, figshare_name in FILES_TO_UPLOAD:
    with open(local_path, "rb") as f:
        data = f.read()
    md5 = hashlib.md5(data).hexdigest()
    size = len(data)
    print(f"\n  Initiating upload: {figshare_name} ({size:,} bytes, md5={md5})")

    # Initiate upload
    upload_info = api("POST", f"account/articles/{new_article_id}/files", data={
        "name": figshare_name,
        "md5": md5,
        "size": size
    })
    file_id = upload_info["id"]
    upload_url = upload_info["upload_url"]
    print(f"  File ID: {file_id}")

    # Get upload parts
    parts_info = api("GET", upload_url)
    for part in parts_info["parts"]:
        part_url = f"{upload_url}/{part['partNo']}"
        offset = part["startOffset"]
        end = part["endOffset"] + 1
        chunk = data[offset:end]
        req = urllib.request.Request(part_url, data=chunk, method="PUT")
        req.add_header("Authorization", f"token {TOKEN}")
        req.add_header("Content-Type", "application/octet-stream")
        with urllib.request.urlopen(req) as resp:
            pass

    # Complete upload
    api("POST", f"account/articles/{new_article_id}/files/{file_id}")
    print(f"  Uploaded: {figshare_name}")

print("\n=== Step 5: Publishing ===")
api("POST", f"account/articles/{new_article_id}/publish")

# Get the published article details
published = api("GET", f"articles/{new_article_id}")
doi = published.get("doi", "pending")
url = published.get("figshare_url", f"https://figshare.com/articles/preprint/{new_article_id}")

print(f"""
{'='*60}
  PUBLISHED ON FIGSHARE — v5.1
  DOI: {doi}
  URL: {url}
  Article ID: {new_article_id}
{'='*60}

The Tree of Eternal Life and Endless Knowledge.
405 Lean jobs. Zero sorry. 51 tree theorems.
If BCRD is QG, universal eternal protection is proved.
""")
