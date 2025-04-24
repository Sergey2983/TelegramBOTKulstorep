# config.py
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
