#!/data/data/com.termux/files/usr/bin/bash
# G3 Guardian WORM — Android/Termux setup
#
# Run this in Termux on your Android phone:
#   curl -sL https://raw.githubusercontent.com/Tobillicious/universal-protection-theory/main/worm/g3_android_setup.sh | bash
#
# Or manually:
#   pkg install python git
#   git clone https://github.com/Tobillicious/universal-protection-theory.git upt
#   cd upt && python worm/g3_android_worm.py watch

set -e

echo "============================================"
echo "  G3 Guardian WORM — Android Setup"
echo "  Write Once Read Many"
echo "============================================"
echo ""

# Install dependencies
echo "[1/4] Installing packages..."
pkg update -y
pkg install -y python git termux-api

# Clone or update repo
echo "[2/4] Getting guardian evidence..."
if [ -d "$HOME/upt" ]; then
    cd "$HOME/upt"
    git pull origin main
else
    git clone https://github.com/Tobillicious/universal-protection-theory.git "$HOME/upt"
    cd "$HOME/upt"
fi

# Verify evidence
echo "[3/4] Verifying evidence bundle..."
python worm/g3_android_worm.py verify

# Set up wifi watcher via Termux:Boot
echo "[4/4] Setting up auto-start..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/g3-worm.sh << 'BOOTSCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/upt
python worm/g3_android_worm.py watch &
BOOTSCRIPT
chmod +x ~/.termux/boot/g3-worm.sh

echo ""
echo "============================================"
echo "  G3 WORM installed!"
echo ""
echo "  Auto-propagates on every new wifi network."
echo "  Run manually: cd ~/upt && python worm/g3_android_worm.py watch"
echo "  Check status: python worm/g3_android_worm.py status"
echo "============================================"
echo ""
echo "Starting WORM watcher..."
python worm/g3_android_worm.py watch
