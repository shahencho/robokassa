import logging
from telegram.ext import Application, CommandHandler, ConversationHandler
from datetime import datetime
import sys

from config import BOT_TOKEN, MESSAGES
from handlers.user import start, help_command, status, subscription_handler
from handlers.admin import admin_command, list_users, admin_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Disable HTTP request logging
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def log_command(update, context, command_name):
    """Log command usage"""
    user = update.effective_user
    logger.info(f"Command /{command_name} used by user {user.id} (@{user.username})")

async def log_response(update, response_text):
    """Log bot response"""
    user = update.effective_user
    # Remove emojis for logging
    clean_text = response_text.encode('ascii', 'ignore').decode('ascii')
    logger.info(f"Bot response to user {user.id} (@{user.username}):\n{clean_text}")

async def error_handler(update, context):
    """Handle errors"""
    error_msg = f"Update {update} caused error: {context.error}"
    logger.error(error_msg)
    if update and update.effective_message:
        response = "An error occurred. Please try again later."
        await update.effective_message.reply_text(response)
        await log_response(update, response)

def main():
    """Start the bot"""
    logger.info("Starting bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers with logging
    async def logged_start(update, context):
        await log_command(update, context, "start")
        response = await start(update, context)
        await log_response(update, MESSAGES["welcome"])
        return response

    async def logged_help(update, context):
        await log_command(update, context, "help")
        response = await help_command(update, context)
        await log_response(update, MESSAGES["help"])
        return response

    async def logged_status(update, context):
        await log_command(update, context, "status")
        response = await status(update, context)
        return response

    async def logged_admin(update, context):
        await log_command(update, context, "admin")
        response = await admin_command(update, context)
        await log_response(update, MESSAGES["admin_help"])
        return response

    async def logged_list_users(update, context):
        await log_command(update, context, "list_users")
        response = await list_users(update, context)
        return response

    # Add handlers
    application.add_handler(CommandHandler("start", logged_start))
    application.add_handler(CommandHandler("help", logged_help))
    application.add_handler(CommandHandler("status", logged_status))
    application.add_handler(subscription_handler)
    
    # Admin handlers
    application.add_handler(CommandHandler("admin", logged_admin))
    application.add_handler(CommandHandler("list_users", logged_list_users))
    application.add_handler(admin_handler)

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot is ready to handle messages")
    application.run_polling()

if __name__ == '__main__':
    main()
