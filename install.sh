#!/usr/bin/env bash
# ============================================================
# Telegram Automation Toolkit — Installer
# Works on Termux (Android) and regular Linux.
# Does NOT change any logic in the toolkit's .py files —
# it only installs dependencies and adds a shortcut command.
# ============================================================
set -e

echo "=================================================="
echo "   Telegram Automation Toolkit — Installer"
echo "=================================================="

# ---- 1. Install system packages ----
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]]; then
    echo "[*] Termux detected."
    pkg update -y
    pkg install -y python git
else
    echo "[*] Non-Termux Linux detected."
    SUDO=""
    if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    fi
    if command -v apt >/dev/null 2>&1; then
        $SUDO apt update -y || true
        $SUDO apt install -y python3 python3-pip git
    fi
fi

# ---- 2. Install Python dependencies ----
echo "[*] Installing Python dependencies (telethon)..."
pip install --upgrade pip >/dev/null 2>&1 || true
pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt

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
