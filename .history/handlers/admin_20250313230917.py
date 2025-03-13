from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden
import logging

from config import ADMIN_IDS, MESSAGES, USERS_FILE
from utils.json_handler import JsonHandler
from utils.subscription_manager import SubscriptionManager

# Set up logging
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_USER = 1
SELECTING_ACTION = 2

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        logger.warning(f"Non-admin user {user_id} attempted to use admin command")
        await update.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    logger.info(f"Admin {user_id} accessed admin help")
    await update.message.reply_text(MESSAGES["admin_help"])
    return ConversationHandler.END

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list_users command"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        logger.warning(f"Non-admin user {user_id} attempted to list users")
        await update.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    logger.info(f"Admin {user_id} requested user list")
    users = JsonHandler.load_data(USERS_FILE)
    if not users:
        logger.info("No users found in database")
        await update.message.reply_text("No users found.")
        return ConversationHandler.END
    
    message = "Registered users:\n\n"
    for user_id, user_data in users.items():
        subscription = SubscriptionManager.get_user_subscription(int(user_id))
        status = "Active" if subscription and SubscriptionManager.is_subscription_active(int(user_id)) else "Inactive"
        message += f"ID: {user_id}\nUsername: @{user_data.get('username', 'N/A')}\nStatus: {status}\n\n"
    
    logger.info(f"Admin {update.effective_user.id} viewed user list with {len(users)} users")
    await update.message.reply_text(message)
    return ConversationHandler.END

async def manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /manage_user command"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        logger.warning(f"Non-admin user {user_id} attempted to manage users")
        await update.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    try:
        target_user_id = int(context.args[0])
        logger.info(f"Admin {user_id} attempting to manage user {target_user_id}")
    except (IndexError, ValueError):
        logger.warning(f"Admin {user_id} provided invalid user ID")
        await update.message.reply_text("Please provide a valid user ID: /manage_user <user_id>")
        return ConversationHandler.END
    
    user_data = JsonHandler.get_user(target_user_id)
    if not user_data:
        logger.warning(f"Admin {user_id} attempted to manage non-existent user {target_user_id}")
        await update.message.reply_text("User not found.")
        return ConversationHandler.END
    
    subscription = SubscriptionManager.get_user_subscription(target_user_id)
    status = "Active" if subscription and SubscriptionManager.is_subscription_active(target_user_id) else "Inactive"
    
    keyboard = [
        [InlineKeyboardButton("Expire Subscription", callback_data=f"expire_{target_user_id}")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
User details:
ID: {target_user_id}
Username: @{user_data.get('username', 'N/A')}
Status: {status}
"""
    logger.info(f"Admin {user_id} viewing details for user {target_user_id}")
    await update.message.reply_text(message, reply_markup=reply_markup)
    return SELECTING_ACTION

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Non-admin user {user_id} attempted to use admin callback")
        await query.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    if query.data == "cancel":
        logger.info(f"Admin {user_id} cancelled operation")
        await query.message.reply_text("Operation cancelled.")
        return ConversationHandler.END
    
    if query.data.startswith("expire_"):
        try:
            target_user_id = int(query.data.split("_")[1])
            logger.info(f"Admin {user_id} expiring subscription for user {target_user_id}")
            SubscriptionManager.expire_subscription(target_user_id)
            await query.message.reply_text(f"Subscription expired for user {target_user_id}")
            logger.info(f"Successfully expired subscription for user {target_user_id}")
        except Exception as e:
            logger.error(f"Error expiring subscription: {e}")
            await query.message.reply_text(f"Error expiring subscription: {str(e)}")
    
    return ConversationHandler.END

# Create conversation handler
admin_handler = ConversationHandler(
    entry_points=[CommandHandler("manage_user", manage_user)],
    states={
        SELECTING_ACTION: [
            CallbackQueryHandler(admin_callback, pattern="^(expire_|cancel)")
        ]
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
) 