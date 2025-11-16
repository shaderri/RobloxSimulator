from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db_manager import add_friend, create_post

router = Router()


@router.message(Command("addfriend"))
async def cmd_add_friend(message: Message):
    """Добавить друга"""
    
    try:
        parts = message.text.split(maxsplit=2)
        
        if len(parts) < 3:
            await message.answer(
                "📝 <b>Использование:</b>\n"
                "<code>/addfriend Никнейм @username</code>"
            )
            return
        
        nickname = parts[1]
        username = parts[2].replace('@', '')
        
        add_friend(message.from_user.id, nickname, username)
        
        await message.answer(
            f"<b>Запрос на добавление в друзья «{nickname}» (@{username})</b>"
        )
        
    except Exception as e:
        await message.answer(
            "❌ Ошибка при добавлении друга.\n"
            "Формат: <code>/addfriend Никнейм @username</code>"
        )


@router.message(Command("post"))
async def cmd_post(message: Message):
    """Опубликовать пост"""
    
    text = message.text.replace('/post', '', 1).strip()
    
    if not text:
        await message.answer(
            "📝 <b>Использование:</b>\n"
            "<code>/post Текст вашего поста</code>"
        )
        return
    
    reactions = create_post(
        message.from_user.id,
        message.from_user.username or "RobloxPlayer",
        text
    )
    
    # Формат ровно как в ТЗ
    post_text = f"""
<b>Ваш пост был опубликован ✅</b>

«{text}»

{reactions['shrug']:,}🤷‍♂️ / {reactions['shocked']:,}😱 / {reactions['christmas']:,}🎄
{reactions['comments']:,}💬
"""
    
    await message.answer(post_text)