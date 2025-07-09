import sqlite3
import csv
import os

DB_NAME = "work_tracker.db"

# Инициализация базы данных SQLite3
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL UNIQUE,
            order_date TEXT NOT NULL,
            client_name TEXT NOT NULL,
            work_status TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            payment_amount REAL
        )
    """
    )
    conn.commit()
    conn.close()

# Функция для добавления данных в базу данных
def add_order_to_db(order_id, order_date, client_name, work_status, payment_status, payment_amount):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_id, order_date, client_name, work_status, payment_status, payment_amount)
            VALUES (?, ?, ?, ?, ?, ?)
    """,(order_id, order_date, client_name, work_status, payment_status, payment_amount))
        conn.commit()

# Экспортируем данные из БД в csv файл
def export_to_csv():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            # Выбираем столбцы в нужном порядке, исключая первичный ключ `id`
            cursor.execute("SELECT order_id, order_date, client_name, work_status, payment_status, payment_amount FROM orders")
            rows = cursor.fetchall()
            headers = ["ID заказа", "Дата заказа", "Имя клиента", "Статус работы", "Статус оплаты", "Сумма оплаты"]
            file_path =("orders.csv")
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            return file_path
    except Exception as ex:
        print(f"Ошибка при экспорте в CSV: {ex}")
        return None

# Функция для получения всех заказов
def get_all_orders(sort_column="id", sort_ascending=True):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        order = "ASC" if sort_ascending else "DESC"

        # Карта для сопоставления имен столбцов из UI с именами в БД
        column_map = {
            "order_id": "order_id",
            "order_date": "order_date",
            "client_name": "client_name",
            "work_status": "work_status",
            "payment_status": "payment_status",
            "payment_amount": "payment_amount",
            "id": "id"  # Сортировка по умолчанию
        }
        db_column = column_map.get(sort_column, "id")

        # Особая обработка для сортировки по дате в формате ДД.ММ.ГГГГ
        if db_column == "order_date":
            order_by_clause = f"ORDER BY substr(order_date, 7, 4) {order}, substr(order_date, 4, 2) {order}, substr(order_date, 1, 2) {order}"
        else:
            order_by_clause = f"ORDER BY {db_column} {order}"

        query = f"SELECT * FROM orders {order_by_clause}"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

def get_aggregation_summary():
    """Получает сводку по нескольким агрегированным значениям за один запрос."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
        SELECT
            COUNT(*) AS total_orders,
            COALESCE(SUM(payment_amount), 0) AS total_payment,
            COALESCE(AVG(payment_amount), 0) AS average_payment,
            COALESCE(SUM(CASE WHEN work_status = 'В работе' THEN 1 ELSE 0 END), 0) AS in_progress_orders,
            COALESCE(SUM(CASE WHEN work_status = 'Выполнено' THEN 1 ELSE 0 END), 0) AS completed_orders
        FROM orders
        """
        cursor.execute(query)
        row = cursor.fetchone()
        # fetchone() для агрегирующего запроса без GROUP BY всегда вернет одну строку.
        # Преобразуем в dict, чтобы обеспечить согласованный тип возвращаемого значения
        # для уровня пользовательского интерфейса и избежать ошибок с None.
        return dict(row)

# Агрегирующие функции
def get_total_payment():
    """Получаем общую сумму всех оплат клиентов"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(payment_amount) FROM orders")
        total = cursor.fetchone()[0]
        return total or 0

def get_average_payment():
    """Получаем среднюю сумму всех оплат клиентов"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(payment_amount) FROM orders")
        average = cursor.fetchone()[0]
        return average or 0

def get_max_payment():
    """Получаем максимальную сумму оплаты клиента"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Используем подзапрос для эффективности
        cursor.execute("SELECT * FROM orders WHERE payment_amount = (SELECT MAX(payment_amount) FROM orders)")
        rows = cursor.fetchall()
        return rows

def get_min_payment():
    """Получаем минимальную сумму оплаты клиента"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE payment_amount = (SELECT MIN(payment_amount) FROM orders)")
        rows = cursor.fetchall()
        return rows

# Функция для поиска по имени клиента
def search_orders_by_client_name(client_name):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Добавляем % для поиска по частичному совпадению
        cursor.execute("SELECT * FROM orders WHERE client_name LIKE ?", (f"%{client_name}%",))
        rows = cursor.fetchall()
        return rows

# Функция для обновления данных в БД
def update_order_in_db(order_id, new_date,new_payment_status):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET order_date = ?, payment_status = ?
            WHERE order_id = ?
        """, (new_date,new_payment_status, order_id))
        conn.commit()

# Функция для удаления заказа из БД
def delete_order_from_db(order_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        conn.commit()

# Функция для поиска заказа по ID
def get_order_by_id(order_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM orders WHERE order_id = ?""", (order_id,))
        order = cursor.fetchone()
        return order