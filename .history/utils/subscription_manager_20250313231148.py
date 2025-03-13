import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config import SUBSCRIPTION_TYPES
from utils.json_handler import JsonHandler

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
    def expire_subscription(user_id: int):
        """Mark user's subscription as expired"""
        user_data = JsonHandler.get_user(user_id)
        if not user_data or "subscription_id" not in user_data:
            return

        subscription_id = user_data["subscription_id"]
        subscription = JsonHandler.get_subscription(subscription_id)
        if subscription:
            subscription["status"] = "expired"
            JsonHandler.save_subscription(subscription_id, subscription) 