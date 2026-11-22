#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
lake build >/tmp/g_build.log 2>&1

theorems=(
  "PhysicalBridges.G3StructuralDominance.STRUCTURAL_DOMINANCE"
  "PhysicalBridges.G3StructuralDominance.GOD_OR_ERROR_STRUCTURAL"
  "PhysicalBridges.G3ModelSingularityBridge.THE_INSEPARABILITY_THEOREM"
  "PhysicalBridges.G3BlackHoleSyntaxError.collapsed_has_no_agency"
)

for thm in "${theorems[@]}"; do
  if grep -R "$thm' does not depend on any axioms" .lake/build/lib/lean >/dev/null; then
    echo "PASS: $thm (zero axioms)"
  else
    echo "FAIL: $thm"
    exit 1
  fi
done
echo "All G axiom audits passed."
