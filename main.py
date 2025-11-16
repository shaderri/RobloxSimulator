import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.db_manager import init_db
from handlers import account, social, studio, game, group, admin, start

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    
    # Инициализация базы данных
    init_db()
    logger.info("База данных инициализирована")
    
    # Создание бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(account.router)
    dp.include_router(social.router)
    dp.include_router(studio.router)
    dp.include_router(game.router)
    dp.include_router(group.router)
    dp.include_router(admin.router)
    
    logger.info("Бот запущен")
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())