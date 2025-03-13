from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden

from config import MESSAGES, SUBSCRIPTION_TYPES
from utils.json_handler import JsonHandler
from utils.subscription_manager import SubscriptionManager

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
    await update.message.reply_text(status_message)
    return ConversationHandler.END

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command"""
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
        await query.message.reply_text("Invalid selection. Please try again.")
        return ConversationHandler.END
    
    subscription_type = query.data.split("_")[1]
    user_id = query.from_user.id
    
    try:
        # Create subscription
        subscription_id = SubscriptionManager.create_subscription(user_id, subscription_type)
        
        # Get groups for this subscription
        groups = SUBSCRIPTION_TYPES[subscription_type]["groups"]
        
        # Create invite links for each group
        invite_links = []
        for group_id in groups:
            try:
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=group_id,
                    member_limit=1,
                    expire_date=int(query.message.date.timestamp()) + 24 * 60 * 60
                )
                invite_links.append(f"- {invite_link.invite_link}")
            except Exception as e:
                print(f"Error creating invite link for group {group_id}: {e}")
                continue
        
        # Send success message with invite links
        success_message = MESSAGES["subscription_success"].format(
            invite_links="\n".join(invite_links)
        )
        await query.message.reply_text(success_message)
        
    except Exception as e:
        await query.message.reply_text(f"Error creating subscription: {str(e)}")
    
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