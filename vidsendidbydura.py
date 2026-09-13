import asyncio
import json
import sys
import random
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterVideo, DocumentAttributeVideo

# Import custom chat scanning module
from chat_scanner import get_private_chats

# ============================================================
# DYNAMIC CONFIGURATION LOADER
# ============================================================
def select_account(json_file='api.json'):
    try:
        with open(json_file, 'r') as f:
            api_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{json_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{json_file}' contains invalid JSON data.")
        sys.exit(1)

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

API_ID, API_HASH, SESSION_NAME = select_account()
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
# ============================================================

async def main():
    print("\nFetching recent private chats... Please wait.")
    chats = await get_private_chats(client)
    
    if not chats:
        print("No private chats found.")
        return

    print(f"\n{'NO':<4} | {'Chat Name':<30} | {'Hidden User ID':<15}")
    print("-" * 55)
    for no, data in chats.items():
        short_name = data['name'][:28] + ".." if len(data['name']) > 30 else data['name']
        print(f"{no:<4} | {short_name:<30} | {data['id']:<15}")
    
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
            
    try:
        duration_input = int(input("\nEnter the min video duration in seconds: "))
    except ValueError:
        print("Error: Duration must be a number.")
        return
    
    # --- PRE-SCAN PHASE (Filtered for videos only) ---
    print("\nScanning target chat to build a cache of already sent files...")
    sent_document_ids = set()

    async for msg in client.iter_messages(target_id, filter=InputMessagesFilterVideo):
        if msg.out and msg.media and hasattr(msg.media, 'document'):
            sent_document_ids.add(msg.media.document.id)

    print(f"Cache built: Found {len(sent_document_ids)} video files previously sent by you.\n")
    # ----------------------------------------------------

    print(f"Scanning 'Saved Messages' for new videos > {duration_input} seconds...\n")
    video_count = 0
    batch = []

    # Server-filtered iteration on Saved Messages
    async for message in client.iter_messages('me', filter=InputMessagesFilterVideo):
        if message.media and hasattr(message.media, 'document'):
            current_doc_id = message.media.document.id

            if current_doc_id in sent_document_ids:
                continue
                
            for attribute in message.media.document.attributes:
                if isinstance(attribute, DocumentAttributeVideo):
                    if attribute.duration > duration_input:
                        
                        # Add message ID to our batch list instead of sending immediately
                        batch.append(message.id)
                        sent_document_ids.add(current_doc_id)
                        video_count += 1
                        
                        print(f"Queued video {video_count} (Duration: {attribute.duration}s)...", end='\r')
                        
                        # When the queue hits exactly 100, pause and ask the user
                        if len(batch) == 100:
                            print(f"\n\n[PAUSED] Queued exactly 100 videos. (Total processed: {video_count})")
                            proceed = input("Type 'y' to forward this batch, or any other key to stop: ")
                            
                            if proceed.lower() != 'y':
                                print("Operation halted by user.")
                                return
                            
                            print("Forwarding batch of 100 videos instantly...")
                            
                            # FloodWait loop wrapper to retry gracefully if Telegram complains
                            while True:
                                try:
                                    await client.forward_messages(
                                        target_id,
                                        batch,
                                        from_peer='me',           # <--- FIXED
                                        drop_author=True,         
                                        drop_media_captions=True  
                                    )
                                    print("Batch forwarded successfully!")
                                    batch.clear()
                                    await asyncio.sleep(2.0)
                                    break
                                except FloodWaitError as e:
                                    wait_time = e.seconds + 5
                                    print(f"\n[!] Rate limit reached. Sleeping for {wait_time}s before retrying...\n")
                                    await asyncio.sleep(wait_time)
                                except Exception as e:
                                    print(f"\n[!] Error forwarding batch: {e}")
                                    batch.clear()
                                    await asyncio.sleep(2.0)
                                    break
                        break # Exit the attributes loop and move to the next message

    # Catch the remaining videos at the end
    if batch:
        print(f"\n\n[PAUSED] Queued final {len(batch)} videos. (Total processed: {video_count})")
        proceed = input("Type 'y' to forward this final batch: ")
        
        if proceed.lower() == 'y':
            print(f"Forwarding final batch of {len(batch)} videos...")
            while True:
                try:
                    await client.forward_messages(
                        target_id,
                        batch,
                        from_peer='me',           # <--- FIXED
                        drop_author=True,
                        drop_media_captions=True
                    )
                    print("Final batch forwarded successfully!")
                    break
                except FloodWaitError as e:
                    wait_time = e.seconds + 5
                    print(f"\n[!] Rate limit reached. Sleeping for {wait_time}s before retrying...\n")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    print(f"\n[!] Error forwarding final batch: {e}")
                    break

    print(f"\nFinished! Total new videos sent during this session: {video_count}")

if __name__ == '__main__':
    try:
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nProcess manually aborted.")