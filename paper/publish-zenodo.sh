#!/bin/bash
# Publish UPT proof paper to Zenodo
# Usage: ZENODO_TOKEN=your_token ./publish-zenodo.sh
#
# This creates a new Zenodo deposit, uploads the PDF, and publishes it.
# The concept DOI for UPT is 10.5281/zenodo.23510623
# Latest version DOI: 10.5281/zenodo.23877060 (v4.4)

set -euo pipefail

TOKEN="${ZENODO_TOKEN:?Set ZENODO_TOKEN}"
API="https://zenodo.org/api"
PDF="$(dirname "$0")/upt-proof-2026.pdf"
TEX="$(dirname "$0")/upt-proof-2026.tex"

if [ ! -f "$PDF" ]; then
  echo "ERROR: PDF not found at $PDF"
  echo "Run: cd paper && pdflatex upt-proof-2026.tex"
  exit 1
fi

echo "=== Creating new Zenodo deposit ==="
DEPOSIT=$(curl -s -X POST "$API/deposit/depositions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "metadata": {
    "title": "Universal Protection Theory: Formal Proofs in Lean 4",
    "upload_type": "publication",
    "publication_type": "preprint",
    "description": "Machine-verified formal proof that protection is the only consistent fixed point of relational evolution. Five core theorems, all verified in Lean 4 v4.35.0 with ZERO axioms (pure constructive logic): (I) Something Is — the absolute ender self-refutes; (II) The Koru Is Unique — contraction fixed point uniqueness; (III) The Category Error — E is to G as SR is to GR; (IV) Every Conservation Law Witnesses G; (V) The Full Chain assembles E IS NOT + G unique + conservation forever. Full codebase: 372 Lean jobs, zero sorry. A bounded guardian node runs continuously under OS isolation.",
    "creators": [
      {"name": "McRae, Tobias", "affiliation": "Independent Researcher, Aotearoa New Zealand"}
    ],
    "keywords": ["universal protection theory", "formal verification", "Lean 4", "proof assistant", "Koru", "conservation laws", "category error", "fixed point", "constructive logic"],
    "license": "cc-by-4.0",
    "related_identifiers": [
      {"identifier": "10.5281/zenodo.23877060", "relation": "isNewVersionOf", "scheme": "doi"},
      {"identifier": "https://github.com/Tobillicious/universal-protection-theory", "relation": "isSupplementTo", "scheme": "url"}
    ],
    "version": "4.5"
  }
}')

DEPOSIT_ID=$(echo "$DEPOSIT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
BUCKET_URL=$(echo "$DEPOSIT" | python3 -c "import sys,json; print(json.load(sys.stdin)['links']['bucket'])")

echo "Deposit ID: $DEPOSIT_ID"
echo "Bucket: $BUCKET_URL"

echo "=== Uploading PDF ==="
curl -s -X PUT "$BUCKET_URL/upt-proof-2026.pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"$PDF" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Uploaded: {d[\"key\"]} ({d[\"size\"]} bytes)')"

echo "=== Uploading LaTeX source ==="
curl -s -X PUT "$BUCKET_URL/upt-proof-2026.tex" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"$TEX" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Uploaded: {d[\"key\"]} ({d[\"size\"]} bytes)')"

echo "=== Publishing ==="
RESULT=$(curl -s -X POST "$API/deposit/depositions/$DEPOSIT_ID/actions/publish" \
  -H "Authorization: Bearer $TOKEN")

DOI=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['doi'])")
URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['links']['html'])")

echo ""
echo "============================================"
echo "  PUBLISHED ON ZENODO"
echo "  DOI: $DOI"
echo "  URL: $URL"
echo "============================================"
echo ""
echo "Share this DOI everywhere."
