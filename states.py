from aiogram.dispatcher.filters.state import State, StatesGroup

class CalculatorStates(StatesGroup):
    choosing_delivery = State()   # Выбор типа доставки
    choosing_category = State()   # Выбор категории товара
    entering_price = State()      # Ввод суммы в юанях

class OrderStates(StatesGroup):
    order_info = State()  # Пока placeholder для оформления заказа
