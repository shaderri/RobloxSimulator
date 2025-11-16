from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_manager import get_user, update_user_account, get_user_balance
import os

router = Router()


class AccountSetup(StatesGroup):
    waiting_for_data = State()


@router.message(Command("myaccount"))
async def cmd_myaccount(message: Message):
    """Показать данные аккаунта"""
    
    user = get_user(message.from_user.id)
    
    if not user or not user[2]:  # Проверяем nickname
        await message.answer(
            "📝 <b>Настройка аккаунта</b>\n\n"
            "Для начала заполните данные вашего Roblox аккаунта.\n\n"
            "Отправьте данные в формате:\n\n"
            "<code>Никнейм: YourNickname\n"
            "Premium: Да/Нет\n"
            "Value: 1000\n"
            "RAP: 5000\n"
            "Друзья: 50\n"
            "Подписчики: 100\n"
            "Подписан: 75\n"
            "Визиты: 10000\n"
            "Avatar URL: https://example.com/avatar.png</code>"
        )
        return
    
    # Формирование ответа
    nickname = user[2]
    premium = user[3]
    value = user[4]
    rap = user[5]
    friends = user[6]
    followers = user[7]
    following = user[8]
    visits = user[9]
    created_at = user[10]
    avatar_url = user[11]
    
    premium_text = f"{nickname} Premium" if premium else nickname
    
    account_text = f"""
<b>Ваш аккаунт — «{premium_text}»</b>

Value — {value} 💎
RAP — {rap} 💸

Друзья — {friends}👤
Подписчики — {followers}👥
Подписан — {following}🔃
———————————>>>>>
Всего визитов — {visits}👤
————————>>>>>
Аккаунт создан: {created_at} г.
"""
    
    # Отправка с аватаром если есть URL
    if avatar_url and avatar_url.startswith('http'):
        try:
            await message.answer_photo(
                photo=avatar_url,
                caption=account_text
            )
        except:
            await message.answer(account_text)
    else:
        await message.answer(account_text)


@router.message(F.text.contains("Никнейм:"))
async def process_account_setup(message: Message):
    """Обработка настройки аккаунта"""
    
    try:
        lines = message.text.split('\n')
        data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Никнейм":
                    data['nickname'] = value
                elif key == "Premium":
                    data['premium'] = value.lower() in ['да', 'yes', 'true', '1']
                elif key == "Value":
                    data['value'] = int(value)
                elif key == "RAP":
                    data['rap'] = int(value)
                elif key == "Друзья":
                    data['friends'] = int(value)
                elif key == "Подписчики":
                    data['followers'] = int(value)
                elif key == "Подписан":
                    data['following'] = int(value)
                elif key == "Визиты":
                    data['visits'] = int(value)
                elif key == "Avatar URL":
                    data['avatar_url'] = value
        
        # Проверка обязательных полей
        required = ['nickname', 'premium', 'value', 'rap', 'friends', 
                   'followers', 'following', 'visits']
        
        if not all(k in data for k in required):
            await message.answer("❌ Заполните все поля корректно!")
            return
        
        if 'avatar_url' not in data:
            data['avatar_url'] = None
        
        # Сохранение данных
        update_user_account(message.from_user.id, data)
        
        await message.answer(
            "✅ <b>Данные аккаунта успешно сохранены!</b>\n\n"
            "Теперь используйте /myaccount для просмотра."
        )
        
    except Exception as e:
        await message.answer(
            "❌ Ошибка при обработке данных.\n"
            "Проверьте формат и попробуйте снова."
        )


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Показать баланс"""
    
    balance = get_user_balance(message.from_user.id)
    
    await message.answer(f"<b>Ваш баланс — {balance} R$💸</b>")