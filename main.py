import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from keyboards import (
    get_start_keyboard, get_main_keyboard, get_standard_categories, get_express_categories,
    get_wholesale_categories, get_back_keyboard, get_order_confirmation_keyboard
)

# Загружаем переменные окружения из .env
TOKEN = "6787101762:AAHSFF2wBo1I2N9tdd_U-7OozAjAlt5iqnk"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Актуальный курс юаня
YUAN_RATE = 12.5

# Таблица тарифов доставки
delivery_costs = {
    "🚘 Стандартная доставка": {"👟 Обувь": 1100, "👕 Одежда / аксессуары": 550},
    "✈️ Экспресс-доставка": {"👕 Футболки": 2000, "🧥 Пуховики": 3000, "👟 Обувь": 4200, "👔 Одежда / аксессуары": 2800},
    "📤 Оптовая доставка": {"📦 По весу (550 ₽/кг)": 0}
}

# Словарь для хранения данных пользователя (для теста)
user_data = {}

##########################################
# FSM для потока "Калькулятор стоимости"
##########################################
class PriceCalcStates(StatesGroup):
    waiting_for_shipping = State()
    waiting_for_category = State()
    waiting_for_price = State()

##########################################
# FSM для потока "Оформить заказ"
##########################################
class OrderStates(StatesGroup):
    waiting_for_shipping = State()
    waiting_for_category = State()
    waiting_for_photo = State()
    waiting_for_link = State()
    waiting_for_size = State()
    waiting_for_price = State()
    waiting_for_confirmation = State()

##########################################
# Стартовая команда – выбор действия
##########################################
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    user_data[message.from_user.id] = {}
    welcome_text = (
        "👋 Привет! Выберите действие:\n\n"
        "🛒 <b>Оформить заказ</b>.\n"
        "📊 <b>Калькулятор стоимости</b> — рассчитать стоимость товара по тарифам доставки.\n\n"
        f"🔹 Актуальный курс юаня: <b>{YUAN_RATE} ₽</b>"
    )
    await message.answer(welcome_text, reply_markup=get_start_keyboard(), parse_mode="HTML")

##########################################
# Поток "Калькулятор стоимости"
##########################################
@dp.message_handler(Text(equals="Калькулятор стоимости"))
async def start_price_calc(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = {"flow": "calc"}
    await message.answer("Выберите тип доставки:", reply_markup=get_main_keyboard())
    await PriceCalcStates.waiting_for_shipping.set()

@dp.message_handler(state=PriceCalcStates.waiting_for_shipping)
async def price_calc_shipping(message: types.Message, state: FSMContext):
    if message.text == "📋 Прайс-лист":
        price_list = (
            "🚘 <b>Стандартная доставка (20–25 дней):</b>\n"
            " • Обувь – 1 100 ₽\n"
            " • Одежда / аксессуары – 550 ₽\n\n"
            "✈️ <b>Экспресс-доставка (около 10 дней):</b>\n"
            " • Футболки – 2 000 ₽\n"
            " • Одежда / аксессуары – 2 800 ₽\n"
            " • Обувь – 4 200 ₽\n"
            " • Пуховики – 3 000 ₽\n\n"
            "📤 <b>Оптовая доставка (от 6 позиций):</b>\n"
            "Стоимость рассчитывается по весу: 550 ₽/кг (по прибытии в Москву).\n\n"
            "🟡 <b>Страховка (по желанию)</b>\n"
            "3% от стоимости товара."
        )
        await message.answer(price_list, parse_mode="HTML")
        return
    if message.text == "📞 Контакты":
        await message.answer("📩 Связаться с администратором:\n🔹 Telegram: @admin\n🔹 Email: support@example.com")
        return
    if message.text not in ["🚘 Стандартная доставка", "✈️ Экспресс-доставка", "📤 Оптовая доставка"]:
        await message.answer("❌ Выберите один из предложенных вариантов!")
        return
    user_data[message.from_user.id]["shipping"] = message.text
    if message.text == "🚘 Стандартная доставка":
        await message.answer("Выберите категорию товара:", reply_markup=get_standard_categories())
    elif message.text == "✈️ Экспресс-доставка":
        await message.answer("Выберите категорию товара:", reply_markup=get_express_categories())
    else:
        await message.answer("Выберите категорию товара:", reply_markup=get_wholesale_categories())
    await PriceCalcStates.waiting_for_category.set()

@dp.message_handler(state=PriceCalcStates.waiting_for_category)
async def price_calc_category(message: types.Message, state: FSMContext):
    shipping = user_data[message.from_user.id].get("shipping", "")
    valid_categories = []
    if shipping == "🚘 Стандартная доставка":
        valid_categories = ["👟 Обувь", "👕 Одежда / аксессуары"]
    elif shipping == "✈️ Экспресс-доставка":
        valid_categories = ["👕 Футболки", "🧥 Пуховики", "👟 Обувь", "👔 Одежда / аксессуары"]
    elif shipping == "📤 Оптовая доставка":
        valid_categories = ["📦 По весу (550 ₽/кг)"]
    if message.text == "⬅️ Назад":
        await start_command(message, state)
        return
    if message.text not in valid_categories:
        await message.answer("❌ Выберите одну из категорий!")
        return
    user_data[message.from_user.id]["category"] = message.text
    await message.answer("Введите стоимость товара в юанях (¥):", reply_markup=get_back_keyboard())
    await PriceCalcStates.waiting_for_price.set()

@dp.message_handler(state=PriceCalcStates.waiting_for_price)
async def price_calc_price(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await start_command(message, state)
        return
    try:
        price_yuan = float(message.text)
    except ValueError:
        await message.answer("❌ Введите число для стоимости!")
        return
    user_data[message.from_user.id]["price_yuan"] = price_yuan
    shipping = user_data[message.from_user.id].get("shipping", "")
    category = user_data[message.from_user.id].get("category", "")
    base_price = (price_yuan + 30) * YUAN_RATE + 1000
    delivery_price = delivery_costs.get(shipping, {}).get(category, 0)
    if shipping == "🚘 Стандартная доставка":
        delivery_price += 150
    final_price = base_price + delivery_price
    await message.answer(f"✅ Итоговая стоимость: <b>{final_price:.2f} ₽</b>", parse_mode="HTML")
    await start_command(message, state)

##########################################
# Поток "Оформить заказ"
##########################################
@dp.message_handler(Text(equals="Оформить заказ"))
async def start_order(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = {"flow": "order"}
    await message.answer("Выберите тип доставки:", reply_markup=get_main_keyboard())
    await OrderStates.waiting_for_shipping.set()

@dp.message_handler(state=OrderStates.waiting_for_shipping)
async def order_shipping(message: types.Message, state: FSMContext):
    if message.text == "📋 Прайс-лист":
        price_list = (
            "🚘 <b>Стандартная доставка (20–25 дней):</b>\n"
            " • Обувь – 1 100 ₽\n"
            " • Одежда / аксессуары – 550 ₽\n\n"
            "✈️ <b>Экспресс-доставка (около 10 дней):</b>\n"
            " • Футболки – 2 000 ₽\n"
            " • Одежда / аксессуары – 2 800 ₽\n"
            " • Обувь – 4 200 ₽\n"
            " • Пуховики – 3 000 ₽\n\n"
            "📤 <b>Оптовая доставка (от 6 позиций):</b>\n"
            "Стоимость рассчитывается по весу: 550 ₽/кг (по прибытии в Москву).\n\n"
            "🟡 <b>Страховка (по желанию)</b>\n"
            "3% от стоимости товара."
        )
        await message.answer(price_list, parse_mode="HTML")
        return
    if message.text == "📞 Контакты":
        await message.answer("📩 Связаться с администратором:\n🔹 Telegram: @admin\n🔹 Email: support@example.com")
        return
    if message.text not in ["🚘 Стандартная доставка", "✈️ Экспресс-доставка", "📤 Оптовая доставка"]:
        await message.answer("❌ Выберите один из предложенных вариантов!")
        return
    user_data[message.from_user.id]["shipping"] = message.text
    if message.text == "🚘 Стандартная доставка":
        await message.answer("Выберите категорию товара:", reply_markup=get_standard_categories())
    elif message.text == "✈️ Экспресс-доставка":
        await message.answer("Выберите категорию товара:", reply_markup=get_express_categories())
    else:
        await message.answer("Выберите категорию товара:", reply_markup=get_wholesale_categories())
    await OrderStates.waiting_for_category.set()

@dp.message_handler(state=OrderStates.waiting_for_category)
async def order_category(message: types.Message, state: FSMContext):
    shipping = user_data[message.from_user.id].get("shipping", "")
    valid_categories = []
    if shipping == "🚘 Стандартная доставка":
        valid_categories = ["👟 Обувь", "👕 Одежда / аксессуары"]
    elif shipping == "✈️ Экспресс-доставка":
        valid_categories = ["👕 Футболки", "🧥 Пуховики", "👟 Обувь", "👔 Одежда / аксессуары"]
    elif shipping == "📤 Оптовая доставка":
        valid_categories = ["📦 По весу (550 ₽/кг)"]
    if message.text == "⬅️ Назад":
        await start_command(message, state)
        return
    if message.text not in valid_categories:
        await message.answer("❌ Выберите одну из категорий!")
        return
    user_data[message.from_user.id]["category"] = message.text
    await message.answer("Пришлите фото товара:")
    await OrderStates.waiting_for_photo.set()

@dp.message_handler(content_types=['photo'], state=OrderStates.waiting_for_photo)
async def order_photo(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    user_data[message.from_user.id]["photo_file_id"] = photo_file_id
    await message.answer("Пришлите ссылку на товар:")
    await OrderStates.waiting_for_link.set()

@dp.message_handler(state=OrderStates.waiting_for_link)
async def order_link(message: types.Message, state: FSMContext):
    if not (message.text.startswith("http://") or message.text.startswith("https://")):
        await message.answer("❌ Введите корректную ссылку (начинается с http:// или https://)")
        return
    user_data[message.from_user.id]["product_link"] = message.text
    await message.answer("Пришлите размер товара:")
    await OrderStates.waiting_for_size.set()

@dp.message_handler(state=OrderStates.waiting_for_size)
async def order_size(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["size"] = message.text
    await message.answer("Введите стоимость товара в юанях (¥):", reply_markup=get_back_keyboard())
    await OrderStates.waiting_for_price.set()

@dp.message_handler(state=OrderStates.waiting_for_price)
async def order_price(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await start_command(message, state)
        return
    try:
        price_yuan = float(message.text)
    except ValueError:
        await message.answer("❌ Введите число для стоимости!")
        return
    user_data[message.from_user.id]["price_yuan"] = price_yuan

    # Расчёт итоговой стоимости
    shipping = user_data[message.from_user.id].get("shipping", "")
    category = user_data[message.from_user.id].get("category", "")
    base_price = (price_yuan + 30) * YUAN_RATE + 1000
    delivery_price = delivery_costs.get(shipping, {}).get(category, 0)
    if shipping == "🚘 Стандартная доставка":
        delivery_price += 150
    final_price = base_price + delivery_price
    user_data[message.from_user.id]["final_price"] = final_price

    # Формирование сводки заказа
    summary = (
        f"📝 <b>Сводка заказа:</b>\n"
        f"Тип доставки: {user_data[message.from_user.id].get('shipping', 'Не указано')}\n"
        f"Категория: {user_data[message.from_user.id].get('category', 'Не указано')}\n"
        f"Ссылка: {user_data[message.from_user.id].get('product_link', 'Не указана')}\n"
        f"Размер: {user_data[message.from_user.id].get('size', 'Не указан')}\n"
        f"Стоимость в ¥: {price_yuan}\n"
        f"Итоговая стоимость: {final_price:.2f} ₽"
    )
    # Отправка одного сообщения с фото и подписью (сводкой заказа)
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=user_data[message.from_user.id]["photo_file_id"],
        caption=summary,
        parse_mode="HTML"
    )
    await message.answer("Подтвердите заказ:", reply_markup=get_order_confirmation_keyboard())
    await OrderStates.waiting_for_confirmation.set()

@dp.message_handler(state=OrderStates.waiting_for_confirmation)
async def order_confirmation(message: types.Message, state: FSMContext):
    if message.text == "Подтвердить заказ":
        # Здесь можно сохранить заказ в БД и сгенерировать уникальный номер
        order_id = 12345  # Эмуляция номера заказа
        await message.answer(f"✅ Заказ подтвержден! Ваш номер заказа: {order_id}")
    elif message.text == "Отмена":
        await message.answer("Заказ отменен.")
    else:
        await message.answer("❌ Выберите один из вариантов!")
        return
    await start_command(message, state)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
