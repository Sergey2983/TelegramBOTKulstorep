from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Оформить заказ"), KeyboardButton("Калькулятор стоимости"))
    return keyboard

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🚘 Стандартная доставка"))
    keyboard.add(KeyboardButton("✈️ Экспресс-доставка"))
    keyboard.add(KeyboardButton("📤 Оптовая доставка"))
    keyboard.add(KeyboardButton("📋 Прайс-лист"), KeyboardButton("📞 Контакты"))
    return keyboard

def get_standard_categories():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👟 Обувь"))
    keyboard.add(KeyboardButton("👕 Одежда / аксессуары"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_express_categories():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👕 Футболки"))
    keyboard.add(KeyboardButton("🧥 Пуховики"))
    keyboard.add(KeyboardButton("👟 Обувь"))
    keyboard.add(KeyboardButton("👔 Одежда / аксессуары"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_wholesale_categories():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📦 По весу (550 ₽/кг)"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_back_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_order_confirmation_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Подтвердить заказ"), KeyboardButton("Отмена"))
    return keyboard
