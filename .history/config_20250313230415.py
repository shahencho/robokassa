from typing import Dict, List

# Bot settings
BOT_TOKEN = "7369759089:AAHNhRi7engGeoEujYBO6Y4WhYNYSM2dmx0"

# Group IDs for access control
GROUP_IDS = [-4657917032, -4644237809, -4690219028]

# Admin user IDs (you can add your admin IDs here)
ADMIN_IDS: List[int] = [344431796, 449708378]  # Added both admin IDs

# Subscription types and their configurations
SUBSCRIPTION_TYPES: Dict[str, Dict] = {
    "beginner": {
        "price": 10,
        "duration_days": 30,
        "groups": GROUP_IDS[:2]  # First two groups
    },
    "pro": {
        "price": 10,
        "duration_days": 30,
        "groups": GROUP_IDS  # All groups
    }
}

# File paths for JSON storage
DATA_DIR = "data"
USERS_FILE = f"{DATA_DIR}/users.json"
SUBSCRIPTIONS_FILE = f"{DATA_DIR}/subscriptions.json"
GROUPS_FILE = f"{DATA_DIR}/groups.json"

# Bot messages
MESSAGES = {
    "welcome": """
Welcome to our subscription bot! 🎉

We offer two subscription plans:

1. Beginner Plan ($10/month)
   - Access to 2 premium groups
   - 30-day subscription

2. Pro Plan ($10/month)
   - Access to all 3 premium groups
   - 30-day subscription

Use /subscribe to start your subscription!
    """,
    "subscription_success": """
🎉 Payment successful! 

Here are your invite links to join the groups:
{invite_links}

Please click each link to join the groups. Links will expire in 24 hours.

Use /status to check your subscription status.
    """,
    "subscription_expired": """
⚠️ Your subscription has expired!

Use /subscribe to renew your subscription and regain access to the groups.
    """,
    "help": """
Available commands:
/start - Start the bot
/subscribe - Start subscription process
/status - Check subscription status
/help - Show this help message
    """,
    "admin_help": """
Admin Commands:
/list_users - List all registered users
/manage_user <user_id> - Manage a specific user's subscription
    """
} 