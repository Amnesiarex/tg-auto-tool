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

# ---- 3. Add a one-word shortcut command ----
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALIAS_LINE="alias tgmenu='cd \"$TOOL_DIR\" && python menu.py'"
SHELL_RC="$HOME/.bashrc"

touch "$SHELL_RC"
if ! grep -Fxq "$ALIAS_LINE" "$SHELL_RC" 2>/dev/null; then
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "[+] Added 'tgmenu' shortcut to $SHELL_RC"

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
