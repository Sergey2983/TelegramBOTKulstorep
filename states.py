from aiogram.dispatcher.filters.state import State, StatesGroup

class CalculatorStates(StatesGroup):
    choosing_delivery = State()   # Выбор типа доставки
    choosing_category = State()   # Выбор категории товара
    entering_price = State()      # Ввод суммы в юанях

class OrderStates(StatesGroup):
    choosing_delivery = State()     # Выбор доставки
    choosing_category = State()     # Выбор категории товара (вставляем!)
    waiting_for_photo = State()     # Фото товара
    waiting_for_link = State()      # Ссылка на товар
    waiting_for_size = State()      # Размер
    waiting_for_price = State()     # Цена
    confirming_order = State()      # Подтверждение заказа
    order_paid = State()
