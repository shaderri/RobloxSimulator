from aiogram import Router, F
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
                "<code>/addfriend Никнейм @username</code>\n\n"
                "Пример: <code>/addfriend BuilderBob @bob123</code>"
            )
            return
        
        nickname = parts[1]
        username = parts[2].replace('@', '')
        
        add_friend(message.from_user.id, nickname, username)
        
        await message.answer(
            f"✅ <b>Запрос на добавление в друзья отправлен!</b>\n\n"
            f"👤 Игрок: <b>{nickname}</b>\n"
            f"📱 Telegram: @{username}\n\n"
            f"<i>Ожидайте подтверждения...</i>"
        )
        
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка при добавлении друга</b>\n\n"
            "Используйте формат:\n"
            "<code>/addfriend Никнейм @username</code>"
        )


@router.message(Command("post"))
async def cmd_post(message: Message):
    """Опубликовать пост"""
    
    text = message.text.replace('/post', '', 1).strip()
    
    if not text:
        await message.answer(
            "📝 <b>Создание поста</b>\n\n"
            "Используйте:\n"
            "<code>/post Текст вашего поста</code>\n\n"
            "Пример:\n"
            "<code>/post Создал новую игру! Заходите играть! 🎮</code>"
        )
        return
    
    reactions = create_post(
        message.from_user.id,
        message.from_user.username or "RobloxPlayer",
        text
    )
    
    post_text = f"""
✅ <b>Пост опубликован!</b>

━━━━━━━━━━━━━━━
📝 <b>Ваш пост:</b>

{text}
━━━━━━━━━━━━━━━

📊 <b>Статистика:</b>
😂 {reactions['laugh']:,} | 😍 {reactions['love']:,} | 🔥 {reactions['fire']:,}
💬 {reactions['comments']:,} комментариев

<i>Ваш пост появился в ленте Roblox!</i>
"""
    
    await message.answer(post_text)