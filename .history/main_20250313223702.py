import logging
from telegram.ext import Application, CommandHandler, ConversationHandler

from config import BOT_TOKEN, MESSAGES
from handlers.user import start, help_command, status, subscription_handler
from handlers.admin import admin_command, list_users, admin_handler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def error_handler(update, context):
    """Handle errors"""
    logging.error(f"Update {update} caused error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Please try again later."
        )

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(subscription_handler)
    
    # Admin handlers
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("list_users", list_users))
    application.add_handler(admin_handler)

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
