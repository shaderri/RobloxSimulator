from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_manager import create_game, get_game, get_user
from config import ADMIN_ID

router = Router()


class GameCreation(StatesGroup):
    waiting_for_game_data = State()


# Временное хранилище для игр на модерации
pending_games = {}


@router.message(Command("creategame"))
async def cmd_create_game(message: Message, state: FSMContext):
    """Создание игры"""
    
    # Проверяем, это инструкция или данные
    if len(message.text.strip()) == len('/creategame'):
        # Показываем инструкцию
        instruction = """
🎮 <b>Для создания игры</b>
Отправьте данные по пунктам:

📸 Фото
📝 Название
📄 Описание
📖 Сюжет
🎟 Геймпассы

<b>Формат отправки:</b>
<code>/creategame
Фото: [прикрепите фото]
Название: Название вашей игры
Описание: Краткое описание
Сюжет: История игры
Геймпассы: VIP, 2x Speed</code>

<i>Прикрепите фото к сообщению с данными!</i>
"""
        await message.answer(instruction)
        await state.set_state(GameCreation.waiting_for_game_data)
        return


@router.message(GameCreation.waiting_for_game_data, F.photo)
async def process_game_creation(message: Message, state: FSMContext):
    """Обработка данных игры с фото"""
    
    try:
        # Получаем фото
        photo = message.photo[-1]
        photo_id = photo.file_id
        
        # Парсим текст
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
        
        # Проверка обязательных полей
        required = ['title', 'description', 'plot', 'gamepasses']
        if not all(k in data for k in required):
            await message.answer("❌ Заполните все поля!")
            return
        
        # Сохраняем игру
        game_id = create_game(
            message.from_user.id,
            message.from_user.username or "Unknown",
            photo_id,
            data['title'],
            data['description'],
            data['plot'],
            data['gamepasses']
        )
        
        # Сохраняем ID игры и пользователя для модерации
        pending_games[game_id] = message.from_user.id
        
        await message.answer("✅ <b>Ваша игра была создана и проходит модерацию 🔍</b>")
        
        # Отправляем админу
        try:
            admin_text = f"""
🎮 <b>Игра от пользователя @{message.from_user.username or 'Unknown'}</b>

<b>Название:</b> {data['title']}
<b>Описание:</b> {data['description']}
<b>Сюжет:</b> {data['plot']}
<b>Геймпассы:</b> {data['gamepasses']}

<b>Вы одобряете игру?</b>
/yes_{game_id} или /no_{game_id}
"""
            
            from aiogram import Bot
            bot = message.bot
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=admin_text
            )
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")
        
        await state.clear()
        
    except Exception as e:
        await message.answer("❌ Ошибка при создании игры. Проверьте формат данных.")
        print(f"Error: {e}")


@router.message(Command("mygame"))
async def cmd_my_game(message: Message):
    """Статистика игры"""
    
    # Получаем название игры
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "📝 <b>Использование:</b>\n"
            "<code>/mygame Название игры</code>"
        )
        return
    
    title = parts[1]
    
    # Получаем игру из БД
    game = get_game(message.from_user.id, title)
    
    if not game:
        await message.answer(
            "❌ Игра не найдена или ещё не одобрена.\n"
            "Проверьте название или дождитесь модерации."
        )
        return
    
    # Получаем данные пользователя для никнейма
    user = get_user(message.from_user.id)
    nickname = user[2] if user and user[2] else "Unknown"
    
    # Форматируем статистику
    stats_text = f"""
📊 <b>Ваша статистика игры «{game[4]}»</b>

В сети игроков — {game[9]}👥
Визиты — {game[10]:,}👤
👍{game[11]:,} 👎{game[12]:,}
📈 Ваша игра находится в рекомендациях
🌟 — {game[13]:,} фаворитов
——————————————>>>
Заработано — {game[14]:,} R$💸
Разработчик — {nickname} 🛠
"""
    
    # Отправляем с фото
    try:
        await message.answer_photo(
            photo=game[3],
            caption=stats_text
        )
    except:
        await message.answer(stats_text)