import asyncio
import json
import sys
from collections import defaultdict
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterVideo

# ============================================================
# DYNAMIC CONFIGURATION LOADER
# ============================================================
def select_account(json_file='api.json'):
    """Reads api.json, prompts the user to select an account, and returns the credentials."""
    try:
        with open(json_file, 'r') as f:
            api_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{json_file}' not found. Please run your session builder script first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{json_file}' contains invalid JSON data.")
        sys.exit(1)

    # Extract all the mobile numbers (the top-level keys in your JSON)
    accounts = list(api_data.keys())
    
    if not accounts:
        print(f"Error: No accounts found inside '{json_file}'.")
        sys.exit(1)

    print("\n--- Select an Account ---")
    for index, number in enumerate(accounts, start=1):
        print(f"{index}. {number}")
        
    while True:
        choice_input = input("\nEnter the number of the account you want to use: ")
        try:
            choice_index = int(choice_input) - 1
            if 0 <= choice_index < len(accounts):
                selected_number = accounts[choice_index]
                break
            else:
                print("Invalid selection. Please choose a number from the list.")
        except ValueError:
            print("Please enter a valid numeric digit.")

    creds = api_data[selected_number]
    print(f"\n[+] Loaded credentials for {selected_number}")
    
    return int(creds['API_ID']), creds['API_HASH'], creds['SESSION_NAME']

# Fetch the credentials before proceeding
API_ID, API_HASH, SESSION_NAME = select_account()

# Initialize the global client with the dynamically selected credentials
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
# ============================================================

async def async_input(prompt: str) -> str:
    """Read console input without blocking the asynchronous event loop."""
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

def format_size(bytes_size: int) -> str:
    """Convert bytes into human-readable units."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

# ============================================================
# MAIN LOGIC
# ============================================================

async def main():
    print(f"Connecting to session: {SESSION_NAME}.session...")
    
    print("Scanning Saved Messages exclusively for video files...")

    # Map document_id -> list of message IDs
    videos_by_doc_id = defaultdict(list)
    video_sizes = {}
    total_videos = 0

    # Leverage server-side video filtering for speed
    async for msg in client.iter_messages('me', filter=InputMessagesFilterVideo):
        if msg.document:
            total_videos += 1
            doc_id = msg.document.id
            videos_by_doc_id[doc_id].append(msg.id)
            video_sizes[doc_id] = msg.document.size

    # Isolate duplicates while strictly preserving the oldest (lowest message ID)
    duplicates_to_delete = []
    reclaimed_bytes = 0

    for doc_id, msg_ids in videos_by_doc_id.items():
        if len(msg_ids) > 1:
            # Sort IDs ascending: lowest ID is the original
            msg_ids.sort()
            redundant_ids = msg_ids[1:]
            
            duplicates_to_delete.extend(redundant_ids)
            reclaimed_bytes += video_sizes[doc_id] * len(redundant_ids)

    print(f"\nScan complete. Examined {total_videos} total videos.")
    print(f"Unique videos found: {len(videos_by_doc_id)}")
    print(f"Duplicate messages detected: {len(duplicates_to_delete)}")
    print(f"Potential space reclaimed: {format_size(reclaimed_bytes)}")

    if not duplicates_to_delete:
        print("\nYour Saved Messages are clean. No duplicates to remove.")
        return

    # --------------------------------------------------------
    # Execution / Deletion Phase
    # --------------------------------------------------------
    confirmation = await async_input(
        f"\nPermanently delete {len(duplicates_to_delete)} duplicate videos? (y/n): "
    )
    
    if confirmation.strip().lower() != 'y':
        print("\nOperation cancelled. No messages were removed.")
        return

    print("\nDeleting duplicate messages in chunks of 100...")
    chunk_size = 100
    deleted_count = 0

    for i in range(0, len(duplicates_to_delete), chunk_size):
        chunk = duplicates_to_delete[i:i + chunk_size]
        while True:
            try:
                await client.delete_messages('me', chunk)
                deleted_count += len(chunk)
                print(f"  -> Deleted {deleted_count}/{len(duplicates_to_delete)} messages...")
                await asyncio.sleep(1)
                break
            except FloodWaitError as e:
                print(f"  [!] Rate limit reached. Sleeping for {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)

    print(f"\nCleanup complete. Successfully deleted {deleted_count} redundant videos.")

if __name__ == '__main__':
    try:
        # Use context manager for smooth, warning-free connection and teardown
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nProcess manually aborted.")