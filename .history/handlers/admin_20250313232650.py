from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.error import BadRequest, Forbidden
import logging

from config import ADMIN_IDS, MESSAGES, USERS_FILE
from utils.json_handler import JsonHandler
from utils.subscription_manager import SubscriptionManager

# Set up logging
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_USER, SELECTING_ACTION = range(2)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin help command"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["not_admin"])
        return ConversationHandler.END
    
    await update.message.reply_text(MESSAGES["admin_help"])
    return ConversationHandler.END

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered users"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["not_admin"])
        return ConversationHandler.END

    users = JsonHandler.load_data(USERS_FILE)
    if not users:
        await update.message.reply_text("No users found in database")
        return ConversationHandler.END

    response = "Registered users:\n\n"
    for user_id, user_data in users.items():
        status = "Active" if SubscriptionManager.is_subscription_active(int(user_id)) else "Inactive"
        response += f"ID: {user_id}\nUsername: @{user_data.get('username', 'N/A')}\nStatus: {status}\n\n"

    await update.message.reply_text(response)
    return ConversationHandler.END

async def manage_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start user management process"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["not_admin"])
        return ConversationHandler.END

    try:
        user_id = int(update.message.text.split()[1])
        user_data = JsonHandler.get_user(user_id)
        if not user_data:
            await update.message.reply_text("User not found")
            return ConversationHandler.END

        context.user_data['selected_user_id'] = user_id
        response = f"User details:\nID: {user_id}\nUsername: @{user_data.get('username', 'N/A')}\n"
        response += f"Subscription: {user_data.get('subscription_type', 'None')}\n"
        response += f"Status: {'Active' if SubscriptionManager.is_subscription_active(user_id) else 'Inactive'}\n\n"
        response += "Actions:\n1. Expire subscription\n2. Cancel"
        
        await update.message.reply_text(response)
        return SELECTING_ACTION
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid user ID")
        return ConversationHandler.END

async def handle_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user management actions"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["not_admin"])
        return ConversationHandler.END

    user_id = context.user_data.get('selected_user_id')
    if not user_id:
        await update.message.reply_text("No user selected")
        return ConversationHandler.END

    try:
        action = int(update.message.text)
        if action == 1:
            await SubscriptionManager.expire_subscription(user_id)
            await update.message.reply_text(f"Successfully expired subscription for user {user_id}")
        elif action == 2:
            await update.message.reply_text("Operation cancelled")
        else:
            await update.message.reply_text("Invalid action")
    except ValueError:
        await update.message.reply_text("Please enter a valid number")
    finally:
        return ConversationHandler.END

# Create conversation handler
admin_handler = ConversationHandler(
    entry_points=[CommandHandler("manage_user", manage_user_start)],
    states={
        SELECTING_ACTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_action)
        ]
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
) 