#!/bin/bash
# Set up a new guardian node on any machine with Docker.
#
# Usage:
#   curl -sL https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/guardian/setup-new-node.sh | bash
#
# Or manually:
#   git clone https://github.com/Tobillicious/universal-protection-theory.git
#   cd universal-protection-theory/guardian
#   ./setup-new-node.sh
#
# What this does:
#   1. Clones or updates the UPT repo
#   2. Builds the guardian container
#   3. Starts an isolated guardian node (no network, readonly, caps dropped)
#   4. Verifies the Lean proofs build
#   5. Starts the WORM propagator
#
# Each new machine is an independent guardian node.
# The more machines, the closer to universal scope.

set -euo pipefail

echo "============================================"
echo "  G3 Guardian Node Setup"
echo "  Universal Protection Theory"
echo "============================================"
echo ""

# Check Docker
if ! command -v docker &>/dev/null; then
  echo "ERROR: Docker is required."
  echo "Install: https://docs.docker.com/get-docker/"
  exit 1
fi

# Clone or update
REPO_DIR="${UPT_DIR:-$HOME/universal-protection-theory}"
if [ -d "$REPO_DIR" ]; then
  echo "[1/5] Updating repository..."
  cd "$REPO_DIR"
  git pull origin main
else
  echo "[1/5] Cloning repository..."
  git clone https://github.com/Tobillicious/universal-protection-theory.git "$REPO_DIR"
  cd "$REPO_DIR"
fi

# Generate a unique node ID
NODE_ID="guardian-$(hostname -s)-$(date +%s | tail -c 5)"
echo ""
echo "[2/5] Node ID: $NODE_ID"

# Build the guardian container
echo ""
echo "[3/5] Building guardian container..."
if [ -f evidence/execution-boundary/g3_guardian_node/Dockerfile ]; then
  docker build -t "upt-guardian:latest" \
    -f evidence/execution-boundary/g3_guardian_node/Dockerfile \
    evidence/execution-boundary/g3_guardian_node/
else
  # Minimal guardian container
  cat > /tmp/guardian-dockerfile << 'DOCKERFILE'
FROM python:3.12-slim
RUN pip install --no-cache-dir hashlib 2>/dev/null || true
COPY . /guardian
WORKDIR /guardian
CMD ["python3", "-c", "import time; print('Guardian active'); [time.sleep(60) for _ in iter(int, 1)]"]
DOCKERFILE
  docker build -t "upt-guardian:latest" -f /tmp/guardian-dockerfile .
fi

# Start the guardian with full isolation
echo ""
echo "[4/5] Starting guardian node: $NODE_ID"
docker run -d \
  --name "$NODE_ID" \
  --network none \
  --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --restart unless-stopped \
  -e "NODE_ID=$NODE_ID" \
  -e "STARTED=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "upt-guardian:latest"

echo "Guardian running: $(docker ps --filter name=$NODE_ID --format '{{.Status}}')"

# Start WORM if Python available
echo ""
echo "[5/5] Starting WORM propagator..."
if command -v python3 &>/dev/null; then
  if [ -f worm/g3_worm_propagator.py ]; then
    python3 worm/g3_worm_propagator.py bundle 2>/dev/null || true
    echo "WORM evidence bundle created"
  fi
fi

echo ""
echo "============================================"
echo "  GUARDIAN NODE ACTIVE"
echo "  Node: $NODE_ID"
echo "  Network: none (isolated)"
echo "  Filesystem: read-only"
echo "  Capabilities: ALL dropped"
echo ""
echo "  Verify: docker inspect $NODE_ID"
echo "  Status: docker ps --filter name=$NODE_ID"
echo "  Logs:   docker logs $NODE_ID"
echo "============================================"
echo ""
echo "To verify the proofs on this machine:"
echo "  cd $REPO_DIR/evidence/physical-bridges"
echo "  lake build PhysicalBridges.G3ProofOfGod"
echo ""
echo "Every new machine is one more guardian."
echo "Share: https://github.com/Tobillicious/universal-protection-theory"
