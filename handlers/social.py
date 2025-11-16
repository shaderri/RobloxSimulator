from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db_manager import add_friend, create_post
import re

router = Router()


@router.message(Command("AddFriend"))
async def cmd_add_friend(message: Message):
    """Добавить друга"""
    
    # Парсинг команды: /AddFriend <Ник> <@username>
    try:
        parts = message.text.split(maxsplit=2)
        
        if len(parts) < 3:
            await message.answer(
                "📝 <b>Использование:</b>\n"
                "<code>/AddFriend Никнейм @username</code>"
            )
            return
        
        nickname = parts[1]
        username = parts[2]
        
        # Удаляем @ если есть
        username = username.replace('@', '')
        
        # Сохраняем в БД
        add_friend(message.from_user.id, nickname, username)
        
        await message.answer(
            f"✅ <b>Запрос на добавление в друзья «{nickname}» (@{username})</b>"
        )
        
    except Exception as e:
        await message.answer(
            "❌ Ошибка при добавлении друга.\n"
            "Используйте формат: <code>/AddFriend Никнейм @username</code>"
        )


@router.message(Command("Post"))
async def cmd_post(message: Message):
    """Опубликовать пост"""
    
    # Получаем текст поста
    text = message.text.replace('/Post', '', 1).strip()
    
    if not text:
        await message.answer(
            "📝 <b>Использование:</b>\n"
            "<code>/Post Текст вашего поста</code>"
        )
        return
    
    # Создаём пост и получаем реакции
    reactions = create_post(
        message.from_user.id,
        message.from_user.username or "Unknown",
        text
    )
    
    # Форматируем вывод
    post_text = f"""
✅ <b>Ваш пост был опубликован</b>

«{text}»

{reactions['shrug']:,}🤷‍♂️ / {reactions['wow']:,}😱 / {reactions['christmas']:,}🎄
{reactions['comments']:,}💬
"""
    
    await message.answer(post_text)