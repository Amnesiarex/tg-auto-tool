import asyncio
import json
import sys
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterVideo, DocumentAttributeVideo

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

    # Extract all mobile numbers (the keys in api.json)
    accounts = list(api_data.keys())
    
    if not accounts:
        print(f"Error: No accounts found inside '{json_file}'.")
        sys.exit(1)

    print("\n--- Select an Account ---")
    for index, number in enumerate(accounts, start=1):
        print(f"{index}. {number}")
        
    while True:
        choice_input = input("\nEnter the number of the account you want to use: ").strip()
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

# Load account credentials dynamically
API_ID, API_HASH, SESSION_NAME = select_account()

# Initialize the client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
# ============================================================

def format_size(bytes_size: int) -> str:
    """Convert bytes into human-readable units."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def format_time(seconds: float) -> str:
    """Convert seconds into HH:MM:SS format."""
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours}h {mins}m {secs}s"
    return f"{mins}m {secs}s"

# ============================================================
# MAIN LOGIC
# ============================================================
async def main():
    # 1. Prompt for minimum duration
    duration_input = input("Enter the minimum video duration in seconds (e.g., 420 for 7 mins): ").strip()
    try:
        min_duration = float(duration_input)
        if min_duration < 0:
            print("Duration must be a positive number.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    print(f"\nScanning Saved Messages for videos > {format_time(min_duration)} ({min_duration}s)...")
    
    total_videos_scanned = 0
    matched_count = 0
    total_matched_size = 0

    # 2. Iterate using server-side video filter
    async for message in client.iter_messages('me', filter=InputMessagesFilterVideo):
        if message.media and hasattr(message.media, 'document'):
            total_videos_scanned += 1
            
            # Extract video duration attribute
            for attr in message.media.document.attributes:
                if isinstance(attr, DocumentAttributeVideo):
                    if attr.duration > min_duration:
                        matched_count += 1
                        total_matched_size += message.media.document.size
                    break
            
            # Live progress indicator every 50 videos checked
            if total_videos_scanned % 50 == 0:
                print(f"Scanned {total_videos_scanned} videos... (Found {matched_count} matches so far)", end='\r')

    # 3. Output Summary
    print("\n" + "=" * 45)
    print("                 SCAN SUMMARY                ")
    print("=" * 45)
    print(f"Threshold:           > {format_time(min_duration)} ({min_duration}s)")
    print(f"Total Videos Checked:{total_videos_scanned:>16}")
    print(f"Matching Videos:     {matched_count:>16}")
    print(f"Total Storage Size:  {format_size(total_matched_size):>16}")
    print("=" * 45)

if __name__ == '__main__':
    try:
        # The 'with client:' block ensures graceful connection and shutdown
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nScan stopped by user.")