# loader.py
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

ADMIN_IDS = [538734522]  # Впиши свой Telegram user_id

bot = Bot(token="6787101762:AAHSFF2wBo1I2N9tdd_U-7OozAjAlt5iqnk", parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
