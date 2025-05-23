import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import json

# Получаем токен из Render
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# ID администратора (замени на свой Telegram ID)
ADMIN_ID = 1359055991

# Вопросы
questions = [
    "На чём ты сегодня сосредоточен?",
    "Что ты сегодня хочешь привлечь в свою жизнь?",
    "Какие мысли ты хочешь отпустить?",
    "Что сегодня принесёт тебе радость?",
    "Чего ты хочешь достичь в ближайшие 24 часа?",
    "Что ты отпустишь, чтобы чувствовать себя лучше?"
]

# Цитаты
quotes = [
    "“Успех — это результат правильного мышления.” — Джим Рон",
    "“Богатые люди фокусируются на возможности. Бедные — на препятствиях.” — Т. Харв Экер",
    "“Думай масштабно.” — Дональд Трамп",
    "“Фокусируйся на результате, а не на препятствиях.” — Тони Роббинс"
]

# Состояние пользователя
user_states = {}
user_data = {}  # id: {"name": ..., "phone": ..., "answers": {"дата": [(вопрос, ответ)]}}

# Кнопки
contact_btn = KeyboardButton("Поделиться контактом", request_contact=True)
contact_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(contact_btn)

# Старт
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    user_states[uid] = 0
    name = message.from_user.full_name
    if uid not in user_data:
        user_data[uid] = {"name": name, "phone": "", "answers": {}}
    await message.answer("Пожалуйста, поделись номером телефона:", reply_markup=contact_kb)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    uid = message.from_user.id
    user_data[uid]["phone"] = message.contact.phone_number
    await message.answer("Спасибо! Начнем утренние вопросы:", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(questions[0])

@dp.message_handler(lambda m: m.from_user.id in user_states)
async def answer_handler(message: types.Message):
    uid = message.from_user.id
    index = user_states[uid]
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in user_data[uid]["answers"]:
        user_data[uid]["answers"][today] = []
    user_data[uid]["answers"][today].append((questions[index], message.text))
    index += 1
    if index < len(questions):
        user_states[uid] = index
        await message.answer(questions[index])
    else:
        await message.answer("Спасибо! Вот цитата на день:")
        await message.answer(quotes[index % len(quotes)])
        user_states.pop(uid)

# Админ-панель
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text.lower() == "admin")
async def admin_panel(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    for uid in user_data:
        name = user_data[uid]["name"]
        kb.add(InlineKeyboardButton(f"{name}", callback_data=f"user_{uid}"))
    await message.answer("Список пользователей:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("user_"))
async def show_user_data(callback: types.CallbackQuery):
    uid = int(callback.data.split("_")[1])
    data = user_data[uid]
    text = f"👤 {data['name']}\n📞 {data['phone']}\n"
    for date, entries in data["answers"].items():
        text += f"\n📅 {date}:\n"
        for q, a in entries:
            text += f"{q}\nОтвет: {a}\n"
    await callback.message.answer(text[:4096])  # Telegram limit

# Рассылка утром и вечером
async def send_daily_questions():
    for uid in user_data:
        user_states[uid] = 0
        await bot.send_message(uid, "Доброе утро! Пришло время вопросов:")
        await bot.send_message(uid, questions[0])

async def send_evening_questions():
    for uid in user_data:
        user_states[uid] = 0
        await bot.send_message(uid, "Добрый вечер! Пришло время вопросов:")
        await bot.send_message(uid, questions[0])

# Планировщик
scheduler.add_job(send_daily_questions, "cron", hour=6, minute=0)
scheduler.add_job(send_evening_questions, "cron", hour=20, minute=30)
scheduler.start()

# Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
