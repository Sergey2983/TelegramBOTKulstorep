from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import ADMIN_IDS, dp, bot
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters import Command
import sqlite3

from keyboards import admin_main_menu, order_action_keyboard, status_choice_keyboard


@dp.message_handler(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("У тебя нет доступа 😎")
    await message.answer("👑 Админ-панель:", reply_markup=admin_main_menu())


@dp.callback_query_handler(lambda c: c.data == "view_orders")
async def view_orders(callback_query: CallbackQuery):
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, link, size, final_price, status, user_id, created_at, photo_id FROM orders ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await callback_query.message.answer("Нет заказов.")
    else:
        for row in rows:
            order_id, link, size, price, status, user_id, created_at, photo_id = row
            user = await bot.get_chat(user_id)
            username = user.username if user.username else f"ID: {user_id}"

            caption = (
                f"🧾 Заказ №{order_id}\n"
                f"🔗 Ссылка: {link}\n"
                f"📏 Размер: {size}\n"
                f"💰 Цена: {price}₽\n"
                f"📌 Статус: {status}\n"
                f"🧑‍💻 Пользователь: @{username}\n"
                f"🗓 Дата создания: {created_at}"
            )

            if photo_id:
                await callback_query.message.answer_photo(photo=photo_id, caption=caption, reply_markup=order_action_keyboard(order_id))
            else:
                await callback_query.message.answer(caption, reply_markup=order_action_keyboard(order_id))


@dp.callback_query_handler(lambda c: c.data.startswith("delete_"))
async def delete_order_handler(callback_query: types.CallbackQuery):
    order_id = int(callback_query.data.split("_")[1])

    # Удаление заказа из базы
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    # Уведомление
    await callback_query.message.delete()
    await callback_query.answer("Удалено ✅")
    await callback_query.message.answer(f"✅ Заказ №{order_id} был удалён.")


    # Уведомление
    await callback_query.message.edit_text(f"✅ Заказ №{order_id} был удалён.")
@dp.callback_query_handler(lambda c: c.data.startswith("edit_"))
async def edit_order(callback_query: CallbackQuery):
    order_id = int(callback_query.data.split("_")[1])
    await callback_query.message.edit_reply_markup(reply_markup=status_choice_keyboard(order_id))


@dp.callback_query_handler(lambda c: c.data.startswith("setstatus_"))
async def set_order_status(callback_query: CallbackQuery):
    _, order_id, new_status = callback_query.data.split("_", 2)
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

    await callback_query.answer("Статус обновлён ✅")
    await callback_query.message.edit_reply_markup(reply_markup=order_action_keyboard(order_id))




@dp.callback_query_handler(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.answer("👑 Админ-панель:", reply_markup=admin_main_menu())






# Регистрация хендлеров
def register_admin_handlers(dp):
    dp.register_message_handler(admin_panel, Command("admin"))

    dp.register_callback_query_handler(view_orders, lambda c: c.data == "view_orders")
    dp.register_callback_query_handler(edit_order, lambda c: c.data.startswith("edit_"))
    dp.register_callback_query_handler(set_order_status, lambda c: c.data.startswith("setstatus_"))
    dp.register_callback_query_handler(back_to_main_menu, lambda c: c.data == "back_to_main_menu")
    dp.register_callback_query_handler(delete_order_handler, Text(startswith="delete_"))  # ✅ Регистрируем удаление


