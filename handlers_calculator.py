from aiogram import types, Dispatcher
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from states import CalculatorStates
from aiogram.types import InputFile
from keyboards import (
    get_delivery_keyboard,
    get_category_keyboard,
    get_main_menu_keyboard, get_start_inline_keyboard
)


YUAN_RATE = 12.8  # курс юаня

from aiogram.types import InputFile


def register_calculator_handlers(dp: Dispatcher):
    @dp.callback_query_handler(lambda c: c.data in ["calculator", "to_back"], state="*")
    async def calculator_start(callback: types.CallbackQuery, state: FSMContext):
        # Удаляем исходное сообщение
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

        # Загружаем фото (укажите корректный путь к файлу)
        photo = InputFile("images/infocargo.png")

        # Отправляем новое сообщение с фото, подписью и клавиатурой
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

        await CalculatorStates.choosing_delivery.set()

    # Выбор типа доставки
    @dp.callback_query_handler(lambda c: c.data.startswith("calc_delivery"), state=CalculatorStates.choosing_delivery)
    async def choose_delivery(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

        delivery_type = callback.data.split("_")[-1]
        await state.update_data(delivery=delivery_type)
        await CalculatorStates.choosing_category.set()
        await callback.message.answer("👕 Выберите категорию товара:", reply_markup=get_category_keyboard(delivery_type))

    # Выбор категории
    @dp.callback_query_handler(lambda c: c.data.startswith("calc_category"), state=CalculatorStates.choosing_category)
    async def choose_category(callback: types.CallbackQuery, state: FSMContext):
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

        category = callback.data.split("_")[-1]
        await state.update_data(category=category)
        await CalculatorStates.entering_price.set()
        await callback.message.answer("Введите сумму в юанях для расчета:")

    # Обработка суммы и вывод результата
    @dp.message_handler(state=CalculatorStates.entering_price)
    async def process_price(message: types.Message, state: FSMContext):
        try:
            yuan_price = float(message.text)
        except ValueError:
            return await message.answer("❌ Введите корректную сумму в юанях.")

        data = await state.get_data()
        delivery = data.get("delivery")
        category = data.get("category")

        # Словари переводов
        delivery_translations = {
            "standard": "Авто доставка",
            "express": "Авиа доставка",
            "bulk": "Оптовая доставка"
        }

        category_translations = {
            "shoes": "Обувь",
            "clothes": "Одежда/аксессуары",
            "tshirts": "Футболки",
            "jackets": "Пуховики",
            "bulk": "Оптовая доставка"
        }

        # Стоимость доставки (таблица тарифов)
        delivery_prices = {
            "standard": {"clothes": 550, "shoes": 1100},
            "express": {"tshirts": 2000, "clothes": 2800, "shoes": 4200, "jackets": 3000}
        }

        delivery_price = delivery_prices[delivery].get(category, 0)
        total = (yuan_price + 30) * YUAN_RATE + delivery_price + 1000

        # Используем русские наименования для вывода
        delivery_rus = delivery_translations.get(delivery, delivery.capitalize())
        category_rus = category_translations.get(category, category.capitalize())

        result = (
            f"<b>Расчёт:</b>\n"
            f"📦 Тип доставки: {delivery_rus}\n"
            f"📂 Категория товара: {category_rus}\n"
            f"💴 Сумма в юанях: {yuan_price}\n"
            f"💰 Итог в рублях: <b>{round(total)} ₽</b>"
        )

        await message.answer(result, reply_markup=get_main_menu_keyboard())
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == "main_menu1", state="*")
    async def main_menu_handler(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await callback.message.delete()
    # Указываем путь к стартовой картинке (тот же, что и в /start)
        photo = InputFile("images/start_logo.png")
        await callback.message.answer_photo(
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

    @dp.callback_query_handler(lambda c: c.data == "main_menu", state="*")
    async def main_menu_handler(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()

        # Указываем путь к стартовой картинке (тот же, что и в /start)
        photo = InputFile("images/start_logo.png")
        await callback.message.answer_photo(
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

