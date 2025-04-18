from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from handlers_order import register_order_handlers
from handlers_calculator import register_calculator_handlers
from keyboards import get_start_inline_keyboard

from aiogram.dispatcher.filters import Command

API_TOKEN = "6787101762:AAHSFF2wBo1I2N9tdd_U-7OozAjAlt5iqnk"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())


register_order_handlers(dp)
register_calculator_handlers(dp)
# Приветственное сообщение
from aiogram.types import InputFile

@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    photo = InputFile("images/start_logo.png")  # укажи корректный путь к картинке
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
