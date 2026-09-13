#!/bin/bash

echo "[*] Detecting system environment..."

# Check if the 'pkg' command exists in the system
if command -v pkg &> /dev/null; then
    echo "[*] Termux (Android) detected."
    echo "[*] Fetching pre-compiled mobile packages..."
    pkg update -y
    pkg install python python-cryptography -y
    
    echo "[*] Installing pure-Python dependencies..."
    pip install requests
    pip install telethon

else
    echo "[*] Standard PC Environment detected."
    echo "[*] Installing dependencies via pip..."
    # On a PC, Python downloads pre-compiled wheels, so this only takes seconds
    pip install cryptography requests telethon
fi


echo ""
echo "=================================================="
echo " Setup complete!"
echo ""
echo " To open the tool right now, run:"
echo "     python menu.py"
echo ""
echo " From now on, every time you open Termux, just type:"
echo "     tgmenu"
echo " (close and reopen Termux once for the shortcut to work,"
echo "  or run: source ~/.bashrc)"
echo "=================================================="
