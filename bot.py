import logging
import random
import csv
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7436585466:AAGTOo1hR5q4VbmeJWXtKwQOx_QMYgDHaRg'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users = {}

final_messages = [
    "✨ Твоя энергия открыла доступ к денежному ресурсу.\n\n🔗 Жми сюда для активации: https://clicktvf.com/ELAb\n\nТы удивишься, как быстро всё изменится!",
    "🎉 Всё готово!\n\n🔮 По твоим данным подобран денежный инструмент.\n\n🔗 Жми для активации: https://clicktvf.com/ELAb\n\nПоток финансов уже рядом — просто открой нужную дверь 💸✨",
    "🌟 Готово. Всё рассчитано.\n\nНажми на ссылку и активируй денежный канал: https://clicktvf.com/ELAb\n\nЭто работает только один раз.",
    "🔓 Пророчество подтвердилось!\n\nТебе доступен денежный источник. Жми для активации: https://clicktvf.com/ELAb\n\nНе упусти момент. Он уникален.",
    "🎲 Судьба дала тебе шанс.\n\nЖми и активируй финансовый поток: https://clicktvf.com/ELAb\n\nОткрытие прошло успешно."
]

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("Начать путь 🔮"))

def save_user_data(user_id, name, city, age):
    with open("leads.csv", mode="a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), user_id, name, city, age])

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Приветствую тебя в пространстве 'Магия и Деньги'! ✨\n\nЗдесь ты сможешь пройти ритуал подбора денежного инструмента, подходящего именно тебе. Готов начать?", reply_markup=start_keyboard)

@dp.message_handler(lambda message: message.text == "Начать путь 🔮")
async def ask_name(message: types.Message):
    users[message.from_user.id] = {}
    await message.answer("Как тебя зовут?")

@dp.message_handler(lambda message: message.from_user.id in users and "name" not in users[message.from_user.id])
async def ask_city(message: types.Message):
    users[message.from_user.id]["name"] = message.text.strip()
    await message.answer("Из какого ты города?")

@dp.message_handler(lambda message: message.from_user.id in users and "city" not in users[message.from_user.id])
async def ask_age(message: types.Message):
    users[message.from_user.id]["city"] = message.text.strip()
    await message.answer("Сколько тебе лет?")

@dp.message_handler(lambda message: message.from_user.id in users and "age" not in users[message.from_user.id])
async def show_final(message: types.Message):
    users[message.from_user.id]["age"] = message.text.strip()
    data = users[message.from_user.id]
    save_user_data(message.from_user.id, data['name'], data['city'], data['age'])

    msg = random.choice(final_messages)
    await message.answer(msg, reply_markup=start_keyboard)

@dp.message_handler()
async def auto_start(message: types.Message):
    if message.text not in ["Начать путь 🔮"]:
        await send_welcome(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
