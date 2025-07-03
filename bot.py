import os
import logging
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Токен бота (возьмите из @BotFather)
API_TOKEN = os.getenv('TELEGRAM_TOKEN') or "ВАШ_ТОКЕН_БОТА"  # ← Замените здесь!

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Ваши финальные сообщения
final_messages = [
    "✨ Твоя энергия открыла доступ к денежному ресурсу...",
    "🎉 Всё готово!...",
    # ... (остальные сообщения оставьте как были)
]

# Клавиатуры
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Начать путь 🔮"))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Приветствую тебя в пространстве 'Магия и Деньги'! ✨\n\n"
        "Готов начать? Нажми кнопку ниже ↓",
        reply_markup=start_keyboard
    )

@dp.message_handler(lambda message: message.text == "Начать путь 🔮")
async def ask_name(message: types.Message):
    await message.answer("Как тебя зовут?")

@dp.message_handler(content_types=['text'])
async def handle_answers(message: types.Message):
    if "Как тебя зовут?" in message.text:
        await message.answer("Из какого ты города?")
    elif "Из какого ты города?" in message.text:
        await message.answer("Сколько тебе лет?")
    elif "Сколько тебе лет?" in message.text:
        msg = random.choice(final_messages)
        await message.answer(msg, reply_markup=start_keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
