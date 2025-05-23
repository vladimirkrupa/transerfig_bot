
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import asyncio

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Вопросы
questions = [
    "На чём ты сегодня сосредоточен?",
    "Что ты сегодня хочешь привлечь в свою жизнь?",
    "Какие мысли ты хочешь отпустить?",
    "Что сегодня принесёт тебе радость?",
    "Чего ты хочешь достичь в ближайшие 24 часа?",
    "Что ты отпустишь, чтобы чувствовать себя лучше?"
]

# Мотивационные цитаты
quotes = [
    "“Успех — это результат правильного мышления.” — Джим Рон",
    "“Богатые люди фокусируются на возможности. Бедные — на препятствиях.” — Т. Харв Экер",
    "“Думай масштабно.” — Дональд Трамп",
    "“Фокусируйся на результате, а не на препятствиях.” — Тони Роббинс"
]

# Состояние пользователя
user_states = {}
user_answers = {}

# Старт
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_states[message.from_user.id] = 0
    user_answers[message.from_user.id] = []
    await message.answer("Добро пожаловать в дневник намерений. Начнём утренние вопросы:")
    await message.answer(questions[0])

# Ответ на вопрос
@dp.message_handler()
async def handle_answer(message: types.Message):
    uid = message.from_user.id
    if uid not in user_states:
        await message.answer("Напиши /start, чтобы начать.")
        return

    q_index = user_states[uid]
    user_answers[uid].append((questions[q_index], message.text))
    user_states[uid] += 1

    if user_states[uid] < len(questions):
        await message.answer(questions[user_states[uid]])
    else:
        await message.answer("Спасибо за ответы. Вот мотивация на день:")
        await message.answer(quotes[q_index % len(quotes)])

       # Сохраняем в файл
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{uid}_log.txt", "a", encoding="utf-8") as f:
    f.write(f"\n--- {now} ---\n")
    for q, a in user_answers[uid]:
        f.write(f"{q}\nОтвет: {a}\n")

user_states.pop(uid)
user_answers.pop(uid)

# Запуск
if name == '__main__':
    executor.start_polling(dp, skip_updates=True)
