import os
import logging
import random
import pandas as pd
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Конфигурация
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')  # Ваш ID для уведомлений
EXCEL_FILE = "users_data.xlsx"
BACKUP_FOLDER = "backups"
BACKUP_DAYS = 30  # Хранить бэкапы N дней

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Создаем папки
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ---
def init_excel():
    """Создает файл Excel при первом запуске"""
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'user_id', 'username', 'first_name', 'last_name',
            'name', 'age', 'city', 'created_at'
        ])
        df.to_excel(EXCEL_FILE, index=False)

async def notify_admin(user_data: dict):
    """Уведомление о новом пользователе"""
    try:
        text = (
            "🆕 Новый пользователь:\n"
            f"👤 Имя: {user_data['name']}\n"
            f"🏙️ Город: {user_data['city']}\n"
            f"🔢 Возраст: {user_data['age']}\n"
            f"🆔 ID: {user_data['user_id']}"
        )
        await bot.send_message(ADMIN_CHAT_ID, text)
    except Exception as e:
        logging.error(f"Ошибка уведомления: {e}")

def clean_backups():
    """Удаление старых бэкапов"""
    try:
        now = datetime.now()
        for filename in os.listdir(BACKUP_FOLDER):
            filepath = os.path.join(BACKUP_FOLDER, filename)
            if os.path.isfile(filepath):
                file_date_str = filename.split('_')[-1].replace('.xlsx', '')
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                if (now - file_date).days > BACKUP_DAYS:
                    os.remove(filepath)
                    logging.info(f"Удален старый бэкап: {filename}")
    except Exception as e:
        logging.error(f"Ошибка очистки бэкапов: {e}")

async def send_backup():
    """Ежедневный бэкап с очисткой"""
    try:
        # Создаем бэкап
        today = datetime.now().strftime("%Y-%m-%d")
        backup_file = f"{BACKUP_FOLDER}/users_backup_{today}.xlsx"
        df = pd.read_excel(EXCEL_FILE)
        df.to_excel(backup_file, index=False)
        
        # Отправляем админу
        await bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            document=InputFile(backup_file),
            caption=f"📊 Бэкап за {today} (всего пользователей: {len(df)})"
        )
        
        # Чистим старые бэкапы
        clean_backups()
    except Exception as e:
        logging.error(f"Ошибка бэкапа: {e}")

# --- ОСНОВНОЙ КОД БОТА ---
init_excel()

# Планировщик задач
scheduler.add_job(send_backup, 'cron', hour=0, minute=5)  # В 00:05
scheduler.start()

# ... (ваши обработчики сообщений из предыдущего кода)

@dp.message_handler(lambda message: message.text == "Начать путь 🔮")
async def start_questionnaire(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"step": "name"}
    await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardMarkup(remove_keyboard=True))

@dp.message_handler(state="age")
async def process_age(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        age = int(message.text)
        if 12 <= age <= 100:
            async with state.proxy() as data:
                data['age'] = age
                user_data = {
                    'user_id': message.from_user.id,
                    'username': message.from_user.username,
                    'first_name': message.from_user.first_name,
                    'last_name': message.from_user.last_name,
                    'name': data['name'],
                    'city': data['city'],
                    'age': age
                }
                
                if save_to_excel(user_data):
                    await notify_admin(user_data)  # Уведомляем админа
                    
                    await message.answer(
                        random.choice(final_messages),
                        reply_markup=repeat_keyboard
                    )
                else:
                    await message.answer("⚠️ Ошибка сохранения. Попробуйте позже.")
            
            await state.finish()
            return
    
    await message.answer("Пожалуйста, введите реальный возраст (12-100):")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
