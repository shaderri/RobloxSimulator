from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_manager import (create_game, get_game_by_title, get_game_stats, 
                                  get_user, add_game_visit, get_pending_game)
from config import ADMIN_ID

router = Router()

class GameCreation(StatesGroup):
    waiting_for_game_data = State()

pending_games = {}


@router.message(Command("creategame"))
async def cmd_create_game(message: Message, state: FSMContext):
    """Создание игры"""
    
    if len(message.text.strip()) == len('/creategame'):
        instruction = """
<b>Для создания игры 🎮</b>
Отправьте данные по пунктам:

• Фото
• Название
• Описание
• Сюжет
• Геймпассы
"""
        await message.answer(instruction)
        await state.set_state(GameCreation.waiting_for_game_data)
        return


@router.message(GameCreation.waiting_for_game_data, F.photo)
async def process_game_creation(message: Message, state: FSMContext):
    """Обработка данных игры"""
    
    try:
        photo = message.photo[-1]
        photo_id = photo.file_id
        text = message.caption or ""
        
        data = {}
        lines = text.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Название":
                    data['title'] = value
                elif key == "Описание":
                    data['description'] = value
                elif key == "Сюжет":
                    data['plot'] = value
                elif key == "Геймпассы":
                    data['gamepasses'] = value
        
        required = ['title', 'description', 'plot', 'gamepasses']
        if not all(k in data for k in required):
            await message.answer("❌ Заполните все поля!")
            return
        
        game_id = create_game(
            message.from_user.id,
            message.from_user.username or "RobloxPlayer",
            photo_id,
            data['title'],
            data['description'],
            data['plot'],
            data['gamepasses']
        )
        
        pending_games[game_id] = message.from_user.id
        
        await message.answer("<b>Ваша игра была создана и проходит модерацию 🔍</b>")
        
        # Отправка админу
        try:
            admin_text = f"""
<b>Игра от пользователя @{message.from_user.username or 'Unknown'}</b>

Фото: (см. выше)
Название: {data['title']}
Описание: {data['description']}
Сюжет: {data['plot']}
Геймпассы: {data['gamepasses']}

<b>Вы одобряете игру?</b>
/yes_{game_id} или /no_{game_id}
"""
            
            await message.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=admin_text
            )
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")
        
        await state.clear()
        
    except Exception as e:
        await message.answer("❌ Ошибка при создании игры.")
        print(f"Error: {e}")


@router.message(Command("mygame"))
async def cmd_my_game(message: Message):
    """Статистика игры с РЕАЛЬНЫМИ данными + симуляция"""
    
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "📝 <b>Использование:</b>\n"
            "<code>/mygame Название игры</code>"
        )
        return
    
    title = parts[1]
    game = get_game_by_title(message.from_user.id, title)
    
    if not game:
        await message.answer(
            "❌ Игра не найдена или ещё не одобрена.\n"
            "Проверьте название или дождитесь модерации."
        )
        return
    
    game_id = game[0]
    
    # Добавляем визит владельца (статистика растет!)
    add_game_visit(game_id, message.from_user.id)
    
    # Симулируем активность ботов (естественное изменение)
    from database.db_manager import simulate_game_activity
    simulate_game_activity(game_id)
    
    # Получаем обновленную статистику
    stats = get_game_stats(game_id)
    
    user = get_user(message.from_user.id)
    nickname = user[2] if user and user[2] else "RobloxPlayer"
    
    # Определяем статус игры
    if stats['online_players'] > 1000:
        status_badge = "🔥 ХИТ!"
    elif stats['online_players'] > 500:
        status_badge = "⭐ ПОПУЛЯРНАЯ"
    elif stats['online_players'] > 100:
        status_badge = "📈 Растущая"
    elif stats['online_players'] > 20:
        status_badge = "✅ Активная"
    else:
        status_badge = "🌱 Новая"
    
    # Формат ровно как в ТЗ
    stats_text = f"""
<b>Ваша статистика игры «{game[4]}»</b>
{status_badge}

В сети игроков — {stats['online_players']}👥
Визиты — {stats['total_visits']:,}👤
👍{stats['likes']}   👎{stats['dislikes']}
📈 Ваша игра находится в рекомендациях
🌟 — {stats['favorites']} фаворитов
——————————————>>>
Заработано с игры — {stats['earned']:,} R$💸
Разработчик — {nickname} 🛠
"""
    
    try:
        await message.answer_photo(photo=game[3], caption=stats_text)
    except:
        await message.answer(stats_text)