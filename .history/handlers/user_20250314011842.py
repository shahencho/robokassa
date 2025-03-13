from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden
import logging

from config import MESSAGES, SUBSCRIPTION_TYPES
from utils.json_handler import JsonHandler
from utils.subscription_manager import SubscriptionManager

# Set up logging
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_SUBSCRIPTION = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    user_data = JsonHandler.get_user(user_id)
    
    if not user_data:
        # Create new user
        user_data = {
            "username": update.effective_user.username,
            "first_name": update.effective_user.first_name,
            "last_name": update.effective_user.last_name,
            "created_at": int(update.message.date.timestamp())
        }
        JsonHandler.save_user(user_id, user_data)
        logger.info(f"New user registered: {user_id} (@{user_data['username']})")

    await update.message.reply_text(MESSAGES["welcome"])
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(MESSAGES["help"])
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    subscription = SubscriptionManager.get_user_subscription(user_id)
    
    if not subscription:
        logger.info(f"User {user_id} checked status: No active subscription")
        await update.message.reply_text("You don't have an active subscription. Use /subscribe to get one!")
        return ConversationHandler.END

    # Calculate remaining days
    current_time = int(update.message.date.timestamp())
    remaining_days = (subscription["end_date"] - current_time) // (24 * 60 * 60)
    
    status_message = f"""
Your subscription status:
Type: {subscription['type'].title()}
Remaining days: {remaining_days}
"""
    logger.info(f"User {user_id} checked status: {subscription['type']} subscription, {remaining_days} days remaining")
    await update.message.reply_text(status_message)
    return ConversationHandler.END

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started subscription process")
    
    keyboard = []
    for sub_type, sub_data in SUBSCRIPTION_TYPES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{sub_type.title()} - ${sub_data['price']}/month",
                callback_data=f"sub_{sub_type}"
            )
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select your subscription plan:",
        reply_markup=reply_markup
    )
    return SELECTING_SUBSCRIPTION

async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription selection"""
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("sub_"):
        logger.warning(f"Invalid subscription selection from user {query.from_user.id}")
        await query.message.reply_text("Invalid selection. Please try again.")
        return ConversationHandler.END
    
    subscription_type = query.data.split("_")[1]
    user_id = query.from_user.id
    
    try:
        logger.info(f"User {user_id} selected {subscription_type} subscription")
        
        # Create subscription
        subscription_id = SubscriptionManager.create_subscription(user_id, subscription_type)
        logger.info(f"Created subscription {subscription_id} for user {user_id}")
        
        # Get groups for this subscription
        groups = SUBSCRIPTION_TYPES[subscription_type]["groups"]
        
        # Create invite links for each group
        invite_links = []
        for group_id in groups:
            try:
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=group_id,
                    member_limit=1,
                    creates_join_request=True,
                    expire_date=int(query.message.date.timestamp()) + 24 * 60 * 60
                )
                invite_links.append(f"- {invite_link.invite_link}")
                logger.info(f"Created invite link for group {group_id} for user {user_id}")
            except Exception as e:
                logger.error(f"Error creating invite link for group {group_id}: {e}")
                continue
        
        # Send success message with invite links
        success_message = MESSAGES["subscription_success"].format(
            invite_links="\n".join(invite_links)
        )
        await query.message.reply_text(success_message)
        logger.info(f"Subscription process completed for user {user_id}")
        
    except Exception as e:
        error_msg = f"Error creating subscription: {str(e)}"
        logger.error(f"Subscription error for user {user_id}: {e}")
        await query.message.reply_text(error_msg)
    
    return ConversationHandler.END

# Create conversation handler
subscription_handler = ConversationHandler(
    entry_points=[CommandHandler("subscribe", subscribe)],
    states={
        SELECTING_SUBSCRIPTION: [
            CallbackQueryHandler(subscription_callback, pattern="^sub_")
        ]
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
) 