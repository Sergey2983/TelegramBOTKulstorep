from aiogram import types, Dispatcher
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from keyboards import get_start_order_keyboard, get_next_step_keyboard, get_delivery_keyboard, get_main_menu_keyboard, get_final_keyboard

from aiogram.dispatcher.filters.state import State, StatesGroup
import re


YUAN_RATE = 12.8  # Курс юаня к рублю

class OrderStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_link = State()
    waiting_for_size = State()
    waiting_for_price = State()
    confirming_order = State()

async def handle_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    photo = InputFile("images/NoOrder.jpg")
    await callback.message.answer_photo(
        photo=photo,
        caption=(
            "Пожалуйста, обратите внимание на то, содержит ли товар знак ≈ (примерное значение). "
            "К сожалению, такие позиции наша команда не сможет приобрести для вас.\n"
            "Почему?\n"
            "Товары, отмеченные символом ≈, доставляются в Китай из других стран. "
            "Из-за ограничений, установленных таможенными правилами Китая, их выкуп невозможен.\n"
            "Для продолжения просто нажмите кнопку «ДАЛЕЕ»."
        ),
        reply_markup=get_start_order_keyboard()
    )

async def handle_further(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    photo = InputFile("images/readme2.jpg")
    await callback.message.answer_photo(
        photo=photo,
        caption="Вы уверены, что Ваш товар не имеет ≈ приблизительного равно перед ценой?\n\n"
                "<b>Такие товары к сожалению мы выкупить не сможем.</b>",
        parse_mode="HTML",
        reply_markup=get_next_step_keyboard()
    )

async def handle_yesimsure(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    photo = InputFile("images/infocargo.png")
    await callback.message.answer_photo(
        photo=photo,
        caption=(
            "🧮 <b>Это калькулятор стоимости.</b>\n"
            "В нем Вы можете сделать расчет стоимости товара вместе с доставкой.\n\n"
            "⚠️<b>Товары с знаком ≈ НЕ ВЫКУПАЮТСЯ</b>\n\n"
            "Укажите способ доставки ниже:"),
        parse_mode="HTML",
        reply_markup=get_delivery_keyboard()
    )

async def handle_delivery(callback: types.CallbackQuery, state: FSMContext):
    delivery_type = callback.data.replace("calc_delivery_", "")
    await state.update_data(delivery_type=delivery_type)
    await callback.message.delete()
    await callback.message.answer("Пожалуйста, вставьте фото товара, как показано на примере:")
    await OrderStates.waiting_for_photo.set()

async def handle_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото товара.")
        return
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer("Теперь отправьте ссылку на товар")
    await OrderStates.waiting_for_link.set()

async def handle_link(message: types.Message, state: FSMContext):
    if not re.match(r"https?://[^\s]+", message.text):
        await message.answer("Пожалуйста, отправьте корректную ссылку на товар")
        return
    await state.update_data(link=message.text)
    await message.answer("Укажите размер товара")
    await OrderStates.waiting_for_size.set()

async def handle_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("Теперь укажите стоимость товара в юанях")
    await OrderStates.waiting_for_price.set()

async def handle_price(message: types.Message, state: FSMContext):
    try:
        price_yuan = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму в юанях")
        return

    user_data = await state.get_data()
    delivery_type = user_data.get("delivery_type")

    # Стоимость доставки по категориям
    delivery_cost = {
        "standard": 550,
        "express": 2800
    }.get(delivery_type, 0)

    final_price = (price_yuan + 30) * YUAN_RATE + delivery_cost + 1000 + (150 if delivery_type == "standard" else 0)

    await state.update_data(price_yuan=price_yuan, final_price=final_price)

    await message.answer(
        f"📦 <b>Заявка на заказ</b>\n"
        f"Ссылка: {user_data.get('link')}\n"
        f"Размер: {user_data.get('size')}\n"
        f"Тип доставки: {'Авто' if delivery_type == 'standard' else 'Авиа'}\n"
        f"Стоимость в юанях: {price_yuan}¥\n"
        f"Итоговая цена: <b>{round(final_price)}₽</b>",
        parse_mode="HTML",
        reply_markup=get_final_keyboard()
    )

    await OrderStates.confirming_order.set()

def register_order_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_order, lambda c: c.data == "order", state="*")
    dp.register_callback_query_handler(handle_further, lambda c: c.data == "further", state="*")
    dp.register_callback_query_handler(handle_yesimsure, lambda c: c.data == "yesimsure", state="*")
    dp.register_callback_query_handler(handle_delivery, lambda c: c.data.startswith("calc_delivery_"), state="*")
    dp.register_message_handler(handle_photo, content_types=types.ContentType.PHOTO, state=OrderStates.waiting_for_photo)
    dp.register_message_handler(handle_link, state=OrderStates.waiting_for_link)
    dp.register_message_handler(handle_size, state=OrderStates.waiting_for_size)
    dp.register_message_handler(handle_price, state=OrderStates.waiting_for_price)
