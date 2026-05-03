#!/bin/bash
# ============================================================
#  setup.sh — Mimi Robot One-Click Installer (Raspberry Pi)
# ============================================================
set -e

echo "========================================"
echo "  Mimi Robot Setup Script"
echo "========================================"

echo "[1/4] Installing system packages..."
sudo apt-get update -q
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    flac \
    mpg123 \
    libportaudio2 \
    libjpeg-dev \
    libopenblas-dev \
    python3-pygame

echo "[2/4] Setting up DSI display..."
# Enable DSI display (7" TFT)
if ! grep -q "display_auto_detect=1" /boot/config.txt; then
    echo "display_auto_detect=1" | sudo tee -a /boot/config.txt
fi

echo "[3/4] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/4] Setting up config..."
if [ ! -f .env ]; then
    #cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and add your TYPHOON_API_KEY"
    echo "    Run: nano .env"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env: nano .env"
echo "  2. Set TYPHOON_API_KEY=your_key_here"
echo "  3. Set DISPLAY_MODE=pygame"
echo "  4. Run: source venv/bin/activate && python main.py"