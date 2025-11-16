from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("robloxstudio"))
async def cmd_roblox_studio(message: Message):
    """Меню Roblox Studio"""
    
    studio_text = """
<b>Добро пожаловать в Roblox Studio 🛠️</b>

1. /creategame
2. /createlimited
3. /creategroup
"""
    
    await message.answer(studio_text)