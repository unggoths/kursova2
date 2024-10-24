import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router
from database.models import create_connection, close_connection


async def main():
    # Створення бота
    bot = Bot(token='7545582976:AAFrEdvIOkIn_tzE36JAEeHkf_L0jN8_J5o')
    dp = Dispatcher()

    # Підключення до бази даних при старті
    connection = create_connection()  # Підключення до бази даних

    dp.include_router(router)

    # Полінг для роботи бота
    try:
        await dp.start_polling(bot)
    finally:
        close_connection(connection)  # Закриття підключення до бази даних після зупинки бота

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is disabled')
