from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("robloxstudio"))
async def cmd_roblox_studio(message: Message):
    """Меню Roblox Studio"""
    
    studio_text = """
🛠 <b>Добро пожаловать в Roblox Studio!</b>

━━━━━━━━━━━━━━━━━━━━

<b>Создавайте свой контент:</b>

🎮 /creategame — Создать игру
💎 /createlimited — Создать Limited (скоро)
👥 /creategroup — Создать группу
🎨 /createavatar — Настроить аватар (скоро)

━━━━━━━━━━━━━━━━━━━━

<i>💡 Создавайте уникальный контент и зарабатывайте Robux!</i>
"""
    
    await message.answer(studio_text)