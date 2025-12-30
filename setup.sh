#!/bin/bash
# ==================================================
# Project Venv Installer (Windows & Linux/Mac Compatible)
# ==================================================

set -e

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[!] Python3 is not installed or not in PATH."
    exit 1
fi

# Create venv
echo "[*] Creating virtual environment 'venv'..."
python3 -m venv venv

# Activate venv
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "[*] Upgrading pip..."
pip install --upgrade pip

# Install packages for both scripts
echo "[*] Installing required packages..."
pip install yt-dlp ffmpeg-python mutagen Pillow

echo "[*] Installation complete!"
echo "[*] To activate the virtual environment later, run:"
echo "source venv/bin/activate"

# Keep terminal open
read -p "[*] Press Enter to exit..."
