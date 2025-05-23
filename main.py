import os
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
import logging

# Логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

# Вставь сюда свой Telegram ID
ADMIN_ID = 1359055991  # ← ЗАМЕНИ на свой ID

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

# Цитаты
quotes = [
    "“Успех — это результат правильного мышления.” — Джим Рон",
    "“Богатые люди фокусируются на возможности. Бедные — на препятствиях.” — Т. Харв Экер",
    "“Думай масштабно.” — Дональд Трамп",
    "“Фокусируйся на результате, а не на препятствиях.” — Тони Роббинс"
]

# Состояния пользователей
user_states = {}
user_answers = {}

# Команда старт
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = 0
    user_answers[user_id] = []
    await message.answer("Добро пожаловать в дневник намерений. Начнём утренние вопросы:")
    await message.answer(questions[0])

# Обработка ответов
@dp.message_handler(lambda message: message.from_user.id in user_states)
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]
    user_answers[user_id].append((questions[state], message.text))
    state += 1
    user_states[user_id] = state

    if state < len(questions):
        await message.answer(questions[state])
    else:
        await message.answer("Спасибо за ответы. Вот мотивация на день:")
        await message.answer(quotes[state % len(quotes)])

        # Сохраняем в файл
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f"{user_id}_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- {now} ---\n")
            for q, a in user_answers[user_id]:
                f.write(f"{q}\nОтвет: {a}\n")

        user_states.pop(user_id)
        user_answers.pop(user_id)

# Админ-панель
@dp.message_handler(commands=["admin"])
async def admin_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ У вас нет доступа к этой команде.")
        return
    await message.answer("🔐 Добро пожаловать в админ-панель.\nВы можете здесь управлять ботом.")

# Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
