import sqlite3
from datetime import datetime
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, CallbackQuery
from states import OrderStates
from keyboards import get_order_delivery_keyboard, get_order_category_keyboard, get_order_final_keyboard, \
    get_payment_keyboard
import re

YUAN_RATE = 13.5  # Установите актуальный курс юаня

def register_order_handlers(dp: Dispatcher):
    @dp.callback_query_handler(lambda c: c.data in ["order"], state="*")
    async def start_order(callback: types.CallbackQuery, state: FSMContext):

        photo = InputFile("../images/infocargo.png")
        await callback.message.answer_photo(
            photo=photo,
            caption=(
                "📦 <b>Начало оформления заказа</b>\n\n"
                "⚠️<i>Товары с знаком ≈ НЕ ВЫКУПАЮТСЯ</i>\n\n"
                "Выберите удобный способ доставки:"
            ),
            parse_mode="HTML",
            reply_markup=get_order_delivery_keyboard()
        )
        await OrderStates.choosing_delivery.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("order_delivery_"), state=OrderStates.choosing_delivery)
    async def choose_delivery(callback: types.CallbackQuery, state: FSMContext):
        delivery_type = callback.data.replace("order_delivery_", "")
        await state.update_data(delivery_type=delivery_type)
        await callback.message.delete()
        await callback.message.answer("👕 Выберите категорию товара:", reply_markup=get_order_category_keyboard(delivery_type))
        await OrderStates.choosing_category.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("order_category_"), state=OrderStates.choosing_category)
    async def choose_category(callback: types.CallbackQuery, state: FSMContext):
        category = callback.data.replace("order_category_", "")
        await state.update_data(category=category)
        await callback.message.delete()

        # Отправка фотографии с подписью
        photo = InputFile("../images/primer.PNG")  # Убедитесь, что путь к изображению корректен
        caption = "📸 <b>Пожалуйста, вставьте фото товара, как показано на примере:</b>"
        await callback.message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
        await OrderStates.waiting_for_photo.set()


    @dp.message_handler(content_types=types.ContentType.PHOTO, state=OrderStates.waiting_for_photo)
    async def handle_photo(message: types.Message, state: FSMContext):
        photo_id = message.photo[-1].file_id
        await state.update_data(photo=photo_id)

        # Отправка фото с примером + HTML-разметка
        example_photo = InputFile("../images/link.png")  # Убедись, что файл существует
        caption = ("⚠️ Товар возврату и обмену не подлежит. Мы оказываем услуги только выкупа и доставки товаров.\n\n"
                   "🔗 <b>Пожалуйста, отправьте ссылку на товар, как показано на примере: https://dw4.co/t/A/1rxTiksWr</b>")

        await message.answer_photo(photo=example_photo, caption=caption, parse_mode="HTML")

        await OrderStates.waiting_for_link.set()





    @dp.message_handler(state=OrderStates.waiting_for_photo)
    async def handle_no_photo(message: types.Message, state: FSMContext):
        await message.answer("❌ Пожалуйста, отправьте фото товара.")

    @dp.message_handler(state=OrderStates.waiting_for_link)
    async def handle_link(message: types.Message, state: FSMContext):
        if not re.match(r"https?://[^\s]+", message.text):
            await message.answer("❌ Пожалуйста, отправьте корректную ссылку на товар.")
            return
        await state.update_data(link=message.text)

        # Отправка изображения с подписью
        example_photo = InputFile("../images/size.PNG")  # Убедитесь, что файл существует
        caption = "📏 <b>Пожалуйста, напишите размер товара, если размера нет — пропустите.</b>\n\nНапример: <i>39.5</i>"
        await message.answer_photo(photo=example_photo, caption=caption, parse_mode="HTML")

        await OrderStates.waiting_for_size.set()





    @dp.message_handler(state=OrderStates.waiting_for_size)
    async def handle_size(message: types.Message, state: FSMContext):
        await state.update_data(size=message.text)

        example_photo = InputFile("../images/infocargo.png")  # Убедитесь, что файл существует
        caption = ("⚠️<b>Введите стоимость выбранного товара В ЮАНЯХ.</b>\n\n"
                "⚠️<b>Товар возврату и обмену не подлежит.</b> Мы оказываем услуги только <u>выкупа и доставки</u> товаров.")

        await message.answer_photo(photo=example_photo, caption=caption, parse_mode="HTML")
        await OrderStates.waiting_for_price.set()

    @dp.message_handler(state=OrderStates.waiting_for_price)
    async def handle_price(message: types.Message, state: FSMContext):
        try:
            price_yuan = float(message.text.replace(",", "."))
        except ValueError:
            await message.answer("❌ Пожалуйста, введите корректную сумму в юанях.")
            return

        user_data = await state.get_data()
        delivery_type = user_data.get("delivery_type")
        category = user_data.get("category")
        photo_id = user_data.get("photo")

        # Стоимость доставки по категориям
        delivery_prices = {
            "standard": {"clothes": 550, "shoes": 1100},
            "express": {"tshirts": 2000, "clothes": 2800, "shoes": 4200, "jackets": 3000}
        }

        delivery_price = delivery_prices.get(delivery_type, {}).get(category, 0)
        final_price = (price_yuan + 30) * YUAN_RATE + delivery_price + 1000 + (
            150 if delivery_type == "standard" else 0)

        await state.update_data(price_yuan=price_yuan, final_price=final_price)

        # Текст заявки
        caption = (
            "<b>📦 Заявка на заказ создана</b>\n\n"
            f"<b>🔗 Ссылка:</b> {user_data.get('link')}\n"
            f"<b>📐 Размер:</b> {user_data.get('size')}\n"
            f"<b>📦 Категория товара:</b> {category.capitalize()}\n"
            f"<b>🚚 Тип доставки:</b> {'Авто' if delivery_type == 'standard' else 'Авиа'}\n"
            f"<b>💴 Стоимость товара:</b> {price_yuan}¥\n"
            f"<b>💰 Итоговая цена:</b> <u>{round(final_price)}₽</u>\n\n"
            "<b>🔴При ошибочной оплате неверной суммы вы можете подать заявку на возврат средств. Обработка возврата занимает до 14 рабочих дней. Пожалуйста, проявляйте внимательность при оплате!🔴</b>\n\n"
        )

        # Отправка фото + текста
        await message.answer_photo(
            photo=photo_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_order_final_keyboard()
        )

        await OrderStates.confirming_order.set()

    @dp.callback_query_handler(lambda c: c.data == "confirm_order", state=OrderStates.confirming_order)
    async def confirm_order_callback(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()

        # Получаем user_id
        user_id = callback.from_user.id  # ID пользователя из Telegram

        # Текущая дата/время
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Создаем соединение с базой данных
        conn = sqlite3.connect("../database.db")
        cursor = conn.cursor()

        # Генерация уникального номера заказа
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_number = cursor.fetchone()[0] + 1  # Номер заказа = количество заказов + 1

        # Вставка данных о заказе в таблицу orders
        cursor.execute("""
            INSERT INTO orders (
                link, size, category_order, type_cargo, price_yuan, final_price, photo_id, order_number, user_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data.get('link'),
            user_data.get('size'),
            user_data.get('category'),
            user_data.get('delivery_type'),
            user_data.get('price_yuan'),
            user_data.get('final_price'),
            user_data.get('photo'),
            order_number,
            user_id,
            created_at
        ))

        conn.commit()
        conn.close()

        # Отправляем сообщение с заказом и номером
        caption = (
            "<b>📦 Ваш заказ был успешно оформлен!</b>\n\n"
            f"<b>Номер заказа:</b> {order_number}\n"
            f"<b>🔗 Ссылка:</b> {user_data.get('link')}\n"
            f"<b>📐 Размер:</b> {user_data.get('size')}\n"
            f"<b>📦 Категория:</b> {user_data.get('category').capitalize()}\n"
            f"<b>🚚 Тип доставки:</b> {'Авто' if user_data.get('delivery_type') == 'standard' else 'Авиа'}\n"
            f"<b>💴 Стоимость товара:</b> {user_data.get('price_yuan')}¥\n"
            f"<b>💰 Итоговая цена:</b> <u>{round(user_data.get('final_price'))}₽</u>\n\n"
            "🔴При ошибочной оплате неверной суммы вы можете подать заявку на возврат средств. Обработка возврата занимает до 7 рабочих дней. Пожалуйста, проявляйте внимательность при оплате!🔴\n\n"
            "🚚 Внимание! Стоимость доставки СДЭК по РФ не включена в цену — оплачивается дополнительно. Отправка ведётся из Москвы.\n\n"
            "🛍 <b>Нажмите «Оплатить», чтобы завершить заказ.</b>"

        )

        # Отправляем фото + информацию о заказе
        await callback.message.answer_photo(
            photo=user_data.get('photo'),
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_payment_keyboard()  # Кнопки для оплаты
        )

        await callback.answer()  # Закрыть callback

        # Переходим в следующее состояние (если нужно)
        await OrderStates.order_paid.set()