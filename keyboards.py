from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_order_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="ДАЛЕЕ", callback_data="further")
    )

def get_next_step_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text="Да уверен!", callback_data="yesimsure")
    )

def get_start_inline_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🛒 Оформить заказ (Alpha)", callback_data="order"),
        InlineKeyboardButton("📊 Калькулятор стоимости", callback_data="calculator"),
        InlineKeyboardButton(text="💌 Отзывы о работе с нами", url="https://t.me/KulStorePFeedBack"),
        InlineKeyboardButton("📞 Помощь", url="https://t.me/kulstoree"),
        InlineKeyboardButton(text="📲 Установить Poizon на Android", url="https://m.anxinapk.com/rj/12201303.html"),
        InlineKeyboardButton(text="🍎 Установить Poizon на IOS", url="https://apps.apple.com/ru/app/%E5%BE%97%E7%89%A9-%E5%BE%97%E5%88%B0%E8%BF%90%E5%8A%A8x%E6%BD%AE%E6%B5%81x%E5%A5%BD%E7%89%A9/id1012871328")
    )

def get_delivery_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🚘 Авто доставка (14-20 дней)", callback_data="calc_delivery_standard"),
        InlineKeyboardButton("✈️ Авиа доставка (5-7 дней)", callback_data="calc_delivery_express"),
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu1")
    )

def get_category_keyboard(delivery_type):
    if delivery_type == "standard":
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("👕 Одежда / Аксессуары", callback_data="calc_category_clothes"),
            InlineKeyboardButton("👟 Обувь", callback_data="calc_category_shoes"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="to_back")
        )
    else:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("👕 Футболки", callback_data="calc_category_tshirts"),
            InlineKeyboardButton("👕 Одежда / Аксессуары", callback_data="calc_category_clothes"),
            InlineKeyboardButton("👟 Обувь", callback_data="calc_category_shoes"),
            InlineKeyboardButton("🧥 Пуховики", callback_data="calc_category_jackets"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="to_back")
        )

def get_main_menu_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    )

def get_final_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Оформить заказ', callback_data="*"),
        InlineKeyboardButton(text='Главное меню', callback_data="main_menu1")
    )