from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden

from config import ADMIN_IDS, MESSAGES
from utils.json_handler import JsonHandler
from utils.subscription_manager import SubscriptionManager

# Conversation states
SELECTING_USER = 1
SELECTING_ACTION = 2

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    await update.message.reply_text(MESSAGES["admin_help"])
    return ConversationHandler.END

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list_users command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    users = JsonHandler.load_data("users.json")
    if not users:
        await update.message.reply_text("No users found.")
        return ConversationHandler.END
    
    message = "Registered users:\n\n"
    for user_id, user_data in users.items():
        subscription = SubscriptionManager.get_user_subscription(int(user_id))
        status = "Active" if subscription and SubscriptionManager.is_subscription_active(int(user_id)) else "Inactive"
        message += f"ID: {user_id}\nUsername: @{user_data.get('username', 'N/A')}\nStatus: {status}\n\n"
    
    await update.message.reply_text(message)
    return ConversationHandler.END

async def manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /manage_user command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    try:
        user_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid user ID: /manage_user <user_id>")
        return ConversationHandler.END
    
    user_data = JsonHandler.get_user(user_id)
    if not user_data:
        await update.message.reply_text("User not found.")
        return ConversationHandler.END
    
    subscription = SubscriptionManager.get_user_subscription(user_id)
    status = "Active" if subscription and SubscriptionManager.is_subscription_active(user_id) else "Inactive"
    
    keyboard = [
        [InlineKeyboardButton("Expire Subscription", callback_data=f"expire_{user_id}")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
User details:
ID: {user_id}
Username: @{user_data.get('username', 'N/A')}
Status: {status}
"""
    await update.message.reply_text(message, reply_markup=reply_markup)
    return SELECTING_ACTION

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.message.reply_text("You are not authorized to use admin commands.")
        return ConversationHandler.END
    
    if query.data == "cancel":
        await query.message.reply_text("Operation cancelled.")
        return ConversationHandler.END
    
    if query.data.startswith("expire_"):
        try:
            user_id = int(query.data.split("_")[1])
            SubscriptionManager.expire_subscription(user_id)
            await query.message.reply_text(f"Subscription expired for user {user_id}")
        except Exception as e:
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