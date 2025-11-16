from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db_manager import update_game_status, get_pending_game
from config import ADMIN_ID
from handlers.game import pending_games

router = Router()  # ← ЭТА СТРОКА БЫЛА ПРОПУЩЕНА!


@router.message(Command("yes"))
async def cmd_approve_game(message: Message):
    """Одобрить игру"""
    
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        command_parts = message.text.split('_')
        
        if len(command_parts) < 2:
            await message.answer("❌ Используйте: /yes_ID")
            return
        
        game_id = int(command_parts[1])
        game = get_pending_game(game_id)
        
        if not game:
            await message.answer("❌ Игра не найдена")
            return
        
        update_game_status(game_id, 'approved')
        
        await message.answer(
            f"✅ <b>Игра одобрена и опубликована!</b>\n\n"
            f"🎮 <b>Название:</b> {game[4]}\n"
            f"👤 <b>Создатель:</b> @{game[2]}\n\n"
            f"🤖 <i>Игра заполняется искусственными игроками...</i>"
        )
        
        user_id = game[1]
        
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"✅ <b>Ваша игра «{game[4]}» одобрена!</b>\n\n"
                     f"🎉 Игра опубликована и доступна!\n"
                     f"🤖 Искусственные игроки начали играть\n\n"
                     f"📊 Посмотреть статистику:\n"
                     f"<code>/mygame {game[4]}</code>"
            )
        except:
            pass
        
        if game_id in pending_games:
            del pending_games[game_id]
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("no"))
async def cmd_reject_game(message: Message):
    """Отклонить игру"""
    
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        command_parts = message.text.split('_')
        
        if len(command_parts) < 2:
            await message.answer("❌ Используйте: /no_ID")
            return
        
        game_id = int(command_parts[1])
        game = get_pending_game(game_id)
        
        if not game:
            await message.answer("❌ Игра не найдена")
            return
        
        update_game_status(game_id, 'rejected')
        
        await message.answer(f"❌ Игра «{game[4]}» отклонена!")
        
        user_id = game[1]
        
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"❌ <b>Ваша игра «{game[4]}» была отклонена</b>"
            )
        except:
            pass
        
        if game_id in pending_games:
            del pending_games[game_id]
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")