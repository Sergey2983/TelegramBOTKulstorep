from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext
from keyboards import get_start_inline_keyboard, get_question_button
from loader import dp, bot
import sqlite3


# Клавиатура для возврата в меню
def get_back_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )


@dp.callback_query_handler(lambda c: c.data == "cart")
async def show_user_cart(callback: CallbackQuery):
    user_id = callback.from_user.id

    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link, size, final_price, status, created_at, photo_id 
        FROM orders 
        WHERE user_id = ?
    """, (user_id,))
    orders = cursor.fetchall()
    conn.close()

    # Удалим предыдущее сообщение


    if not orders:
        await callback.message.answer("🛒 Ваша корзина пуста.", reply_markup=get_back_keyboard())
    else:
        for order in orders:
            order_id, link, size, price, status, created_at, photo_id = order

            caption = (
                f"🧾 Заказ №{order_id}\n"
                f"🔗 Ссылка: {link}\n"
                f"📏 Размер: {size}\n"
                f"💰 Цена: {price}₽\n"
                f"📌 Статус: {status}\n"
                f"🗓 Дата создания: {created_at}"
            )

            if photo_id:
                try:
                    await callback.message.answer_photo(photo=photo_id, caption=caption, reply_markup=get_question_button())
                except Exception as e:
                    print(f"Ошибка при отправке фото: {e}")
                    await callback.message.answer(caption, reply_markup=get_question_button())
            else:
                await callback.message.answer(caption, reply_markup=get_question_button())



@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    # Удаляем предыдущее сообщение (опционально, если надо очистить)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

    # Загружаем фото
    photo = InputFile("../images/start_logo.png")

    # Отправляем фото с приветственным сообщением
    await bot.send_photo(
        chat_id=callback.message.chat.id,
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


# Импортировать в main.py
def register_cart_handlers(dp):
    dp.register_callback_query_handler(show_user_cart, lambda c: c.data == "cart")
    dp.register_callback_query_handler(back_to_menu, lambda c: c.data == "back_to_menu")
