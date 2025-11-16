from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.db_manager import create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    
    # Создаём пользователя в БД
    create_user(message.from_user.id, message.from_user.username or "Unknown")
    
    welcome_text = f"""
🎮 <b>Добро пожаловать в Roblox Simulator!</b>

Привет, <b>{message.from_user.first_name}</b>!

📋 <b>Доступные команды:</b>

<b>👤 Аккаунт:</b>
/myaccount - Ваш Roblox аккаунт
/balance - Текущий баланс

<b>👥 Социальное:</b>
/AddFriend - Добавить друга
/Post - Опубликовать пост

<b>🛠 Roblox Studio:</b>
/RobloxStudio - Меню создания контента
/creategame - Создать игру
/mygame - Статистика игры
/creategroup - Создать группу

Начните с настройки вашего аккаунта командой /myaccount!
"""
    
    await message.answer(welcome_text)