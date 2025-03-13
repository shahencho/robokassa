7369759089:AAHNhRi7engGeoEujYBO6Y4WhYNYSM2dmx0

from telegram import Bot
from telegram.error import BadRequest
import time

# Telegram bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Group IDs for access control
GROUP_IDS = [-4657917032, -4644237809, -4690219028]

# Mock database for user subscriptions
USER_SUBSCRIPTIONS = {}

# Initialize bot
bot = Bot(token=BOT_TOKEN)

def add_user_to_groups(user_id: int):
    """Adds a user to all predefined Telegram groups."""
    for group_id in GROUP_IDS:
        try:
            bot.add_chat_member(chat_id=group_id, user_id=user_id)
            print(f"User {user_id} added to group {group_id}")
        except BadRequest as e:
            print(f"Error adding user {user_id} to group {group_id}: {e}")

def remove_user_from_groups(user_id: int):
    """Removes a user from all predefined Telegram groups."""
    for group_id in GROUP_IDS:
        try:
            bot.kick_chat_member(chat_id=group_id, user_id=user_id)
            print(f"User {user_id} removed from group {group_id}")
        except BadRequest as e:
            print(f"Error removing user {user_id} from group {group_id}: {e}")

def mock_robokassa_response(user_id: int):
    """Mocks a successful payment response from Robokassa."""
    print(f"[Mock] Payment received for user {user_id}")
    USER_SUBSCRIPTIONS[user_id] = time.time() + (30 * 24 * 60 * 60)  # Subscription valid for 30 days
    add_user_to_groups(user_id)

def check_subscriptions():
    """Checks and removes expired users from groups."""
    current_time = time.time()
    expired_users = [user_id for user_id, expiry in USER_SUBSCRIPTIONS.items() if expiry < current_time]
    for user_id in expired_users:
        remove_user_from_groups(user_id)
        del USER_SUBSCRIPTIONS[user_id]
        print(f"Subscription expired for user {user_id}, removed from groups.")

# Example usage
# mock_robokassa_response(123456789)  # Simulate payment and add user
# check_subscriptions()  # Check and remove expired users
