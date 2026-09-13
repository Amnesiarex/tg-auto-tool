#!/usr/bin/env python3
"""
Telegram Automation Toolkit — Terminal Menu Launcher
-----------------------------------------------------
This file adds ONLY a menu on top of your existing scripts.
It never edits, imports, or changes a single line of logic inside
session_creator.py, savevidbyid3op.py, vidsendidbydura.py,
countvidbytime.py, duplicateremsav.py, or chat_scanner.py.

Each menu option simply launches the matching script as its own
process (python <script>.py), exactly as if you had typed that
command yourself in the terminal. All prompts, inputs, and output
from the original scripts behave 100% the same as before.

Usage:
    python menu.py
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Order and wording here is presentation only — the "script" value
# is the exact, untouched file that gets executed.
MENU_ITEMS = [
    {
        "key": "1",
        "title": "Create / Add Telegram Session",
        "desc": "Log in with a phone number, save credentials to api.json",
        "script": "session_creator.py",
    },
    {
        "key": "2",
        "title": "Save Videos From a Chat -> Saved Messages",
        "desc": "Pick a private chat, forward its videos to Saved Messages",
        "script": "savevidbyid3op.py",
    },
    {
        "key": "3",
        "title": "Send Videos From Saved Messages -> a Chat",
        "desc": "Filter Saved Messages videos by min duration, send to a chat",
        "script": "vidsendidbydura.py",
    },
    {
        "key": "4",
        "title": "Count Videos by Duration (Saved Messages)",
        "desc": "Scan Saved Messages, report videos above a duration threshold",
        "script": "countvidbytime.py",
    },
    {
        "key": "5",
        "title": "Remove Duplicate Videos (Saved Messages)",
        "desc": "Find duplicate videos in Saved Messages and optionally delete them",
        "script": "duplicateremsav.py",
    },
]

REQUIRED_SUPPORT_FILES = ["chat_scanner.py"]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("=" * 60)
    print("           TELEGRAM AUTOMATION TOOLKIT".center(60))
    print("=" * 60)


def missing_files():
    missing = []
    for item in MENU_ITEMS:
        if not (BASE_DIR / item["script"]).exists():
            missing.append(item["script"])
    for f in REQUIRED_SUPPORT_FILES:
        if not (BASE_DIR / f).exists():
            missing.append(f)
    return missing


def print_menu():
    banner()
    print()
    for item in MENU_ITEMS:
        print(f"  [{item['key']}] {item['title']}")
        print(f"      {item['desc']}")
        print()
    print("  [0] Exit")
    print("-" * 60)


def run_script(script_name: str):
    script_path = BASE_DIR / script_name
    print()
    print("-" * 60)
    print(f" Launching: {script_name}")
    print("-" * 60)
    print()
    try:
        # Runs the original file, unmodified, as its own process.
        # cwd is set to this folder so api.json / .session files and
        # the chat_scanner.py import are found exactly like before.
        subprocess.run([sys.executable, str(script_path)], cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
    print()
    input("Press Enter to return to the main menu...")


def main():
    missing = missing_files()
    if missing:
        print("[!] Warning: these required files were not found next to menu.py:")
        for m in missing:
            print(f"    - {m}")
        print("\nPlace menu.py in the SAME folder as all the original scripts.")
        input("Press Enter to continue anyway, or Ctrl+C to quit...")

    while True:
        clear_screen()
        print_menu()
        choice = input("  Select an option: ").strip()

        if choice == "0":
            print("\nGoodbye!")
            break

        match = next((i for i in MENU_ITEMS if i["key"] == choice), None)
        if match:
            run_script(match["script"])
        else:
            input("\nInvalid choice. Press Enter to try again...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExited by user.")
