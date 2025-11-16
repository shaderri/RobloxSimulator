from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_manager import create_group, get_group

router = Router()


class GroupCreation(StatesGroup):
    waiting_for_group_data = State()


@router.message(Command("creategroup"))
async def cmd_create_group(message: Message, state: FSMContext):
    """Создание группы"""
    
    if len(message.text.strip()) == len('/creategroup'):
        instruction = """
👥 <b>Для создания группы:</b>

📸 Фото
📝 Название
📄 Описание

<b>Формат отправки:</b>
<code>/creategroup
Название: Название группы
Описание: Описание группы</code>

<i>Прикрепите фото к сообщению с данными!</i>
"""
        await message.answer(instruction)
        await state.set_state(GroupCreation.waiting_for_group_data)
        return


@router.message(GroupCreation.waiting_for_group_data, F.photo)
async def process_group_creation(message: Message, state: FSMContext):
    """Обработка создания группы"""
    
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
        
        # Проверка обязательных полей
        if 'title' not in data or 'description' not in data:
            await message.answer("❌ Заполните все поля!")
            return
        
        # Создаём группу
        group_id = create_group(
            message.from_user.id,
            photo_id,
            data['title'],
            data['description']
        )
        
        # Получаем данные группы
        group = get_group(group_id)
        
        # Формируем ответ
        group_text = f"""
✅ <b>Ваша статистика группы:</b>

<b>{group[3]}</b>
{group[4]}
{group[5]}👥 — участники
"""
        
        await message.answer_photo(
            photo=photo_id,
            caption=group_text
        )
        
        await state.clear()
        
    except Exception as e:
        await message.answer("❌ Ошибка при создании группы. Проверьте формат данных.")
        print(f"Error: {e}")