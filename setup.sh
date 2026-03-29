#!/bin/bash
# ============================================================
#  setup.sh — Mimi Robot One-Click Installer (Raspberry Pi)
# ============================================================
set -e

echo "========================================"
echo "  Mimi Robot Setup Script"
echo "========================================"

# System packages needed for audio and display
echo "[1/4] Installing system packages..."
sudo apt-get update -q
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    flac \
    espeak \
    mpg123 \
    i2c-tools \
    python3-smbus \
    libportaudio2 \
    libatlas-base-dev \
    libjpeg-dev \
    libopenblas-dev

# Enable I2C for OLED display
echo "[2/4] Enabling I2C..."
sudo raspi-config nonint do_i2c 0 || echo "(Skipped — not on Pi or already enabled)"

# Create virtual environment
echo "[3/4] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example if not exists
echo "[4/4] Setting up config..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    echo "    Run: nano .env"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env: nano .env"
echo "  2. Set GEMINI_API_KEY=your_key_here"
echo "  3. Run: source venv/bin/activate && python main.py"
echo ""
echo "For OLED display, set DISPLAY_MODE=oled in .env"
echo "For laptop test, keep DISPLAY_MODE=pygame"
