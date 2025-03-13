import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from config import DATA_DIR, USERS_FILE, SUBSCRIPTIONS_FILE, GROUPS_FILE

class JsonHandler:
    @staticmethod
    def ensure_data_dir():
        """Ensure data directory exists"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    @staticmethod
    def load_data(file_path: str) -> Dict:
        """Load data from JSON file"""
        JsonHandler.ensure_data_dir()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_data(file_path: str, data: Dict):
        """Save data to JSON file"""
        JsonHandler.ensure_data_dir()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_user(user_id: int) -> Optional[Dict]:
        """Get user data"""
        users = JsonHandler.load_data(USERS_FILE)
        return users.get(str(user_id))

    @staticmethod
    def save_user(user_id: int, user_data: Dict):
        """Save user data"""
        users = JsonHandler.load_data(USERS_FILE)
        users[str(user_id)] = user_data
        JsonHandler.save_data(USERS_FILE, users)

    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict]:
        """Get subscription data"""
        subscriptions = JsonHandler.load_data(SUBSCRIPTIONS_FILE)
        return subscriptions.get(subscription_id)

    @staticmethod
    def save_subscription(subscription_id: str, subscription_data: Dict):
        """Save subscription data"""
        subscriptions = JsonHandler.load_data(SUBSCRIPTIONS_FILE)
        subscriptions[subscription_id] = subscription_data
        JsonHandler.save_data(SUBSCRIPTIONS_FILE, subscriptions)

    @staticmethod
    def get_group(group_id: int) -> Optional[Dict]:
        """Get group data"""
        groups = JsonHandler.load_data(GROUPS_FILE)
        return groups.get(str(group_id))

    @staticmethod
    def save_group(group_id: int, group_data: Dict):
        """Save group data"""
        groups = JsonHandler.load_data(GROUPS_FILE)
        groups[str(group_id)] = group_data
        JsonHandler.save_data(GROUPS_FILE, groups)

    @staticmethod
    def create_subscription_id(user_id: int) -> str:
        """Create unique subscription ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"sub_{user_id}_{timestamp}" 