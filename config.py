import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# ID администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))

# Путь к базе данных
DB_PATH = 'database/roblox_bot.db'

# Настройки Roblox (как в настоящем Roblox!)
DEFAULT_BALANCE = 0  # В Roblox новые аккаунты начинают с 0 Robux
DEFAULT_PREMIUM = False
DAILY_ROBUX_PREMIUM = 450  # Премиум игроки получают ежедневно
STARTER_ROBUX = 0  # Стартовые Robux