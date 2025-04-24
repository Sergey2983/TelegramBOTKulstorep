import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from handlers.handlers_cart import register_cart_handlers
from handlers.handlers_admin import register_admin_handlers
from handlers.handlers_order import register_order_handlers
from handlers.handlers_calculator import register_calculator_handlers
from keyboards import get_start_inline_keyboard
import sqlite3
import uuid

load_dotenv()  # Загружаем переменные из .env
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

register_cart_handlers(dp)
register_admin_handlers(dp)
register_order_handlers(dp)
register_calculator_handlers(dp)
# Приветственное сообщение
from aiogram.types import InputFile

@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    # Подключение к базе данных
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Проверка, существует ли уже пользователь
    cursor.execute("SELECT id, cart_id FROM accounts WHERE tg_id = ?", (tg_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cart_id = str(uuid.uuid4())[:8]  # Укороченный UUID
        cursor.execute("INSERT INTO accounts (tg_id, cart_id) VALUES (?, ?)", (tg_id, cart_id))
        conn.commit()
        user_id = cursor.lastrowid  # Получаем id (PRIMARY KEY)
        print(f"🆕 Новый пользователь добавлен: id={user_id}, cart_id={cart_id}")
    else:
        user_id, cart_id = existing_user
        print(f"🔁 Существующий пользователь: id={user_id}, cart_id={cart_id}")

    conn.close()

    # Отправка приветственного сообщения с картинкой
    photo = InputFile("images/start_logo.png")
    await message.answer_photo(
        photo=photo,
        caption=(
            "<b>🚀 Добро пожаловать в бота по выкупу товаров из Китая!</b>\n\n"
            "🛒 <b>Мы помогаем с выкупом и доставкой товаров со всех Китайских платформ:</b>\n"
            "- <a href=\"https://www.dewu.com\">Poizon (DEWU)</a>\n"
            "- <a href=\"https://www.taobao.com\">TaoBao</a>\n"
            "И многих других 🧾\n\n"
            "📦 Мы занимаемся исключительно выкупом и доставкой — всё просто, быстро и надёжно!\n\n"
            "⚠️ <b>Товар возврату и обмену не подлежит.</b>\n"
            "Мы оказываем услуги только выкупа и доставки товаров.\n\n"
            "👇 Выберите нужное действие ниже:"
        ),
        reply_markup=get_start_inline_keyboard(),
        parse_mode="HTML"
    )



# Регистрируем все хендлеры калькулятора
register_calculator_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
