from telegram import Bot
from telegram.ext import Application
from telegram.error import BadRequest, Forbidden
import time
import asyncio

# Telegram bot token
BOT_TOKEN = "7369759089:AAHNhRi7engGeoEujYBO6Y4WhYNYSM2dmx0"

# Group IDs for access control
GROUP_IDS = [-4657917032, -4644237809, -4690219028]

# Mock database for user subscriptions
USER_SUBSCRIPTIONS = {}

# Initialize application
application = Application.builder().token(BOT_TOKEN).build()

async def add_user_to_groups(user_id: int):
    """Adds a user to all predefined Telegram groups."""
    for group_id in GROUP_IDS:
        try:
            # First check if bot is admin in the group
            bot_member = await application.bot.get_chat_member(chat_id=group_id, user_id=application.bot.id)
            if not bot_member.can_invite_users:
                print(f"Bot doesn't have permission to invite users in group {group_id}")
                continue
                
            await application.bot.add_chat_member(chat_id=group_id, user_id=user_id)
            print(f"User {user_id} added to group {group_id}")
        except BadRequest as e:
            print(f"Error adding user {user_id} to group {group_id}: {e}")
        except Forbidden as e:
            print(f"Bot doesn't have permission to add users in group {group_id}: {e}")
        except Exception as e:
            print(f"Unexpected error adding user {user_id} to group {group_id}: {e}")

async def remove_user_from_groups(user_id: int):
    """Removes a user from all predefined Telegram groups."""
    for group_id in GROUP_IDS:
        try:
            # First check if bot is admin in the group
            bot_member = await application.bot.get_chat_member(chat_id=group_id, user_id=application.bot.id)
            if not bot_member.can_restrict_members:
                print(f"Bot doesn't have permission to remove users in group {group_id}")
                continue
                
            await application.bot.ban_chat_member(chat_id=group_id, user_id=user_id)
            print(f"User {user_id} removed from group {group_id}")
        except BadRequest as e:
            print(f"Error removing user {user_id} from group {group_id}: {e}")
        except Forbidden as e:
            print(f"Bot doesn't have permission to remove users in group {group_id}: {e}")
        except Exception as e:
            print(f"Unexpected error removing user {user_id} from group {group_id}: {e}")

async def mock_robokassa_response(user_id: int):
    """Mocks a successful payment response from Robokassa."""
    print(f"[Mock] Payment received for user {user_id}")
    USER_SUBSCRIPTIONS[user_id] = time.time() + (30 * 24 * 60 * 60)  # Subscription valid for 30 days
    await add_user_to_groups(user_id)

async def check_subscriptions():
    """Checks and removes expired users from groups."""
    current_time = time.time()
    expired_users = [user_id for user_id, expiry in USER_SUBSCRIPTIONS.items() if expiry < current_time]
    for user_id in expired_users:
        await remove_user_from_groups(user_id)
        del USER_SUBSCRIPTIONS[user_id]
        print(f"Subscription expired for user {user_id}, removed from groups.")

async def start():
    """Test function to demonstrate the bot's functionality."""
    print("Starting bot test...")
    
    # Test user ID (you can change this to any valid Telegram user ID)
    test_user_id = 123456789
    
    print("\n1. Testing user addition to groups...")
    await add_user_to_groups(test_user_id)
    
    print("\n2. Testing subscription mock...")
    await mock_robokassa_response(test_user_id)
    
    print("\n3. Testing subscription check...")
    await check_subscriptions()
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(start())
