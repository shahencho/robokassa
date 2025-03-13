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
        logger.info(f"Non-admin user {update.effective_user.id} attempted to use admin command")
        return ConversationHandler.END
    
    await update.message.reply_text(MESSAGES["admin_help"])
    logger.info(f"Admin {update.effective_user.id} viewed admin help")
    return ConversationHandler.END

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered users"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["not_admin"])
        logger.info(f"Non-admin user {update.effective_user.id} attempted to use admin command")
        return ConversationHandler.END

    users = JsonHandler.load_data(USERS_FILE)
    if not users:
        response = "Пользователи не найдены в базе данных"
        await update.message.reply_text(response)
        logger.info(f"Admin {update.effective_user.id} viewed empty user list")
        return ConversationHandler.END

    response = "Зарегистрированные пользователи:\n\n"
    for user_id, user_data in users.items():
        status = "Активна" if SubscriptionManager.is_subscription_active(int(user_id)) else "Неактивна"
        response += f"ID: {user_id}\nПользователь: @{user_data.get('username', 'N/A')}\nСтатус: {status}\n\n"

    await update.message.reply_text(response)
    logger.info(f"Admin {update.effective_user.id} viewed user list:\n{response}")
    return ConversationHandler.END

async def manage_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start user management process"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["not_admin"])
        logger.info(f"Non-admin user {update.effective_user.id} attempted to manage users")
        return ConversationHandler.END

    try:
        user_id = int(update.message.text.split()[1])
        user_data = JsonHandler.get_user(user_id)
        if not user_data:
            await update.message.reply_text(MESSAGES["user_not_found"])
            logger.info(f"Admin {update.effective_user.id} attempted to manage non-existent user {user_id}")
            return ConversationHandler.END

        context.user_data['selected_user_id'] = user_id
        
        # Create inline keyboard
        keyboard = [
            [InlineKeyboardButton("Деактивировать подписку", callback_data=f"expire_{user_id}")],
            [InlineKeyboardButton("Отмена", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = f"Информация о пользователе:\nID: {user_id}\nПользователь: @{user_data.get('username', 'N/A')}\n"
        response += f"Тариф: {user_data.get('subscription_type', 'Нет')}\n"
        response += f"Статус: {'Активна' if SubscriptionManager.is_subscription_active(user_id) else 'Неактивна'}"
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        logger.info(f"Admin {update.effective_user.id} viewing user details:\n{response}")
        return SELECTING_ACTION
    except (IndexError, ValueError):
        await update.message.reply_text(MESSAGES["invalid_user_id"])
        logger.info(f"Admin {update.effective_user.id} provided invalid user ID")
        return ConversationHandler.END

async def handle_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user management actions"""
    query = update.callback_query
    await query.answer()
    
    if update.effective_user.id not in ADMIN_IDS:
        await query.message.reply_text(MESSAGES["not_admin"])
        logger.info(f"Non-admin user {update.effective_user.id} attempted to use admin callback")
        return ConversationHandler.END

    if query.data == "cancel":
        await query.message.reply_text(MESSAGES["operation_cancelled"])
        logger.info(f"Admin {update.effective_user.id} cancelled operation")
        return ConversationHandler.END
    
    if query.data.startswith("expire_"):
        try:
            user_id = int(query.data.split("_")[1])
            logger.info(f"Admin {update.effective_user.id} expiring subscription for user {user_id}")
            await SubscriptionManager.expire_subscription(user_id)
            await query.message.reply_text(MESSAGES["subscription_expired_admin"])
            logger.info(f"Admin {update.effective_user.id} expired subscription for user {user_id}")
            
            # Show updated user status
            user_data = JsonHandler.get_user(user_id)
            status_response = f"Обновленный статус пользователя:\nID: {user_id}\nПользователь: @{user_data.get('username', 'N/A')}\n"
            status_response += f"Тариф: {user_data.get('subscription_type', 'Нет')}\n"
            status_response += f"Статус: Неактивна"
            await query.message.reply_text(status_response)
            logger.info(f"Updated user status:\n{status_response}")
            
        except Exception as e:
            response = MESSAGES["error_removing_from_group"].format(error=str(e))
            await query.message.reply_text(response)
            logger.error(f"Error expiring subscription: {e}")
    
    return ConversationHandler.END

# Create conversation handler
admin_handler = ConversationHandler(
    entry_points=[CommandHandler("manage_user", manage_user_start)],
    states={
        SELECTING_ACTION: [
            CallbackQueryHandler(handle_user_action, pattern="^(expire_|cancel)")
        ]
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
) 