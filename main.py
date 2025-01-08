from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import add_subscriber, remove_subscriber, create_db
from scheduler import start_scheduler
from config import API_TOKEN
import asyncio

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Введи свой класс (например, 12A), чтобы получать уведомления о следующих уроках.")

@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    remove_subscriber(message.from_user.id)
    await message.reply("Вы отписались от уведомлений.")

@dp.message_handler()
async def handle_class(message: types.Message):
    user_class = message.text.strip()
    add_subscriber(message.from_user.id, user_class)
    await message.reply(f"Вы подписаны на уведомления для класса {user_class}.")

async def main():
    create_db()
    start_scheduler(bot)
    print("Планировщик запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
