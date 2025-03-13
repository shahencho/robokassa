from typing import Dict, List

# Bot settings
BOT_TOKEN = "7369759089:AAHNhRi7engGeoEujYBO6Y4WhYNYSM2dmx0"

# Group IDs for access control
GROUP_IDS = [-4652743742, -4644237809, -4690219028]  # [test_group1, test_group2, test_group3]

# Subscription groups mapping:
# -4652743742 - Test Group 1 (replaces robo1)
# -4644237809 - Test Group 2
# -4690219028 - Test Group 3

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
Добро пожаловать в наш бот подписок! 🎉

Мы предлагаем два тарифных плана:

1. Тариф "Начальный" ($10/месяц)
   - Доступ к 2 премиум группам
   - Подписка на 30 дней

2. Тариф "Про" ($10/месяц)
   - Доступ ко всем 3 премиум группам
   - Подписка на 30 дней

Используйте /subscribe чтобы оформить подписку!
    """,
    "subscription_success": """
🎉 Оплата прошла успешно! 

Вот ваши пригласительные ссылки для входа в группы:
{invite_links}

Пожалуйста, нажмите на каждую ссылку, чтобы присоединиться к группам. Ссылки действительны в течение 24 часов.

Используйте /status чтобы проверить статус вашей подписки.
    """,
    "subscription_expired": """
⚠️ Срок действия вашей подписки истек!

Используйте /subscribe чтобы продлить подписку и восстановить доступ к группам.
    """,
    "help": """
Доступные команды:
/start - Запустить бота
/subscribe - Начать процесс подписки
/status - Проверить статус подписки
/help - Показать это сообщение помощи
    """,
    "admin_help": """
Команды администратора:
/list_users - Список всех пользователей
/manage_user <user_id> - Управление подпиской пользователя
    """,
    "not_admin": "У вас нет прав администратора для использования этой команды.",
    "subscription_status_active": """
Статус вашей подписки:
Тип: {subscription_type}
Статус: Активна
Дата окончания: {end_date}
    """,
    "subscription_status_inactive": """
У вас нет активной подписки.
Используйте /subscribe чтобы оформить подписку.
    """,
    "subscription_choose": """
Выберите тарифный план:

1. Начальный ($10/месяц)
   - Доступ к 2 премиум группам
   - Подписка на 30 дней

2. Про ($10/месяц)
   - Доступ ко всем 3 премиум группам
   - Подписка на 30 дней
    """,
    "payment_success": "🎉 Оплата успешно обработана!",
    "payment_cancelled": "❌ Оплата отменена. Попробуйте снова с помощью команды /subscribe",
    "payment_error": "⚠️ Произошла ошибка при обработке оплаты. Пожалуйста, попробуйте позже.",
    "user_not_found": "Пользователь не найден.",
    "invalid_user_id": "Пожалуйста, укажите корректный ID пользователя.",
    "operation_cancelled": "Операция отменена.",
    "subscription_expired_admin": "Подписка пользователя успешно деактивирована.",
    "error_removing_from_group": "Ошибка при удалении пользователя из группы: {error}"
} 