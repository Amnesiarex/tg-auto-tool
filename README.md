# Telegram Automation Toolkit

A menu-driven Telegram automation tool (built on Telethon). Works great on
Termux (Android).

## For your friend — one-time setup on Termux

Open Termux and paste this (installs git + python, then clones the repo):

```bash
pkg update -y && pkg install -y git python
git clone <YOUR_GITHUB_REPO_URL>
cd <YOUR_REPO_FOLDER_NAME>
bash install.sh
```

`install.sh` automatically installs the one Python dependency (`telethon`)
and adds a shortcut command called **`tgmenu`**.

## Opening the tool

Right after setup:
```bash
python menu.py
```

Every time after that — close and reopen Termux once, then just type:
```bash
tgmenu
```
That's it — no need to remember folders or commands again.

## First run

Choose option **1** in the menu to log into a Telegram account (asks for
API_ID, API_HASH, session name, phone number, and the login code). After
that, options 2–5 become usable.

## Files

| File | Purpose |
|---|---|
| `menu.py` | The menu — this is what you run |
| `session_creator.py` | Logs into Telegram, saves `api.json` |
| `savevidbyid3op.py` | Forwards videos from a chat into Saved Messages |
| `vidsendidbydura.py` | Sends videos from Saved Messages to a chat |
| `countvidbytime.py` | Counts videos above a duration in Saved Messages |
| `duplicateremsav.py` | Finds/removes duplicate videos in Saved Messages |
| `chat_scanner.py` | Shared helper module (not run directly) |
| `install.sh` | One-time setup script |

`api.json` and any `.session` file are created locally on first login and
are **not** part of this repo (see `.gitignore`) — they hold your live
Telegram login, so never share or commit them.
