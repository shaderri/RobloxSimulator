from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db_manager import update_game_status, get_pending_game, get_user
from config import ADMIN_ID
from handlers.game import pending_games

router = Router()


@router.message(Command("yes"))
async def cmd_approve_game(message: Message):
    """Одобрить игру (только для админа)"""
    
    # Проверка прав админа
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        # Парсим ID игры из команды /yes_123
        command_parts = message.text.split('_')
        
        if len(command_parts) < 2:
            await message.answer("❌ Используйте формат: /yes_ID")
            return
        
        game_id = int(command_parts[1])
        
        # Получаем игру
        game = get_pending_game(game_id)
        
        if not game:
            await message.answer("❌ Игра не найдена")
            return
        
        # Одобряем игру
        update_game_status(game_id, 'approved')
        
        await message.answer(f"✅ Игра «{game[4]}» одобрена!")
        
        # Уведомляем пользователя
        user_id = game[1]
        
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"✅ <b>Ваша игра «{game[4]}» одобрена!</b>\n\n"
                     f"Теперь вы можете посмотреть статистику: /mygame {game[4]}"
            )
        except:
            pass
        
        # Удаляем из pending
        if game_id in pending_games:
            del pending_games[game_id]
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("no"))
async def cmd_reject_game(message: Message):
    """Отклонить игру (только для админа)"""
    
    # Проверка прав админа
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        # Парсим ID игры из команды /no_123
        command_parts = message.text.split('_')
        
        if len(command_parts) < 2:
            await message.answer("❌ Используйте формат: /no_ID")
            return
        
        game_id = int(command_parts[1])
        
        # Получаем игру
        game = get_pending_game(game_id)
        
        if not game:
            await message.answer("❌ Игра не найдена")
            return
        
        # Отклоняем игру
        update_game_status(game_id, 'rejected')
        
        await message.answer(f"❌ Игра «{game[4]}» отклонена!")
        
        # Уведомляем пользователя
        user_id = game[1]
        
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"❌ <b>Ваша игра «{game[4]}» была отклонена</b>\n\n"
                     "Попробуйте создать новую игру с учётом правил."
            )
        except:
            pass
        
        # Удаляем из pending
        if game_id in pending_games:
            del pending_games[game_id]
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")