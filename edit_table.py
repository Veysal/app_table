import sqlite3
import flet as ft

# Функция для обновления данных в БД
def update_order_in_db(order_id, new_date,new_payment_status):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders
        SET order_date = ?, payment_status = ?
        WHERE order_id = ?
    """, (new_date,new_payment_status, order_id)
    )
    conn.commit()
    conn.close()

# Функция для поиска заказа по ID
def get_order_by_id(order_id):
    conn = sqlite3
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders
        WHERE order_id = ?
    """, (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order