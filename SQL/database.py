import sqlite3
import os

# Определение пути к базе данных (можно изменить на абсолютный путь)


# Подключение к базе данных и создание курсора
conn = sqlite3.connect('SQL/database.db')  # или укажи путь к базе данных
cursor = conn.cursor()

# Создание таблицы accounts
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    cart_id TEXT
)
""")

# Создание таблицы orders
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link TEXT,
    size TEXT,
    category_order TEXT,
    type_cargo TEXT,
    price_yuan REAL,
    final_price REAL,
    photo_id TEXT,
    order_number INTEGER,
    user_id INTEGER,
    created_at TEXT
)
""")

# Подтверждаем изменения и закрываем соединение
conn.commit()
conn.close()

print("Таблицы созданы или уже существуют.")
