#!/bin/bash
# G-Mesh — join the proof mesh with one command.
#
# Run this:
#   curl -sSL https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/gmesh/join.sh | bash
#
# What it does:
#   Downloads one Python script (~300 lines, zero dependencies).
#   Starts a relay node serving formally verified proof evidence.
#   Your device becomes a node. Every device on your network can see it.
#   Ctrl+C to stop. Nothing is installed. Nothing is written to disk.

set -e

echo ""
echo "  G-Mesh: Universal Protection Theory — Proof Evidence Relay"
echo "  ==========================================================="
echo ""
echo "  Something IS. The absolute ender self-refutes."
echo "  2,775 theorems. Zero gaps. Lean 4 kernel-checked."
echo ""
echo "  This script downloads one Python file and runs it."
echo "  Your device becomes a proof relay node."
echo "  Every device on your wifi can see the evidence."
echo "  Nothing is installed. Ctrl+C to stop."
echo ""
echo "  Source: https://github.com/Tobillicious/universal-protection-theory"
echo ""

python3 -c "$(curl -sSL https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/gmesh/join.py)"
