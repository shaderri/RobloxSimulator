import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# ID администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))

# Путь к базе данных
DB_PATH = 'database/roblox_bot.db'

# Настройки
DEFAULT_BALANCE = 1000
DEFAULT_PREMIUM = False