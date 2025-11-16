from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.db_manager import get_user, update_user_account, get_user_balance

router = Router()


@router.message(Command("myaccount"))
async def cmd_myaccount(message: Message):
    """Показать данные аккаунта"""
    
    user = get_user(message.from_user.id)
    
    if not user or not user[2]:
        await message.answer(
            "📝 <b>Настройка аккаунта Roblox</b>\n\n"
            "Для начала заполни данные своего аккаунта.\n\n"
            "<b>Отправь данные в формате:</b>\n\n"
            "<code>Никнейм: YourNickname\n"
            "Premium: Да/Нет\n"
            "Value: 1000\n"
            "RAP: 5000\n"
            "Друзья: 50\n"
            "Подписчики: 100\n"
            "Подписан: 75\n"
            "Визиты: 10000\n"
            "Avatar URL: https://example.com/avatar.png</code>\n\n"
            "<i>💡 Все поля обязательны</i>"
        )
        return
    
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
    balance = user[12]
    
    premium_badge = "⭐ Premium" if premium else ""
    
    account_text = f"""
👤 <b>{nickname}</b> {premium_badge}

━━━━━━━━━━━━━━━━━━━━

💎 <b>Value:</b> {value:,}
💸 <b>RAP:</b> {rap:,}
💰 <b>Robux:</b> {balance:,} R$

👥 <b>Социальное:</b>
• Друзья: {friends:,} 👤
• Подписчики: {followers:,} 👥
• Подписок: {following:,} 🔃

📊 <b>Статистика:</b>
• Визиты профиля: {visits:,} 👁
• Аккаунт создан: {created_at}

━━━━━━━━━━━━━━━━━━━━

<i>🎮 Играй, создавай, зарабатывай!</i>
"""
    
    if avatar_url and avatar_url.startswith('http'):
        try:
            await message.answer_photo(photo=avatar_url, caption=account_text)
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
        
        required = ['nickname', 'premium', 'value', 'rap', 'friends', 
                   'followers', 'following', 'visits']
        
        if not all(k in data for k in required):
            await message.answer("❌ Заполни все поля корректно!")
            return
        
        if 'avatar_url' not in data:
            data['avatar_url'] = None
        
        update_user_account(message.from_user.id, data)
        
        await message.answer(
            "✅ <b>Аккаунт успешно настроен!</b>\n\n"
            "🎉 Добро пожаловать в Roblox!\n\n"
            "Используй /myaccount для просмотра профиля."
        )
        
    except Exception as e:
        await message.answer(
            "❌ <b>Ошибка при обработке данных</b>\n\n"
            "Проверь формат и попробуй снова."
        )


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Показать баланс"""
    
    balance = get_user_balance(message.from_user.id)
    user = get_user(message.from_user.id)
    
    premium_text = ""
    if user and user[3]:
        premium_text = "\n\n⭐ <b>Premium активен!</b>\nЕжедневный бонус: 450 R$"
    
    await message.answer(
        f"💰 <b>Твой баланс Robux</b>\n\n"
        f"<b>{balance:,} R$</b> 💎{premium_text}\n\n"
        f"<i>💡 Зарабатывай Robux создавая игры!</i>"
    )