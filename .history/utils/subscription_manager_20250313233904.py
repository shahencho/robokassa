import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Bot
import logging

from config import SUBSCRIPTION_TYPES, BOT_TOKEN
from utils.json_handler import JsonHandler

# Set up logging
logger = logging.getLogger(__name__)

class SubscriptionManager:
    @staticmethod
    def create_subscription(user_id: int, subscription_type: str) -> str:
        """Create a new subscription"""
        if subscription_type not in SUBSCRIPTION_TYPES:
            raise ValueError(f"Invalid subscription type: {subscription_type}")

        # Create subscription ID
        subscription_id = JsonHandler.create_subscription_id(user_id)
        
        # Calculate subscription dates
        start_date = int(time.time())
        duration_days = SUBSCRIPTION_TYPES[subscription_type]["duration_days"]
        end_date = start_date + (duration_days * 24 * 60 * 60)

        # Create subscription data
        subscription_data = {
            "user_id": user_id,
            "type": subscription_type,
            "start_date": start_date,
            "end_date": end_date,
            "status": "active"
        }

        # Save subscription
        JsonHandler.save_subscription(subscription_id, subscription_data)

        # Update user data
        user_data = JsonHandler.get_user(user_id) or {}
        user_data.update({
            "subscription_id": subscription_id,
            "subscription_type": subscription_type,
            "subscription_start": start_date,
            "subscription_end": end_date
        })
        JsonHandler.save_user(user_id, user_data)

        return subscription_id

    @staticmethod
    def get_user_subscription(user_id: int) -> Optional[Dict]:
        """Get user's active subscription"""
        user_data = JsonHandler.get_user(user_id)
        if not user_data or "subscription_id" not in user_data:
            return None

        subscription_id = user_data["subscription_id"]
        subscription = JsonHandler.get_subscription(subscription_id)
        
        if not subscription or subscription["status"] != "active":
            return None

        return subscription

    @staticmethod
    def is_subscription_active(user_id: int) -> bool:
        """Check if user has active subscription"""
        subscription = SubscriptionManager.get_user_subscription(user_id)
        if not subscription:
            return False

        current_time = int(time.time())
        return subscription["end_date"] > current_time

    @staticmethod
    def get_subscription_groups(user_id: int) -> List[int]:
        """Get list of groups user has access to"""
        subscription = SubscriptionManager.get_user_subscription(user_id)
        if not subscription:
            return []

        subscription_type = subscription["type"]
        return SUBSCRIPTION_TYPES[subscription_type]["groups"]

    @staticmethod
    async def expire_subscription(user_id: int):
        """Mark user's subscription as expired and remove from groups"""
        user_data = JsonHandler.get_user(user_id)
        if not user_data or "subscription_id" not in user_data:
            logger.warning(f"No subscription found for user {user_id}")
            return

        subscription_id = user_data["subscription_id"]
        subscription = JsonHandler.get_subscription(subscription_id)
        if subscription:
            # Get groups before marking subscription as expired
            subscription_type = subscription["type"]
            groups = SUBSCRIPTION_TYPES[subscription_type]["groups"]
            logger.info(f"User {user_id} has access to groups: {groups}")
            
            # Remove user from all groups
            bot = Bot(token=BOT_TOKEN)
            for group_id in groups:
                try:
                    logger.info(f"Attempting to remove user {user_id} from group {group_id}")
                    # First try to get chat member to check if user is in the group
                    try:
                        member = await bot.get_chat_member(chat_id=group_id, user_id=user_id)
                        if member.status in ['left', 'kicked', 'banned']:
                            logger.info(f"User {user_id} is already not in group {group_id}")
                            continue
                    except Exception as e:
                        logger.warning(f"Could not get chat member status for user {user_id} in group {group_id}: {e}")
                        continue

                    # Try to remove user
                    try:
                        await bot.ban_chat_member(
                            chat_id=group_id,
                            user_id=user_id,
                            until_date=datetime.now() + timedelta(seconds=35)  # Temporary ban
                        )
                        await bot.unban_chat_member(
                            chat_id=group_id,
                            user_id=user_id
                        )
                        logger.info(f"Successfully removed user {user_id} from group {group_id}")
                    except Exception as e:
                        logger.error(f"Failed to remove user {user_id} from group {group_id}: {e}")
                        # Try alternative method if first method fails
                        try:
                            await bot.ban_chat_member(
                                chat_id=group_id,
                                user_id=user_id,
                                until_date=datetime.now() + timedelta(seconds=1)  # Very short ban
                            )
                            logger.info(f"Successfully removed user {user_id} from group {group_id} using alternative method")
                        except Exception as e2:
                            logger.error(f"Alternative removal method also failed for user {user_id} in group {group_id}: {e2}")
                except Exception as e:
                    logger.error(f"Error in group removal process for user {user_id} in group {group_id}: {e}")

            # Mark subscription as expired after attempting to remove from groups
            subscription["status"] = "expired"
            JsonHandler.save_subscription(subscription_id, subscription)
            logger.info(f"Marked subscription {subscription_id} as expired for user {user_id}") 