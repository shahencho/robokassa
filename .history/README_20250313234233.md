# Telegram Subscription Bot

A Telegram bot that manages paid subscriptions and group access for users.

## Features

- User registration and subscription management
- Two subscription tiers: Beginner and Pro
- Automatic group access management
- Admin panel for user management
- JSON-based data storage (can be migrated to MySQL later)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the bot:
   - Copy your bot token from @BotFather
   - Update the `BOT_TOKEN` in `config.py`
   - Add your admin Telegram IDs to `ADMIN_IDS` in `config.py`
   - Configure group IDs in `GROUP_IDS` in `config.py`

## Usage

### User Commands

- `/start` - Start the bot and register
- `/help` - Show help message
- `/status` - Check subscription status
- `/subscribe` - Subscribe to a plan

### Admin Commands

- `/admin` - Show admin help
- `/list_users` - List all registered users
- `/manage_user <user_id>` - Manage a specific user's subscription

## Data Storage

The bot currently uses JSON files for data storage:
- `data/users.json` - User information
- `data/subscriptions.json` - Subscription data
- `data/groups.json` - Group access data

## Future Improvements

- Migrate to MySQL database
- Add payment integration with Robokassa
- Implement subscription renewal notifications
- Add more admin features
- Add user statistics and analytics 