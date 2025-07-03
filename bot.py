import os
import logging
import random
from datetime import datetime
import pandas as pd
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Настройки
API_TOKEN = os.getenv('TELEGRAM_TOKEN') or "ВАШ_ТОКЕН_БОТА"  # ← Замените!
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Файл для данных
EXCEL_FILE = "users_data.xlsx"

# Загружаем существующие данные или создаем новую таблицу
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'user_id', 'username', 'first_name', 'last_name', 
            'name', 'age', 'city', 'created_at'
        ])
        df.to_excel(EXCEL_FILE, index=False)

# Сохраняем нового пользователя
def save_to_excel(user_data: dict):
    try:
        df = pd.read_excel(EXCEL_FILE)
        new_row = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'name': user_data['name'],
            'age': user_data['age'],
            'city': user_data['city'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
    except Exception as e:
        logging.error(f"Ошибка сохранения в Excel: {e}")

# Инициализация при запуске
init_excel()

# Остальной код остается как в предыдущей версии (клавиатуры, обработчики)
user_data = {}

final_messages = [
    "✨ Твоя энергия открыла доступ к денежному ресурсу...",
    "🎉 Всё готово! Вот твоя ссылка: https://clicktvf.com/ELAb"
]

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Начать путь 🔮"))
repeat_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Хочешь еще?🔮"))

@dp.message_handler(commands=['start', 'help'])
@dp.message_handler(content_types=['text'])
async def auto_start(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            "step": "name",
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name
        }
        await message.answer("🔮 Как тебя зовут?", reply_markup=ReplyKeyboardMarkup(remove_keyboard=True))
    else:
        await continue_questionnaire(message)

async def continue_questionnaire(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})
    
    if data.get("step") == "name":
        user_data[user_id]["name"] = message.text
        user_data[user_id]["step"] = "city"
        await message.answer("Из какого ты города?")
        
    elif data.get("step") == "city":
        user_data[user_id]["city"] = message.text
        user_data[user_id]["step"] = "age"
        await message.answer("Сколько тебе лет? (только цифры)")
        
    elif data.get("step") == "age":
        if message.text.isdigit():
            age = int(message.text)
            if 12 <= age <= 100:
                user_data[user_id]["age"] = age
                user_data[user_id]["user_id"] = user_id
                
                # Сохраняем в Excel
                save_to_excel(user_data[user_id])
                
                await message.answer(
                    random.choice(final_messages),
                    reply_markup=repeat_keyboard
                )
                user_data[user_id] = {"step": "name"}  # Сброс для повторного прохождения
            else:
                await message.answer("Введите возраст от 12 до 100 лет!")
        else:
            await message.answer("Пожалуйста, введите число!")

@dp.message_handler(lambda message: message.text == "Хочешь еще?🔮")
async def repeat_questionnaire(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "step": "name",
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name
    }
    await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardMarkup(remove_keyboard=True))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
