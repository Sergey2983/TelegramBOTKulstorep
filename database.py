import sqlite3

# Подключение к базе данных и создание таблиц, если они ещё не созданы
conn = sqlite3.connect("database.db")
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




conn.commit()
conn.close()

