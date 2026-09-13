import asyncio
import json
import sys
import random
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterVideo

# Import your custom chat scanning module
from chat_scanner import get_private_chats

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
    
    # Return the dictionary values mapped to their respective variables
    return int(creds['API_ID']), creds['API_HASH'], creds['SESSION_NAME']

# Fetch the credentials before proceeding
API_ID, API_HASH, SESSION_NAME = select_account()

# Initialize the global client with the dynamically selected credentials
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
# ============================================================

async def main():
    print("\nFetching recent private chats... Please wait.")
    
    # 1. Fetch the chats using the imported module
    chats = await get_private_chats(client)
    
    if not chats:
        print("No private chats found.")
        return

    # 2. Render the UI Table
    print(f"\n{'NO':<4} | {'Chat Name':<30} | {'Hidden User ID':<15}")
    print("-" * 55)
    for no, data in chats.items():
        # Truncate names that are too long to maintain table structure
        short_name = data['name'][:28] + ".." if len(data['name']) > 30 else data['name']
        print(f"{no:<4} | {short_name:<30} | {data['id']:<15}")
    
    # 3. Handle Target Selection logic
    while True:
        target_input = input("\nEnter the NO of the target chat: ")
        try:
            target_no = int(target_input)
            if target_no in chats:
                target_id = chats[target_no]['id']
                print(f"Selected: {chats[target_no]['name']} (ID: {target_id})")
                break
            else:
                print("Error: That NO is not in the list.")
        except ValueError:
            print("Error: Please enter a valid number.")

    # 4. Ask for direction preference
    print("\nSelect which videos to forward:")
    print("1. Incoming media (Received from them)")
    print("2. Outgoing media (Sent by you)")
    print("3. All media")
    
    choice = input("Enter 1, 2, or 3: ")
    if choice not in ['1', '2', '3']:
        print("Invalid choice. Exiting.")
        return

    print("\nScanning chat for videos... This might take a moment.")
    video_count = 0
    batch = []
    
    # 5. Iterate using the native video filter
    async for message in client.iter_messages(target_id, filter=InputMessagesFilterVideo):
        
        # Apply the direction logic based on message.out
        if choice == '1' and message.out:
            continue
        elif choice == '2' and not message.out:
            continue
            
        batch.append(message.id)
        video_count += 1
        print(f"Queued video {video_count}...", end='\r')
        
        # Once we collect 100 IDs, forward them in a single batch
        if len(batch) == 100:
            print(f"\n[+] Forwarding batch of 100 videos to Saved Messages...")
            while True:
                try:
                    # from_peer is strictly required when forwarding by ID
                    await client.forward_messages('me', batch, from_peer=target_id)
                    batch.clear()
                    break
                except FloodWaitError as e:
                    wait_time = e.seconds + 5
                    print(f"\n[WARNING] Telegram API limit hit. Mandatory sleep for {wait_time} seconds...\n")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    print(f"\n[ERROR] Unexpected error forwarding batch: {e}")
                    batch.clear() # Clear to prevent infinite crash loops
                    break
            
            # --------------------------------------------------------
            # AUTOMATED BATCH-BASED JITTER
            # --------------------------------------------------------
            if video_count % 2000 == 0:
                pause_time = random.uniform(120.0, 180.0) # 2 to 3 minutes
                print(f"[!] MEGA-BATCH REACHED: Cooling down for {pause_time:.1f} seconds...\n")
                await asyncio.sleep(pause_time)
                
            elif video_count % 500 == 0:
                pause_time = random.uniform(30.0, 60.0) # 30 to 60 seconds
                print(f"[-] MACRO-BATCH REACHED: Pausing for {pause_time:.1f} seconds...\n")
                await asyncio.sleep(pause_time)
                
            else:
                # Normal sleep between standard batches of 100
                pause_time = random.uniform(2.0, 5.0)
                await asyncio.sleep(pause_time)

    # 6. Forward any remaining messages (e.g., the last 45 videos)
    if batch:
        print(f"\n[+] Forwarding final batch of {len(batch)} videos to Saved Messages...")
        while True:
            try:
                await client.forward_messages('me', batch, from_peer=target_id)
                break
            except FloodWaitError as e:
                wait_time = e.seconds + 5
                print(f"\n[WARNING] Telegram API limit hit. Mandatory sleep for {wait_time} seconds...\n")
                await asyncio.sleep(wait_time)
            except Exception as e:
                print(f"\n[ERROR] Unexpected error forwarding final batch: {e}")
                break

    print(f"\nFinished! Total videos forwarded to Saved Messages: {video_count}")

if __name__ == '__main__':
    try:
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nProcess manually aborted.")