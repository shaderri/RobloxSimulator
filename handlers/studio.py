from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("RobloxStudio"))
async def cmd_roblox_studio(message: Message):
    """Меню Roblox Studio"""
    
    studio_text = """
🛠️ <b>Добро пожаловать в Roblox Studio</b>

Выберите, что хотите создать:

🎮 /creategame — Создать игру
🎨 /createlimited — Создать Limited (в разработке)
👥 /creategroup — Создать группу
"""
    
    await message.answer(studio_text)