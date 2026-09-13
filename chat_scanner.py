# chat_scanner.py
import asyncio

async def get_private_chats(client) -> dict:
    """
    Takes an active TelegramClient, iterates through dialogs, 
    and returns a dictionary of private users.
    Format: {1: {'name': 'John Doe', 'id': 12345678}, 2: ...}
    """
    chats_dict = {}
    count = 1
    
    # iter_dialogs() goes through the chat list from newest to oldest
    async for dialog in client.iter_dialogs():
        # Filter to only show private chats with people (ignores groups/channels/bots)
        if dialog.is_user and not dialog.entity.bot:
            
            # Handle users without a visible name
            display_name = dialog.name if dialog.name else "Unknown User"
            
            chats_dict[count] = {
                'name': display_name,
                'id': dialog.id
            }
            count += 1
            
    return chats_dict