from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database import get_subscribers
import sqlite3
from config import API_TOKEN
import pytz

bot = Bot(token=API_TOKEN)
KZ_TIMEZONE = pytz.timezone("Asia/Oral")

def get_next_lesson(user_class, current_time):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    today = current_time.strftime("%A")

    cursor.execute('''
        SELECT subject, room, time_start, time_end 
        FROM timetable
        WHERE class = ? AND weekday = ? AND time_start > ?
        ORDER BY time_start ASC LIMIT 1
    ''', (user_class, today, current_time.strftime("%H:%M")))

    result = cursor.fetchone()
    conn.close()
    return result

async def send_notifications():
    subscribers = get_subscribers()
    now = datetime.now(KZ_TIMEZONE)

    for user_id, user_class in subscribers:
        conn = sqlite3.connect('schedule.db')
        cursor = conn.cursor()

        today = now.strftime("%A")
        current_time = now.strftime("%H:%M")


        cursor.execute('''
            SELECT subject, room, time_start, time_end
            FROM timetable
            WHERE class = ? AND weekday = ? AND time_end = ?
            ORDER BY time_start ASC LIMIT 1
        ''', (user_class, today, current_time))

        current_lesson = cursor.fetchone()

        if current_lesson:

            next_lesson = get_next_lesson(user_class, now)
            if next_lesson:
                next_subject, next_room, next_start, _ = next_lesson
                message = f"Следующий урок: {next_subject}, кабинет: {next_room} (в {next_start})"
            else:
                message = "Уроки на сегодня закончились."


            await bot.send_message(user_id, message)

        conn.close()

def start_scheduler(bot_instance):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_notifications, "interval", seconds=60)
    scheduler.start()
