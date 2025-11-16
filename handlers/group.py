from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_manager import create_group, get_group, get_group_stats

router = Router()

class GroupCreation(StatesGroup):
    waiting_for_group_data = State()


@router.message(Command("creategroup"))
async def cmd_create_group(message: Message, state: FSMContext):
    """Создание группы"""
    
    if len(message.text.strip()) == len('/creategroup'):
        instruction = """
<b>Для создания группы:</b>

• Фото
• Название
• Описание
"""
        await message.answer(instruction)
        await state.set_state(GroupCreation.waiting_for_group_data)
        return


@router.message(GroupCreation.waiting_for_group_data, F.photo)
async def process_group_creation(message: Message, state: FSMContext):
    """Обработка создания группы"""
    
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
        
        if 'title' not in data or 'description' not in data:
            await message.answer("❌ Заполните все поля!")
            return
        
        group_id = create_group(message.from_user.id, photo_id, data['title'], data['description'])
        
        # Получаем количество участников
        members = get_group_stats(group_id)
        
        group_text = f"""
<b>Ваша статистика группы:</b>

{data['title']}
{data['description']}
{members}👥 — участники
"""
        
        await message.answer_photo(photo=photo_id, caption=group_text)
        await state.clear()
        
    except Exception as e:
        await message.answer("❌ Ошибка при создании группы.")
        print(f"Error: {e}")