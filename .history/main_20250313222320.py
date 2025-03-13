from telegram import Bot
from telegram.ext import Application
from telegram.error import BadRequest, Forbidden
import time
import asyncio
import inspect

# Telegram bot token
BOT_TOKEN = "7369759089:AAHNhRi7engGeoEujYBO6Y4WhYNYSM2dmx0"

# Group IDs for access control
GROUP_IDS = [-4657917032, -4644237809, -4690219028]

# Mock database for user subscriptions
USER_SUBSCRIPTIONS = {}

# Add this at the top with other global variables
GROUP_INVITE_LINKS = {}

async def verify_groups(application: Application):
    """Verifies bot's access to groups and prints group information."""
    print("\nVerifying group access...")
    for group_id in GROUP_IDS:
        try:
            # Try to get chat information
            chat = await application.bot.get_chat(group_id)
            bot_member = await application.bot.get_chat_member(chat_id=group_id, user_id=application.bot.id)
            
            print(f"\nGroup: {chat.title} (ID: {group_id})")
            print(f"Type: {chat.type}")
            print(f"Bot is admin: {bot_member.status in ['administrator', 'creator']}")
            print(f"Can invite users: {bot_member.can_invite_users}")
            print(f"Can restrict members: {bot_member.can_restrict_members}")
            print(f"Bot status: {bot_member.status}")
            
            # Try to get group invite link to verify permissions
            try:
                invite_link = await application.bot.export_chat_invite_link(chat_id=group_id)
                print(f"Can create invite links: True")
            except Exception as e:
                print(f"Can create invite links: False (Error: {str(e)})")
                
        except BadRequest as e:
            print(f"\nError accessing group {group_id}: {e}")
            print("This might mean:")
            print("1. The bot is not a member of this group")
            print("2. The group ID is incorrect")
            print("3. The group no longer exists")
        except Exception as e:
            print(f"\nUnexpected error with group {group_id}: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {str(e)}")

async def create_permanent_invite_links(application: Application):
    """Creates and stores permanent invite links for all groups."""
    print("\nCreating permanent invite links for groups...")
    for group_id in GROUP_IDS:
        try:
            # Create a permanent invite link
            invite_link = await application.bot.create_chat_invite_link(
                chat_id=group_id,
                name=f"Permanent link for {group_id}",
                creates_join_request=True  # This means admins need to approve joins
            )
            GROUP_INVITE_LINKS[group_id] = invite_link.invite_link
            print(f"Created permanent invite link for group {group_id}")
        except Exception as e:
            print(f"Error creating invite link for group {group_id}: {e}")

async def add_user_to_groups(application: Application, user_id: int):
    """Adds a user to all predefined Telegram groups."""
    # First verify if we can contact the user
    try:
        # Try to send a test message to the user
        await application.bot.send_message(
            chat_id=user_id,
            text="Hello! This is a test message to verify I can contact you."
        )
        print(f"Successfully verified contact with user {user_id}")
    except BadRequest as e:
        print(f"Cannot contact user {user_id}. Error: {e}")
        print("This might mean:")
        print("1. The user has not started a conversation with the bot")
        print("2. The user ID is incorrect")
        print("3. The user has blocked the bot")
        print("\nTo join the groups, please:")
        print("1. Start a conversation with this bot by clicking 'Start' or sending any message")
        print("2. Then try the operation again")
        return
    except Exception as e:
        print(f"Unexpected error contacting user {user_id}: {e}")
        return

    # If we can contact the user, proceed with group invites
    for group_id in GROUP_IDS:
        try:
            # First check if bot is admin in the group
            bot_member = await application.bot.get_chat_member(chat_id=group_id, user_id=application.bot.id)
            if not bot_member.can_invite_users:
                print(f"Bot doesn't have permission to invite users in group {group_id}")
                continue
                
            # Create an invite link for the user
            invite_link = await application.bot.create_chat_invite_link(
                chat_id=group_id,
                member_limit=1,  # Limit to 1 user
                expire_date=int(time.time() + 3600)  # Link expires in 1 hour
            )
            
            # Send the invite link to the user
            await application.bot.send_message(
                chat_id=user_id,
                text=f"Here's your invite link to join the group: {invite_link.invite_link}"
            )
            print(f"Invite link sent to user {user_id} for group {group_id}")
            
        except BadRequest as e:
            print(f"Error creating invite link for user {user_id} in group {group_id}: {e}")
        except Forbidden as e:
            print(f"Bot doesn't have permission to create invite links in group {group_id}: {e}")
        except Exception as e:
            print(f"Unexpected error creating invite link for user {user_id} in group {group_id}: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {str(e)}")

async def remove_user_from_groups(application: Application, user_id: int):
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
            print(f"Error type: {type(e)}")
            print(f"Error details: {str(e)}")

async def mock_robokassa_response(application: Application, user_id: int):
    """Mocks a successful payment response from Robokassa."""
    print(f"[Mock] Payment received for user {user_id}")
    USER_SUBSCRIPTIONS[user_id] = time.time() + (30 * 24 * 60 * 60)  # Subscription valid for 30 days
    await add_user_to_groups(application, user_id)

async def check_subscriptions(application: Application):
    """Checks and removes expired users from groups."""
    current_time = time.time()
    expired_users = [user_id for user_id, expiry in USER_SUBSCRIPTIONS.items() if expiry < current_time]
    for user_id in expired_users:
        await remove_user_from_groups(application, user_id)
        del USER_SUBSCRIPTIONS[user_id]
        print(f"Subscription expired for user {user_id}, removed from groups.")

async def start():
    """Test function to demonstrate the bot's functionality."""
    print("Starting bot test...")
    
    # Initialize application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Start the application
    await application.initialize()
    await application.start()
    
    try:
        # First verify group access
        await verify_groups(application)
        
        # Create permanent invite links
        await create_permanent_invite_links(application)
        
        # Test user ID (you can change this to any valid Telegram user ID)
        test_user_id = 344431796
        
        print("\n1. Testing user addition to groups...")
        await add_user_to_groups(application, test_user_id)
        
        print("\n2. Testing subscription mock...")
        await mock_robokassa_response(application, test_user_id)
        
        print("\n3. Testing subscription check...")
        await check_subscriptions(application)
        
        print("\nTest completed!")
    finally:
        # Stop the application
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(start())
